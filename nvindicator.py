#!/usr/bin/env python3

"""nvindicator.py: An nvidia GPU indicator applet"""

__author__ = "Jeff Channell"
__copyright__ = "Copyright 2017, Jeff Channell"
__credits__ = ["Jeff Channell"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Jeff Channell"
__email__ = "me@jeffchannell.com"
__status__ = "Prototype"

import signal
import subprocess
import sys
from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib
from lxml import objectify
from subprocess import run

class NvIndicator:
	def __init__(self):
		# check for nvidia app
		check = run(
			["nvidia-smi"],
			stdout=subprocess.PIPE, 
			universal_newlines=True
		)
		
		# track menus
		self.menus = []
		
		# track gpus
		self.gpus = []
		xml = self.read_nvidia()
		
		for gpu in xml.gpu:
			# create a new indicator
			ind = appindicator.Indicator.new(
				"NvIndicator",
				"nvidia-settings",
				appindicator.IndicatorCategory.APPLICATION_STATUS
			)
			ind.set_status(appindicator.IndicatorStatus.ACTIVE)
			self.gpus.append(ind)
			menu = Gtk.Menu()
			
			# add an nvidia-settings menu item
			item = Gtk.MenuItem()
			item.set_label("Nvidia Settings")
			item.connect("activate", self.run_nvidia_settings)
			menu.append(item)
			
			# add a quit menu item
			item = Gtk.MenuItem()
			item.set_label("Quit")
			item.connect("activate", self.quit)
			menu.append(item)
			
			# set the menu
			menu.show_all()
			gpu.set_menu(menu)
			self.menus.append(menu)
		
	def clear(self):
		for gpu in self.gpus:
			gpu.set_status(appindicator.IndicatorStatus.ACTIVE)
		
	def main(self):
		self.run_loop()
		Gtk.main()

	def quit(self, widget):
		Gtk.main_quit()
		
	def read_nvidia(self):
		result = run(
			["nvidia-smi", "-q", "-x"],
			stdout=subprocess.PIPE, 
			universal_newlines=True
		)
		xml = objectify.fromstring(result.stdout)
		return xml
		
	def run_loop(self):
		xml = self.read_nvidia()
		idx = 0
		for gpu in xml.gpu:
			self.update_gpu(idx, gpu)
			idx = idx + 1
		# end with another loop
		GLib.timeout_add_seconds(1, self.run_loop)
		
	def run_nvidia_settings(self, widget):
		run(["nvidia-settings"])
		
	def update_gpu(self, idx, gpu):
		self.gpus[idx].set_label(
			"GPU: {}% MEM: {}%".format(
				str(gpu.utilization[0].gpu_util[0]).split()[0],
				str(gpu.utilization[0].memory_util[0]).split()[0]
			),
			"NvInidicatorUsage"
		)

def main():
	# allow app to be killed using ctrl+c
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	indicator = NvIndicator()
	indicator.main()

if __name__ == '__main__':
	main()
