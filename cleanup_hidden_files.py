# SPDX-FileCopyrightText: Copyright (c) 2022 Neradoc
#
# SPDX-License-Identifier: MIT
"""
TODO: an applescript app/droplet version.
Note: discotool includes that feature too.
"""
import os
import click
default_drive = "/Volumes/CIRCUITPY"

def tree_clean(root, force=False):
	for target in os.listdir(root):
		file = os.path.join(root,target)
		if os.path.isdir(file):
			tree_clean(file)
		else:
			if os.path.basename(file).startswith("._"):
				if force:
					click.echo(f"Deleting {file}")
					os.remove(file)
				elif click.confirm(f"Delete {file} ?"):
					os.remove(file)

@click.group(invoke_without_command=True)
@click.option(
	"--path",
	default=default_drive,
	help="#######",
)
@click.option(
	"--force",
	is_flag=True,
	help="#######",
)
@click.pass_context
def main(ctx, path, force):
	if os.path.isdir(path):
		tree_clean(path, force)
	else:
		print(f"Drive {path} not found")

if __name__ == "__main__":
	main()
