# TVHrec
A program to initiate instant recording for any channel with [TVheadend](https://tvheadend.org).

![TVHrec screenshot](screenshot.png)


## Why?
This app was created out of my frustration with finding an efficient way to instantly record a channel on TVheadend. Essentially, this app serves as a simplified, streamlined "record" button for TVheadend. The default TVheadend web UI doesn’t support instant recording for a channel unless there’s an EPG (Electronic Program Guide) available, and Android clients face similar limitations. The only workaround to start an immediate recording is by using Kodi, which isn’t the most convenient solution. This app aims to solve that by providing a one-tap recording option, giving users a much-needed quick and direct way to capture their desired content without waiting for schedules or guides.

## Features: 
- Add multiple servers
- Get channel list from server
- Set duration for recording
- Cross-platform - the app runs on Linux, macOS, Windows and Android (cli only, using termux)
- GUI and CLI versions available (cli version is linux only)

## Download
- Head to the [releases](https://github.com/mfat/TVHrec/releases/) section to download the latest version for your operating system.

## Installation

### Linux
- Linux users should download the executable file called [tvhrec-gui](https://github.com/mfat/TVHrec/releases/latest/download/tvhrec-gui) (for commandline version see below)
- - Make sure it's executable `chmod +x tvhrec-gui`
- - Double click the file to run it.

- If you use Debian or Ubuntu you can download the [deb package](https://github.com/mfat/TVHrec/releases/latest/download/tvhrec_amd64.deb) 

### Windows
- Download and run [tvhrec.exe](https://github.com/mfat/TVHrec/releases/latest/download/tvhrec.exe) from the releases section.


### GUI app for linux - manual install
Make sure python is installed.
Install rquired python modules:

- PyQt6
- requests

`pip3 install PyQt6 requests`

Download tvhrec-gui.py and run it:
`python3 tvhrec-gui.py`

### Commandline app for linux:
- If you use the deb package, both gui and cli versions are automatically installed.
- Download [tvhrec.sh](https://raw.githubusercontent.com/mfat/TVHrec/refs/heads/main/tvhrec-v2.sh) from the repo
- Make it executable `chmod +x tvhrec.sh`
- Run it with `./tvhrec.sh`

For systemwide installation:

- `sudo cp tvhrec.sh /usr/local/bin/tvhrec`
- `sudo chmod +x /usr/local/bin/tvhrec`

Now you can run `tvhrec` from anywhere.

## Android
- Download [tvhrec.sh](https://raw.githubusercontent.com/mfat/TVHrec/refs/heads/main/tvhrec-v2.sh) and run in termux

