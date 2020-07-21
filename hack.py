import sys
import socket
import itertools


args = sys.argv
conn = socket.socket()
conn.connect((args[1], int(args[2])))

c = ''.join([chr(c) for c in range(97, 97 + 26)] + [str(c) for c in range(10)])
pass_dict = []
password = ''
while not password:
    pass_dict.append(c)

    for p in itertools.product(*pass_dict):
        pass_to_try = ''.join(p)
        conn.send(pass_to_try.encode())
        serv_resp = conn.recv(50).decode()
        if serv_resp == 'Connection success!':
            password = pass_to_try
            print(password)
            break

conn.close()
