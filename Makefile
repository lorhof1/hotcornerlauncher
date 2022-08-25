default:
	which python3 || echo --- python3 not found --- > /dev/stderr
	which python3
	which zenity  || echo --- zenity not found --- > /dev/stderr
	which zenity
	echo --- Completed ---

install:
	install main.py /usr/local/bin/hotcornerlauncher

uninstall:
	rm /usr/local/bin/hotcornerlauncher
