#!/bin/bash

# Colors for output
RED='\033[1;31m'
GREEN='\033[1;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default TVHeadend settings
DEFAULT_URL="http://127.0.0.1:9981"
TVH_URL=""
TVH_USER=""
TVH_PASS=""

# Declare associative array to store channel numbers and UUIDs
declare -A channel_map

# Function to get server configuration
get_server_config() {
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
    else
        echo -e "${RED}Failed to connect to server. Please check your settings.${NC}"
        exit 1
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
get_server_config
list_channels
record_channel
