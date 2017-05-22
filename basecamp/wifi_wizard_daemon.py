import ble_wifi
import subprocess
import threading
import time

WPA_FILE = '/tmp/wpa.conf'
INTERFACE = 'wlan0'


class WifiWizardDaemon(object):
    def __init__(self):
        self.ble = ble_wifi.BasecampWifiBLE(self)
        self.ble_thread = None

    def __cmd(self, cmd):
        return subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        ).stdout.read().decode()

    def try_connect(self, ssid, password):
        print "Try to connec to wifi, SSID:", ssid

        # Stop all previous attemps
        self.__cmd('sudo killall wpa_supplicant')

        # Create wpa file
        f = open(WPA_FILE, 'w')
        f.write('network={{\n    ssid="{}"\n    psk="{}"\n}}\n'.format(
            ssid, password))
        f.close()

        # Attempt to connect
        self.__cmd('sudo wpa_supplicant -i{} -c{} -B'.format(INTERFACE, WPA_FILE))

    def read_status(self):
        # get interface status
        response = self.__cmd('iwconfig {}'.format(INTERFACE))
        networks = []

        # the current network is on the first line like ESSID:"network"
        for line in response.splitlines():
            line = line.replace('"', '')
            parts = line.split('ESSID:')
            if len(parts) > 1:
                network = parts[1].strip()
                if network != 'off/any':
                    networks.append(network)

        print "Wifi status query:", networks
        return networks

    def start(self):
        if self.ble_thread is not None:
            return

        self.ble_thread = threading.Thread(target=self.ble.serve)
        self.ble_thread.daemon = True
        self.ble_thread.start()

        check_timeout_ms = 5000
        while check_timeout_ms > 0 and (self.ble.mainloop is None or not self.ble.mainloop.is_running()):
            time.sleep(0.01)
            check_timeout_ms -= 10

        if check_timeout_ms > 0:
            print "BLE thread started"
            return True
        else:
            print "BLE start timeout"
            return False
