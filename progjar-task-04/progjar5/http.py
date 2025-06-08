import os
import urllib.parse as urlparse
from urllib.parse import parse_qs
import base64
import time  # Tambahan untuk delay

class HttpServer:
    def proses(self, data):
        baris = data.split("\r\n")
        baris_request = baris[0]
        try:
            method, path, _ = baris_request.split(" ")
        except ValueError:
            return b"HTTP/1.0 400 Bad Request\r\n\r\n"

        if method == "GET" and path == "/list":
            return self.daftar_file()

        elif method == "POST" and path == "/upload":
            return self.upload_file(baris)

        elif method == "DELETE" and path.startswith("/delete"):
            return self.hapus_file(path)

        return b"HTTP/1.0 400 Bad Request\r\n\r\nUnknown Request"

    def daftar_file(self):
        try:
            time.sleep(2)
            folder = "upload"
            os.makedirs(folder, exist_ok=True)
            files = os.listdir(folder)
            if not files:
                body = "Tidak ada file yang sudah di-upload."
            else:
                body = "\n".join(files)
            return f"HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\n{body}".encode()
        except Exception as e:
            return f"HTTP/1.0 500 Internal Server Error\r\n\r\n{str(e)}".encode()

    def upload_file(self, baris):
        try:
            time.sleep(2)
            index = baris.index('')
            body_lines = baris[index + 1:]
            isi = "\r\n".join(body_lines)

            if ":" in isi:
                filename, b64content = isi.split(":", 1)
                folder = "upload"
                os.makedirs(folder, exist_ok=True)
                path = os.path.join(folder, filename.strip())
                with open(path, "wb") as f:
                    f.write(base64.b64decode(b64content))
                return b"HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nUpload berhasil. Tekan Enter untuk kembali ke menu."
            else:
                return b"HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nFormat tidak valid. Tekan Enter untuk kembali ke menu."
        except Exception as e:
            return f"HTTP/1.0 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nTerjadi kesalahan: {str(e)}\nTekan Enter untuk kembali ke menu.".encode()

    def hapus_file(self, path):
        try:
            time.sleep(2)
            parsed = urlparse.urlparse(path)
            params = parse_qs(parsed.query)
            filename = params.get("filename", [None])[0]
            folder = "upload"
            full_path = os.path.join(folder, filename) if filename else None
            if full_path and os.path.exists(full_path):
                os.remove(full_path)
                return b"HTTP/1.0 200 OK\r\n\r\nFile dihapus"
            else:
                return b"HTTP/1.0 404 Not Found\r\n\r\nFile tidak ditemukan"
        except Exception as e:
            return f"HTTP/1.0 500 Internal Server Error\r\n\r\n{str(e)}".encode()
