# 0.0.5
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio
import sys
import os
import re
import time
import csv
from termcolor import colored
from datetime import datetime as dt
import math

# Global variables ------------------------- Start
Interfaces = []
Interface = ""

MY_DIRECTORY = os.popen("pwd").read()
DEFAULT_SAVE_LOCATION = "{}/wifis/".format(MY_DIRECTORY[:-1])
SaveLocation = ""

# Arguments
DO_NOT_KILL  	= False
DO_NOT_LOG 	 	= False
DO_NOT_CLEAN 	= False

# Window triggers
Show_Aircrack = False
Show_Aireplay = False
Show_Airodump = False

# Dialog triggers
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
				log("Scanning for interfaces.")
				restart_network_manager()
				update_interfaces()
			else:
				exit()
		else:
			response = No_Interface_Dialog.run()
			if response == Gtk.ResponseType.OK:
				log("Scanning for interfaces.")
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
		
def log(string, logtype = 0, nonewline = False):
	if DO_NOT_LOG:
		return

	type_indicator = ""
	if logtype == 0:
		type_indicator = colored("INFO", "green")
	if logtype == 1:
		type_indicator = colored("WARNING", "yellow")
	if logtype == 2:
		type_indicator = colored("ERROR", "red")
	if nonewline:
		print("[" + colored(str(dt.now().time()).split(".")[0], "blue") + "] [" + type_indicator + "] " + string, end="\r")
	else:
		print("[" + colored(str(dt.now().time()).split(".")[0], "blue") + "] [" + type_indicator + "] " + string)
	
def run_command(command):
	return os.popen(command).read()
	
def run_command_background(command):
	return os.popen(command)


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
		log("Selected interface: " + Interface + ".")
		return True


	def on_button_toggled_airmon(self, button, name):
		if button.get_active():
			button.set_label("Stop airmon-ng")
			if not DO_NOT_KILL:
				log("Killing processes.")
				output_airmon_check_kill = os.popen("sudo airmon-ng check kill").read()
			else:
				log("NOT killing processes.", 1)
			log("Starting airmon-ng on: {}.".format(Interface))
			run_command("sudo airmon-ng start {}".format(Interface))
			update_interfaces()
		else:
			button.set_label("Start airmon-ng")
			log("Stopping airmon-ng on: {}.".format(Interface))
			run_command("sudo airmon-ng stop {}".format(Interface))
			log("Starting Network Manager.")
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
					log("Stopping airmon-ng on {}".format(Interface))
					run_command("sudo airmon-ng stop {}".format(Interface))
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
		
		headerbar = Gtk.HeaderBar()
		headerbar.set_show_close_button(True)
		headerbar.props.title = "Aircrack-ng GUI"
		self.set_titlebar(headerbar)

		parent = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		self.add(parent)

		stack = Gtk.Stack()
		stack.set_hexpand(True)
		stack.set_vexpand(True)

		stacksidebar = Gtk.StackSidebar()
		stacksidebar.set_stack(stack)
		
		parent.pack_start(stacksidebar,  True, True, 6)
		parent.pack_start(stack, True, True, 6)
		
		networks = self.scan_networks()
		if networks == '':
			self.destroy()
		
		for index, network in enumerate(networks):
			vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
			
			label = Gtk.Label()
			label.set_markup("<big>Bssid: </big>{}\n<big>Channel: </big>{}\n<big>Signal Strength: </big>{}\n<big>Encryption: </big>{}".format(network[0], network[2], network[3], network[4]))
			vbox.pack_start(label, True, True, 0)
			
			self.airodumpButton = Gtk.Button(label="Start airodump-ng on chosen network")
			self.airodumpButton.connect("pressed", self.on_button_clicked_airodump, "1", network)
			vbox.pack_start(self.airodumpButton, True, True, 6)
			
			name = "label%i" % index
			stack.add_titled(vbox, name, network[1])


	def scan_networks(self):
		networks = []
		
		splited_output_scan_wifi = run_command("nmcli dev wifi").split("\n")
		del splited_output_scan_wifi[0]
		
		if splited_output_scan_wifi == []:
			log("No networks found", 2)
			return networks
		
		if splited_output_scan_wifi[0] == '':
			log("No networks found", 2)
			return networks
			
		for record in splited_output_scan_wifi:
			record = re.sub(" +", " ", record).strip()
			
			splitted_record = record.split(" ")
			if splitted_record == ['']:
				continue
			
			if splitted_record[0] == '*':
				del splitted_record[0]
			
			#fix for names with spaces (note for my future self)
			i = 2
			while i < splitted_record.index("Infra"):
				splitted_record[1] += " " + splitted_record[i]
				splitted_record.remove(splitted_record[i])
				
			index_infra = splitted_record.index("Infra")
			del splitted_record[index_infra]
			del splitted_record[index_infra+1]
			del splitted_record[index_infra+1]
			del splitted_record[index_infra+2]
			
			for index in range(index_infra + 2, len(splitted_record) - 1):
				splitted_record[index] += ", " + splitted_record[index + 1]
				splitted_record.remove(splitted_record[index + 1])
			
			networks.append(splitted_record)
		return networks


	def on_button_clicked_airodump(self, button, name, wifi):
		global Show_Airodump
		if button.activate():
			if Show_Airodump is False:
				self.airodumpWindow = Airodump_ng(app, wifi)
				self.airodumpWindow.show_all()
				Show_Airodump = True
				self.destroy()


