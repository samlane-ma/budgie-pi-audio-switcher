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
        
        button1 = Gtk.RadioButton(label="Remember Last Setting")
        button1.connect("toggled", self.toggled_cb)
        button2 = Gtk.RadioButton.new_from_widget(button1)
        button2.set_label("Always Start With HDMI Output")
        button2.connect("toggled", self.toggled_cb)
        button2.set_active(False)
        button3 = Gtk.RadioButton.new_with_label_from_widget(
            button1, "Always Start With 3.5mm Output")
        button3.connect("toggled", self.toggled_cb)
        button3.set_active(False)

        self.config_path = os.getenv("HOME")+'/.config/piaudioswitcher.ini'
        self.config = SafeConfigParser()
        self.config.read(self.config_path)
        self.forcemode = self.config.get('Default','Force')
        if self.forcemode == 'Last':
            button1.set_active(True)
        elif self.forcemode == 'HDMI':
            button2.set_active(True)
        else:
            button3.set_active(True)

        grid = Gtk.Grid.new()
        self.attach(button1, 0, 0, 1, 1)
        self.attach(button2, 0, 1, 1, 1)
        self.attach(button3, 0, 2, 1, 1)
        self.add(grid)

    
    def toggled_cb(self, button):
        
        if button.get_active():
            switchtomode = button.get_label()
            if switchtomode == 'Remember Last Setting':
                forcesetting = 'Last'
            elif switchtomode == 'Always Start With HDMI Output':
                forcesetting = 'HDMI'
            else:
                forcesetting = 'JACK'
  
            self.config.set('Default','Force',forcesetting)
            with open(self.config_path, 'w') as f:
                self.config.write(f)
        # else do nothing
        



class BudgiePiAudioApplet(Budgie.Applet):
    """ Budgie.Applet is in fact a Gtk.Bin """
    manager = None

    
    def __init__(self, uuid):
        
        Budgie.Applet.__init__(self)
        
        self.uuid = uuid
    
        self.config_path = os.getenv("HOME")+'/.config/piaudioswitcher.ini'
        self.config = SafeConfigParser()
        
        self.box = Gtk.EventBox()
      
        self.hdmiicon = Gtk.Image.new_from_icon_name(
            "video-display-symbolic",
            Gtk.IconSize.MENU,
        )

        self.jackicon = Gtk.Image.new_from_icon_name(
            "audio-headphones-symbolic",
            Gtk.IconSize.MENU,
        )
 
        if os.path.isfile(self.config_path):
            #File Found
            self.config.read(self.config_path)
            if not self.config.has_option('Default','Output'):
                # The key doesn't exist
                if not self.config.has_section('Default'):
                    # Section Not Found - Create it and add the key
                    self.config.add_section('Default')
                    self.config.set('Default','Output','HDMI')
                    self.config.set('Default','Force','Last')
                    with open(self.config_path, 'w') as f:
                        self.config.write (f)
                else:
                    # Section Exists - Just Create the Key
                    self.config.set('Default','Output','HDMI')
                    with open(self.config_path, 'w') as f:
                        self.config.write (f)
        else:
            # File Doesn't exist - Create it
            self.config.read(self.config_path)
            self.config.add_section('Default')
            self.config.set('Default','Output','HDMI')
            self.config.set('Default','Force','Last')
            with open(self.config_path, 'w') as f:
                self.config.write (f)
                
        self.config.read(self.config_path)
        if not self.config.has_option('Default','Force'):
            self.config.set('Default','Force','Last')
            with open(self.config_path, 'w') as f:
                self.config.write (f)
        
        self.config.read(self.config_path)
        
        self.forcemode = self.config.get('Default','Force')
        if not self.forcemode in ['HDMI','JACK','Last']:
           self.forcemode = 'Last'
           self.config.set('Default','Force','Last')
           with open(self.config_path, 'w') as f:
               self.config.write(f)
               
        if self.forcemode in ['HDMI','JACK']:
            self.config.set('Default','Output',self.forcemode)
            with open(self.config_path, 'w') as f:
                self.config.write(f)
        
        self.audiomode = self.config.get('Default','Output')
        if not self.audiomode in ['HDMI','JACK']:
            self.audiomode = 'HDMI'
            self.config.set('Default','Output','HDMI')
            with open(self.config_path, 'w') as f:
                self.config.write(f)
        
        if not self.forcemode == 'Last':
            self.audiomode = self.forcemode
           
        if self.audiomode == 'JACK':
            self.displayicon = self.jackicon
            os.system("amixer cset numid=3 1 >> /dev/null")
        else:
            self.displayicon = self.hdmiicon
            os.system("amixer cset numid=3 2 >> /dev/null")

        self.box.add(self.displayicon)
        self.add(self.box)
        self.box.show_all()
        self.show_all()
        self.box.connect("button-press-event", self.on_press)
        
    
    def on_press(self, box, arg):
        self.box.remove(self.displayicon)
        

        if self.audiomode == 'HDMI':
            self.displayicon = self.jackicon
            self.audiomode = 'JACK'
            os.system("amixer cset numid=3 1 >> /dev/null")
        else:
            self.displayicon = self.hdmiicon
            self.audiomode = 'HDMI'
            os.system("amixer cset numid=3 2 >> /dev/null")
        
        self.config.set('Default','Output',self.audiomode)
        with open(self.config_path, 'w') as f:
            self.config.write(f)
            
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
        

        
       
