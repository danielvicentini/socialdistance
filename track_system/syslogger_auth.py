#!/usr/bin/python
# -*- encoding: iso-8859-1 -*-

"""
Python syslog client.

This code is placed in the public domain by the author.
Written by Christian Stigen Larsen.

This is especially neat for Windows users, who (I think) don't
get any syslog module in the default python installation.

See RFC3164 for more info -- http://tools.ietf.org/html/rfc3164

Note that if you intend to send messages to remote servers, their
syslogd must be started with -r to allow to receive UDP from
the network.

---------------------------------------------------------------------

usage: logger [-h] [-m MESSAGE] [-l LEVEL] [-H HOST] [-p PORT]

optional arguments:
  -h, --help            show this help message and exit
  -m MESSAGE, --message MESSAGE
                        Body of the log message.
  -l LEVEL, --level LEVEL
                        Syslog level, info: 6, alert: 1, warning: 4
  -H HOST, --host HOST  remote syslog server ip.
  -p PORT, --port PORT  remove syslog server port.

"""

import socket
import argparse
import time
from random import *

FACILITY = {
    'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
    'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
    'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
    'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
    'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23,
}

LEVEL = {
    'emerg': 0, 'alert':1, 'crit': 2, 'err': 3,
    'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}

def syslog(message, level=LEVEL['notice'], facility=FACILITY['daemon'],
    host='159.89.238.176', port=514):
    """
    Send syslog UDP packet to given host and port.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = '<%d>%s' % (level + facility*8, message)
    #sock.sendto(data, (host, port))
    sock.sendto(data.encode('utf-8'), (host.encode('utf-8'), port))
    sock.close()

t = time.time()
t = str(t) + str(randint(10,20))
r = randint(739553015,839553015)
user = "lpavanell@cisco.com"
msg = " BCIC events type=8021x_auth radio='1' vap='3' client_mac='D8:8F:76:93:6B:D1' identity='"+user+"' aid='"
msg = "1 " + str(t) + msg + str(r) + "'"
parser = argparse.ArgumentParser()
parser.add_argument('-m', "--message", help="Body of the log message.", default=msg)
parser.add_argument('-l', "--level", help="Syslog level, info: 6, alert: 1, warning: 4", type=int, default=6)
parser.add_argument('-H', "--host", help="remote syslog server ip.", default="localhost")
parser.add_argument('-p', "--port", help="remove syslog server port.", type=int, default=514)
args = parser.parse_args()

#if not (args.message):
#    parser.error('No message specified, add --message or -m or go home.')

syslog(message=args.message,level=args.level,host=args.host,port=args.port)