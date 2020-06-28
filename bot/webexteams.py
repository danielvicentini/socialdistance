# -*- coding: utf-8 -*-

##########################################################
# Webexteams functions from webexteamssdk

from webexteamssdk import WebexTeamsAPI
from config import bottoken

#########################################################
## FIXED VARS


api = WebexTeamsAPI(access_token=bottoken)


#########################################################
## WEBEX TEAMS FUNCTIONS

#########################################################
## Webhooks functions

def ValidaWebhook(webhook_name,webhook_url):

    # validates and creates webhook if necessary

    # Portuguese:
	# Valida existencia de webhook, na ausencia cria novo
    # Retorna sucesso ou erro na operacao

    resultado=""
    webhookok=0
    webhook=api.webhooks.list()
    for b in webhook:
        if b.name==webhook_name:
            webhookok=1
    
    # Cria novo caso nao encontrado
    if webhookok == 0:
        resultado=CriaWebhook(webhook_name,webhook_url)
        
    return resultado

def CriaWebhook(webhook_name,webhook_url):

    # Create Webhook

	# Cria Webhook para receber msg via POST
	# Avisa Teams para gerar hooks para mensagems criadas somente
    # Retorna ok ou erro
    
	# Webhook para msgs
    try:
        api.webhooks.create(webhook_name,webhook_url,"messages","created")
        resultado="ok"
    except:
        resultado="erro"
        pass

	# Webhook para nova sala criada - boas vindas - ainda nao funcionando
    #api.webhooks.create(webhook_name+"-new",webhook_url,"rooms","created")
	
    return resultado

def CleanUpWebhook():

    # Show all active webhooks
    # delete all inactive webhooks

    # cleaning de webhooks
	# lista webhooks, e apaga os desativados
    # retorna resultado

    x = api.webhooks.list()
    msg=("lista de webhooks:\n")
    count = 0
    for b in x:
        msg=msg+("id: " + str(b.id)+"\n")
        msg=msg+("nome: "+str(b.name)+"\n")
        msg=msg+("status: "+str(b.status)+"\n")
        # Limpa webhooks desativados
        if (b.status)=='disabled':
            msg=msg+("apagando webhook "+str(b.name)+"...\n")
            try:
                api.webhooks.delete(b.id)
            except:
                print("erro")
                pass
        if (b.status)=="active":
            count = count + 1

    msg=msg+(str(count)+" webhooks ativos\n")
    
    return msg

def DeleteWebhook(webhook):    
        
    # Delete a webhook     

    # apaga todos os webhooks com <nome> caso nome seja informado
    # retorna o resultado

    x = api.webhooks.list()
    msg=("lista de webhooks:\n")
    count = 0
    for b in x:
	    #Limpa webhooks desativados
        if (b.name)==webhook:
            msg=msg+("apagando webhook... \n")
            try:
                api.webhooks.delete(b.id)
                count = count + 1
            except:
                print ("erro")
                pass
        
    msg=msg+(str(count)+" webhooks apagados\n")

    return msg



#########################################################
# People Session

def webexME():

    # details about myself

	# detalhes sobre mim, retorna dados
	data = api.people.me()

	return data

def getwebexUserID(mail):
	

    # Returns userid from email

    # pesquisa ID do usuário e retorna; retorna vazio se nao encontrado
	
    try:
        usuario = api.people.list(email=mail)
        for x in usuario:
            user = x.id

    except:
        user="erro"
        pass
    
   
    return user


#########################################################
# Rooms Session

def WebexRoomCreate(name):

    # Create a new room by name

	# Cria Sala Webex,name aqui e' o nome da Sala, e retorna o ID da sala. Vazio se erro.

    try:
        api.rooms.create(name)
    except:
        pass

	# Encontra roomID da sala para devolver
    novasala = getwebexRoomID(name)

    return novasala

def WebexRoomDel(id):

    # Delete a room by roomid

    resultado=""
	#Remove sala Webex,id aqui e' roomID, retorna sucesso ou nao
    try:
        api.rooms.delete(id)
        resultado = "ok"
    except:
        resultado="erro"
        pass

    return resultado

