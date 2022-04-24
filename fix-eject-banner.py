# This file © PaintYourDragon
# https://gist.github.com/PaintYourDragon/a229f7c5f1992943a34ce1a5c7cb527c
# https://blog.adafruit.com/2021/05/11/how-to-tone-down-macos-big-surs-circuitpy-eject-notifications/
"""
Fixes an annoyance with macOS Big Sur and 'DISK NOT EJECTED PROPERLY'
notifications (which occur with every CircuitPython board disconnect or
reset). Changes notification from an alert (which pile up until each is
manually dismissed) to a banner (auto dismissed after a few seconds),
as it behaved in prior macOS releases.

USE AT YOUR OWN RISK. MODIFIES USER'S ncprefs.plist FILE.
STRONGLY RECOMMENDED THAT YOU SAVE A BACKUP FIRST, e.g.:
  cp ~/Library/Preferences/com.apple.ncprefs.plist ~/Desktop
REQUIRES python3.
"""

import os
import plistlib

PREFS_FILE = os.path.expanduser('~') + '/Library/Preferences/com.apple.ncprefs.plist'

with open(PREFS_FILE, 'rb') as fp:
    try:
        plist = plistlib.load(fp)
    except:
        print("python3 plz!")
        exit(0)
    for app in plist['apps']:
        if app['bundle-id'] == '_SYSTEM_CENTER_:com.apple.DiskArbitration.DiskArbitrationAgent':
            # Clear 'alert' bit, set 'banner' and 'modified' bits:
            app['flags'] = (int(app['flags']) & ~0b00010000) | 0b01001000
            # Reverse operation if you need it back would be:
            #app['flags'] = (int(app['flags']) & ~0b01001000) | 0b00010000

with open(PREFS_FILE, 'wb') as fp:
    plistlib.dump(plist, fp, fmt=plistlib.FMT_BINARY)

os.system('killall usernoted cfprefsd') # Restart Notification Center
