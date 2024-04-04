import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
# import json
# from datetime import datetime
import socket


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self): # відправити повідомлення
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(post_data)
        send_to_socket(post_data) # Відправляємо байтову строку через сокет # відправляємо дані через сокет
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self): 
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/': # головна сторінка
            self.send_html_file('index.html')
        elif pr_url.path == '/message': # надіслати повідомлення
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
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

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()

