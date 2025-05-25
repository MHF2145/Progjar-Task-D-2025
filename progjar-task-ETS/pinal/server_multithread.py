import socket
import os
import threading
from concurrent.futures import ThreadPoolExecutor

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 3535
MAX_WORKERS = 10
STORAGE_DIR = 'storage_multithread'

os.makedirs(STORAGE_DIR, exist_ok=True)

def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode()
        if not data:
            return

        if data == "LIST":
            files = os.listdir(STORAGE_DIR)
            conn.sendall("\n".join(files).encode())

        elif data.startswith("UPLOAD"):
            _, filename, filesize = data.split()
            filesize = int(filesize)
            conn.sendall(b"OK")

            path = os.path.join(STORAGE_DIR, filename)
            with open(path, "wb") as f:
                received = 0
                while received < filesize:
                    chunk = conn.recv(min(4096, filesize - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
            conn.sendall(b"SUCCESS")

        elif data.startswith("DOWNLOAD"):
            _, filename = data.split()
            path = os.path.join(STORAGE_DIR, filename)
            if not os.path.exists(path):
                conn.sendall(b"ERROR: File not found")
                return
            filesize = os.path.getsize(path)
            conn.sendall(str(filesize).encode())

            ack = conn.recv(1024)
            if ack != b"OK":
                return

            with open(path, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    conn.sendall(chunk)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def start_server():
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((SERVER_HOST, SERVER_PORT))
            s.listen(100)
            print(f"[THREAD SERVER] Listening on {SERVER_PORT} with {MAX_WORKERS} threads")

            while True:
                conn, addr = s.accept()
                executor.submit(handle_client, conn, addr)

if __name__ == "__main__":
    start_server()
