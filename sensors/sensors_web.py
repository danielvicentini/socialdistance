import requests
import json
import random
import time
from webexteams import getwebexRoomID, webexmsgRoomviaID

# dados para salas

def sensor_salas():

    # Sensor das salas

    sala_meeting=random.randint(1,100)
    sala_cafe=random.randint(1,35)

    salas={
        "meeting rom": {
            "max": 60,
            "ap": sala_meeting,
            "video": sala_meeting-4
        },
        "cafeteria": {
            "max": 30,
            "ap": sala_cafe,
            "video":sala_cafe+2
        }
    }

    return salas

# dados para alertas

def alertas(mensagem):

    # gera alerta aleatorio com uma mensagem pre definida
    numero=random.randint(1,1000)

    alertas={
        "alert": {
            "message": mensagem,
            "imagem": "https://i.picsum.photos/id/"+str(numero)+"/250/200.jpg"

        }
    }

    return alertas

def posta (content):

    # posta no dweet os dados

   headers = {'content-type': 'application/json'}
   
   site="http://dweet.io/dweet/for/distance-aps"
   resultado=requests.post(site,data=json.dumps(content),headers=headers)
   print (resultado)
   print (resultado.content)
    

   return resultado


def alerta (content):

   # posta alertas

   headers = {'content-type': 'application/json'}
   
   site="http://dweet.io/dweet/for/distance-alerts"
   resultado=requests.post(site,data=json.dumps(content),headers=headers)
   print (resultado)
   print (resultado.content)
    

   return resultado


def teams (content):

    # envia no webex teams
    mensagem=content['alert']['message']
    imagem=content['alert']['imagem']

    sala=getwebexRoomID("Distanciamento Piloto")
    webexmsgRoomviaID(sala,mensagem,imagem)

    return


# codigo

running = True



while running:

    #Sensoreia
    print ("sensorando...")
    content = sensor_salas()
    print (content)
    print ("postando...")

    # Envia atualização das salas
    posta (content)

    # Entende se tem alertas a fazer
    if content['meeting rom']['ap']>content['meeting rom']['max']:
        m="Sala Meeting Room com problema"
    elif content['cafeteria']['ap']>content['cafeteria']['max']:
        m="Sala Cafeteria com problema"
    else:
        m=""

    #atualiza alertas no dashboard
    aviso=alertas(m)

    alerta(aviso)

    #avisa no teams tb
    if m!="":
        teams(aviso)
    
    
    time.sleep(60)
