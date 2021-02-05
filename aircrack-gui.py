# 0.0.4
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib
import sys
import os
import re
import time
import csv
from termcolor import colored
from datetime import datetime as dt

# Global variables ------------------------- Start
Interfaces = []
Interface = ""

MY_DIRECTORY = os.popen("pwd").read()
DEFAULT_SAVE_LOCATION = "{}/wifis/".format(MY_DIRECTORY[:-1])
SaveLocation = ""

#Window triggers
Show_Aircrack = False
Show_Aireplay = False
Show_Airodump = False

#Dialog triggers
Show_No_Interface = False
Show_Monitor_Mode_Enabled = False
# Global variables ------------------------- End

# Custom functions ------------------------- Start
def check_monitor_mode(interface):
	command_get_mode = "sudo iwconfig {} | awk -F: '/Mode/{{print$2}}'".format(interface)
	if os.popen(command_get_mode).read().split(" ", 1)[0] == "Monitor":
		return True
	else:
		return False

#Update all network interfaces
def update_interfaces():
	global Interfaces
	global Show_No_Interface
	global No_Interface_Dialog
	del Interfaces[:]
	interfaces = os.popen("sudo iwconfig 2>&1 | grep -oP '^\w+'").read().split("\n")[:-1]
	for interface in interfaces:
		if interface != "lo" and interface != "eth0":
			command_set_interface_up = "sudo ifconfig {} up".format(interface)
			os.popen(command_set_interface_up)
			Interfaces.append(interface)
			
	if len(Interfaces) == 0:
		if Show_No_Interface == False:
			Show_No_Interface = True
			
			No_Interface_Dialog = NoInterfacesFoundDialog()
			response = No_Interface_Dialog.run()
			if response == Gtk.ResponseType.OK:
				print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('INFO', 'green') + "] Scanning")
				restart_network_manager()
				update_interfaces()
			else:
				exit()
		else:
			response = No_Interface_Dialog.run()
			if response == Gtk.ResponseType.OK:
				print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('INFO', 'green') + "] Scanning")
				restart_network_manager()
				update_interfaces()
			else:
				exit()
	elif Show_No_Interface == True:
		Show_No_Interface = False
		No_Interface_Dialog.destroy()


def start_network_manager():
	if "Unit dhcpcd.service" in os.popen("sudo systemctl start dhcpcd 2>&1").read():
		os.popen("sudo systemctl start NetworkManager").read()


def restart_network_manager():
	if "Unit dhcpcd.service" in os.popen("sudo systemctl restart dhcpcd 2>&1").read():
		os.popen("sudo systemctl restart NetworkManager").read()


