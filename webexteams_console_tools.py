from webexteams import *


def webexconsole(box):

    #################################################################
    # FERRAMENTAS DE MANUTENCAO PARA CONSOLE
    # Utiliza para entender existencia de webhooks, salas e respectiva manutencao
     
    if box == "help+":
       msg="Comandos disponiveis:\nuserid: Identifica ID do usuario\nroomid: Identifica ID da sala\nusermail: troca usuario\nnovasala: Cria uma sala nova com usuario\nremovesala: Remove sala\nsalas: lista salas que pertenco\n"
       msg=msg+("webhook_create: cria webhook\nwebhook_del: apaga webhooks com este nome\nwebhook_clean: lista webhooks autuais, apagando os desativos\n")
       print (msg)

    #troca usuario para testar aplicacoes webexteams
    if box=="usermail":
        usermail=input("seu email>")

    # chamada funcao para encontrar id do user
    if box == "userid":
       email=input("Email do user:")
       msg = getwebexUserID(email)
       print (msg)

    # chamada funcao para encontrar nome da sala
    if box == "roomid":
        sala=input("nome da sala? (todo ou partes):")
        msg = getwebexRoomID(sala)
        print (msg)

    # cleaning de webhooks
    # lista webhooks, e apaga os desativados
    if box =="webhook_clean":
        msg=CleanUpWebhook()
        print(msg)

	# apaga todos os webhooks com <nome> caso nome seja informado
    if box =="webhook_del":
        nome=input("nome do webhook:")
        msg=DeleteWebhook(nome)
        print(msg)

    # cria webhook
    if box =="webhook_create":
       nome=input("nome do webhook:")
       url=input("endereço http:")
       msg=CriaWebhook(nome,url)
       print(msg)

	# chamada de funcao para Criar nova sala com user 
    if box == "novasala":
       email=input ("Qual email para incluir na sala?:")
       msg=getwebexUserID(email)

       if msg!="erro":
           novasala=input ('qual o nome da sala?:')
           msg=WebexIncUser(novasala,email)
           webexmsgRoom(novasala,"ola' "+str(email))
       else:
            msg="erro para identificar user"

       print(msg)

    # Remove Sala
    if box == "removesala":
        nome_sala=input('qual o nome da sala?:')
        msg=WebexRoomDel(getwebexRoomID(nome_sala))
        print(msg)

    # Lista salas
    if box =="salas":
        msg = webexRoomsList()
        print (msg)
            
    # FIM DAS FERRAMENTAS
    #################################################################

    return