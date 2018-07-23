import http.server
import socketserver
import os

directorio_script = os.path.dirname(__file__)
directorio_http = os.path.join(directorio_script,'http/')
os.chdir(directorio_http)

PORT = 44444
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()
