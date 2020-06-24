# este grupo e' para chamar modulos que estao na pasta 'bot'
import sys
import os
sys.path.append(os.path.abspath('bot'))

from config import webhook_name, webhook_url
from webexteams_console_tools import webexconsole
from webexteams import ValidaWebhook
from logica import logica
from webserver import run

# Testa existencia do Webhook. Caso negativo, cria
msg=ValidaWebhook(webhook_name,webhook_url)
# Imprime erro caso validacao do Webhook nao funcionou
if msg=="erro":
    print ("Erro de Webhook")


#Formato de execucao em modo console (teste)
formato = "c"

if formato=="c":

    box=""

    # aviso
    print("exit para sair. help para comandos de usuario. help+ para comandos avançados")

    # a definicao do usermail (emai) e' importante para testar os filtros de usuario
    usermail=input("seu email>")


    while box !="exit":

        box=input(">")

        # testa console de ferramentas
        webexconsole(box)

        # logica para usuarios
        msg,arquivo=logica(box,usermail)
        print (msg)
        print ("arquivo:"+str(arquivo))

elif formato=='w':
    
    run()

else:

    print ("nenhum formato selecionado. Selecione (c) para teste ou (w) para producao")
