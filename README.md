# TVHrec
A program to initiate instant recording for any channel on your TVheadend server.

## Features: 
- Get channel list from server
- Choose duration for recording

## Installation

### Easy way: download linux executable
-Download the executable ([tvhrec-gui](https://github.com/mfat/TVHrec/raw/refs/heads/main/tvhrec-gui))
-Make sure it's executable `chmod +x tvhrec-gui`
-Double click the file to run it.

### Manual way: GUI linux app:
Make sure python is installed.
Install rquired python modules:
-PyQt6
-requests
-pyinstaller

`pip3 install PyQt6 requests pyinstaller`

Download tvhrec-gui.py and run it:
`python3 tvhrec-gui.py`

### Commandline app on linux:
Download tvhrec.sh
Make it executable chmod +x tvhrec.sh
Run it with `./tvhrec.sh`

For systemwide installation:
`sudo cp tvhrec.sh /usr/local/bin/tvhrec`
`sudo chmod +x /usr/local/bin/tvhrec`

Now you can run `tvhrec` from anywhere.




