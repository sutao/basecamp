'''
Reference
https://tobiastrumm.de/2016/10/04/turning-a-raspberry-pi-3-into-a-bluetooth-low-energy-peripheral/
https://github.com/WIStudent/Bluetooth-Low-Energy-LED-Matrix
https://github.com/WIStudent/Bluetooth-LED-Matrix-App
'''

import dbus
import dbus.mainloop.glib
import base64
import json

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import ble_bluez_rpi3 as ble


class WifiTryConnectChrc(ble.Characteristic):
    UUID = '081403ad-8c87-4f72-a4db-05b260da0010'

    def __init__(self, bus, index, service):
        super(WifiTryConnectChrc, self).__init__(
            bus, index, self.UUID, ['write'], service)

    def WriteValue(self, value, options):
        # Try to connect
        print('[BLE] WifiTryConnectChrc WRITE: {}'.format(value))
        ssid, password = value.split(':')
        try:
            ssid = base64.b64decode(ssid)
            password = base64.b64decode(password)
        except TypeError:
            pass
        self.service.wifi_wizard.try_connect(ssid, password)


class WifiStatusChrc(ble.Characteristic):
    UUID = '081403ad-8c87-4f72-a4db-05b260da0020'

    def __init__(self, bus, index, service):
        super(WifiStatusChrc, self).__init__(
            bus, index, self.UUID, ['read'], service)

    def ReadValue(self, options):
        status = base64.b64encode(json.dumps(self.service.wifi_wizard.read_status()))
        print('[BLE] WifiStatusChrc READ: {}'.format(status))
        return status


class BasecampWifiService(ble.Service):
    UUID = '081403ad-8c87-4f72-a4db-05b260da0000'

    def __init__(self, bus, index, wifi_wizard):
        super(BasecampWifiService, self).__init__(bus, index, self.UUID, True)
        self.add_characteristic(WifiStatusChrc(bus, 0, self))
        self.add_characteristic(WifiTryConnectChrc(bus, 1, self))
        self.wifi_wizard = wifi_wizard


class BasecampWifiApplication(ble.Application):
    def __init__(self, bus, wifi_wizard):
        super(BasecampWifiApplication, self).__init__(bus)
        self.add_service(BasecampWifiService(bus, 0, wifi_wizard))


class BasecampWifiAdvertisement(ble.Advertisement):
    def __init__(self, bus, index):
        super(BasecampWifiAdvertisement, self).__init__(bus, index, 'peripheral')
        self.add_service_uuid(BasecampWifiService.UUID)
        self.include_tx_power = True


class BasecampWifiBLE(object):
    def __init__(self, wifi_wizard):
        self.mainloop = None
        self.wifi_wizard = wifi_wizard

    def register_ad_cb(self):
        """
        Callback if registering advertisement was successful
        """
        print('[BLE] Advertisement registered')


    def register_ad_error_cb(self, error):
        """
        Callback if registering advertisement failed
        """
        print('[BLE] Failed to register advertisement: ' + str(error))
        self.mainloop.quit()


    def register_app_cb(self):
        """
        Callback if registering GATT application was successful
        """
        print('[BLE] GATT application registered')


    def register_app_error_cb(self, error):
        """
        Callback if registering GATT application failed.
        """
        print('[BLE] Failed to register application: ' + str(error))
        self.mainloop.quit()

    def serve(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        bus = dbus.SystemBus()

        # Get ServiceManager and AdvertisingManager
        service_manager = ble.get_service_manager(bus)
        ad_manager = ble.get_ad_manager(bus)

        # Create gatt services
        app = BasecampWifiApplication(bus, self.wifi_wizard)

        # Create advertisement
        test_advertisement = BasecampWifiAdvertisement(bus, 0)

        self.mainloop = GObject.MainLoop()

        # Register gatt services
        service_manager.RegisterApplication(app.get_path(), {},
                                            reply_handler=self.register_app_cb,
                                            error_handler=self.register_app_error_cb)

        # Register advertisement
        ad_manager.RegisterAdvertisement(test_advertisement.get_path(), {},
                                         reply_handler=self.register_ad_cb,
                                         error_handler=self.register_ad_error_cb)

        self.mainloop.run()
