import socket
import argparse
import threading
from subprocess import *

import os

port = 4000

Send_Buffer = []

os.chdir('/')


def handle_receive(lient_socket, user):
    global Send_Buffer
    while 1:
        try:
            data = client_socket.recv(1024)
        except:
            print("연결 끊김")
            break
        data = data.decode('utf-8')
        cmd = data.split()

        if len(cmd) > 0:
            if cmd[0] == 'cd':
                try:
                    s = os.path.join(os.getcwd(), cmd[1])
                    os.chdir(s)
                    res = os.getcwd() + '\n' + '이동'
                except:
                    res = 'No such file or directory'
            elif cmd[0] == 'docker':
                thread = threading.Thread(target=lambda : check_output(cmd, universal_newlines=True, stderr=STDOUT), args=())
                thread.daemon = True
                thread.start()
            else:
                try:
                    res = check_output(cmd, universal_newlines=True, stderr=STDOUT)
                except CalledProcessError as e:
                    print(e.output)
                    res = e.output
                except Exception as e:
                    res = 'not found cmd'
                    print(res)
            if len(res) == 0:
                res = '반환값이 없으나 잘 되었을 겁니다'
            Send_Buffer.append(res.encode())
            print(res)
            print(data)
        else:
            print('cmd len == 0')


def handle_send(client_socket):
    global Send_Buffer
    while 1:
        if len(Send_Buffer) > 0:
            data = Send_Buffer[0]
            client_socket.send(data)
            if data == "/종료":
                break
            Send_Buffer.pop(0)
    client_socket.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="\nJoo's client\n-p port\n-i host\n-s string")
    parser.add_argument('-p', help="port")
    parser.add_argument('-i', help="host")
    parser.add_argument('-u', help="user")

    args = parser.parse_args()
    host = args.i

    user = str(args.u)
    if user == 'None':
        user = 'ooc'

    print(user)
    host = '172.17.0.1'
    try:
        port = int(args.p)
    except:
        pass
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((host, port))

    client_socket.send(user.encode('utf-8'))

    receive_thread = threading.Thread(target=handle_receive, args=(client_socket, user))
    receive_thread.daemon = True
    receive_thread.start()

    send_thread = threading.Thread(target=handle_send, args=(client_socket,))
    send_thread.daemon = True
    send_thread.start()

    send_thread.join()
    receive_thread.join()
