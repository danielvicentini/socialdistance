# -*- coding: utf-8 -*-

# import vars from config_shared 
# bot info
# admins info

from config_shared import bot_token, bot_email, bot_webhook, bot_tag, admins

# DONT TOUCH THIS VARS - THEY'RE GET FROM config_shared.py

bottoken=bot_token
botmail=bot_email
webhook_url=bot_webhook
webhook_name=bot_tag

# Novidade 27.4.20

#global vars
memoria={}


# Sample inventory
configuracao ={
	"version": "1",
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
# admin = list of admins
# max = max people per rooms
# 
configa= {
	"versao": "1",
	"admin":admins ,
	"data": {
		"max":30
	}
}
