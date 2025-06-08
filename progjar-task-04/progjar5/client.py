import socket
import base64
import os
import logging

# Logging ke file, bukan ke terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CLIENT - %(message)s',
    filename='client.log',
    filemode='a'
)

def pilih_server():
    while True:
        print("Pilih server:")
        print("1. Thread Pool (port 8885)")
        print("2. Process Pool (port 8889)")
        pilihan = input("Masukkan pilihan (1/2): ").strip()
        if pilihan == "1":
            return "localhost", 8885
        elif pilihan == "2":
            return "localhost", 8889
        else:
            print("Pilihan tidak valid. Coba lagi.\n")

def kirim_permintaan(ip, port, permintaan):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(permintaan.encode())
        hasil = baca_respon(s)
        print("📩 Respon dari server:\n", hasil)
        logging.info("Feedback diterima dari server:\n" + hasil)

def baca_respon(sock):
    buffer = b""
    while True:
        data = sock.recv(1024)
        if not data:
            break
        buffer += data
    try:
        return buffer.decode("utf-8")
    except UnicodeDecodeError:
        return buffer.decode("utf-8", errors="replace")

def upload_file(ip, port):
    files = [f for f in os.listdir(".") if os.path.isfile(f)]
    if not files:
        print("❌ Tidak ada file di direktori saat ini untuk di-upload.")
        return

    print("\n📂 File di direktori saat ini:")
    for idx, f in enumerate(files):
        print(f"{idx+1}. {f}")

    pilihan = input("Pilih file yang ingin di-upload (nomor): ").strip()
    if not pilihan.isdigit() or int(pilihan) < 1 or int(pilihan) > len(files):
        print("❌ Pilihan tidak valid.")
        return

    filename = files[int(pilihan) - 1]
    with open(filename, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    body = f"{filename}:{encoded}"
    headers = (
        "POST /upload HTTP/1.0\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        "Content-Type: text/plain\r\n"
        "\r\n"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(headers.encode() + body.encode())
        hasil = baca_respon(s)
        print("📩 Respon dari server:\n", hasil)
        logging.info(f"Feedback diterima setelah upload '{filename}':\n{hasil}")

def hapus_file(ip, port):
    filename = input("Masukkan nama file yang ingin dihapus dari folder 'upload': ").strip()
    permintaan = f"DELETE /delete?filename={filename} HTTP/1.0\r\n\r\n"
    kirim_permintaan(ip, port, permintaan)

def menu(ip, port):
    while True:
        print("\nMenu:")
        print("1. Lihat daftar file")
        print("2. Upload file")
        print("3. Hapus file")
        print("4. Keluar")
        pilihan = input("Masukkan pilihan: ").strip()

        if pilihan == "1":
            kirim_permintaan(ip, port, "GET /list HTTP/1.0\r\n\r\n")
        elif pilihan == "2":
            upload_file(ip, port)
        elif pilihan == "3":
            hapus_file(ip, port)
        elif pilihan == "4":
            print("Keluar dari program.")
            logging.info("Client keluar dari program.")
            break
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    ip, port = pilih_server()
    print(f"\n📡 Terhubung ke server di {ip}:{port}")
    logging.info(f"Terhubung ke server {ip}:{port}")
    menu(ip, port)
