#!/bin/bash

set -e

sudo mkdir -p /usr/lib/budgie-desktop/plugins/budgie-pi-audio-switcher
sudo cp budgie_pi_audio_switcher.py /usr/lib/budgie-desktop/plugins/budgie-pi-audio-switcher
sudo cp BudgiePiAudioSwitcher.plugin /usr/lib/budgie-desktop/plugins/budgie-pi-audio-switcher
sudo cp audio-hdmi-symbolic.svg /usr/share/pixmaps
sudo cp audio-jack-symbolic.svg /usr/share/pixmaps
sudo cp com.budgie-pi.audio-switcher.gschema.xml /usr/share/glib-2.0/schemas
sudo sudo glib-compile-schemas /usr/share/glib-2.0/schemas
