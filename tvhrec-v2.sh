#!/bin/bash

# Colors for output
RED='\033[1;31m'
GREEN='\033[1;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Config file path
CONFIG_FILE="$HOME/.tvhrec.conf"

# Default TVHeadend settings
DEFAULT_URL="http://127.0.0.1:9981"
TVH_URL=""
TVH_USER=""
TVH_PASS=""

# Declare associative array to store channel numbers and UUIDs
declare -A channel_map

# Function to load saved servers
load_servers() {
    if [ ! -f "$CONFIG_FILE" ]; then
        return 1
    fi
    return 0
}

# Function to save server configuration
save_server() {
    local server_name=$1
    local server_url=$2
    local username=$3
    local password=$4

    # Create directory if it doesn't exist
    mkdir -p "$(dirname "$CONFIG_FILE")"

    # Encrypt password with base64 (basic obfuscation)
    local encoded_pass=$(echo -n "$password" | base64)

    # Add server to config file
    echo "$server_name|$server_url|$username|$encoded_pass" >> "$CONFIG_FILE"
    echo -e "${GREEN}Server '$server_name' saved successfully!${NC}"
}

# Function to list saved servers
list_servers() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}No saved servers found.${NC}"
        return 1
    fi

    echo -e "\n${BLUE}Saved Servers:${NC}"
    echo -e "${YELLOW}-------------${NC}"
    
    local counter=1
    while IFS='|' read -r name url user pass; do
        echo -e "${GREEN}$counter: $name ($url)${NC}"
        ((counter++))
    done < "$CONFIG_FILE"
    
    return 0
}

# Function to select or add server
select_server() {
    while true; do
        echo -e "\n${BLUE}Server Selection:${NC}"
        echo -e "${YELLOW}1: Use saved server${NC}"
        echo -e "${YELLOW}2: Add new server${NC}"
        read -r choice

        case $choice in
            1)
                if list_servers; then
                    echo -e "\n${BLUE}Enter server number:${NC}"
                    read -r server_num
                    
                    # Validate input
                    if ! [[ "$server_num" =~ ^[0-9]+$ ]]; then
                        echo -e "${RED}Please enter a valid number${NC}"
                        continue
                    fi
                    
                    # Load selected server configuration
                    local counter=1
                    while IFS='|' read -r name url user pass; do
                        if [ "$counter" -eq "$server_num" ]; then
                            TVH_URL=$url
                            TVH_USER=$user
                            TVH_PASS=$(echo -n "$pass" | base64 -d)
                            echo -e "${GREEN}Selected server: $name${NC}"
                            return 0
                        fi
                        ((counter++))
                    done < "$CONFIG_FILE"
                    
                    echo -e "${RED}Invalid server number${NC}"
                else
                    echo -e "${YELLOW}No saved servers. Please add a new server.${NC}"
                    select_server
                fi
                ;;
            2)
                echo -e "${BLUE}Enter server name:${NC}"
                read -r server_name
                
                echo -e "${BLUE}Enter TVHeadend server address (example: $DEFAULT_URL):${NC}"
                read -r server_url
                TVH_URL=${server_url:-$DEFAULT_URL}

                echo -e "${BLUE}Enter username (press Enter for none):${NC}"
                read -r username
                TVH_USER=$username

                echo -e "${BLUE}Enter password (press Enter for none):${NC}"
                read -rs password
                echo # New line after password input
                TVH_PASS=$password

                # Save new server
                save_server "$server_name" "$TVH_URL" "$TVH_USER" "$TVH_PASS"
                return 0
                ;;
            *)
                echo -e "${RED}Please enter 1 or 2${NC}"
                ;;
        esac
    done
}

# Function to test server connection
test_connection() {
    # Construct curl auth options
    if [ -n "$TVH_USER" ] || [ -n "$TVH_PASS" ]; then
        AUTH_OPTS="-u $TVH_USER:$TVH_PASS"
    else
        AUTH_OPTS=""
    fi

    # Test connection
    echo -e "${YELLOW}Testing connection to server...${NC}"
    if curl -s $AUTH_OPTS "$TVH_URL/api/serverinfo" >/dev/null; then
        echo -e "${GREEN}Successfully connected to server!${NC}"
        return 0
    else
        echo -e "${RED}Failed to connect to server. Please check your settings.${NC}"
        return 1
    fi
}

