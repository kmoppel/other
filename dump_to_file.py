#!/usr/bin/python

# Plugin by Kaarel Moppel <kaarel.moppel@gmail.com>
# See LICENSE of Terminator package.

""" dump_to_file.py - Terminator Plugin to save text content of individual
terminals to ~/.terminator directory"""

import os
import sys
import gtk
import terminatorlib.plugin as plugin
from terminatorlib.translation import _
import datetime

AVAILABLE = ['DumpToFile']

class DumpToFile(plugin.MenuItem):
    capabilities = ['terminal_menu']
    dumpers = None

    def __init__(self):
        plugin.MenuItem.__init__(self)
        if not self.dumpers:
            self.dumpers = {}

    def callback(self, menuitems, menu, terminal):
        """ Add dump-to-file command to the terminal menu """
        vte_terminal = terminal.get_vte()
        if not self.dumpers.has_key(vte_terminal):
            item = gtk.MenuItem(_('Dump terminal to file'))
            item.connect("activate", self.dump_console, terminal)
        menuitems.append(item)
                        
    def dump_console(self, _widget, Terminal):
        """ Handle menu item callback by saving console text to a predefined location and creating the ~/.terminator folder if necessary """
        # TODO delete logs older than 3m automatically?
        try:
            path = os.path.expanduser("~") + "/.terminator/"
            if not os.path.exists(path):
                os.mkdir(path)
            filename = "console_" + datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')+".log"
            fd = open(path + filename, 'w+')
            vte_terminal = Terminal.get_vte()
            fd.write(vte_terminal.get_text(lambda *a: True).strip() + "\n")
            fd.flush()
        except Exception as e:
            print e
