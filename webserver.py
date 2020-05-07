from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json 
import os
from logica import trataPOST

# http server
class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

 	    # POST valida se o que chega sem dados via o Webhook
   	    # do POST e' que se chama a rotina de respnder ao usuario

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n", str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

	    # Conteudo
        content=json.loads(post_data.decode('utf-8'))

        # chama funcao para tratar POST
        trataPOST(content)


    


def run(server_class=HTTPServer, handler_class=S, port=int(os.getenv('PORT',8080))):
        #Esta funcao roda efetivamente o servidor Web
        # PORT usa variavel PORT (tipico de servicos PaaS) ou porta 8080 caso nao definida (tipico para teste local http://localhost:8080)
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