# Custom functions ------------------------- Start
#Main window
class Air_gui(Gtk.ApplicationWindow):
	def __init__(self, app):
		global Air_Gui_Window
		Gtk.Window.__init__(self, application=app)
		self.set_default_size(292, -1)
		self.set_border_width(10)
		
		Air_Gui_Window = self
		
		hb = Gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = "Aircrack-ng GUI"
		self.set_titlebar(hb)
		
		self.aircrackButton = Gtk.Button(label="Open Aircrack-ng")
		self.aircrackButton.connect("pressed", self.on_button_clicked_aircrack, "1")
		
		self.airmonButton = Gtk.ToggleButton(label="Start airmon-ng")
		self.airmonButton.connect("toggled", self.on_button_toggled_airmon, "1")
		
		self.scanButton = Gtk.Button(label="Scan for networks")
		self.scanButton.connect("pressed", self.on_button_clicked_scan, "1")
		
		self.pathEntry = Gtk.Entry()
		self.pathEntry.connect("activate", self.path_entry_submit)
		self.pathEntry.set_placeholder_text("Location of folder for airodump-ng output")

		# add boxes to position things (vbox = vertical box; hbox = horizontal box)
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		hbox = Gtk.Box(spacing=6)
		self.add(vbox)
		vbox.pack_start(hbox, True, True, 0)
		vbox.pack_start(self.pathEntry, True, True, 0)
		vbox.pack_start(self.airmonButton, True, True, 0)
		vbox.pack_start(self.aircrackButton, True, True, 0)
		
		update_interfaces()
		self.initiate_combo_box(hbox)
		
		hbox.pack_start(self.scanButton, True, True, 0)
		
		self.airmonButton.set_active(check_monitor_mode(Interface))

			
	def path_entry_submit(self, entry):
		SaveLocation = entry.get_text()
		
	def initiate_combo_box(self, hbox):
		global Interface
		listmodel = Gtk.ListStore(str)
		for i in Interfaces:
			listmodel.append([i])

		self.combobox = Gtk.ComboBox(model=listmodel)

		cell = Gtk.CellRendererText()

		self.combobox.pack_start(cell, False)

		self.combobox.add_attribute(cell, "text", 0)

		self.combobox.set_active(0)

		self.combobox.connect("changed", self.on_changed_combo)
		hbox.pack_start(self.combobox, True, True, 0)
		Interface = Interfaces[self.combobox.get_active()]
		
	def update_combo_box(self):
		global Interface
		listmodel = Gtk.ListStore(str)
		for i in Interfaces:
			listmodel.append([i])
		self.combobox.set_model(model=listmodel)
		self.combobox.set_active(0)
		Interface = Interfaces[self.combobox.get_active()]
		
	def on_changed_combo(self, combo):
		global Interface
		# if the row selected is not the first one, write its value on the
		# terminal
		Interface = Interfaces[self.combobox.get_active()]
		print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('INFO', 'green') + "] Updated interface " + Interface + ".")
		return True
		
	def on_button_toggled_airmon(self, button, name):
		if button.get_active():
			button.set_label("Stop airmon-ng")
			print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('INFO', 'green') + "] Killing processes...")
			command_airmon_check_kill = "sudo airmon-ng check kill"
			output_airmon_check_kill = os.popen(command_airmon_check_kill).read()
			print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('INFO', 'green') + "] Starting airmon-ng on {}...".format(Interface))
			command_airmon_start = "sudo airmon-ng start {}".format(Interface)
			output_airmon_start = os.popen(command_airmon_start).read()
			update_interfaces()
		else:
			button.set_label("Start airmon-ng")
			print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('INFO', 'green') + "] Stopping airmon-ng on {}...".format(Interface))
			command_airmon_stop = "sudo airmon-ng stop {}".format(Interface)
			output_airmon_stop = os.popen(command_airmon_stop).read()
			print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('INFO', 'green') + "] Starting Network Manager...")
			start_network_manager()
			update_interfaces()
		self.update_combo_box()
		self.airmonButton.set_active(check_monitor_mode(Interface))
		
	def on_button_clicked_aircrack(self, button, name):
		global Show_Aircrack
		if button.activate():
			self.aircrackWindow = Aircrack_ng(app)
			self.aircrackWindow.show_all()
			Show_Aircrack = True
			
	def on_button_clicked_scan(self, button, name):
		global Show_Monitor_Mode_Enabled
		if button.activate():
			Show_Monitor_Mode_Enabled = False
			if check_monitor_mode(Interface):
				response = type(Gtk.ResponseType)
				if Show_Monitor_Mode_Enabled == False:
					Monitor_Mode_Enabled_Dialog = MonitorModeEnabledDialog()
					response = Monitor_Mode_Enabled_Dialog.run()
					Show_Monitor_Mode_Enabled = True
				else:
					response = No_Interface_Dialog.run()
				if response == Gtk.ResponseType.OK:
					Monitor_Mode_Enabled_Dialog.destroy()
					print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('INFO', 'green') + "] Stopping airmon-ng on {}".format(Interface))
					command_airmon_stop = "sudo airmon-ng stop {}".format(Interface)
					output_airmon_stop = os.popen(command_airmon_stop).read()
					start_network_manager()
						
					update_interfaces()
					self.update_combo_box()
						
					self.airmonButton.set_active(check_monitor_mode(Interface))

					self.scanWindow = Scan(app)
					self.scanWindow.show_all()
			else:
				if Show_Monitor_Mode_Enabled == True:
					self.moniotor_mode_dialog.destroy()
				self.scanWindow = Scan(app)
				self.scanWindow.show_all()
				
