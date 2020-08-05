# budgie-pi-audio-switcher


Due to recent changes to Ubuntu on the Raspberry Pi, audio output is now able to be properly selected from both Raven and the sound settings.  Therefore, this applet is no longer necessary and in fact will no longer properly work with the improvements.

Adds an applet for Ubuntu Budgie to allow easy switching from HDMI audio output to 3.5mm jack audio output.

This applet will only have the correct effect on a Raspberry Pi.

To install:

- chmod +x install.sh
- ./install.sh
   
   
This will
- copy the plugin files to /usr/lib/budgie-desktop/plugins/budgie-pi-audio-switcher/
- copy the icons to /usr/share/pixmaps
- install the schema

To use, simply click the icon to switch modes.
The plugin can be configured to start up in HDMI mode, 3.5mm jack mode, or the last mode used.

![image](https://user-images.githubusercontent.com/67085765/87239279-5c2e1700-c3db-11ea-8a68-59dd38561117.png)
