# esqueleto de uma api
# 1 funçao de post que memoriza um dado json
# 1 função de get que devolve o último valor json dado

import json
from bottle import route, run, request, post, get

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
  
# looping
run(host='localhost', port=8080, debug=True)