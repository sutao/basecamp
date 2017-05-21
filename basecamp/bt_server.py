import bluetooth as bt
import subprocess
import threading

UUID = "1fab9d30-2a09-4331-b347-b2c4b5bcf302"
SERVICE_NAME = "Basecamp"


class BasecampBluetoothServer(object):
    def __init__(self, client_callback, uuid=None, service_name=None):
        self.server_sock = None
        self.server_thread = None
        self.client_threads = []
        self.client_callback = client_callback
        self.uuid = UUID if uuid is None else uuid
        self.service_name = SERVICE_NAME if service_name is None else service_name

    def start(self):
        if self.server_sock is not None:
            return

        assert self.client_callback, "Client callback must be set"
        assert self.uuid, "Server UUID must be set"
        assert self.service_name, "Service name must be set"

        # Makes the device discoverable
        subprocess.call(['sudo', 'hciconfig', 'hci0', 'piscan'])

        # Create the bluetooth socket
        server_sock = bt.BluetoothSocket(bt.RFCOMM)
        server_sock.bind(("", bt.PORT_ANY))
        server_sock.listen(1)

        port = server_sock.getsockname()[1]

        # Advertise the service
        bt.advertise_service(server_sock, self.service_name,
                             service_id=self.uuid,
                             service_classes=[self.uuid, bt.SERIAL_PORT_CLASS],
                             profiles=[bt.SERIAL_PORT_PROFILE])

        self.server_sock = server_sock

        # Create the serve thread
        self.server_thread = threading.Thread(target=self.serve)
        self.server_thread.daemon = True
        self.server_thread.start()

        print("Waiting for connection on RFCOMM channel %d" % port)

    def serve(self):
        while True:
            try:
                client_sock, client_info = self.server_sock.accept()
                print("Accepted connection from ", client_info)
                self.client_callback(client_sock, client_info)
            except IOError:
                pass
            finally:
                client_sock.close()