def WebexIncUser(sala,mail):

    # Includes a user by usermail to a room by name
    # If room does not exist, creates it

    msg=""
	# Inclui usuario como membro da sala, criando sala caso nao exista
    # Descobre roomID da sala (sala e' o nome completo ou parte dela)
	# Retorna dados do sucesso ou nao da criacao da sala

    salaaincluir=getwebexRoomID(sala)

	# Cria sala caso esta nao exista
    if salaaincluir == None:
        try:
            salaaincluir = WebexRoomCreate(sala)
            msg=msg+"sala "+sala+" criada\n"
        except:
            msg="erro na criacao da sala\n"
            pass

    try:
        useraincluir=getwebexUserID(mail)
        msg=msg+"user "+mail+" encontrado\n"
    except:
        msg=msg+"erro para encontrar user\n"
        pass

	# inclui usuario caso id encontrado
    if useraincluir !=None:
			#executa a operacao
            try:
                api.memberships.create(salaaincluir,useraincluir)
                msg=msg+"user "+mail+" incluido na sala "+sala
            except:
                msg=msg+'erro na inclusao do usuario'
                pass

    return msg

def webexRoomsList():

    # returns list of rooms I belong to

	# lista salas que pertenco, retorna msg com a lista
 
    rooms=api.rooms.list()
    resultado = ""
    
    try:
	    for room in rooms:
		    resultado = resultado + "Sala " + str(room.title) + "\n"
    except:
        resultado="erro"

    return resultado


def getwebexRoomID(sala):

    # Returns roomid given by room name

	# Retorna ID da Sala; retorna vazio se nao encontrado
   	# O parametro sala e' todo ou parte do nome da sala procurada
	
    # Salas que pertenco
    rooms=api.rooms.list()
    
    salawebex=None

	# for para encontrar ID da sala determinada

    try:
        for room in rooms:
            if sala in room.title:
                salawebex = room
                break
    except:
        pass
			
	# identifica ID da sala
    if salawebex != None:
        resultado = (str(salawebex.id))
    else:
        resultado = salawebex
		
    return resultado



#########################################################
# Message session

def getwebexMsg(msgID):
	
    # Return msg contents by msgid

	# msgID é o parametro resgatado do corpo do webhook
	# Retorna lista com o [0]texto da mensagem informada [1]ID da sala e [2]email da pessoa
	mensagem=api.messages.get(msgID)
				
	return mensagem.text,mensagem.roomId,mensagem.personEmail


def webexmsgUser(user,msg):

    # Sent a 1:1 message

    # Manda 1 msg para 1 user específico baseado no email informado
    # caso não consiga, retorna erro

    try:
        # coleta id do usuario pelo seu email
        usuario=getwebexUserID(user)
        # envia
        api.messages.create(toPersonId=usuario,markdown=msg)
        resultado="ok"
    except:
        resultado="erro"
    pass

    return resultado

def webexmsgRoom(sala,msg):

    # Sent message to a room by room name

	# Manda msg para 1 sala especifica, procurando salas onde estou (usando partes do nome informado em sala).
    # Retorna sucesso ou erro

    # rooms=api.rooms.list()
    salawebex = None

    #resgata ID da sala
    salawebex = getwebexRoomID(sala)
    
    # mandando uma mensagem para a Sala caso encontrada
    if salawebex != None:
        try:
            api.messages.create(salawebex,None,None,None,msg)
            resultado="ok"
        except:
            resultado="erro"
            pass

    return resultado

def webexmsgRoomviaID(sala,msg,arquivo):

    # Send message + file (optinal) by room name

	# Manda msg para 1 sala especifica informada via sala=roomID,  retorna sucesso ou erro
    # 21.11.19 - caso tenha arquivo na mensagem, vai inclui-lo

    try:
        # envia arquivo caso positivo
        if arquivo!="":
            
            # envia msg somente caso nao tenha produto de erro no arquivo
            if arquivo!="erro":
                # convert string para list
                n_arquivo=list(arquivo.split("\n"))
                api.messages.create(sala,None,None,None, msg, n_arquivo)
                msg="ok"

        # Envia mensagem de texto somente para os casos onde nao ha arquivo anexo ou erro no arquivo    
        if arquivo=="" or arquivo==None or arquivo=="erro":
            api.messages.create(sala,None,None,None, msg)
            msg="ok"
            
    except:
        msg="erro"
        print ("Erro no envio da msg via webexteams")
        pass

    return msg
