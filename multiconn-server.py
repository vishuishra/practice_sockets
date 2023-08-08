import sys
import socket
import selectors
import types

# Selectors module allows high-level and efficient I/O multiplexing, 
sel = selectors.DefaultSelector()


def accept_wrapper(sock):
    # the listening socket was registered for the event selectors.EVENT_READ, it should be ready to read. 

    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    # if connection blocks, then the entire server is stalled until it returns. That means other sockets are left waiting even though the server isn’t actively working. This is the dreaded “hang” state that you don’t want your server to be in.
    conn.setblocking(False)
    # an object to hold the data that you want included along with the socket using a SimpleNamespace.
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    # the client connection is ready for either reading or writing, both of those events are set with the bitwise OR operator
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # events mask, socket, and data objects are then passed to sel.register() to be monitored with sel.select() for the events
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    #  key is the namedtuple returned from .select() that contains the socket object (fileobj) and data object. mask contains the events that are ready.
    
    sock = key.fileobj
    data = key.data
    # If the socket is ready for reading, then mask & selectors.EVENT_READ will evaluate to True, so sock.recv() is called. 
    # Any data that’s read is appended to data.outb so that it can be sent later.
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            # If no data is received, this means that the client has closed their socket, so the server should too. call sel.unregister() before closing, so it’s no longer monitored by .select().
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    # If socket is ready for writing then the received data stored in data.outb is echoed to the client using sock.send(). The bytes sent are then removed from the send buffer. 
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)
            # .send() method returns the number of bytes sent. This number can then be used with slice notation on the .outb buffer to discard the bytes sent  
            data.outb = data.outb[sent:]


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

#creating listening socket
host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
# lsock.setblocking(False) to configure the socket in non-blocking mode. Calls made to this socket will no longer block.
lsock.setblocking(False) 
# sel.register() registers the socket to be monitored with sel.select() for the events that you’re interested in. For the listening socket, you want read events: selectors.EVENT_READ.
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        # sel.select(timeout=None) blocks until there are sockets ready for I/O. It returns a list of tuples, one for each socket. Each tuple contains a key and a mask. 
        # The key is a SelectorKey namedtuple that contains a fileobj attribute. key.fileobj is the socket object, and mask is an event mask of the operations that are ready.

        # If key.data is None, then you know it’s from the listening socket and you need to accept the connection. Created accept_wrapper() function to get the new socket object and register it with the selector.

        # If key.data is not None, then you know it’s a client socket that’s already been accepted, and you need to service it. service_connection() is then called with key and mask as arguments, and that’s everything you need to operate on the socket.
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
