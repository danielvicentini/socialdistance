#import os
from config_shared import bot_token, bot_email, bot_webhook, bot_tag

# Ponha aqui os dados do seu robozinho
bottoken=bot_token
#exemplo='Yia0dsfdsfsdf...' - tirado do site developer.webex.com
botmail=bot_email
#exemplo='mybotmail@spark.io' - tirado do site developer.webex.com

# Ponha aqui os dados do seu Webhook
# webhook_url o endereco publico onde esta o app
webhook_url=bot_webhook
# exemplo webhook_url="https://mywebhook.com"
# webhook_name e' o nome do gatilho que o Webex Teams gera para seu aplicativo entender
webhook_name=bot_tag
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

# nova config 8.6.20
# PIN = senha para comitar alteraçoes
# admin = lista de pessoas que podem aplicar config
# max = max pessoas numa sala/andar, interval = periodo de coleta de dados
# distance True/False = liga desliga análise
# mask True/False = liga desliga análise de mascara
# 
configa= {
	"versao": "1",
	"PIN": "2504",
	"admin":"flcorrea,acassemi,dvicenti,maralves,aluciade,lpavanel",
	"data": {
		"max":30,
		"interval":15,
		"distance": False,
		"mask": False,
		"tracing": False
	}
}
