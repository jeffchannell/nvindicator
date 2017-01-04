#!/usr/bin/env python3

"""nvindicator.py: An NVIDIA GPU indicator applet"""

__author__ = "Jeff Channell"
__copyright__ = "Copyright 2017, Jeff Channell"
__credits__ = ["Jeff Channell"]
__license__ = "GPL"
__version__ = "1.0.2"
__maintainer__ = "Jeff Channell"
__email__ = "me@jeffchannell.com"
__status__ = "Prototype"

import gi
import signal
import subprocess
import sys

gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")

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
		
		# about window init
		self.about = None
		
		# track menus
		self.menus = []
		
		# track gpus
		self.gpus = []
		xml = self.read_nvidia()

		# all menus display the driver version
		driver = str(xml.driver_version[0])
		
		for gpu in xml.gpu:
			items = []
			
			# create a new indicator
			ind = appindicator.Indicator.new(
				"NvIndicator",
				"nvidia-settings",
				appindicator.IndicatorCategory.HARDWARE
			)
			ind.set_status(appindicator.IndicatorStatus.ACTIVE)
			menu = Gtk.Menu()

			# add an nvidia-settings menu item
			item = Gtk.MenuItem()
			item.set_label("Open NVIDIA Settings")
			item.connect("activate", self.run_nvidia_settings)
			menu.append(item)
			
			# sep
			item = Gtk.SeparatorMenuItem()
			menu.append(item)

			# gpu name
			item = Gtk.MenuItem()
			item.set_label(str(gpu.product_name[0]))
			item.connect("activate", self.do_nothing)
			menu.append(item)

			# driver version
			item = Gtk.MenuItem()
			item.set_label("Driver\tv{}".format(driver))
			item.connect("activate", self.do_nothing)
			menu.append(item)
			
			# memory usage - update 0
			item = Gtk.MenuItem()
			item.set_label(
				"Using {} of {}".format(
					str(gpu.fb_memory_usage[0].used[0]),
					str(gpu.fb_memory_usage[0].total[0])
				)
			)
			item.connect("activate", self.do_nothing)
			items.append(item)
			menu.append(item)

			# temperature - update 1
			item = Gtk.MenuItem()
			item.set_label(
				"Temperature\t\t{}".format(
					str(gpu.temperature[0].gpu_temp[0])
				)
			)
			item.get_children()[0].set_justify(Gtk.Justification.FILL)
			item.connect("activate", self.do_nothing)
			items.append(item)
			menu.append(item)

			# power draw - update 2
			item = Gtk.MenuItem()
			item.set_label(
				"Power Draw\t\t{}".format(
					str(gpu.power_readings[0].power_draw[0])
				)
			)
			item.get_children()[0].set_justify(Gtk.Justification.FILL)
			item.connect("activate", self.do_nothing)
			items.append(item)
			menu.append(item)

			# processes - update 3
			item = Gtk.MenuItem()
			item.set_label(
				"Processes\t\t\t{}".format(
					str(len(gpu.processes))
				)
			)
			item.get_children()[0].set_justify(Gtk.Justification.FILL)
			item.connect("activate", self.do_nothing)
			items.append(item)
			menu.append(item)
			
			# sep
			item = Gtk.SeparatorMenuItem()
			menu.append(item)
			
			# about me
			item = Gtk.MenuItem()
			item.set_label("About")
			item.connect("activate", self.show_about)
			menu.append(item)
			
			# add a quit menu item
			item = Gtk.MenuItem()
			item.set_label("Quit")
			item.connect("activate", self.quit)
			menu.append(item)
			
			# set the menu
			menu.show_all()
			ind.set_menu(menu)
			self.menus.append(items)
			
			self.gpus.append(ind)
			
	def add_about_window_contents(self):
		text = Gtk.Label()
		text.set_markup(
			"<b>About NvIndicator</b>\n\n{}\n\n"
			"An NVIDIA GPU indicator applet\n\n"
			"<a href=\"https://github.com/jeffchannell/nvindicator\">"
			"https://github.com/jeffchannell/nvindicator</a>\n\n"
			"<small>"
			"© 2017 Jeff Channell\n\n"
			"This program comes with absolutely no warranty.\n"
			"See the GNU General Public License, version 3 or later for details."
			"</small>".format(__version__)
		)
		text.set_line_wrap(True)
		text.set_justify(Gtk.Justification.CENTER)
		
		self.about.add(text)
		
	def clear(self):
		for gpu in self.gpus:
			gpu.set_status(appindicator.IndicatorStatus.ACTIVE)
			
	def destroy_about(self, widget, something):
		self.about = None
		return False

	def do_nothing(self, widget):
		pass
		
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
		
	def show_about(self, widget):
		if None == self.about:
			self.about = Gtk.Window()
			self.about.set_title("About NvInidicator")
			self.about.set_keep_above(True)
			self.about.connect("delete-event", self.destroy_about)
			self.add_about_window_contents()
			
		self.about.set_position(Gtk.WindowPosition.CENTER)
		self.about.set_size_request(400, 200)
		self.about.show_all()
			
		
	def update_gpu(self, idx, gpu):
		self.gpus[idx].set_label(
			"GPU: {}% MEM: {}%".format(
				str(gpu.utilization[0].gpu_util[0]).split()[0].rjust(3),
				str(gpu.utilization[0].memory_util[0]).split()[0].rjust(3)
			),
			"NvInidicatorUsage"
		)
		
		self.menus[idx][0].set_label(
			"Using {} of {}".format(
				str(gpu.fb_memory_usage[0].used[0]),
				str(gpu.fb_memory_usage[0].total[0])
			)
		)
		
		self.menus[idx][1].set_label(
			"Temperature\t\t{}".format(
				str(gpu.temperature[0].gpu_temp[0])
			)
		)
		
		self.menus[idx][2].set_label(
			"Power Draw\t\t{}".format(
				str(gpu.power_readings[0].power_draw[0])
			)
		)
		
		self.menus[idx][3].set_label(
			"Processes\t\t\t{}".format(
				str(len(gpu.processes))
			)
		)

def main():
	# allow app to be killed using ctrl+c
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	indicator = NvIndicator()
	indicator.main()

if __name__ == '__main__':
	main()
