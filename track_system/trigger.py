import json
import requests
from bottle import route, run, request, post, get
from bottle_rest import json_to_params
import time
import tracemalloc
import sys
import os
sys.path.append(os.path.abspath('..'))
import config_shared

tracemalloc.start()

triggers = {'ap_name': 'BCIC', 'ap_user_count': 0, 'clients_identity': [], 'last_update': '1593387920.489039717'}

last_time = 0

basedir = os.path.abspath(os.path.dirname("../"))
print(basedir)
with open(basedir + "/config.json", "r") as json_file:
    config = json.load(json_file)

def mensagem_user(new_trigger, x):
    url = "http://" + str(config_shared.bot_server) + ":" + str(config_shared.bot_server_port)
    print(new_trigger['name'])
    a = "a"
    for x in new_trigger["clients_identity"]:
        a = str(a) + ", " + str(x)

    payload = "{\r\n\t\"alarm\": \"distance-bot\",\r\n\t\"data\": {\r\n\t\t\"type\": \"00\",\r\n\t\t\"message\": \"You are in room " + new_trigger['name'] + "hat reached the limit of people (total " + str(x) + " pessoas (informacao recebida via wifi) \",\r\n\t\t\"who\":\""+str(a)+"\"\r\n\t}\r\n\r\n}\r\n"
    headers = {
        'Content-Type': 'text/plain'
    }
    print(payload)
    response = requests.request("POST", url, headers=headers, data = payload)

    return response

def mensagem_admin(new_trigger, x):
    url = "http://" + str(config_shared.bot_server) + ":" + str(config_shared.bot_server_port)
    print(new_trigger['name'])
    payload = "{\r\n\t\"alarm\": \"distance-bot\",\r\n\t\"data\": {\r\n\t\t\"type\": \"01\",\r\n\t\t\"message\": \"ADMIN : A sala " + new_trigger['name'] + " ultrapassou o limite de " + str(x) + " pessoas (informacao recebida via wifi)\",\r\n\t\t\"who\":\"\",\r\n\t\t\"image\": \"https://www.immi-canada.com/wp-content/uploads/2015/06/attention-1080x675.jpg\"\r\n\t}\r\n\r\n}\r\n"
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("POST", url, headers=headers, data = payload)

    return response

def calc(new_trigger, updated, last_time):
    
    for b in config['rooms']:
        roomName=b
        if new_trigger['name'] == roomName:
            x=config['rooms'][roomName]
        else:
            print()
   
    print()
    print("Room: " + new_trigger['name'] + " com um limite de : " + str(x))
    print()
    if new_trigger['ap_user_count'] > x:
        #last_time = triggers[len(triggers)-1]['last_update']
        timestamp = "1593387920.489039717"
        #print(last_time)
        if float(last_time) < float(timestamp):
            last_time = timestamp
            mensagem_admin(new_trigger, x)
            mensagem_user(new_trigger, x)
        time_now = time.time()
        dif = time_now - float(last_time)
        print("Timestamp recebido e " + str(last_time) + " timestamp de agora " + str(time_now) + " e a diferenca dos dois e " + str(dif))
        if dif > 60:
            v = True
            if v == True:
                #print("AEEEEEEEEOOOOOOOOOO") # === funçao msg bot
                mensagem_admin(new_trigger, x)
                mensagem_user(new_trigger, x)
                last_time = new_trigger['last_update']
        else:
            v = False
        #print("merdaaaaaa ")
    
    else:
        del(triggers[0])

    return last_time

@route('/hello')
def hello():
    return "Hello World!"

# POST
# Recebe um JSON via POST e armazena na variavel valor_atual

@post('/triggers')
def addOne():
    global last_time
    new_trigger = {'name' : request.json.get('ap_name'), 'ap_user_count' : request.json.get('ap_user_count'), 'clients_identity': request.json.get('clients_identity'), 'last_update': request.json.get('last_update')}
    #print(new_trigger)
    #print("-------------------------------------------------------------------")
    print("Timestamp inicial: "+ str(last_time))
    update_time = new_trigger['last_update']
    last_time = calc(new_trigger,update_time,last_time)
    print("Timestamp para a proxima verificacao: " + str(last_time))
    triggers.append(new_trigger)
    return {'triggers' : triggers}

@get('/triggers')
def getAll():
	return {'triggers' : triggers}

run(host=config_shared.trigger_server, port=config_shared.trigger_server_port, debug=True)