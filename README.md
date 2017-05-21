Basecamp
--------

```sh
sudo apt-get install python-dev libbluetooth-dev python-dbus
sudo pip install virtualenv
make venv
source env/bin/activate
make install
```

To prepare the system:

To add Serial Port Profile:
Change `/etc/systemd/system/dbus-org.bluez.service` and add `-C` after `bluetoothd` and reboot.
Run `sudo sdptool add SP`.
