import os

# Ponha aqui os dados do seu robozinho
bottoken=os.environ['TOKEN']
#exemplo='Yia0dsfdsfsdf...' - tirado do site developer.webex.com
botmail="infobot@sparkbot.io"
#exemplo='mybotmail@spark.io' - tirado do site developer.webex.com

# Ponha aqui os dados do seu Webhook
# webhook_url o endereco publico onde esta o app
webhook_url=os.environ['WEBHOOK_URL']
# exemplo webhook_url="https://mywebhook.com"
# webhook_name e' o nome do gatilho que o Webex Teams gera para seu aplicativo entender
webhook_name="distancebot"
# exemplo webhook_name="meuprimeirochatbot"

# Novidade 27.4.20

#variaveis globais
#memoriza comandos
memoria={}


# Config para teste
configuracao ={
	"versao": "1",
	"inventario": [{
			"sala": "Cafeteria",
			"access-point": "AP-1",
			"distancia": 10
		},
		{
			"sala": "Reunião",
			"access-point": "AP-2",
			"distancia": 30 }]}