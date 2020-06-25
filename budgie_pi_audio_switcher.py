import gi.repository

gi.require_version('Budgie', '1.0')
from gi.repository import Budgie, GObject, Gtk, Gio
from configparser import SafeConfigParser
import os
import os.path


"""
    Budgie Pi Audio Switcher Plugin - switch audio output modes on Raspberry Pi
    Copyright (C) 2020  Samuel Lane

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

def load_settings(config_file):

    # Load the settings from the config file.
    # If the config file does not exist, create it.
    # If the config file has invalid data, reset it.
    
    need_new = False
    
    if not os.path.isfile(config_file):
        need_new = True
    config = SafeConfigParser()
    config.read(config_file)
    if not config.has_option('Default','Output'):
        need_new = True
    if not config.has_option('Default','Force'):
        need_new = True
        
    if need_new:
        create_settings(config_file)
        need_new = False
    config.read(config_file)
    
    read_last = config.get('Default','Output')
    read_forced = config.get('Default','Force')
    if not read_last in ['HDMI','JACK']:
        need_new = True
    if not read_forced in ['HDMI','JACK','LAST']:
        need_new = True
    if need_new:
        create_settings(config_file)

    config.read(config_file)
    read_last = config.get('Default','Output')
    read_forced = config.get('Default','Force')       

    return read_last, read_forced


def save_settings(save_mode, save_forced, config_file):

    # saves the settings to the config file

    config = SafeConfigParser()
    config.read(config_file)
    config.set('Default','Output', save_mode)
    config.set('Default','Force',save_forced)
    with open(config_file, 'w') as f:
        config.write (f)
        
    
def create_settings(config_file):
    
    # Deletes the config file if it exists, and creates a new one
    # using default values.  Called when file is missing or invalid.

    if os.path.isfile(config_file):
        os.remove(config_file)
    config = SafeConfigParser()
    config.read(config_file)
    config.add_section('Default')
    config.set('Default','Output','HDMI')
    config.set('Default','Force','LAST')
    with open(config_file, 'w') as f:
        config.write (f)



class BudgiePiAudio(GObject.GObject, Budgie.Plugin):
    """ This is simply an entry point into your Budgie Applet implementation.
        Note you must always override Object, and implement Plugin.
    """
    # Good manners, make sure we have unique name in GObject type system
    __gtype_name__ = "BudgiePiAudioSwitcher"
    
    def __init__(self):
        """ Initialisation is important.
        """
        GObject.Object.__init__(self)
    
    def do_get_panel_widget(self, uuid):
        """ This is where the real fun happens. Return a new Budgie.Applet
            instance with the given UUID. The UUID is determined by the
            BudgiePanelManager, and is used for lifetime tracking.
        """
        return BudgiePiAudioApplet(uuid)

class BudgiePiAudioSettings(Gtk.Grid):

    def __init__(self, setting):
        super().__init__()
        
        button_last = Gtk.RadioButton(label="Remember Last Setting")
        button_last.connect("toggled", self.toggled_cb)
        button_hdmi = Gtk.RadioButton.new_from_widget(button_last)
        button_hdmi.set_label("Always Start With HDMI Output")
        button_hdmi.connect("toggled", self.toggled_cb)
        button_hdmi.set_active(False)
        button_jack = Gtk.RadioButton.new_with_label_from_widget(
            button_last, "Always Start With 3.5mm Output")
        button_jack.connect("toggled", self.toggled_cb)
        button_jack.set_active(False)

        self.config_path = os.getenv("HOME")+'/.config/piaudioswitcher.ini'
        self.audiomode, self.forcemode = load_settings(self.config_path)
        
        if self.forcemode == 'LAST':
            button_last.set_active(True)
        elif self.forcemode == 'HDMI':
            button_hdmi.set_active(True)
        else:
            button_jack.set_active(True)

        blank = Gtk.Label(" ")
        
        self.set_row_spacing (10)
        self.attach(blank, 0, 0, 1, 1)
        self.attach(button_last, 0, 1, 1, 1)
        self.attach(button_hdmi, 0, 2, 1, 1)
        self.attach(button_jack, 0, 3, 1, 1)
        self.show_all()

    
    def toggled_cb(self, button):
        
        if button.get_active():
            switchtomode = button.get_label()
            if switchtomode == 'Remember Last Setting':
                forcesetting = 'LAST'
            elif switchtomode == 'Always Start With HDMI Output':
                forcesetting = 'HDMI'
            else:
                forcesetting = 'JACK'
            
            save_settings(self.audiomode, forcesetting, self.config_path)  
        # else do nothing
        



class BudgiePiAudioApplet(Budgie.Applet):
    """ Budgie.Applet is in fact a Gtk.Bin """
    manager = None

    
    def __init__(self, uuid):
        
        Budgie.Applet.__init__(self)
        
        self.uuid = uuid
    
        self.config_path = os.getenv("HOME")+'/.config/piaudioswitcher.ini'
        self.config = SafeConfigParser()
        
        self.audiomode, self.forcemode = load_settings(self.config_path)
        
        self.box = Gtk.EventBox()
      
        self.hdmiicon = Gtk.Image.new_from_icon_name(
            "video-display-symbolic",
            Gtk.IconSize.MENU,
        )

        self.jackicon = Gtk.Image.new_from_icon_name(
            "audio-headphones-symbolic",
            Gtk.IconSize.MENU,
        )
         
        if not self.forcemode == 'LAST':
            self.audiomode = self.forcemode
           
        if self.audiomode == 'JACK':
            self.displayicon = self.jackicon
            self.box.set_tooltip_text('Audio output set to 3.5mm jack')
            os.system("amixer cset numid=3 1 >> /dev/null")
        else:
            self.displayicon = self.hdmiicon
            self.box.set_tooltip_text('Audio output set to HDMI')
            os.system("amixer cset numid=3 2 >> /dev/null")

        self.box.add(self.displayicon)
        self.add(self.box)
        self.box.show_all()
        self.show_all()
        self.box.connect("button-press-event", self.on_press)
        
    
    def on_press(self, box, arg):
    
        self.box.remove(self.displayicon)
        self.config.read(self.config_path)
        self.forcemode = self.config.get('Default','Force')

        if self.audiomode == 'HDMI':
            self.displayicon = self.jackicon
            self.audiomode = 'JACK'
            self.box.set_tooltip_text('Audio output currently set to 3.5mm jack')
            os.system("amixer cset numid=3 1")
        else:
            self.displayicon = self.hdmiicon
            self.audiomode = 'HDMI'
            self.box.set_tooltip_text('Audio output currently set to HDMI')
            os.system("amixer cset numid=3 2")
        
        save_settings(self.audiomode, self.forcemode, self.config_path)
            
        self.box.add(self.displayicon)
        self.box.show_all()

    def do_supports_settings(self):
        """Return True if support setting through Budgie Setting,
        False otherwise.
        """
        return True
        
    def do_get_settings_ui(self):
        """Return the applet settings with given uuid"""
        return BudgiePiAudioSettings(self.get_applet_settings(self.uuid))
        

        
       
