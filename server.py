#!/usr/bin/env python3

import socket
import threading as thr
import time

HOST = '127.0.0.1'
PORT = 65432

sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock1.bind((HOST, PORT))
sock1.listen()
conn, addr = sock1.accept()
conn1, addr1 = sock1.accept()

print(f'received a connection from {addr}')
print(f'received a connection from {addr1}')

with conn:
    while True:
        data = conn.recv(1024)
        start = time.perf_counter()  # received the request

        print(f"received: {data}")

        if not data:
            break

        data = data.decode("utf-8")  # decode from bytes
        data = int(data)  # convert to int

        if data > 30:
            sock1.close()
            break
        else:
            data += 1
            data = f'{data}'  # convert to string
            data = str.encode(data)  # convert to bytes

        print(f"sending: {data}")

        end = time.perf_counter()  # handled the request

        print(f'handled the request in {end - start}ms')
        conn.sendall(data)
