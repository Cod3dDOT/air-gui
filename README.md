# aircrack-gui

Aircrack-Gui is a Python gui for Aicrack written with help of Gtk 3.0.

First priority was to make every step intuitive and easy)

## Requirements

PyGoObject version: 3.36.0

Python version: >= 3

## Installation

```
git clone https://github.com/Cod3dDOT/aircrack-gui
```

## Usage 

Run:

```
python3 aircrack-gui.py
```
If any interface will be found, a window will open with option to choose an interface, scan, open aircrack-ng or start airmon-ng.

Step 1: Set path to where you want the folder with the name of the network you will airodump to be put in a field (defualt /home/SUDO_USER/Desktop/aircrack-ng/wifi/)

Step 2: Press 'Scan', wait for ~3 seconds. A window will show up with network list. Choose any network, check that it has WPA2 encryption (right now WEp encryption is not implemented), hit 'Start Airmon-ng on bssid: network bssid'.

Step 3: 2 windows will show up: airmon-ng (probably asking for password) and aireplay. In aireplay window, set deauth packets amount to send (default 2) and wait for station to appear, then hit 'Autofill station bssid' (you can also type it in manually). Hit 'Start aircrack-ng'. If after ~2 seconds on top of airmon-ng window you see 'WPA handshake...', you were successful.

Step 4: Now, close all windows except main. Press 'Open Aircrack-ng', select .cap file (capture file located wherever you set it to in Step 1). Select a worlist, hit start aircrack and hope for the best).

## Todo
1. Extra labels.
2. Add screenshots.
3. Comment out everything.

## Changelog
- 0.0.3 --- Hashcat support.

- 0.0.2 --- README changes, etc.

- 0.0.1 --- Initial commit.

## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0//)