class Scan(Gtk.ApplicationWindow):
	def __init__(self, app):
		global Show_Airodump
		Show_Airodump = False
		Gtk.Window.__init__(self, title="Scan for networks", application=app)
		self.set_default_size(500, 200)
		self.set_border_width(10)
		
		hb = Gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = "Aircrack-ng GUI"
		self.set_titlebar(hb)
			
		wifis = self.scan_networks()
		if wifis == '':
			self.destroy()

		grid = Gtk.Grid()
		self.add(grid)

		stack = Gtk.Stack()
		stack.set_hexpand(True)
		stack.set_vexpand(True)
		grid.attach(stack, 1, 0, 1, 1)

		stacksidebar = Gtk.StackSidebar()
		stacksidebar.set_stack(stack)
		grid.attach(stacksidebar, 0, 0, 1, 1)
			
		num = 0
		for wifi in wifis:
			vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
			label = Gtk.Label()
			label.set_markup("<big>Bssid: </big>{}\n<big>Channel: </big>{}\n<big>Signal Strength: </big>{}\n<big>Encryption: </big>{}".format(wifi[0],wifi[2],wifi[3],wifi[4]))
			vbox.pack_start(label, True, True, 0)
			self.airodumpButton = Gtk.Button(label="Start airodump-ng on chosen network")
			self.airodumpButton.connect("pressed", self.on_button_clicked_airodump, "1", wifi)
			vbox.pack_start(self.airodumpButton, True, True, 6)
			name = "label%i" % num
			title = wifi[1]
			stack.add_titled(vbox, name, title)
			num+=1
				
	def scan_networks(self):
		wifis = []
		
		command_scan_wifi = "nmcli dev wifi"
		output_scan_wifi = os.popen(command_scan_wifi).read()
		splited_output_scan_wifi = output_scan_wifi.split("\n")
		del splited_output_scan_wifi[0]
		if splited_output_scan_wifi[0] == '':
			time.sleep(5)
			output_scan_wifi = os.popen(command_scan_wifi).read()
			splited_output_scan_wifi = output_scan_wifi.split("\n")
			del splited_output_scan_wifi[0]
		
		if splited_output_scan_wifi[0] == '':
			print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('ERROR', 'red') + "] No networks found")
			return ''
			
		for record in splited_output_scan_wifi:
			record = re.sub(" +", " ",record)
			record = record.strip()
			splitted_record = record.split(" ")
			if splitted_record != ['']:
				if splitted_record[0] == '*':
					del splitted_record[0]
				i = 2;
				while i < splitted_record.index("Infra"):
					splitted_record[1] += " " + splitted_record[i]
					splitted_record.remove(splitted_record[i])
				if "WPA1" in splitted_record:
					index = splitted_record.index("WPA1")+1;
					splitted_record[splitted_record.index("WPA1")]+= " " + splitted_record[index]
					splitted_record.remove(splitted_record[index])
				del splitted_record[2]
				del splitted_record[3]
				del splitted_record[3]
				del splitted_record[4]
				wifis.append(splitted_record)
		return wifis
				
	def on_button_clicked_airodump(self, button, name, wifi):
		global Show_Airodump
		if button.activate():
			if Show_Airodump == False:
				self.airodumpWindow = Airodump_ng(app, wifi)
				self.airodumpWindow.show_all()
				Show_Airodump = True
				self.destroy()

