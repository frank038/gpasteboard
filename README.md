(Python) Gtk3 Clipboard.

Free to use and modify.

Gpasteboard is a clipboard program for Linux.
The main program and its applet are built using
Python3 and the Gtk3 libraries. 
No additional modules are required.

Gpasteboard can store and set pieces of text and
can store, set and save pictures (or disable this option in the config file). It can show the 
preview of the stored items, can delete each entry
or the whole history.

As default option, the path names of the copied files and folders are not stored.
This behaviour, and other settings, can be changed in the config file.

This program has an option that discharges all text over a certain lenght (actually 1000 characters), unless this option is setted to 0.

All clipboards are stored in text files, that can be modified with a text editor; because this program store statically the previews internally (instead of the full texts for fast loading and less resources usage), after a modification of the files, this program needs to be restarted to update the previews.

To execute this program from the terminal:
./gpasteboard.sh
or
python3 Gpasteboard.py

![My image](https://github.com/frank038/gpasteboard/blob/master/Screen1.png)

![My image](https://github.com/frank038/gpasteboard/blob/master/Screen2.png)
