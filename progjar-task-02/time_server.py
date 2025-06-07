import socket
import threading
from datetime import datetime

def handle_client(conn, addr):
    print(f"[TERHUBUNG] {addr} terhubung.")
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break

            data = data.strip('\r\n')

            if data == "QUIT":
                print(f"[PUTUS] {addr} mengakhiri koneksi.")
                break

            if data.startswith("TIME"):
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                response = f"JAM {current_time}\r\n"
                conn.sendall(response.encode('utf-8'))
    finally:
        conn.close()


def main():
    host = '0.0.0.0'
    port = 45000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[MENUNGGU] Server berjalan di port {port}...")

    while True:
        conn, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    main()