#Airodump-ng window on selected network
class Airodump_ng(Gtk.ApplicationWindow):
	Wifi = []
	Station = ""
	SaveTo = ""
	stationsArray = []
	deauthPacketsAmount = 10
	
	def __init__(self, app, wifi):
		if not check_monitor_mode(Interface):
			Air_Gui_Window.airmonButton.set_active(True)
		
		print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('INFO', 'green') + "] Starting airodump-ng on bssid: {}".format(wifi[0]))
		self.Wifi = wifi
		Gtk.Window.__init__(self, title="Airodump-ng", application=app)
		self.connect("destroy", self.on_destroy)
		self.set_default_size(500, -1)
		self.set_border_width(10)
		
		hb = Gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = "Aircrack-ng GUI"
		self.set_titlebar(hb)
		
		if SaveLocation != "":
			self.SaveTo = SaveLocation + self.Wifi[1] + "/"
		else:
			self.SaveTo = DEFAULT_SAVE_LOCATION + self.Wifi[1] + "/"
			
		i = 1;
		while os.path.isdir(self.SaveTo):
			for i in range(int(i/10)):
				self.SaveTo = self.SaveTo[:-1]
			self.SaveTo = self.SaveTo[:-1]
			self.SaveTo += str(i) + "/"
			i += 1
		
		os.makedirs(self.SaveTo)
		command_airodump = "sudo airodump-ng --bssid '{}' -c '{}' --write-interval 1 --write '{}' {} > /dev/null 2>&1".format(self.Wifi[0], self.Wifi[2], self.SaveTo, Interface)
		output_airodump = os.popen(command_airodump)
		
		
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		hbox = Gtk.Box(spacing=6)
		
		self.add(vbox)
		self.amountOfPacketsEntry = Gtk.Entry()
		self.amountOfPacketsEntry.connect('changed', self.on_changed_packet_number_entry)
		self.amountOfPacketsEntry.set_placeholder_text("Amount of deauth packets you want to send. 10 by default")
		
		self.statusbar = Gtk.Statusbar()
		self.context_id = self.statusbar.get_context_id("example")
		self.statusbar.push(self.context_id, "Waiting for you to do something...")
		
		vbox.pack_start(self.statusbar, True, True, 0)
		vbox.pack_start(self.amountOfPacketsEntry, True, True, 0)
		
		
		self.stationEntry = Gtk.Entry()
		self.stationEntry.connect('changed', self.on_station_manual_entry)
		self.stationEntry.set_placeholder_text("Station address")
		
		hbox.pack_start(self.stationEntry, True, True, 0)
		self.initiate_station_selector_box(hbox)
		vbox.pack_start(hbox, True, True, 0)
		
		#autofillButton = Gtk.CheckButton(label="Autofill station address")
		#autofillButton.connect("toggled", self.start_continuos_scan)
		#vbox.pack_start(autofillButton, True, True, 0)
		
		self.timeout = GLib.timeout_add_seconds(1, self.autofill_station_address)
		
		startTime = time.time()
		
		runAireplayBtn = Gtk.Button(label="Run deauth (aireplay-ng)")
		runAireplayBtn.connect("clicked", self.run_aireplay)
		vbox.pack_start(runAireplayBtn, True, True, 0)
		
		
	def autofill_station_address(self):
			del self.stationsArray[:]
			self.parse_airmon_output()
			if len(self.stationsArray) > 0:
				if self.Station not in self.stationsArray:
					self.Station = self.stationsArray[0]
				self.update_station_selector_box()
			#else:
				#print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('ERROR', 'red') + "] No stations found")
			return True
			
	def initiate_station_selector_box(self, hbox):
		listmodel = Gtk.ListStore(str)
		for i in self.stationsArray:
			listmodel.append([i])

		self.stationSelector = Gtk.ComboBox(model=listmodel)

		cell = Gtk.CellRendererText()
		self.stationSelector.pack_start(cell, False)

		self.stationSelector.add_attribute(cell, "text", 0)

		self.stationSelector.set_active(0)

		self.stationSelector.connect("changed", self.on_changed_station_selector)
		hbox.pack_start(self.stationSelector, True, True, 0)
		
	def update_station_selector_box(self):
		listmodel = Gtk.ListStore(str)
		for i in self.stationsArray:
			listmodel.append([i])
		self.stationSelector.set_model(model=listmodel)
		if len(self.stationsArray) > 0:
			self.stationSelector.set_active(self.stationsArray.index(self.Station))
			self.stationEntry.set_text(self.Station)
		
	def on_changed_station_selector(self, combo):
		self.Station = self.stationsArray[self.stationSelector.get_active()]
		self.stationEntry.set_text(self.Station)
		
		
	def on_station_manual_entry(self, entry):
		self.Station = entry.get_text()
		
	def on_changed_packet_number_entry(self, entry):
		text = entry.get_text().strip()
		entry.set_text(''.join([i for i in text if i in '0123456789']))
		self.deauthPacketsAmount = entry.get_text()
		 
	def run_aireplay(self, button):
		command_aireplay = "sudo aireplay-ng --deauth '{}' -a '{}' -c '{}' {}".format(self.deauthPacketsAmount, self.Wifi[0], self.Station, Interface)
		os.popen(command_aireplay)
		command_aircrack_output = type(int)
		try:
			command_aircrack = "sudo aircrack-ng {}-01.cap | sed -n '7p' | tr -s ' ' | tr -d '()\n'".format(self.SaveTo)
			command_aircrack_output = int(os.popen(command_aircrack).read().split(" ")[5])
		except IndexError:
			command_aircrack = "sudo aircrack-ng {}-01.cap | sed -n '6p' | tr -s ' ' | tr -d '()\n'".format(self.SaveTo)
			command_aircrack_output = int(os.popen(command_aircrack).read().split(" ")[5])
		if command_aircrack_output > 0:
			self.statusbar.push(self.context_id, "Success, handshake recieved")

		
	def on_destroy(self, widget):
		print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('INFO', 'green') + "] Stopping airodump-ng on bssid: {}".format(self.Wifi[0]))
		if check_monitor_mode(Interface):
			Air_Gui_Window.airmonButton.set_active(False)
	
	def parse_airmon_output(self):
		with open('{}-01.csv'.format(self.SaveTo), 'r') as csvfile:
			for i, l in enumerate(csvfile):
				if i + 1 > 5:
					if l.split(',')[0] != "\n":
						self.stationsArray.append(l.split(',')[0])


