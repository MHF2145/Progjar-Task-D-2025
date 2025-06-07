import socket

host = '127.0.0.1'
port = 45000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))

    s.sendall(b'TIME\r\n')
    data = s.recv(1024)
    print('Dari server:', data.decode('utf-8'))

    s.sendall(b'QUIT\r\n')
