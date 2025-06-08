from socket import *
import socket
import time
import sys
import logging
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

# Konfigurasi logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')

def ProcessTheClient(connection, address):
    rcv = b""
    headers_done = False
    content_length = 0

    while True:
        try:
            data = connection.recv(1024)
            if not data:
                break
            rcv += data

            if not headers_done:
                if b"\r\n\r\n" in rcv:
                    headers_done = True
                    headers, rest = rcv.split(b"\r\n\r\n", 1)
                    for line in headers.decode().split("\r\n"):
                        if line.lower().startswith("content-length"):
                            content_length = int(line.split(":")[1].strip())
                    rcv = headers + b"\r\n\r\n" + rest
                    if len(rest) >= content_length:
                        break
            else:
                body = rcv.split(b"\r\n\r\n", 1)[1]
                if len(body) >= content_length:
                    break
        except Exception as e:
            logging.warning(f"❌ Error saat menerima data dari {address}: {e}")
            break

    try:
        logging.warning(f"\n📩 Permintaan dari {address}:\n{rcv.decode(errors='ignore')}")
        hasil = httpserver.proses(rcv.decode(errors='ignore'))
        hasil = hasil + b"\r\n\r\n"
        connection.sendall(hasil)
        logging.warning(f"📤 Balasan ke {address}:\n{hasil.decode(errors='ignore')}")
    except Exception as e:
        logging.warning(f"❌ Gagal memproses data dari {address}: {e}")
    finally:
        connection.close()

def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', 8885))
    my_socket.listen(1)

    logging.warning("🚀 Server thread pool aktif di port 8885 (1 thread aktif untuk layanan bergantian).")

    # Hanya 1 thread aktif agar permintaan dilayani bergantian
    with ThreadPoolExecutor(1) as executor:
        while True:
            connection, client_address = my_socket.accept()
            logging.warning(f"🔗 Koneksi dari {client_address}")
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)
            aktif = sum(1 for i in the_clients if not i.done())
            print(f"🔁 Jumlah thread aktif: {aktif}")

def main():
    Server()

if __name__ == "__main__":
    main()
