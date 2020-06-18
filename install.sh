#!/bin/bash

set -e

sudo mkdir -p /usr/lib/budgie-desktop/plugins/budgie-pi-audio-switcher
sudo cp budgie_pi_audio_switcher.py /usr/lib/budgie-desktop/plugins/budgie-pi-audio-switcher
sudo cp BudgiePiAudioSwitcher.plugin /usr/lib/budgie-desktop/plugins/budgie-pi-audio-switcher

