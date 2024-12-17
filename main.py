import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import os

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path == '/read':
            self.send_messages()
        elif pr_url.path.startswith('/static/'):
            self.send_static_file(pr_url.path)
        else:
            self.send_html_file('error.html', 404)

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)

            username = form_data.get('username', [''])[0]
            message = form_data.get('message', [''])[0]

            self.save_message(username, message)

            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

    def send_messages(self):
        try:
            with open('storage/data.json', 'r', encoding='utf-8') as file:
                messages = json.load(file)
        except FileNotFoundError:
            messages= {}

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        response = "<html><body><h1>All Messages</h1><ul>"
        for timestamp, message_data in messages.items():
            response += f"<li><strong>{message_data['username']}:</strong> {message_data['message']} <em>({timestamp})</em></li>"
        response += "</ul><a href='/'>Back to Home</a></body></html>"

        self.wfile.write(response.encode('utf-8'))


    def save_message(self, username, message):
        data = {}
        timestamp = datetime.now().isoformat()

        if not os.path.exists('storage'):
            os.makedirs('storage')

        try:
            with open('storage/data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        data[timestamp] = {'username': username, 'message': message}

        with open('storage/data.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def send_html_file(self, filename, status=200):
        try:
            with open(f"templates/{filename}", 'rb') as fd:
                self.send_response(status)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(fd.read())
        except FileNotFoundError:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open("templates/error.html", 'rb') as error_fd:
                self.wfile.write(error_fd.read())



    def send_static_file(self, path):
        try:
            with open(path.lstrip('/'), 'rb') as file:
                if path.endswith('.css'):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/css')
                elif path.endswith('.png'):
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                else:
                    self.send_response(404)
                    self.end_headers()
                    return

                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()



def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

if __name__ == '__main__':
    run()
