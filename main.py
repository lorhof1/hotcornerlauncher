#!/usr/bin/env python3
# Configuration layout:
# [
# 	{ "menu-name":"name",
#		"top-left":{
#			"option-name":"name",
#			"command":"command"
# 		},
#		"top-right":{
#			"option-name":"",
#			"command":""
#		},
#		"bottom-left":{
#			"option-name":"",
#			"command":""
#		},
#		"bottom-right":{
#			"option-name":"name",
#			"command":"command"
#		}
# 	}
# ]

# --- Empty commands default to closing the menu ---

config = [ { "menu-name":"default", "top-left":{ "option-name":"more", "command":"hotcornerlauncher more" }, "top-right":{ "option-name":"terminal", "command":"gnome-terminal" }, "bottom-left":{ "option-name":"browser", "command":"epiphany" }, "bottom-right":{ "option-name":"close", "command":"" } } ]

import sys, os, subprocess
EXIT_ARGS = 4
EXIT_DEPENDS = 2
EXIT_FILES = 3
EXIT_OTHER = 1
EXIT_SUCCESS = 0

zenity_processes = []
initial_state = ""

def print_usage():
	print("Usage: " + sys.argv[0] + " menu-name")

def check_args():
	if len(sys.argv) < 2:
		print_usage()
		sys.exit(EXIT_ARGS)
	for menu in config:
		if menu["menu-name"] == sys.argv[1]:
			return

	print_usage()
	sys.exit(EXIT_ARGS)

def check_depends():
	if os.system("zenity --version > /dev/null") != 0:
		print("zenity not found")
		sys.exit(EXIT_DEPENDS)
	if os.system("gsettings get org.cinnamon hotcorner-layout > /dev/null") != 0:
		print("either gsettings or the value org.cinnamon hotcorner-layout are not found. Is cinnamon installed?")
		sys.exit(EXIT_DEPENDS)

def check_files():
	if not os.path.isdir("/dev/shm"):
		print("/dev/shm not found; does your kernel support it?")

def save_state():
	os.system("gsettings get org.cinnamon hotcorner-layout > /dev/shm/hotcorner_layout")
	global initial_state
	initial_state = open("/dev/shm/hotcorner_layout").read().split("\n")[0]

def close_zenity():
	for process in zenity_processes:
		process.terminate()

def restore_state():
	os.system("gsettings set org.cinnamon hotcorner-layout \"" + initial_state + "\" > /dev/null")

def command_to_hotcorner(command):
	if command == "":
		return "'touch /dev/shm/hotcorner_exit:true:0'"
	return "'sh -c \"touch /dev/shm/hotcorner_exit && " + command + "\":true:0'"

def set_corners_gsettings(top_left, top_right, bottom_left, bottom_right):
	subprocess.Popen(["gsettings", "set", "org.cinnamon", "hotcorner-layout", "[" + command_to_hotcorner(top_left) + ", " + command_to_hotcorner(top_right) + ", " + command_to_hotcorner(bottom_left) + ", " + command_to_hotcorner(bottom_right) + "]"])

def set_corners():
	for menu in config:
		if menu["menu-name"] == sys.argv[1]:
			set_corners_gsettings(menu["top-left"]["command"], menu["top-right"]["command"], menu["bottom-left"]["command"], menu["bottom-right"]["command"])
			break

def show_info():
	text = ""
	for menu in config:
		if menu["menu-name"] == sys.argv[1]:
			text = "%s\t\t\t\t\t\t\t\t%s\n\n%s\t\t\t\t\t\t\t\t%s" % (menu["top-left"]["option-name"], menu["top-right"]["option-name"], menu["bottom-left"]["option-name"], menu["bottom-right"]["option-name"])
			break
	zenity_processes.append(subprocess.Popen(["zenity", "--title=", "--ok-label=", "--width", "750", "--height", "200","--info", "--text", text]))

def await_action():
	while not os.path.isfile("/dev/shm/hotcorner_exit"):
		pass

def remove_closefile():
	if os.path.isfile("/dev/shm/hotcorner_exit"):
		os.remove("/dev/shm/hotcorner_exit")

def prepare():
	remove_closefile()
	check_args()
	check_depends()
	check_files()
	save_state()

def close():
	close_zenity()
	restore_state()
	remove_closefile()
	sys.exit(EXIT_SUCCESS)

def main():
	prepare()
	set_corners()
	show_info()
	await_action()
	close()

if __name__ == "__main__":
	main()
