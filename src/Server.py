import socket
import argparse
import threading
import time

host = "0.0.0.0"
port = 4000
user_list = {}
notice_flag = 0

default_cmd_executor = None


def msg_func(msg, user):
    global default_cmd_executor

    print(msg)
    if user == 'bot':
        lst = msg.split()

        if lst[-2] == 'setup_cmd':  # default cmd executor setup
            if lst[-1] in user_list:
                default_cmd_executor = lst[-1]
            else:
                msg = "not found cmd executor"
                user_list[user].send(msg.encode('utf-8'))
            return

        if lst[-1] in user_list:
            try:
                msg = " ".join(lst[0:-1])

                print(lst)
                print(msg)
                user_list[lst[-1]].send(msg.encode('utf-8'))
            except:
                print("연결이 비 정상적으로 종료된 소켓 발견")
        else:
            for con in user_list.values():
                try:
                    if con != user_list[user]:
                        print(con)
                        con.send(msg.encode('utf-8'))
                except:
                    print("연결이 비 정상적으로 종료된 소켓 발견")
    else:
        try:
            user_list['bot'].send(msg.encode('utf-8'))
        except:
            print("연결이 비 정상적으로 종료된 소켓 발견")

def handle_receive(client_socket, addr, user):
    msg = "---- %s님이 들어오셨습니다. ----" % user
    msg_func(msg, user)
    while 1:
        data = client_socket.recv(1024)
        string = data.decode('utf-8')
        if not string:
            print('끈김')
            del user_list[user]
            break
        if "/종료" in string:
            msg = "---- %s님이 나가셨습니다. ----" % user
            # 유저 목록에서 방금 종료한 유저의 정보를 삭제
            del user_list[user]
            # msg_func(msg, user)
            break
        # string = "%s : %s" % (user, string)
        msg_func(string, user)
    client_socket.close()


def handle_notice(client_socket, addr, user):
    pass


def accept_func():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 포트를 사용 중 일때 에러를 해결하기 위한 구문
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))

    server_socket.listen(5)

    while 1:
        try:
            client_socket, addr = server_socket.accept()
        except KeyboardInterrupt:
            for user, con in user_list:
                con.close()
            server_socket.close()
            print("Keyboard interrupt")
            break
        user = client_socket.recv(1024).decode('utf-8')
        user_list[user] = client_socket

        notice_thread = threading.Thread(target=handle_notice, args=(client_socket, addr, user))
        notice_thread.daemon = True
        notice_thread.start()

        receive_thread = threading.Thread(target=handle_receive, args=(client_socket, addr, user))
        receive_thread.daemon = True
        receive_thread.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="\nJoo's server\n-p port\n")
    parser.add_argument('-p', help="port")

    args = parser.parse_args()
    try:
        port = int(args.p)
    except:
        pass
    accept_func()
