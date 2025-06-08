import socket
import logging
import time

logging.basicConfig(level=logging.INFO)

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        logging.info(f"Could not get IP address: {e}")
        return "127.0.0.1"

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ('0.0.0.0', 32444)
    logging.info(f"starting up on {server_address}")
    sock.bind(server_address)

    local_ip = get_ip_address()
    logging.info(f"Server is running at IP address: {local_ip}, port: {server_address[1]}")

    sock.listen(1)
    while True:
        logging.info("waiting for a connection")
        connection, client_address = sock.accept()
        try:
            logging.info(f"connection from {client_address}")
            full_data = b""

            # Receive all data from client (until it stops sending)
            connection.settimeout(2)  # Short timeout to detect end of transmission
            while True:
                try:
                    data = connection.recv(1024)
                    if data:
                        logging.info(f"received: {data}")
                        full_data += data
                    else:
                        break
                except socket.timeout:
                    break  # End receiving if client stops sending for 2 seconds

            if full_data:
                logging.info("sending back data")
                connection.sendall(full_data)

            # Optional: Wait silently before closing (matches client waiting)
            time.sleep(3)

        except Exception as e:
            logging.info(f"Error during connection handling: {e}")
        finally:
            connection.close()
            logging.info("connection closed")

except Exception as ee:
    logging.info(f"ERROR: {str(ee)}")
finally:
    logging.info('closing')
    sock.close()
