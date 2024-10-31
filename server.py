import json
import socket
import threading
import uuid

from variables import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = dict()


def broadcast(message):
    print(f'BroadcastMessage: {message}')
    for client in clients.keys():
        print(f'BroadcastKeyClient: {client}')
        print(f'BroadcastClientSocket: {clients[client]['socket']}')
        clients[client]['socket'].send(json.dumps(message).encode(DECODE))
        print('BroadcastSended')


def close_connect(client: socket.socket, about):
    if about['uuid'] in clients.keys() and client == clients[about['uuid']]['socket']:
        clients.pop(about['uuid'])
        client.close()


def handle(client: socket.socket):
    while True:
        try:
            message = client.recv(SIZE_PACK)
            if message:
                message = json.loads(message.decode(DECODE))
                print(f'HandleMessage: {message}')
                if 'connect' in message['about'].keys() and not message['about']['connect']:
                    print('Закрытие соединения')
                    close_connect(client, message['about'])
                else:
                    print('Групповая рассылка')
                    broadcast(message)
            else:
                raise Exception('Connect refused')
        except Exception as err:
            print('Connect refused')
            print(f'Error: {err}')
            client.close()
            break


def reg_client(client: socket.socket):
    new_uuid = str(uuid.uuid4())
    while new_uuid in clients.keys():
        new_uuid = str(uuid.uuid4())
    client.send(json.dumps({'uuid': new_uuid}).encode(DECODE))
    clients[new_uuid] = {'socket': client}



def receive():
    while True:
        client, address = server.accept()
        print(f'Connect {client} by address {address}')

        message = client.recv(SIZE_PACK)
        if message:
            message = json.loads(message.decode(DECODE))
            if not message.get('uuid') or not len(message['uuid']) != 36 or message['uuid'] not in clients.keys():
                reg_client(client)

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


receive()
