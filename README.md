Nautilus Plugin for DeepaMehta 3
================================

Enriches your favourite GNOME filebrowser nautilus with a direct link to a topic map and therewith brings complex information organization to and around your files and folders.

##Installation

_Note:_ This program is currently just reported to be working with **Ubuntu 10.04** and GNOME Desktop. If you would like to help making it work on other platforms as well, check out the python libraries of your favourite filebrowser and the current [issues](https://github.com/mukil/deepamehta3-nautilus/issues).

 -  download and unpack the deepamehta3-nautilus archive
 -  adapt your current deepamehta installation dir (optional)
 -  copy its content to the .nautilus folder
 -  install required ubuntu packages and the deepamehta3-foldercanvas plugin for your personal deepamehta3 installation

To install the software on your computer Ubuntu 10.04 operating system open up a terminal and enter
    unzip deepamehta3-nautilus-v1.0.zip
    adapt the path of your DM_INSTALLATION_DIR (optional in the just extracted file _monty.py_)
    switch from firefox to google-chrome as your default browser for the deepamehta client 
      through changing the value of START_DM_IN_CHROME to _True_ (optional in the just extracted file deepamehta3-nautilus.py)

    mkdir .nautilus/python-extensions/ (if this folder does not already exist)
    cp deepamehta3-nautilus-v1.0/deepamehta3-nautilus.py ~/.nautilus/python-extensions/
    cp deepamehta3-nautilus-v1.0/monty.py ~/.nautilus/python-extensions/

    sudo apt-get install python-nautilus
    sudo apt-get install python-setuptools
    sudo easy_install restclient

To install the deepamehta3-foldercanvas plugin enter into your deepamehta3-server terminal the following line
    start http://www.deepamehta.de/maven2/de/deepamehta/deepamehta3-foldercanvas/0.4.1/deepamehta3-foldercanvas-0.4.1.jar

##Requirements

The [DeepaMehta3 Server](https://github.com/jri/deepamehta3/downloads) (at least in v0.4.1) provides you the underlying networked semantic desktop for nuts the [Folder Canvas Plugin](https://github.com/jri/deepamehta3-foldercanvas) uses to be the tool that brings a topic map in harmony with any folder in your unix filesystem in harmony.

Ubuntu & Python Packages: _python-nautilus 2.0_ (0.6.1-1 lucid), _python-setuptools_ (0.6.4-10 lucid) and the [restclient](http://pypi.python.org/pypi/restclient/) python egg (0.9.10)

Developer Hints
-----------

use the nautilus context menu and listen what the plugin does already through executing in your favourite shell:
    tail -fn 500 /var/log/syslog

Version History
---------------
**v1.0b** -- November 12, 2010

* enables folder - topic map synchronization via your nautilus and topic map context menu
* beginning of modularization towards a dm3c python client (monty.py)
* installation tested for the first time

**v0.1a** -- August 19, 2010

* DeepaMehta 3 v0.4.1-SNAPSHOT

---------------------------------------------
Author: Malte Reißig malte aed deepamehta.org
Last Modified: November 12, 2010
