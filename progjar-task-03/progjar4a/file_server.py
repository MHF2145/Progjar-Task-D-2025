from socket import *
import socket
import threading
import logging
import json

from file_protocol import FileProtocol
fp = FileProtocol()


class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = address

    def run(self):
        buffer = ""
        try:
            while True:
                data = self.connection.recv(32)
                if not data:
                    break
                buffer += data.decode()

                # Check if full request ended by \r\n\r\n
                if "\r\n\r\n" in buffer:
                    # Split requests by delimiter, in case multiple requests in buffer
                    requests = buffer.split("\r\n\r\n")
                    for req in requests[:-1]:
                        logging.info(f"Request from {self.address}: {req}")
                        response = fp.proses_string(req.strip())
                        response += "\r\n\r\n"
                        self.connection.sendall(response.encode())
                    # Keep last partial request in buffer
                    buffer = requests[-1]

        except Exception as e:
            logging.error(f"Error with client {self.address}: {e}")
        finally:
            self.connection.close()
            logging.info(f"Connection closed with {self.address}")


class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=6666):
        threading.Thread.__init__(self)
        self.ipinfo = (ipaddress, port)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        logging.info(f"Server listening on {self.ipinfo[0]}:{self.ipinfo[1]}")

        try:
            while True:
                connection, client_address = self.my_socket.accept()
                logging.info(f"Connection from {client_address}")

                clt = ProcessTheClient(connection, client_address)
                clt.start()
                self.the_clients.append(clt)

        except KeyboardInterrupt:
            logging.info("Server shutting down...")
        finally:
            self.my_socket.close()


def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S')

    svr = Server(ipaddress='0.0.0.0', port=6666)
    svr.start()


if __name__ == "__main__":
    main()