#Aircrack-ng window
class Aircrack_ng(Gtk.ApplicationWindow):
	capFilePath = ""
	wordlistFilePath = ""
	def __init__(self, app):
		Gtk.Window.__init__(self, title="Aircrack-ng", application=app)
		self.set_default_size(500, -1)
		self.set_border_width(10)
		
		hb = Gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = "Aircrack-ng GUI"
		self.set_titlebar(hb)
		
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.add(vbox)
		hbox = Gtk.Box(spacing = 6)
		vbox.pack_start(hbox, True, True, 0)
		
		self.capFilePathEntry = Gtk.Entry()
		self.capFilePathEntry.connect('activate', self.submit_cap_filepath)
		self.capFilePathEntry.set_placeholder_text("Capture file location")
		hbox.pack_start(self.capFilePathEntry, True, True, 0)
		
		self.chooseCapFilePath = Gtk.Button(label = "Choose capture file")
		self.chooseCapFilePath.connect("pressed", self.choose_cap_filepath, "1")
		hbox.pack_start(self.chooseCapFilePath, True, True, 0)
		
		
		hbox2 = Gtk.Box(spacing = 6)
		vbox.pack_start(hbox2, True, True, 0)
		self.wordlistFilePathEntry = Gtk.Entry()
		self.wordlistFilePathEntry.connect('activate', self.submit_wordlist_filepath)
		self.wordlistFilePathEntry.set_placeholder_text("Wordlist location")
		hbox2.pack_start(self.wordlistFilePathEntry, True, True, 0)
		
		self.chooseWordlistFilePath = Gtk.Button(label = "   Choose wordlist    ") # yeah i know but im too sleepy
		self.chooseWordlistFilePath.connect("pressed", self.choose_wordlist_filepath, "1")
		hbox2.pack_start(self.chooseWordlistFilePath, True, True, 0)
		
		hbox3 = Gtk.Box(spacing = 6)
		vbox.pack_start(hbox3, True, True, 0)
		
		self.startAircrack = Gtk.Button(label = "Start Aircrack-ng")
		self.startAircrack.connect("pressed", self.start_aircrack, "1")
		
		self.startHashcat = Gtk.Button(label = "   Start Hashcat  ")
		self.startHashcat.connect("pressed", self.start_hashcat, "1")
		hbox3.pack_start(self.startAircrack, True, True, 0)
		hbox3.pack_start(self.startHashcat, True, True, 0)
		
	def start_hashcat(self, button, name):
		if self.capFilePath.split(".")[1] == "cap":
			command_cap2hccapx="cap2hccapx.bin {} {}.hccapx".format(self.capFilePath, self.capFilePath.split(".")[0])
			os.popen(command_cap2hccapx)
		command_hashcat='''xterm -T "hashcat" -hold -e "sudo hashcat -m 2500 '{}' '{}'"'''.format(self.capFilePath, self.wordlistFilePath)
		os.popen(command_hashcat)
	
	def start_aircrack(self, button, name):
		command_aircrack='''xterm -T "aircrack-ng" -hold -e "sudo aircrack-ng -w '{}' '{}'"'''.format(self.wordlistFilePath, self.capFilePath)
		os.popen(command_aircrack)
		
	def submit_cap_filepath(self, entry):
		self.capFilePath = entry.get_text()
		
	def choose_cap_filepath(self, button, name):
		chooser = Gtk.FileChooserDialog(title="Open dot File", action=Gtk.FileChooserAction.OPEN)
		chooser.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		chooser.add_buttons(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
		
		chooser.set_default_response(Gtk.ResponseType.OK)
		chooser.set_default_size(500, -1)
		chooser.set_border_width(10)
		
		filter = Gtk.FileFilter()
		filter.set_name("Capture .cap files")
		filter.add_pattern("*.cap") 
		chooser.add_filter(filter)
		filter = Gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		chooser.add_filter(filter)
		if chooser.run() == Gtk.ResponseType.OK:
			self.capFilePath = chooser.get_filename()
			self.capFilePathEntry.set_text(self.capFilePath)
			chooser.destroy()
		else:
			chooser.destroy()
			
	def submit_wordlist_filepath(self, entry):
		self.wordlistFilePath = entry.get_text()
		
	def choose_wordlist_filepath(self, button, name):
		chooser = Gtk.FileChooserDialog(title="Open dot File", action=Gtk.FileChooserAction.OPEN)
		chooser.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		chooser.add_buttons(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
		
		chooser.set_default_response(Gtk.ResponseType.OK)
		chooser.set_default_size(500, -1)
		chooser.set_border_width(10)
		
		filter = Gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		chooser.add_filter(filter)
		if chooser.run() == Gtk.ResponseType.OK:
			self.wordlistFilePath = chooser.get_filename()
			self.wordlistFilePathEntry.set_text(self.wordlistFilePath)
			chooser.destroy()
		else:
			chooser.destroy() 

#Dialog shown on start if no network interfaces were found
class NoInterfacesFoundDialog(Gtk.MessageDialog):
	def __init__(self):
		Gtk.Dialog.__init__(self, transient_for=None, flags=0, text="Interfaces not found")
		self.set_default_size(150, 100)
		
		hb = Gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = "Aircrack-ng GUI"
		self.set_titlebar(hb)
		
		self.format_secondary_text("No network interfaces were found.\nWant to try to restart network manager and check for any interfaces that are down?")
		
		self.add_buttons("Rescan for interfaces", Gtk.ResponseType.OK)

		self.show_all()

#Dialog shown when you try to scan networks, but monitor mode is enabled
class MonitorModeEnabledDialog(Gtk.MessageDialog):
	def __init__(self):
		Gtk.Dialog.__init__(self, transient_for=None, flags=0, text = "Monitor mode is enabled")
		self.set_default_size(150, 100)
		
		hb = Gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = "Aircrack-ng GUI"
		self.set_titlebar(hb)
		
		self.format_secondary_text("In order to scan for networks inetrface needs to be in managed mode.\nWant to disable monitor mode?")
		
		self.add_buttons("Disable airmon-ng (Monitor mode)", Gtk.ResponseType.OK)
		
		self.show_all()
		
Air_Gui_Window = type(Air_gui)

#Programm main body
class Aircrack_gui(Gtk.Application):
	
	def __init__(self):
		Gtk.Application.__init__(self)

	def do_activate(self):
		global Air_Gui_Window
		Air_Gui_Window = Air_gui(self)
		Air_Gui_Window.show_all()

	def do_startup(self):
		Gtk.Application.do_startup(self)
		
No_Interface_Dialog = type(NoInterfacesFoundDialog)
Monitor_Mode_Enabled_Dialog = type(MonitorModeEnabledDialog)


#System required things (set app = programm, exit when programm exit status say to)
app = Aircrack_gui()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