# Function to fetch and list channels
list_channels() {
    echo -e "${GREEN}Fetching channel list...${NC}"
    
    # Fetch channel grid and store in temporary file
    CHANNELS=$(curl -s $AUTH_OPTS "$TVH_URL/api/channel/grid" | jq '.entries[] | {uuid, name}')
    
    echo -e "\n${BLUE}Available Channels:${NC}"
    echo -e "${YELLOW}-------------------${NC}"
    
    # Counter for channel numbers
    counter=1
    
    # Process and display channels
    while IFS= read -r channel; do
        uuid=$(echo "$channel" | jq -r '.uuid')
        name=$(echo "$channel" | jq -r '.name')
        
        # Store UUID in associative array with counter as key
        channel_map[$counter]=$uuid
        
        # Display channel with number
        echo -e "${GREEN}$counter: $name${NC}"
        
        ((counter++))
    done < <(echo "$CHANNELS" | jq -c '.')
    
    # Store total number of channels
    total_channels=$((counter - 1))
}

# Function to select recording duration
select_duration() {
    while true; do
        echo -e "\n${BLUE}Select recording duration:${NC}"
        echo -e "${YELLOW}1: 30 minutes${NC}"
        echo -e "${YELLOW}2: 1 hour${NC}"
        echo -e "${YELLOW}3: 2 hours${NC}"
        echo -e "${YELLOW}4: 3 hours${NC}"
        echo -e "${YELLOW}5: 4 hours${NC}"
        read -r duration_choice

        case $duration_choice in
            1) DURATION=$((30 * 60)); break;;
            2) DURATION=$((60 * 60)); break;;
            3) DURATION=$((120 * 60)); break;;
            4) DURATION=$((180 * 60)); break;;
            5) DURATION=$((240 * 60)); break;;
            *) echo -e "${RED}Please enter a number between 1 and 5${NC}";;
        esac
    done

    # Convert duration to hours and minutes for display
    hours=$((DURATION / 3600))
    minutes=$(((DURATION % 3600) / 60))
    if [ $hours -gt 0 ] && [ $minutes -gt 0 ]; then
        duration_text="$hours hours and $minutes minutes"
    elif [ $hours -gt 0 ]; then
        duration_text="$hours hours"
    else
        duration_text="$minutes minutes"
    fi
}

# Function to initiate instant recording
record_channel() {
    while true; do
        echo -e "\n${BLUE}Enter the number of the channel to record (1-$total_channels):${NC}"
        read -r channel_number
        
        # Validate input is a number
        if ! [[ "$channel_number" =~ ^[0-9]+$ ]]; then
            echo -e "${RED}Please enter a valid number${NC}"
            continue
        fi
        
        # Check if number is within valid range
        if [ "$channel_number" -lt 1 ] || [ "$channel_number" -gt "$total_channels" ]; then
            echo -e "${RED}Please enter a number between 1 and $total_channels${NC}"
            continue
        fi
        
        # Get UUID from channel map
        CHANNEL_UUID="${channel_map[$channel_number]}"
        break
    done
    
    # Get recording duration
    select_duration
    
    echo -e "${YELLOW}Starting recording for $duration_text...${NC}"
    
    # API call to initiate recording
    RESPONSE=$(curl -s $AUTH_OPTS --data "conf={
        \"start\": $(date +%s),
        \"stop\": $(( $(date +%s) + DURATION )),
        \"channel\": \"$CHANNEL_UUID\",
        \"title\": {\"eng\": \"Instant Recording\"},
        \"subtitle\": {\"eng\": \"Recorded via Script\"}
    }" "$TVH_URL/api/dvr/entry/create")
    
    echo -e "\n${GREEN}Recording request sent successfully!${NC}"
}

# Main script logic
clear
echo -e "${RED}TVHeadend Instant Recorder${NC}"
echo -e "${YELLOW}---------------------------${NC}\n"

# Select or add server
select_server

# Test connection before proceeding
if test_connection; then
    list_channels
    record_channel
else
    exit 1
fi
