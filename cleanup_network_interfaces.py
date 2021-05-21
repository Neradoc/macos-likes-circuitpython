"""
Generates a SystemConfiguration preferences file without the Circuitpython boards
Removes everything that has an interface in "usbmodem"
Creates a "output_preferences.plist" to replace the original with:

sudo cp output_preferences.plist /Library/Preferences/SystemConfiguration/preferences.plist

Might not work on Big Sur's heightened security.
Not tested with a reboot.
There might a better way to do that using the defaults command, once the python script has found all the service_id to remove.
"""

import plistlib

preferences_file = "/Library/Preferences/SystemConfiguration/preferences.plist"

with open(preferences_file,"rb") as fp:
	data = plistlib.load(fp)

removed_services = []
services = list(data['NetworkServices'].keys())

for service_id in services:
	service = data['NetworkServices'][service_id]

	try:
		name = service['UserDefinedName']
	except:
		continue

	try:
		interface = service['Interface']['DeviceName']
	except:
		print(f"{name} - Keep")
		continue

	keep = not interface.startswith("usbmodem")
	
	print(f"{name} ({interface}) - ",end="")
	if keep:
		print("Keep")
	else:
		print("Remove")
		removed_services.append(name)
		del data['NetworkServices'][service_id]

with open("output_preferences.plist","wb") as fp:
	plistlib.dump(data,fp)

print("")
if removed_services:
	print("And now:\nsudo cp output_preferences.plist /Library/Preferences/SystemConfiguration/preferences.plist")
else:
	print("No service removed, nothing to do")
