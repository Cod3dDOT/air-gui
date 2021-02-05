# aircrack-gui

Aircrack-Gui is a Python gui for Aicrack written with help of Gtk 3.0.

First priority was to make every step intuitive and easy)

## Requirements

PyGoObject version: 3.36.0

Python version: 3

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

Step 1: Set path (default /home/SUDO_USER/Desktop/aircrack-ng/wifi/)
![main window](/demo/main_window.png)

Step 2: Press 'Scan', wait for ~3 seconds. A window will show up with network list. Choose any network, check that it has WPA2 encryption (right now WEP is not implemented), hit 'Start Airmon-ng on BSSID: NETWORK_BSSID'.
![scanning window](/demo/scanning_window.png)

Step 3: 2 windows will show up: airmon-ng (probably asking for password) and aireplay-ng. In aireplay-ng window, set amount of deauth packets to send (default 10) and wait for station to appear, then hit 'Autofill station BSSID' (you can also type it in manually). Hit 'Start aircrack-ng'. If after ~2 seconds on top of airmon-ng window you see 'WPA handshake...', you were successful.
![aireplay-ng window](/demo/aireplay-ng_window.png)

Step 4: Now, close all windows except main. Press 'Open Aircrack-ng', select .cap file (capture file located wherever you set it to in Step 1). Select a worlist, hit start aircrack-ng/hashcat and hope for the best).
![aireplay-ng window](/demo/aircrack-ng_window.png)

## Todo
1. Extra labels.
2. Add screenshots.
3. Comment out everything.

## Changelog
- 0.0.3 --- Hashcat support.

- 0.0.2 --- README changes, etc.

- 0.0.1 --- Initial commit.
