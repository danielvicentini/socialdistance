# -*- coding: utf-8 -*-

# esqueleto de uma api
# 1 funçao de post que memoriza um dado json
# 1 função de get que devolve o último valor json dado
# 1 função que devolve imagen do disco local

import json
from bottle import route, run, request, post, get, static_file

# variavel tipo dicionario
valor_atual = {}

# POST
# Recebe um JSON via POST e armazena na variavel valor_atual
@post('/api/v1/input')
def input():
    global valor_atual
    valor_atual=request.json
    print(valor_atual)

# GET
# Devolve o valor na variavel valor_atual em json
@get('/api/v1/valor')
def valor():
    global valor_atual
    return valor_atual

# GET
# Devolve uma imagem
# A imagem deve ser salva em pasta 'imagens' (variável root=imagens na funcão server_static) criada no mesmo nível de diretório onde este código ficará
# diretorio:
# +codigo.py
# +imagens/arquivo.png

@route('/imagens/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='imagens')
# Exemplo para chamar imagem: http://localhost:porta/imagens/arquivo.png

# looping
run(host='localhost', port=8080, debug=True)