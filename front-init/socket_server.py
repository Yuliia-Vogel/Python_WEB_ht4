
import socket
import json
from datetime import datetime
import urllib.parse


UDP_IP = '127.0.0.1'
UDP_PORT = 5000


def run_socket_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            print('Waiting to receive message')
            data, address = sock.recvfrom(4096)
            print(f'Received data: {data.decode()} from: {address}') # отримали дані
            parsed_data = urllib.parse.unquote_plus(data.decode()) # декодували дані і відкинули непотрібну нам частину
            parsed_dict = {key: value for key, value in [el.split('=') for el in parsed_data.split('&')]}
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            data_to_save = {timestamp: parsed_dict}
            print(data_to_save)
            save_to_json(data_to_save)

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


def save_to_json(data):
    with open('storage/data.json', 'a', encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write('\n')


if __name__ == '__main__':
    run_socket_server(UDP_IP, UDP_PORT)