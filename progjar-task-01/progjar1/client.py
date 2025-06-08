import socket
import logging
import os
import time

logging.basicConfig(level=logging.INFO)

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)  # Timeout for initial connect attempt

    server_address = ('172.18.0.3', 32444)
    logging.info(f"connecting to {server_address}")
    sock.connect(server_address)

    sock.settimeout(None)  # Reset timeout after connection

    filepath = 'test.txt'
    if not os.path.exists(filepath):
        logging.error("File 'test.txt' tidak ditemukan!")
        exit(1)

    with open(filepath, 'r') as f:
        message = f.read()

    logging.info(f"sending file content: {message}")
    sock.sendall(message.encode())

    # Receive response (up to 10 seconds total)
    start_time = time.time()
    while time.time() - start_time < 10:
        try:
            sock.settimeout(1)
            data = sock.recv(1024)
            if data:
                logging.info(f"received: {data.decode()}")
        except socket.timeout:
            continue
        except Exception as e:
            logging.info(f"Receive error: {e}")
            break

    # ✅ Additional silent waiting time (e.g., 3 seconds)
    time.sleep(3)

except Exception as ee:
    logging.info(f"ERROR: {str(ee)}")
    exit(0)
finally:
    logging.info("closing")
    sock.close()
