# aircrack-gui

Aircrack-gui is a python gui for [aircrack-ng](https://www.aircrack-ng.org/) using [gtk 3.0](https://pygobject.readthedocs.io/en/latest/).

The priority was to make every step intuitive and easy)

## Requirements

PyGoObject version: > 3.38.0

Python version: 3: stable, 2: not tested.

## Installation

```
git clone https://github.com/Cod3dDOT/aircrack-gui
cd aircrack-gui
pip install -r requirements.txt
```

## IMPORTANT

1. You must use aircrack-gui only on networks you have permission to.
2. As this tool is only a gui, it will not work if the tools it uses behind the scenes do not work: python, [aircrack-ng](https://www.aircrack-ng.org/)aircrack-ng, [hcxtools](https://github.com/ZerBea/hcxtools).

## Usage 

Run:

```
cd aircrack-gui
python3 aircrack-gui.py
```
If any interface will be found, a window will open with the option to choose an interface, scan, start airmon-ng or open aircrack-ng.

Step 1: Set path (default: /home/SUDO_USER/Desktop/aircrack-ng/wifi/)

![main window](/demo/main_window.png)

Step 2: Press 'Scan for networks', wait for ~5 seconds (the main window can become unresponsive, that's normal). A new window will show up with a network list. Choose desired network, check that it has WPA2 encryption (right now WEP/WPA1 are not implemented), hit 'Start Airmon-ng on BSSID: NETWORK_BSSID'.

![scanning window](/demo/scanning_window.png)

Step 3: Aireplay-ng window will show up. Set amount of deauth packets to send (default: 10) and wait for station to appear (you can choose if several are found or type in a station mac address manually (format: xx-xx, xx:xx, xxxx)). Hit 'Run deauth (aireplay-ng)'. If you see 'Success' on top of the window, then a handshake was received successfully. If not, try changing the station or amount of packets.

P.S: If no stations are found, your signal strength is probably too low. Signal strength can be checked when you select your network in Step 2 and is measured from 0 to 100, higher being better.

![aireplay-ng window](/demo/aireplay-ng_window.png)

Step 4: Now, you can close aireplay-ng window. In the main window, press 'Open aircrack-ng', select .cap file (capture file located wherever you set it to in Step 1). Select a wordlist, hit 'Start aircrack-ng / hashcat' and hope for the best ;)

P.S If you want to convert your .cap to .22000 manually, visit [official hashcat conversion website](https://hashcat.net/cap2hashcat/). Or, you can install [hcxtools](https://github.com/ZerBea/hcxtools) and .22000 files will be generated automatically. 

![aireplay-ng window](/demo/aircrack-ng_window.png)

## Command line arguments

Can be found by typing ```python3 aircrack-gui.py -h```.
```
Application Options:
  --nokill                   Do not run 'airmon-ng check kill'. Will retain internet connection on other devices, but is probably a bad idea.
  --noclean                  Do not clean .csv files generated by airodump-ng when scanning for clients.
  --nolog                    Do not print anything to console.
  --display=DISPLAY          X display to use
```

## Todo

- Change network scanning from nmcli to airmon-ng

<details>
  <summary>Changelog</summary>
  
- 0.0.6 --- Added command line arguments. Files, generated by airodump-ng (.csv, .netxml) are now automatically deleted. Minor log improvements and code formatting.

- 0.0.5 --- Added automatic .cap to .22000 conversion when selecting hashcat and [hcxtools](https://github.com/ZerBea/hcxtools) are installed. Minor ui updates.

- 0.0.4 --- Removed xterm windows (except for aircrack-ng/hashcat), fixed selected station deselecting/changing when updated.

- 0.0.3 --- Hashcat support.

- 0.0.2 --- README.md changes, etc.

- 0.0.1 --- Initial commit.
</details>
