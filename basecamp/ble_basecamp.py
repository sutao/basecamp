'''
Reference
https://tobiastrumm.de/2016/10/04/turning-a-raspberry-pi-3-into-a-bluetooth-low-energy-peripheral/
https://github.com/WIStudent/Bluetooth-Low-Energy-LED-Matrix
https://github.com/WIStudent/Bluetooth-LED-Matrix-App
'''

import dbus
import dbus.mainloop.glib

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import ble_bluez_rpi3 as ble


class WifiConnectionChrc(ble.Characteristic):
    UUID = '8b3db1a6-cd57-4f57-af04-c818612f8fc3'

    def __init__(self, bus, index, service):
        super(WifiConnectionChrc, self).__init__(
            bus, index, self.UUID, ['read', 'write'], service)
        self.value = ''

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        # Try to connect
        self.value = value


class WifiStatusChrc(ble.Characteristic):
    UUID = '9c8af7ec-9a45-4ea4-a1bd-e8e2ced01c87'

    def __init__(self, bus, index, service):
        super(WifiStatusChrc, self).__init__(
            bus, index, self.UUID, ['read'], service)

    def ReadValue(self, options):
        return 'unknown'


class DeviceStatusChrc(ble.Characteristic):
    UUID = '3b6bb4ea-347c-4cc5-a133-ffb8841b9ef6'

    def __init__(self, bus, index, service):
        super(DeviceStatusChrc, self).__init__(
            bus, index, DeviceStatusChrc.UUID, ['read'], service)

    def ReadValue(self, options):
        return 'unknown'


class BasecampService(ble.Service):
    UUID = '081403ad-8c87-4f72-a4db-05b260da4b8a'

    def __init__(self, bus, index):
        super(BasecampService, self).__init__(bus, index, self.UUID, True)
        self.add_characteristic(DeviceStatusChrc(bus, 0, self))
        self.add_characteristic(WifiStatusChrc(bus, 1, self))
        self.add_characteristic(WifiConnectionChrc(bus, 2, self))


class BasecampApplication(ble.Application):
    def __init__(self, bus):
        super(BasecampApplication, self).__init__(bus)
        self.add_service(BasecampService(bus, 0))


class BasecampAdvertisement(ble.Advertisement):
    def __init__(self, bus, index):
        super(BasecampAdvertisement, self).__init__(bus, index, 'peripheral')
        self.add_service_uuid(BasecampService.UUID)
        self.include_tx_power = True


class BasecampBLE(object):
    def __init__(self):
        self.mainloop = None

    def register_ad_cb(self):
        """
        Callback if registering advertisement was successful
        """
        print('Advertisement registered')


    def register_ad_error_cb(self, error):
        """
        Callback if registering advertisement failed
        """
        print('Failed to register advertisement: ' + str(error))
        self.mainloop.quit()


    def register_app_cb(self):
        """
        Callback if registering GATT application was successful
        """
        print('GATT application registered')


    def register_app_error_cb(self, error):
        """
        Callback if registering GATT application failed.
        """
        print('Failed to register application: ' + str(error))
        self.mainloop.quit()

    def serve(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        bus = dbus.SystemBus()

        # Get ServiceManager and AdvertisingManager
        service_manager = ble.get_service_manager(bus)
        ad_manager = ble.get_ad_manager(bus)

        # Create gatt services
        app = BasecampApplication(bus)

        # Create advertisement
        test_advertisement = BasecampAdvertisement(bus, 0)

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
