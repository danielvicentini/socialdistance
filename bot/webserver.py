# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer

# Web server port
from config_shared import bot_server_port
import logging
import json 
from logica import trataPOST

# http server
class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    # GET
    # Does nothing today

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

 	# POST function

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n", str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

	    # Content
        content=json.loads(post_data.decode('utf-8'))

        # call function to understand post
        trataPOST(content)

 

def run(server_class=HTTPServer, handler_class=S, port=bot_server_port):
        # Web Server run
        # Server port comes from bot_server_port from config_shared
        logging.basicConfig(level=logging.INFO)
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        logging.info('Starting httpd...\n')
        
        try:
     	    httpd.serve_forever()
        except KeyboardInterrupt:
       	    pass
        httpd.server_close()
        logging.info('Stopping httpd...\n')
