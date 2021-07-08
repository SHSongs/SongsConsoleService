import socket
import argparse
import threading
import asyncio
from discord.ext import tasks
from discord.ext import commands
import discord

TOKEN = ''
port = 4000

Receive_Buffer = []
Send_Buffer = []


def handle_receive(lient_socket, user):
    global Receive_Buffer
    while 1:
        try:
            data = client_socket.recv(1024)
        except:
            print("연결 끊김")
            break
        data = data.decode('utf-8')
        Receive_Buffer.append(data)
        print("data :", data)


def handle_send(client_socket):
    global Send_Buffer
    while 1:
        if len(Send_Buffer):
            data = Send_Buffer[0]
            client_socket.send(data)
            Send_Buffer.pop(0)
            if not data:
                print('끊김')
            if data == "/종료":
                break

    client_socket.close()


intent = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intent)

send_channel = None


class chatbot(discord.Client):

    # 1초에 한번 수행될 작업
    # 여기 함수는 에러가 나도 에러 메시지가 출력되지 않으므로 주의.
    @tasks.loop(seconds=0.5)
    async def every_hour_notice(self):
        global send_channel

        if send_channel == None:
            return
        if len(Receive_Buffer) != 0:
            msg = Receive_Buffer[0]
            Receive_Buffer.pop(0)
            client.get_all_channels()
            await send_channel.send(msg)

    # on_ready는 봇을 다시 구성할 때도 호출 됨 (한번만 호출되는 것이 아님.)
    async def on_ready(self):
        game = discord.Game("TEST")
        await client.change_presence(status=discord.Status.online, activity=game)
        print("READY")

        self.every_hour_notice.start()

    # 봇에 메시지가 오면 수행 될 액션
    async def on_message(self, message):
        global send_channel
        if message.author.bot:
            return None
        msg = message.content
        if msg.startswith('!cmd'):
            # 현재 채널을 받아옴
            print(message)
            msg = msg.split()
            cmd = " ".join(msg[1:])
            print(cmd)
            Send_Buffer.append(cmd.encode('utf-8'))
            send_channel = message.channel
            # print(f"channel : {send_channel.id}")
            return None


client = chatbot()


async def start():
    global client
    await client.start(TOKEN)


def run_it_forever(loop):
    loop.run_forever()


def init():
    loop = asyncio.get_event_loop()
    loop.create_task(start())

    thread = threading.Thread(target=run_it_forever, args=(loop,))
    thread.start()


init()

host = '127.0.0.1'
user = 'bot'

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
