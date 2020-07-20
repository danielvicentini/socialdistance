# -*- coding: utf-8 -*-

# Social main config file
# import vars from config_shared 
# bot info
# admins info

from config_shared import bot_token, bot_email, bot_webhook, bot_tag
import json

# DONT TOUCH THIS VARS - THEY'RE GET FROM config_shared.py

bottoken=bot_token
botmail=bot_email
webhook_url=bot_webhook
webhook_name=bot_tag

# Novidade 27.4.20

#global vars
memoria={}

#------------------------------------------------------
#  Config Room
#------------------------------------------------------
# Config agora é criado pelo bot e salva
# Se ja'existir, recupera
# 15.7.20
#padrao= {
#	"admin":admins ,
#	"rooms": {
#		 "<rom name>": <max people> ,
#		 "<other rooms>": <max peopled>
#		... : ...
#	}
#}

#---------------------------------------------------
# Bot options
#---------------------------------------------------

def le_config():
    try:
        with open('config.json',encoding='utf-8') as json_file:
            configuracao=json.load(json_file)  
    except:
        pass
    return configuracao

configuracao=dict()
# carrega  configuracoes, caso tenha
configuracao = le_config()

# Bot options
# config strcuture
# { opcoes: [{
#		"tag": "<list of words to sugest>",
#		"title": "<option title>",
#		"desc": "<option description>",
#		"option": <integer code>,
#		"admin": <true or false, to be diplayed for admin users>,
#		"req": <true or false in case command requires parameters>,
#		"params": "<list of parameters comma separated"}
# },{ next option } ] }

# opçoes
# roadmap: 1) Arquivo JSON DONE, 2) GET num site http

# NOTA IMPORTANTE:
# O Arquivo json precisa ser salvo em UTF-8 e EOL deve ser Unix LF
# Usar o notepad++ para isto
# do contrário dará erro na leitura do arquivo no Unix

novas_opcoes=dict()
# carrega opcoes do arquivo options.json
try:
    with open('options.json',encoding='utf-8') as json_file:
        novas_opcoes=json.load(json_file)
    
except:
    print ("erro na leitura do arquivo de opçoes")
