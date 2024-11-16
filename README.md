# TVHrec
A program to initiate instant recording for any channel with [TVheadend](https://tvheadend.org).

![TVHrec screenshot](screenshot.png)

## Features: 
- Get channel list from server
- Choose duration for recording

## Download
- Head to the [releases]([/releases](https://github.com/mfat/TVHrec/releases/)) section to download the latest version for your operating system.
- 

## Installation

### GUI app for linux
- Linux users should download the executable file called [tvhrec-gui](https://github.com/mfat/TVHrec/releases/latest/download/tvhrec-gui)

- Make sure it's executable `chmod +x tvhrec-gui`

- Double click the file to run it.

### Windows app:
- Download and run tvhrec.exe from the [releases]([/releases](https://github.com/mfat/TVHrec/releases/)) section.

### GUI app for linux - manual install
Make sure python is installed.
Install rquired python modules:

- PyQt6
- requests
- pyinstaller

`pip3 install PyQt6 requests pyinstaller`

Download tvhrec-gui.py and run it:
`python3 tvhrec-gui.py`

### Commandline app on linux:
- Download [tvhrec.sh] from the repo
- Make it executable `chmod +x tvhrec.sh`
- Run it with `./tvhrec.sh`

For systemwide installation:

- `sudo cp tvhrec.sh /usr/local/bin/tvhrec`
- `sudo chmod +x /usr/local/bin/tvhrec`

Now you can run `tvhrec` from anywhere.