#Airodump-ng window on selected network
class Airodump_ng(Gtk.ApplicationWindow):
	Network = []
	Station = ""
	Stations = []
	Directory = ""
	DeauthPackets = 10
	
	def __init__(self, app, network):
		if not check_monitor_mode(Interface):
			Air_Gui_Window.airmonButton.set_active(True)
		
		self.Network = network
		log("Starting airodump-ng on bssid: {}".format(self.Network[0]))
		Gtk.Window.__init__(self, title="Airodump-ng", application=app)
		self.connect("destroy", self.on_destroy)
		self.set_default_size(500, -1)
		self.set_border_width(10)
		
		headerbar = Gtk.HeaderBar()
		headerbar.set_show_close_button(True)
		headerbar.props.title = "Aircrack-ng GUI"
		self.set_titlebar(headerbar)
		
		if SaveLocation != "":
			self.Directory = SaveLocation + self.Network[1] + ":1"
		else:
			self.Directory = DEFAULT_SAVE_LOCATION + self.Network[1] + ":1"
			
		index = 1
		while os.path.isdir(self.Directory + "/"):
			for k in range(math.ceil((index/10))):
				self.Directory = self.Directory[:-1]
			self.Directory += str(index)
			index += 1
		
		self.Directory += "/"
		
		os.makedirs(self.Directory)
		run_command_background("sudo airodump-ng --bssid {} -c {} --write-interval 1 --write {} {} > /dev/null 2>&1".format(self.Network[0], self.Network[2], self.Directory, Interface))
		
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		hbox = Gtk.Box(spacing=6)
		
		self.add(vbox)
		self.amountOfPacketsEntry = Gtk.Entry()
		self.amountOfPacketsEntry.connect("changed", self.on_changed_packet_number_entry)
		self.amountOfPacketsEntry.set_placeholder_text("Amount of deauth packets you want to send. 10 by default.")
		
		self.statusbar = Gtk.Statusbar()
		self.context_id = self.statusbar.get_context_id("statusbar")
		self.statusbar.push(self.context_id, "Scanning for stations.")
		
		vbox.pack_start(self.statusbar, True, True, 0)
		vbox.pack_start(self.amountOfPacketsEntry, True, True, 0)
		
		self.stationEntry = Gtk.Entry()
		self.stationEntry.connect("changed", self.on_station_manual_entry)
		self.stationEntry.set_placeholder_text("Station address")
		
		self.autofill_station_address()
		self.timeout = GLib.timeout_add_seconds(1, self.autofill_station_address)
		startTime = time.time()
		
		hbox.pack_start(self.stationEntry, True, True, 0)
		self.initiate_station_selector_box(hbox)
		vbox.pack_start(hbox, True, True, 0)
		
		self.runAireplayBtn = Gtk.Button(label="Run deauth (aireplay-ng)")
		self.runAireplayBtn.connect("clicked", self.run_aireplay)
		self.runAireplayBtn.set_sensitive(False)
		
		vbox.pack_start(self.runAireplayBtn, True, True, 0)


	def autofill_station_address(self):
		self.get_stations_from_airmon()
		if len(self.Stations) > 0:
			if self.Station not in self.Stations:
				self.Station = self.Stations[0]
			self.update_station_selector_box()
		#else:
			#print('[' + colored(str(dt.now().time()).split('.')[0], "blue") + "] [" + colored('ERROR', 'red') + "] No stations found")
		return True


	def initiate_station_selector_box(self, hbox):
		listmodel = Gtk.ListStore(str)
		for i in self.Stations:
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
		for i in self.Stations:
			listmodel.append([i])
		self.stationSelector.set_model(model=listmodel)
		if len(self.Stations) > 0:
			self.stationSelector.set_active(self.Stations.index(self.Station))
			self.stationEntry.set_text(self.Station)

	def on_changed_station_selector(self, combo):
		self.Station = self.Stations[self.stationSelector.get_active()]
		self.stationEntry.set_text(self.Station)


	def on_station_manual_entry(self, entry):
		self.Station = entry.get_text()
		if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", self.Station.lower()):
			self.runAireplayBtn.set_sensitive(True)
		else:
			self.runAireplayBtn.set_sensitive(False)


	def on_changed_packet_number_entry(self, entry):
		text = entry.get_text().strip()
		entry.set_text(''.join([i for i in text if i in '0123456789']))
		self.DeauthPackets = entry.get_text()


	def run_aireplay(self, button):
		log("Sending {} packets to {}".format(self.DeauthPackets, self.Station), 0, True)
		run_command("sudo aireplay-ng --deauth '{}' -a '{}' -c '{}' {}".format(self.DeauthPackets, self.Network[0], self.Station, Interface))
		
		hanshakes = 0
		try:
			command_aircrack_output = run_command("sudo aircrack-ng {}-01.cap | sed -n '7p' | tr -s ' ' | tr -d '()\n'".format(self.Directory))
			hanshakes = int(command_aircrack_output.split(" ")[5])
		except IndexError:
			command_aircrack_output = run_command("sudo aircrack-ng {}-01.cap | sed -n '6p' | tr -s ' ' | tr -d '()\n'".format(self.Directory))
			hanshakes = int(command_aircrack_output.split(" ")[5])
		
		if hanshakes > 0:
			self.statusbar.push(self.context_id, "Success, handshake recieved.")
			log("Sending {} packets to {}: {}".format(self.DeauthPackets, self.Station, colored("Success", "green")))
		else:
			self.statusbar.push(self.context_id, "Failed, handshake not found. Try again or change the target.")
			log("Sending {} packets to {}: {}".format(self.DeauthPackets, self.Station, colored("Failure", "yellow")))


	def on_destroy(self, widget):
		log("Stopping airodump-ng on bssid: {}".format(self.Network[0]))
		if check_monitor_mode(Interface):
			Air_Gui_Window.airmonButton.set_active(False)
		self.manage_temporary_files()
			
	def manage_temporary_files(self):
		if DO_NOT_CLEAN:
			os.makedirs(self.Directory + "stations/")
		for _file in os.listdir(self.Directory):
			if os.path.splitext(_file)[1] == ".csv" or os.path.splitext(_file)[1] == ".netxml":
				path = os.path.join(self.Directory, _file)
				if DO_NOT_CLEAN:
					os.rename(path, os.path.join(self.Directory + "stations/", _file))
				else:
					os.remove(path)


	def get_stations_from_airmon(self):
		del self.Stations[:]
		if os.path.isfile("{}-01.csv".format(self.Directory)) == False:
			return
		with open("{}-01.csv".format(self.Directory), "r") as csvfile:
			for index, value in enumerate(csvfile):
				if index < 5:
					continue
				value = value.split(',')[0]
				if value != "\n":
					self.Stations.append(value)


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
		self.capFilePathEntry.connect("changed", self.submit_cap_filepath)
		self.capFilePathEntry.set_placeholder_text("Capture file location")
		hbox.pack_start(self.capFilePathEntry, True, True, 0)
		
		self.chooseCapFilePath = Gtk.Button(label = "Choose capture file")
		self.chooseCapFilePath.connect("pressed", self.choose_cap_filepath, "1")
		hbox.pack_start(self.chooseCapFilePath, True, True, 0)
		
		hbox2 = Gtk.Box(spacing = 6)
		vbox.pack_start(hbox2, True, True, 0)
		self.wordlistFilePathEntry = Gtk.Entry()
		self.wordlistFilePathEntry.connect("changed", self.submit_wordlist_filepath)
		self.wordlistFilePathEntry.set_placeholder_text("Wordlist location")
		hbox2.pack_start(self.wordlistFilePathEntry, True, True, 0)
		
		self.chooseWordlistFilePath = Gtk.Button(label = "   Choose wordlist    ") # yeah i know but im too sleepy
		self.chooseWordlistFilePath.connect("pressed", self.choose_wordlist_filepath, "1")
		hbox2.pack_start(self.chooseWordlistFilePath, True, True, 0)
		
		hbox3 = Gtk.Box(spacing = 6)
		vbox.pack_start(hbox3, True, True, 0)
		
		self.startAircrack = Gtk.Button(label = "Start Aircrack-ng")
		self.startAircrack.connect("pressed", self.start_aircrack, "1")
		self.startAircrack.set_sensitive(False)
		
		self.startHashcat = Gtk.Button(label = "   Start Hashcat  ")
		self.startHashcat.connect("pressed", self.start_hashcat, "1")
		self.startHashcat.set_sensitive(False)
		
		hbox3.pack_start(self.startAircrack, True, True, 0)
		hbox3.pack_start(self.startHashcat, True, True, 0)


	def start_hashcat(self, button, name):
		if self.capFilePath.split(".")[1] == "cap":
			command_hcxpcapngtool="hcxpcapngtool {} -o {}.22000".format(self.capFilePath, self.capFilePath.split(".")[0])
			os.popen(command_hcxpcapngtool)
		command_hashcat = '''xterm -T "hashcat" -hold -e "sudo hashcat -m 22000 '{}' '{}'"'''.format(self.capFilePath.split(".")[0] + ".22000", self.wordlistFilePath)
		os.popen(command_hashcat)


	def start_aircrack(self, button, name):
		command_aircrack='''xterm -T "aircrack-ng" -hold -e "sudo aircrack-ng -w '{}' '{}'"'''.format(self.wordlistFilePath, self.capFilePath)
		os.popen(command_aircrack)
		
	def ready_check(self):
		if(os.path.isfile(self.capFilePath) and os.path.isfile(self.wordlistFilePath)):
			if(self.capFilePath.split(".")[1] == "cap"):
				self.startAircrack.set_sensitive(True)
				
				command_check_hcxpcapngtool = "which hcxpcapngtool";
				if (os.popen(command_check_hcxpcapngtool).read() != "hcxpcapngtool not found\n"):
					self.startHashcat.set_sensitive(True)


	def submit_cap_filepath(self, entry):
		self.capFilePath = entry.get_text()
		self.ready_check()


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
			self.ready_check()
		chooser.destroy()


	def submit_wordlist_filepath(self, entry):
		self.wordlistFilePath = entry.get_text()
		self.ready_check()


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
			self.ready_check()
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
		Gtk.Application.__init__(self, flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
		#print(app.args)
		self.add_main_option(
			"nokill",
			0,
			GLib.OptionFlags.NONE,
			GLib.OptionArg.NONE,
			"Do not run 'airmon-ng check kill'. Will retain internet connection on other devices, but is probably a bad idea.",
			None,
		)
		self.add_main_option(
			"noclean",
			0,
			GLib.OptionFlags.NONE,
			GLib.OptionArg.NONE,
			"Do not clean .csv files generated by airodump-ng when scanning for clients.",
			None,
		)
		self.add_main_option(
			"nolog",
			0,
			GLib.OptionFlags.NONE,
			GLib.OptionArg.NONE,
			"Do not print anything to console.",
			None,
		)

	def do_activate(self):
		global Air_Gui_Window
		Air_Gui_Window = Air_gui(self)
		Air_Gui_Window.show_all()

	def do_startup(self):
		Gtk.Application.do_startup(self)
		
	def do_command_line(self, command_line):
		options = command_line.get_options_dict()
		# convert GVariantDict -> GVariant -> dict
		options = options.end().unpack()
		
		global DO_NOT_KILL
		DO_NOT_KILL = True if "nokill" in options and options["nokill"] is True else False #evil laughing intensifies
		global DO_NOT_LOG
		DO_NOT_LOG = True if "nolog" in options and options["nolog"] is True else False #evil laughing intensifies
		global DO_NOT_CLEAN
		DO_NOT_CLEAN = True if "noclean" in options and options["noclean"] is True else False #evil laughing intensifies

		self.activate()
		return 0
		
	def on_quit(self, action, param):
		self.quit()


No_Interface_Dialog = type(NoInterfacesFoundDialog)
Monitor_Mode_Enabled_Dialog = type(MonitorModeEnabledDialog)

#System required things (set app = programm, exit when program exit status say to)
app = Aircrack_gui()
exit_status = app.run(sys.argv)
sys.exit(exit_status)