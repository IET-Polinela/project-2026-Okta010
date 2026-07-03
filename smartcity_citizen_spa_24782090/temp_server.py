import json
import os
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith('/search/'):
            query = urllib.parse.parse_qs(parsed.query).get('q', [''])[0]
            results = []
            if query.lower() in ['lampu', 'listrik', 'jalan']:
                results = [{
                    'title': 'Lampu Jalan Rusak',
                    'category': 'Infrastruktur',
                    'location': 'Jl. Merdeka',
                    'status': 'REPORTED'
                }]
            body = json.dumps({'results': results}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 5500), Handler).serve_forever()
