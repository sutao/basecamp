Basecamp
========

Preparation
-----------
```sh
sudo apt-get install python-dbus
sudo pip install virtualenv
make venv
source env/bin/activate
make install
```

Notes
-----
* Might have to upgrade BlueZ to the latest version
* Must enable BlueZ experimental features
* Refer to this document: https://stackoverflow.com/questions/41351514/leadvertisingmanager1-missing-from-dbus-objectmanager-getmanagedobjects

References
----------
* https://tobiastrumm.de/2016/10/04/turning-a-raspberry-pi-3-into-a-bluetooth-low-energy-peripheral/
* https://github.com/WIStudent/Bluetooth-Low-Energy-LED-Matrix
* https://github.com/WIStudent/Bluetooth-LED-Matrix-App
* https://github.com/comarius/bunget
* https://medium.com/@kbabcockuf/bridging-the-gap-bluetooth-le-security-aab27232a767
