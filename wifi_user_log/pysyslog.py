#!/usr/bin/env python
##
## Tiny Syslog Server in Python.
##
## This is a tiny syslog server that is able to receive UDP based syslog
## entries on a specified port and save them to a file.
## That's it... it does nothing else...
## There are a few configuration parameters.

import logging
import socketserver

LOG_FILE = 'youlogfile.log'
HOST, PORT = "0.0.0.0", 514

logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='w')

class SyslogUDPHandler(socketserver.BaseRequestHandler):
	
	def handle(self):
		data = bytes.decode(self.request[0].strip())
		socket = self.request[1]
		if ("identity" in str(data)): #[MA]: Only identity logs to be logged:
		    #print( "%s : " % self.client_address[0], str(data))
		    logging.info(str(data))

if __name__ == "__main__":
	try:
		server = socketserver.UDPServer((HOST,PORT), SyslogUDPHandler)
		server.serve_forever(poll_interval=0.5)
	except (IOError, SystemExit):
		raise
	except KeyboardInterrupt:
		print ("Crtl+C Pressed. Shutting down.")
