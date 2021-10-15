# aircrack-gui

Aircrack-gui is a python gui for [aicrack-ng](https://www.aircrack-ng.org/) using [Gtk 3.0](https://pygobject.readthedocs.io/en/latest/).

First priority was to make every step intuitive and easy)

## Requirements

PyGoObject version: > 3.38.0

Python version: 3 - stable; 2 - not tested;

## Installation

```
git clone https://github.com/Cod3dDOT/aircrack-gui
```

## Usage 

Run:

```
cd aircrack-gui
python3 aircrack-gui.py
```
If any interface will be found, a window will open with option to choose an interface, scan, open aircrack-ng or start airmon-ng.

Step 1: Set path (default: /home/SUDO_USER/Desktop/aircrack-ng/wifi/)

![main window](/demo/main_window.png)

Step 2: Press 'Scan', wait for ~5 seconds (the window will become unresponsive, thats normal). A window will show up with network list. Choose any network, check that it has WPA2 encryption (right now WEP/WPA1 are not implemented), hit 'Start Airmon-ng on BSSID: NETWORK_BSSID'.

![scanning window](/demo/scanning_window.png)

Step 3: Aireplay-ng window will show up. Set amount of deauth packets to send (default: 10) and wait for station to appear (you can choose if several are found or type in a station address manually). Hit 'Run deauth (aireplay-ng)'. If you see 'Success' on top of the window, then a hanshake was recieved successfuly. If not, try changing station or amount of packets.

P.S: If no stations are found, your signal strength is probably too low. Signal strength can be checked when you select your network in Step 2.

![aireplay-ng window](/demo/aireplay-ng_window.png)

Step 4: Now, you can close aireplay-ng window. In main window, press 'Open aircrack-ng', select .cap file (capture file located wherever you set it to in Step 1). Select a worlist, hit 'Start aircrack-ng / hashcat' and hope for the best ;)

P.S If you want to use hashcat, you need to convert your .cap to .hccapx (one way to do it is to visit [official hashcat conversion website](https://hashcat.net/cap2hashcat/)

![aireplay-ng window](/demo/aircrack-ng_window.png)

## Todo
- Change network scanning from nmcli to airmon-ng

## Changelog
- 0.0.5 --- Added automatic .cap to .22000 conversion when selecting hashcat and [hcxtools](https://github.com/ZerBea/hcxtools) are installed. Minor ui updates.

- 0.0.4 --- Removed unnecessary xterm windows (except for aircrack-ng/hashcat), fixed selected station deselecting/changing when updated.

- 0.0.3 --- Hashcat support.

- 0.0.2 --- README.md changes, etc.

- 0.0.1 --- Initial commit.