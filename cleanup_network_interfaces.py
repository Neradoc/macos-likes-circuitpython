"""
Generates a SystemConfiguration preferences file without the Circuitpython boards
Removes everything that has an interface in "usbmodem"
Creates a "output_preferences.plist" to replace the original with:

sudo cp output_preferences.plist /Library/Preferences/SystemConfiguration/preferences.plist

Might not work on Big Sur's heightened security.
Not tested with a reboot.
There might be a better way to do that using the defaults command, once the python script has found all the service_id to remove.
"""
import click
import os
import plistlib
import subprocess

preferences_file = "/Library/Preferences/SystemConfiguration/preferences.plist"
output_file = "output_preferences.plist"

@click.group(invoke_without_command=True)
@click.option(
    "--yes", is_flag=True, help="Validate without warning."
)
def main(yes):
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

		if keep:
			click.secho(f"{name} ({interface}) - Keep", fg="green")
		else:
			click.secho(f"{name} ({interface}) - Remove", fg="red")
			removed_services.append(name)
			del data['NetworkServices'][service_id]

	with open(output_file,"wb") as fp:
		plistlib.dump(data,fp)

	print("")
	if removed_services:
		if os.getuid() == 0:
			if yes or click.confirm("Do you want to validate the changes ?"):
				subprocess.run(["sudo", "cp", output_file, preferences_file])
				print("Done.")
		else:
			print(f"Run this script with sudo or do:")
			print(f"sudo cp {output_file} {preferences_file}")
	else:
		print("No service removed, nothing to do")


if __name__ == "__main__":
	main()
