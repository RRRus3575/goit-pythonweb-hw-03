from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path.startswith('/static/'):
            self.send_static_file(pr_url.path)
        else:
            self.send_html_file('error.html', 404)

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
