import socket
import os
import time

SERVER_HOST = '127.0.0.1'


def list_files(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, port))
            s.sendall(b"LIST")
            result = s.recv(8192).decode()
            return result.split('\n'), True
    except Exception as e:
        return str(e), False


def upload_file(port, filepath):
    try:
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, port))
            s.sendall(f"UPLOAD {filename} {filesize}".encode())
            ack = s.recv(1024)
            if ack != b"OK":
                return f"Server refused: {ack.decode()}", False

            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    s.sendall(chunk)

            status = s.recv(1024).decode()
            return status, status == "SUCCESS"
    except Exception as e:
        return str(e), False


def download_file(port, filename, output_dir):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, port))
            s.sendall(f"DOWNLOAD {filename}".encode())
            header = s.recv(1024).decode()
            if header.startswith("ERROR"):
                return header, False

            filesize = int(header)
            s.sendall(b"OK")

            output_path = os.path.join(output_dir, filename)
            with open(output_path, "wb") as f:
                received = 0
                while received < filesize:
                    data = s.recv(min(4096, filesize - received))
                    if not data:
                        break
                    f.write(data)
                    received += len(data)
            return f"Downloaded {filename}", True
    except Exception as e:
        return str(e), False

