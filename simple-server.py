import socket

# client connection handler
def request_handler(client_socket):
    client_socket.recv(1024)
    response = b'HTTP/1.1 200 OK\r\nContent-Length: 12\r\n\r\nHello, world!'
    #send() returns the number of bytes sent, which may be less than the size of the data passed in. You’re responsible for checking this and calling send() as many times as needed to send all of the data.
    # Unlike send(), sendall() method continues to send data from bytes until either all data has been sent or an error occurs. None is returned on success.”
    client_socket.sendall(response)
    client_socket.close()


def server_on_loop(server_socket):
    try:
        while True:
            # The .accept() method blocks execution and waits for an incoming connection. When a client connects, it returns a new socket object representing the connection and a tuple holding the address of the client. 
            # We have a new socket object from .accept(). This is important because it’s the socket that you’ll use to communicate with the client. 
            # It’s distinct from the listening socket that the server is using to accept new connections.
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            request_handler(client_socket)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        server_socket.close()

HOST = '127.0.0.1' #network interface; local host
PORT = 8080 #port

#creating listening socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket() creates a socket object; AF_INET is the Internet address family for IPv4 and SOCK_STREAM is for defining socket type (TCP protocol)
server_socket.bind((HOST, PORT)) #.bind() method is used to associate the socket with a specific network interface and port number
server_socket.listen(2) #backlog queue=2; 2 here means that 2 connections are kept waiting if the server is busy and if a 3rd socket tries to connect then the connection is refused.
print(f"Serving at {HOST}:{PORT}")

try:
    server_on_loop(server_socket)
finally:
    server_socket.close()
    print("Server stopped.")
