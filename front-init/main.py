import json
import mimetypes
import pathlib
import socket
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self): # відправити повідомлення
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(post_data)
        send_to_socket(post_data) # Відправляємо байтову строку через сокет 
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self): # отримати сторінку 
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/': # головна сторінка
            self.send_html_file('index.html')
        elif pr_url.path == '/message': # надіслати повідомлення
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static() # картинки та стилі з папки statics
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def send_to_socket(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 5000)
    try:
        sock.sendto(data, server_address)
    finally:
        sock.close()

def run_http_server(): # запуск сервера веб-застосунку
    server_address = ('', 3000)
    http = HTTPServer(server_address, HttpHandler)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def run_socket_server(): # запуск сервера сокета
    UDP_IP = '127.0.0.1'
    UDP_PORT = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = UDP_IP, UDP_PORT
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
        sock.close()

        

def save_to_json(data):
    with open('storage/data.json', 'a', encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write('\n')

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_http_server)
    server_thread.start()

    socket_server_thread = threading.Thread(target=run_socket_server)
    socket_server_thread.start()

    server_thread.join()
    socket_server_thread.join()