import json
import socket
import threading

# import time

from variables import *

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

about_me = {
    'nickname': input('Введите свой никнейм: '),
    'connect': True,
}


def receive():
    while about_me['connect']:
        message = client.recv(SIZE_PACK)
        if message:
            message = json.loads(message.decode(DECODE))
            who = 'Я: ' if message['about']['uuid'] == about_me['uuid'] else f'{message["about"]["nickname"]}: '
            print(f'{who}{message["msg"]["text"]}')


def write():
    while about_me['connect']:
        new_msg = input('Я (@exit для выхода) > ')
        if new_msg.lower() == '@exit':
            print('Закрытие программы')
            about_me['connect'] = False
            client.send(json.dumps({'about': about_me}).encode(DECODE))
            client.close()
            print('Программа завершила работу')
            exit()
        else:
            print("Отправка нового сообщения")
            message = {
                'about': about_me,
                'msg': {
                    'text': new_msg
                }
            }
            client.send(json.dumps(message).encode(DECODE))


client.send(json.dumps(about_me).encode(DECODE))
uuid = client.recv(SIZE_PACK)
if uuid and len(json.loads(uuid)['uuid']) == 36:
    about_me.update(json.loads(uuid))

    write_thread = threading.Thread(target=write)
    write_thread.start()

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
