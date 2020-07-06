# -*- coding: utf-8 -*-

# REPORT CODE
# This code receive commands via GET/POST and update/consult DB as requested

import sys
import os
sys.path.append(os.path.abspath('DB'))


import json
from bottle import route, run, request, post, get, static_file
from bdware import bd_update, bd_consulta
from config_shared import report_server, report_server_port

# variavel tipo dicionario
valor_atual = {}

# POST data input
# POST para enviar dados ao BD
@post('/api/v1/banco')
def input():
    Content=request.json
    resultado=bd_update(Content)
    print(resultado)

# GET
# Devolve o valor na variavel valor_atual em json
@get('/api/v1/consulta/<tabela>/<filtro>')
def valor(tabela,filtro):
    resultado=bd_consulta(tabela,filtro)
    return resultado

# looping
run(host=report_server, port=report_server_port, debug=True)