# SPDX-FileCopyrightText: Copyright (c) 2022 Neradoc
#
# SPDX-License-Identifier: MIT
"""
Generates a SystemConfiguration preferences file without the Circuitpython boards.
Removes everything that has an interface in "usbmodem" from the active services list.

The boards are still in the interface list, and will pop up in new settings but should not come back in the current settings.

Creates a "output_preferences.plist" to replace the original with:

sudo cp output_preferences.plist /Library/Preferences/SystemConfiguration/preferences.plist

Might not work on Big Sur's heightened security.
Not tested with a reboot.
There might be a better way to do that using the defaults command,
once the python script has found all the service_id to remove.
"""
import click
import os
import plistlib
import subprocess
import uuid
import traceback

PREFS_FILE = "/Library/Preferences/SystemConfiguration/preferences.plist"
OUTPUT_FILE = "/tmp/output_preferences.{}.plist".format(str(uuid.uuid4())[:8])
DEBUG = False

def remove_in_services(data, service_id):
    for skey, sett in data["Sets"].items():
        try:
            ServiceOrder = sett["Network"]["Global"]["IPv4"]["ServiceOrder"]
            if service_id in ServiceOrder:
                ServiceOrder.remove(service_id)
        except KeyError as ex:
            if DEBUG:
                traceback.print_exception(ex,ex,ex.__traceback__)
        try:
            services = sett["Network"]["Service"].keys()
            if service_id in services:
                # output.append(["Sets", skey, "Network", "Service", service_id])
                del sett["Network"]["Service"][service_id]
        except KeyError as ex:
            if DEBUG:
                traceback.print_exception(ex,ex,ex.__traceback__)


@click.group(invoke_without_command=True)
@click.option(
    "--yes",
    is_flag=True,
    help="Validate changes without asking.",
)
@click.option(
    "--debug",
    is_flag = True,
    help="Debug prints in try/excepts.",
)
def main(yes, debug):
    """This is the main part of the programm !"""
    global DEBUG
    DEBUG = debug
    click.secho(f"Note: this will modify your system configuration preferences:\n{PREFS_FILE}\nYou might want to back that up before validating anything.\n", fg="yellow")

    with open(PREFS_FILE, "rb") as fp:
        data = plistlib.load(fp)

    removed_services = []
    services = list(data["NetworkServices"].keys())

    for service_id in services:
        service = data["NetworkServices"][service_id]

        try:
            name = service["UserDefinedName"]
        except:
            continue

        try:
            interface = service["Interface"]["DeviceName"]
        except:
            print(f"{name} - Keep")
            continue

        keep = not interface.startswith("usbmodem")

        if keep:
            click.secho(f"{name} ({interface}) - Keep", fg="green")
        else:
            click.secho(f"{name} ({interface}) - Remove", fg="red")
            removed_services.append(name)
            # del data["NetworkServices"][service_id]
            remove_in_services(data, service_id)

    with open(OUTPUT_FILE, "wb") as fp:
        plistlib.dump(data, fp)

    print("")
    if removed_services:
        if os.getuid() == 0:
            if yes or click.confirm("Do you want to validate the changes ?"):
                subprocess.run(["sudo", "cp", OUTPUT_FILE, PREFS_FILE])
                print("Done.")
        else:
            print(f"Run this script with sudo or do:")
            print(f"sudo cp {OUTPUT_FILE} {PREFS_FILE}")
    else:
        print("No service removed, nothing to do")


if __name__ == "__main__":
    main()
