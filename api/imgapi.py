# -*- coding: utf-8 -*-

# esqueleto de uma api
# Simple WEB image server

import json
from bottle import route, run, request, post, get, static_file


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
run(host='159.89.238.176', port=12000, debug=True)