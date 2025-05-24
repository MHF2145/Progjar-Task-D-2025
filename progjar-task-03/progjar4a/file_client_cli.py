import socket
import json
import base64
import logging
import os

# Fixed server address according to your server config
server_address = ('127.0.0.1', 6666)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu():
    clear_screen()
    print("FILE CLIENT MENU")
    print("----------------")
    print("1. List files on server")
    print("2. Download a file")
    print("3. Upload a file")
    print("4. Delete a file")
    print("5. Exit")
    print()
    print(f"Current server: {server_address[0]}:{server_address[1]}\n")

def send_command(command_str=""):
    global server_address

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(5)  # Timeout 5 seconds
        sock.connect(server_address)
        logging.warning(f"connecting to {server_address}")

        # Append protocol terminator
        full_command = command_str + "\r\n\r\n"
        sock.sendall(full_command.encode())

        data_received = ""
        while True:
            data = sock.recv(4096)
            if not data:
                break
            data_received += data.decode()
            if "\r\n\r\n" in data_received:
                # Got full response
                break
        # Remove terminator before parsing JSON
        data_received = data_received.replace("\r\n\r\n", "")
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except ConnectionRefusedError:
        print("\nError: Connection refused. Server may be down.")
        return dict(status='ERROR', data='Connection refused')
    except socket.gaierror:
        print("\nError: Invalid server address.")
        return dict(status='ERROR', data='Invalid server address')
    except json.JSONDecodeError:
        print("\nError: Failed to decode JSON from server response.")
        return dict(status='ERROR', data='Invalid JSON response')
    except Exception as e:
        logging.warning(f"error during data receiving: {str(e)}")
        return dict(status='ERROR', data=str(e))
    finally:
        sock.close()

def remote_list():
    result = send_command("LIST")
    if result['status'] == 'OK':
        print("\nDaftar file di server:")
        for filename in result['data']:
            print(f"- {filename}")
    else:
        print(f"\nError: {result['data']}")
    input("\nPress Enter to continue...")

def remote_get():
    filename = input("Masukkan nama file yang ingin didownload: ").strip()
    if filename == '':
        print("Nama file tidak boleh kosong")
        input("\nPress Enter to continue...")
        return
    result = send_command(f"GET {filename}")
    if result['status'] == 'OK':
        nama = result.get('data_namafile', 'file_unduhan')
        isi_base64 = result.get('data_file', '')
        try:
            with open(nama, 'wb') as f:
                f.write(base64.b64decode(isi_base64))
            print(f"\nFile '{nama}' berhasil didownload.")
        except Exception as e:
            print(f"\nError menyimpan file: {str(e)}")
    else:
        print(f"\nError: {result['data']}")
    input("\nPress Enter to continue...")

def remote_upload():
    filepath = input("Masukkan path file yang akan diupload: ").strip()
    if not os.path.exists(filepath):
        print("\nFile tidak ditemukan!")
        input("\nPress Enter to continue...")
        return
    try:
        with open(filepath, 'rb') as f:
            file_content = f.read()
        encoded_content = base64.b64encode(file_content).decode()
        filename = os.path.basename(filepath)
        cmd = f"UPLOAD {filename} {encoded_content}"
        result = send_command(cmd)
        if result['status'] == 'OK':
            print(f"\n{result['data']}")
        else:
            print(f"\nError: {result['data']}")
    except Exception as e:
        print(f"\nError: {str(e)}")
    input("\nPress Enter to continue...")

def remote_delete():
    filename = input("Masukkan nama file yang ingin dihapus: ").strip()
    if filename == '':
        print("Nama file tidak boleh kosong")
        input("\nPress Enter to continue...")
        return
    result = send_command(f"DELETE {filename}")
    if result['status'] == 'OK':
        print(f"\n{result['data']}")
    else:
        print(f"\nError: {result['data']}")
    input("\nPress Enter to continue...")

def main():
    while True:
        display_menu()
        choice = input("Pilih menu [1-5]: ").strip()
        if choice == '1':
            remote_list()
        elif choice == '2':
            remote_get()
        elif choice == '3':
            remote_upload()
        elif choice == '4':
            remote_delete()
        elif choice == '5':
            print("Keluar dari program. Bye!")
            break
        else:
            print("\nPilihan tidak valid!")
            input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()
