import bluetooth as bt

server_sock=bt.BluetoothSocket(bt.RFCOMM)
server_sock.bind(("",bt.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "1fab9d30-2a09-4331-b347-b2c4b5bcf302"

bt.advertise_service(server_sock, "Basecamp",
                     service_id = uuid,
                     service_classes = [uuid, bt.SERIAL_PORT_CLASS],
                     profiles = [ bt.SERIAL_PORT_PROFILE ])
                   
print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)

try:
    while True:
        data = client_sock.recv(1024)
        if len(data) == 0: break
        print("received [%s]" % data)
except IOError:
    pass

print("disconnected")

client_sock.close()
server_sock.close()
print("all done")
