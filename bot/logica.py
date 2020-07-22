# -*- coding: utf-8 -*-

# This code was originaly Documented in Portuguese Language
# Daniel 6.26.2020

# Webex Teams rooms from config_shared
from config_shared import admins_room, admins
# Bot config
from config import memoria, botmail, webhook_name, configuracao, novas_opcoes
from config_shared import report_server, report_server_port
from config_shared import mask_server, mask_server_port

# Meraki Devices from Inventory
from inventory import DeviceInventory, getDeviceInfoName

# Webex functions
from webexteams import getwebexMsg, webexmsgRoomviaID, getwebexRoomID, getwebexUserID, webexmsgUser
import json
import requests



# ver 1.5 - 11.5.20

# Functions

#### FUNÇÕES A RESPEITO DAS OPÇÕES/COMANDOS DISPONÍVEIS AO USUÁRIO
#####################################################################

# Funcão para retornar menu com opções ao usuário
# Estas funções são chamadas dentro da logica

# Reads and presentes options to the user (from comando such as 'Help')

def opcoes_para_user(usermail):
    
    # acessa cada uma das opcoes da configuracao de opcoes
    # para apresentar a lista de comandos disponiveis ao user
    # esta condicionado a apresentar as opcoes se usuario for admin

    msg="***Commands that I understand***:  \n\n"
    z=1
    try:
        for b in novas_opcoes['opcoes']:
            if usermail not in admins and b['admin']==True:
                # pula sessão se usuário não for admin
                continue
            else:
                msg=msg+f"***{z}) {b['title']}***  \n"
                msg=msg+f"{b['desc']}  \n"
                z=z+1
            
        msg=msg+"  \nType keywords so we can start our chat.  \n"
    except:
        msg="No options found.  \n"

    return msg


# This function returns data from an specific user option

# Função que retorna dados a respeito de cada opção
# Ex: se requer parametros, quais as tags

def optparam(codigo,item):
    
    # investiga nas opcoes existentes para o user
    # devolve o valor do item conforme o codigo da opcao
    
    for b in novas_opcoes['opcoes']:
        if b['option']==codigo:
            try:
                dado=b[item]
            except:
                dado = "erro"
        

    return dado

# This function try to understand the best match for an available option for the user based on keywords sent.

# Função que sugere melhor comando de acordo com o entendimento do usuário
# Entendimento é feito comparando o que o usuário escreveu com o valor da "tag" da opção    

def sugere_opcao(comando,usermail):

    global admins

    # recebe o comando, procura qual a melhor opcao mais proxima a este comando e devolve o código
    # update: analisa sugestões dependendo do usuário ser normal ou admin

    #variável para entencer qual a opcao da lista de comandos qu é mais parecido com o comando digitado
    score=0.0
    # loop para cada um das opções conhecidos
    # variavel c usada para procurar na lista de opcoes
    
    try:
        for b in novas_opcoes['opcoes']:

            if usermail not in admins and b['admin']==True:
                # pula sessão se usuário não for admin
                continue
            else:
                #
                txtnow=b['tag'].lower()
                opcao_cod=b['option']
                
                #variaveis
                # qtde de palavras no que foi digitado
                sp=comando.split(" ")
                y=len(sp)
                a=0
                found=0
                resultado=0.0
                
                # este laço conta a qtde de palavras que o comando digitado tem em comum com a opcao conhecida
                while a<y:
                    if sp[a] in txtnow:
                        found=found+1
                    a+=1

                # calcula o % de aproximacao do comando conhecido    
                resultado=found/len(txtnow.split(" "))
                
                # se tiver a melhor nota, vira provisoriamente a melhor opcao
                if resultado>score:
                    score=resultado
                    opescolhido=opcao_cod
                
                # Memoriza o comando escolhido como o mais proximo
                # somente se a nota for igual ou melhor que .3 
                # do contrario devolve 0 = nenhum
    except:
        # error in options
        pass

    if score>=.3:
        return opescolhido
    else:
        return 0

# Initiates memory for a user - used by the robot to chat with the user

# Função que inicia valores para um usuário conversando com o robo
# iniciar valores = convesarsa começando do zero.

def reinicia_user(usermail):
    
    global aguardando
    #global memoria
    #global configuracao
    
    # reinicia variavies da memoria par ao usuario
    # robo vai comecar do zero com este usuario
    try:
        var={ 'wait':False, 'option':0, 'req':False, 'params':False, 'typed':'','typing':False}
        memoria[usermail]=var
        aguardando=memoria[usermail]['wait']
    except:
        pass

# custom comands function for this bot

def configRoom(sala,maximo):

    # This function will define max user per room.
    # Also, save the config

    msg = ""
    # testa se tem config de salas, se nao cria
    try:
        
        configuracao['versao']=int(configuracao['versao'])+1
        # ok, ja tem e incrementa versao
    except:
        #inicializa
        configuracao['versao']=1
        configuracao['rooms']={}

    try:
        configuracao['rooms'][sala]=int(maximo)
        msg=msg+f"Defining max distance of ***{maximo}*** peopleo for room ***{sala}***."
                        
        # gravacao da config
        arq="config.json"
        # Salva
        try:
            # Salva com LF (Unix like para funcionar no Windows e no Unix (variavel newline))
            # Salva com encoding UTF-8 para funcionar caracteres especiais no Unix
            with open(arq, 'w', encoding="utf-8", newline='\n') as file:
                json.dump(configuracao, file, indent=4, sort_keys=True, ensure_ascii=False)

            msg=msg+"\nConfig saved.  \n"
        except:
            msg=msg+"\nError saving config.  \n"
    except:
            msg=msg+f"Couldn't define. Chech your parameters."
        
    return msg

def showInventory():

    # Show inventory
    msg=""
    saida = "  \nCurrent Inventory:  \n"
                
    try:
    # Read data from inventory.py
        for dado in DeviceInventory:
            sala=f"Room: {dado['Location']}  \n"
            device=f"Device Name:***{dado['Nome']}*** SN:{dado['SerialNumber']} Type:{dado['Device']}   \nNetId:{dado['NetworkID']}  \n"
            saida=saida+sala+device+"___  \n"
        
    except:
        saida="\nNo inventory Found.  \n"
    
    msg=msg+saida

    return msg

def showRunning():
    # config rodando
    msg=""

    administradores=admins.split(",")
    msg=msg+f"Current config: ***Admins:***  \n\n"
    for b in administradores:
        msg=msg+f"{b}  \n"

    msg=msg+f"  \nAdmins Webex room:{admins_room}  \n"

    msg=msg+"\n***Room Distancing configuration:***  \n\n"
    try:
        for b in configuracao['rooms']:
            roomName=b
            valor=configuracao['rooms'][roomName]
            msg=msg+f"Room Name ***{roomName}***  Max People: {valor}  \n"
    except:    
        msg=msg+"\nNo rooms defined yet.  \n"

    return msg

def reportDistancing(periodo):

    # adiciona sinal negativo
    periodo=f"-{periodo}"
  
# funcao historico

    msg=""
    msg=msg+"  \nHistory of Maximum distance Out of Compliance:  \n\n"

    try:
        # Teste de código para consultar report
        url = f"http://{report_server}:{report_server_port}/api/v1/consulta/totalcount/{periodo}"
        headers = {'Content-Type': "application/json" }
        response = requests.request("GET", url, headers=headers)
        
        resposta=json.loads(response.text)
        msg=msg+f"{resposta['msg']}  \n"

        
        #msg=msg+response.text
    except:
        msg="\nCan't connect to server.  \n"

    return f"***{msg}***"

def reportBestday(periodo):

    # adiciona sinal negativo
    periodo=f"-{periodo}"
  
    msg=""
    msg=msg+"  \nBest Day to go to the office:  \n\n"

    try:
        # Teste de código para consultar report
        url = f"http://{report_server}:{report_server_port}/api/v1/consulta/bestday/{periodo}"
        headers = {'Content-Type': "application/json" }
        response = requests.request("GET", url, headers=headers)
        
        resposta=json.loads(response.text)
        msg=msg+f"{resposta['msg']}  \n"

        
        #msg=msg+response.text
    except:
        msg="\nCan't connect to server.  \n"

    return f"***{msg}***"


def reportTracing (pessoa,start,end):
  
    # report of people tracing
    
    msg=""
    msg=msg+f"  \nTracing: {pessoa} for the period:{start} to {end} \n\n"

    # Teste de código para consultar report
    try:
        url = f"http://{report_server}:{report_server_port}/api/v1/consulta/peoplelog/{pessoa}&{start}&{end}"
        headers = {'Content-Type': "application/json" }
        response = requests.request("GET", url, headers=headers)
        resposta=json.loads(response.text)
        msg=msg+f"{resposta['msg']}  \n"

        #msg=msg+response.text
    except:
        msg="\nCan't connect to server.  \n"

    return f"***{msg}***"
        
def reportMask(timeframe):

    # Mask Detection
    msg=""
    msg=msg+"  \nReport of people not wearing mask:  \n\n"
                            
    try: 
        # Chama report server API
        url = f"http://{report_server}:{report_server_port}/api/v1/consulta/sanityMask/{timeframe}"
        headers = {'Content-Type': "application/json" }
        response = requests.request("GET", url, headers=headers)
        resposta=json.loads(response.text)
        msg=msg+f"{resposta['msg']}  \n"
    except:
        msg="\nCan't connect to server.  \n"

    return f"***{msg}***"

def cameraStart(camera):

    # Start camera/Mask Detection
    
    msg=""
    serial=getDeviceInfoName("SerialNumber",camera)
    netid=getDeviceInfoName("NetworkID",camera)
    if serial!="erro" or netid!="erro":
      
        # chama api
        try:
            url = f'http://{mask_server}:{mask_server_port}/loop'
            params = {"network_id": netid, "mv_serial": serial, "turn":"on" }
            response = requests.post(url,params=params)
            msg=msg+f"***{response.text}***  \n"
        except:
            msg="\n Can't connect to server.  \n"
    else:
        msg = "Couldn't find the device information you asked."

    return msg


def cameraStop(camera):

    # Stop camera/Mask Detection

    msg=""
    serial=getDeviceInfoName("SerialNumber",camera)
    netid=getDeviceInfoName("NetworkID",camera)
    if serial!="erro" or netid!="erro":
      
        # chama api
        try:
            url = f'http://{mask_server}:{mask_server_port}/loop'
            params = {"network_id": netid, "mv_serial": serial, "turn":"off" }
            response = requests.post(url, params=params) 
            msg=msg+f"***{response.text}***  \n"
        except:
            msg="\n Can't connect to server.  \n"
    else:
        msg = "Couldn't find the device information you asked."

    return msg


### Main Code


#### PROGRAMA PRINCIPAL


### Step 0 - Ready options available from options.json
#################################################################

# 0) Inicio
# leitura do arquivo de opcoes


### Part 1 - Logic - main function - this function is called whenever a text arrives for the bot
#################################################################

# 1) logica
# É chamado a medida que um comando chega do usuário, seja via console (testes) ou via http (produção)

def logica(comando,usermail):
   
    global aguardando
    global memoria
    global configuracao
    global DeviceInventory

    # faz a logica de entender o comando pedido e a devida resposta para o usuario
    # o parametro usermail e' utilizado para identificar o usuario que solicitou o comando
    # Retorna mensagem para ser enviada para console ou Webex teams
    
    #Separa o comando por espacos
    #Primeiro item e'o comando em si, os demais sao parametros deste comando
    comando=comando.lower()
    sp=comando.split(" ")
        
    # 21.11.19
    # variavel arquivo para o caso do bot devolver arquivos anexados
    arquivo=""
    
    # no final, a função retorna o conteúdo de arquivo e msg = texto do robo
    msg=""
	
    # passo 1) recupera a conversa, caso ja tenha comecado
    # Do contrario entende que é uma conversa nova

    # entendendo se usuario já fez solicitacoes e o robo aguardo respostas
    # explicacao da memoria:
    # wait (true/false) = se robo esta esperando uma info do usuario
    # opcao = codigo do comando
    # req = se comando precisa de parametros
    # params = lista de parametros
    # para cada solicitacao do parceiro, esta logica atualiza estas variaveis



    try:
        # recupera o estado da memoria
        aguardando=memoria[usermail]['wait']
        
    except:
        # se chegamos aqui, usuario esta se comunicando pela primeira vez,
        # protanto variaveis serao criadas
        reinicia_user(usermail)
        aguardando=memoria[usermail]['wait']


        
    ### Part 2 - Start decision tree
    #################################################################

        
    # 2) Análise
    # Caso esteja no começa da conversa, este bloco entende o que o usuário quer fazer

    # 2.1 este bloco é para o caso do robo não saber ainda o que o user quer:
    if aguardando==False:
        
        # 2.1a. teste se user pediu ajuda
        if "help" in comando or "ajuda" in comando:
            # roda as opcaoes disponives
            # a reposta está condicionado ao user ser admin ou não
            msg=opcoes_para_user(usermail)
                
        #2.1b. tenta adivinhar o comando consultando os comandos disponiveis
        # caso ele encontre uma opcao, apresenta e apos isto o robo entra em modo de espera

        if msg=="" and len(sp)>0 and len(comando)>=5:
            # chama função que devolve o cod da opcao mais aproximada
            opescolhido=sugere_opcao(comando,usermail)
            if opescolhido != 0:
                # popula variaveis e pergunta se e' a escolhida
                memoria[usermail]['option']=opescolhido
                memoria[usermail]['wait']=True
                memoria[usermail]['req']=optparam(opescolhido,"req")
                if memoria[usermail]['req']==False:
                    # Se comando nao requer parametros, então ele está pronto para a logica de execucao
                    memoria[usermail]['params']=True
                else:
                    # Se o comando requer parametros, entao o prox passo é a logica de entrada de parametros
                    memoria[usermail]['params']=False

                # Portuguese
                msg=f"Você quiz dizer: {optparam(opescolhido,'title')} ?  \n"
                # English
                msg=f"Do you mean: {optparam(opescolhido,'title')} ?  \n"

                # Se chegou até aqui... na próxima interação robo fica a espera da continuidade da conversa
 
        # 2.1c nada conhecido, então devolve msg padrão

        if msg=="":
            # Portuguese
            msg="Olá. Digite ***ajuda*** para ver as opçoes disponíveis.  \nVou tentar adivinhar também o que você está procurando :-)  \n"
            # English
            msg="Hello. Type ***help*** to see available options.  \nI'll try to guess what you are looking for :-)  \n"

   # Part 3
   # Robot expects information from user
   #################################################

    # 3) Conversando
    # Caso conversa já iniciado, usa este bloco

    # vai por este caminho se o robo espera resposta do usuario
    if aguardando==True:

        # resgata o código do comando em questão
        codigo=memoria[usermail]['option']
    
        # Textos padrão
        # Portuguese
        #msg_titulo="Bem? Eu tinha entendido: ***"+optparam(memoria[usermail]['option'],'title')+"***.  \n"
        # English
        msg_titulo=f"I understood ***{optparam(memoria[usermail]['option'],'title')}***.  \n"

        # Portuguese
        #msg_sn="Diga ***sim*** ou ***ok*** para continuar ou digite ***não*** ou ***reinicie*** para recomeçarmos.  \n"   
        # English
        msg_sn="Type ***yes*** or ***ok*** to continue. Type ***no*** or ***restart*** to restart conversation.   \n"
        # Portuguese
        #msg_ready="Estou pronto para executar seu comando.  \n"
        # English
        msg_ready="I'm ready to execute you command.  \n"
        # Portuguese
        #msg_comma="Digite os parametros separados por virgulas. Você pode reiniciar digitando ***reinicie*** ou ***não***.  \n"
        # English
        msg_comma="Type your parameters separated by commas. You can also restart chat by typing ***restart*** or ***no***.  \n"

        # Portuguese
        #msg_restart = "Ok, vou reiniciar nossa conversa.  \nDigite ***ajuda*** se quiser saber mais o que posso fazer."
        # English
        msg_restart = "Ok, I'll restart our chat.  \nType ****help*** if you want to know what I can do."

        # texto para
        # parametros necessários, caso precise
        if memoria[usermail]['req']==True:
            # Portuguese
            msg_need_params=f"Digite os parametros para completar o comando:***{optparam(memoria[usermail]['option'],'params')}***  \n\n"    
            # English
            msg_need_params=f"The following parameters are needed:***{optparam(memoria[usermail]['option'],'params')}***  \n\n"   


        # Se chegou até aqui, robo aguarda sim ou não para executar o comando
        if memoria[usermail]['params']==True:
            
            # resgata parametros caso comando precise deles
            if memoria[usermail]['req']==True:
                parametros=memoria[usermail]['typed']
                msg_params="Voce digitou os parâmetros : ("+parametros+")  \n"
                # English
                msg_params=f"You typed: {parametros}  \n"
                          
            if "yes" in comando or 'ok' in comando or "sim" in comando:
            # se chegou aqui no Sim, vai executar se achar funcões para o código desejado
                msg="vou executar o que você me pediu:  \n"
                # English
                msg="Executing what you asked me:  \n  \n"
               
                # Os parametros digitados estao na variavel do tipo lista abaixo
                lista_parametros=memoria[usermail]['typed'].split(",")
 
                #---------------------------------------------------------------------------------
                # DIGITE SUA INTERPRETAÇÃO DE CÓDIGOS AQUI
                # codigo = codigo do comando
                # lista_parametros = lista com os parametros digitados pelo usuario, separado por virgulas
                # o resultado do seu código deve ser atribuido a variavel msg

                                            
                if codigo==12:
                    # config rooms
                    # aplica a nova config e salva
                    sala=lista_parametros[0].strip()
                    maximo=lista_parametros[1].strip()
                    func=configRoom(sala,maximo)
                    msg=msg+func
                    
                elif codigo==13:
                    # Start Camera for mask detection
                    camera=lista_parametros[0]
                    func=cameraStart(camera)
                    msg=msg+func

                elif codigo==14:
                    # Stop camera for mask detection
                    camera=lista_parametros[0]
                    func=cameraStop(camera)
                    msg=msg+func

                elif codigo==51:
                    # Calls Inventory function
                    func=showInventory()
                    msg=msg+func
                                    
                elif codigo==52:
                    # Tracing
                    # terminar... ainda não está pedindo todos os parametros
                    pessoa=lista_parametros[0]
                    start=lista_parametros[1]
                    end=lista_parametros[2]
                    func=reportTracing(pessoa,start,end)
                    msg=msg+func
                                       
                elif codigo==53:
                    # Best Day
                    periodo=lista_parametros[0]
                    func=reportBestday(periodo)
                    msg=msg+func

                elif codigo==54:
                    # Mask Detection
                    timeframe=lista_parametros[0]
                    func=reportMask(timeframe)
                    msg=msg+func
                
                elif codigo==55:
                    func=showRunning()
                    msg=msg+func

                elif codigo==31:
                    periodo=lista_parametros[0]
                    func=reportDistancing(periodo)
                    msg=msg+func
                    












                #------------------------------------
                # FIM DO BLOCO PARA INTERPRETAÇÃO DE CÓDGIOS       

                else:
                    msg="Não encontrei um forma de executar o comando que você me pediu devido a um erro na minha programação.  \n"
                    # English
                    msg="I couldn't find a way to execute what you asked me due to a failure in my code.  \n"

                # Portuguese
                #msg=msg+"  \nEspero ter atendido sua expectativa.  \n"
                #English
                msg=msg+"  \nI hope you've got what you asked.  \n"

                # uma vez que serviço entregue, zera a memória da conversa
                reinicia_user(usermail) 

            else:

                # caso ainda não tenha digitado o sim, então pede o prox passo:

                # mensagem do robo caso comando requer parametros
                if memoria[usermail]['req']==True:
                    msg=msg_titulo+msg_params+msg_ready+msg_sn
                else:
                # mensagem do robo caso comando nao requer parametros
                    msg=msg_titulo+msg_ready+msg_sn
                
        # se chegou aqui, aguarda parametros, mas ainda não estão prontos
        elif memoria[usermail]['params']==False:
            
            if memoria[usermail]['typing']==True:


                # fica neste modo a espera dos parametros
                # quando qtde de comandos está ok, define que qtde de parametros esta correta
                                    
                #copia ultimo comando para memoria
                memoria[usermail]['typed']=comando
                parametros=memoria[usermail]['typed']
                
                # testa se qtde de comandos está ok
                # lista de comandos que se espera
                parametros_esperados=(optparam(memoria[usermail]['option'],"params").split(","))
                # lista de comandos digitadaos
                parametros_digitados=(parametros.split(","))
                
                # testa se qtde de comandos está ok
                if len(parametros_esperados) == len(parametros_digitados):
                    texto=""
                    c=0
                    while c<len(parametros_digitados):
                        texto=texto+parametros_esperados[c]+"="+parametros_digitados[c]+" "
                        c+=1
                    # Se chegou até aqui, avisa agora que falta só o sim
                    msg=msg_titulo
                    msg=msg+f"You typed: {texto}  \n"
                    msg=msg+msg_sn
                    memoria[usermail]['params']=True
                else:
                    msg=msg_titulo+msg_need_params+msg_comma


               # se chegou aqui, aguarda user dizer se é o comando inicialmente está correto ou não
            else:

                if 'yes' in comando or 'ok' in comando or 'sim' in comando:
                    msg=msg_need_params
                    msg=msg+msg_comma
                    memoria[usermail]['typing']=True
                    # sendo sim, significa agora que está a espera de parametros
                else:
                    msg=msg_titulo+msg_sn

        # 4 - User cancelled conversation
        ##############################################

        # 4)  Usuário cancelou a conversa  então este bloco recomeça

        # Reinicia conversa se usuario pedir
        if 'restart' in comando or "no" in comando or "não" in comando or "reinicia" in comando:
            msg=msg_restart
            reinicia_user(usermail)

    # comandos de teste
    
    if 'memoria' in comando:
        
        #resgata a memoria
        #caso falhe, sinal de que nao ha memoria
        try:
            msg="cógigo:"+str(memoria[usermail]['option'])
            msg=msg+"  \nwait:"+str(memoria[usermail]['wait'])
            msg=msg+"  \nrequer parametros:"+str(memoria[usermail]['req'])
            msg=msg+"  \nparametros:"+str(memoria[usermail]['params'])
            msg=msg+"  \ndigitando parametros:"+str(memoria[usermail]['typing'])
            msg=msg+"  \no que foi digitado:"+str(memoria[usermail]['typed'])
        except:
            msg="Erro no resgate da memoria"    

    #print (memoria)

    return msg,arquivo


def trataPOST(content):


    # HTTP POST Functions

    # Deals with POST
    # Webhook from user or
    # Alarms generated by other modules

    # webhooks aqui
   
    # Webex Webhooks
    ######

    try:
        # resposta as perguntas via webexteams
        # trata mensagem quando nao e' gerada pelo bot. Se nao e' bot, entao usuario     
        if content['name']==webhook_name and content['data']['personEmail']!=botmail:
            # identifica id da mensagem
            msg_id=(content['data']['id'])
            # identifica dados da mensagem
            mensagem,sala,usermail=getwebexMsg(msg_id)
            #usermail=webextalk[2]
            #mensagem=webextalk[0]
            #sala=webextalk[1]

            # executa a logica
            try:
                msg,arquivo=logica(mensagem,usermail)
            except:
                print ("Erro de logica.")
        
            # Envia resposta na sala apropriada
            webexmsgRoomviaID(sala,msg,arquivo)

    
    except:
        print ("não é webhook esperado")


    # Alarms sent via POST
    ###############################

    # alarmes aqui

    # código para tratar alarmes
    # formato do alarme esperado:

    #{"alarm": "distance-bot",
    #"data": {
    #    "type": "00",
    #    "message": "Mensagem para o user",
    #    "who": "lista de pessoas para avisar"
    #    "image": "endereço da imagem"
    #}}

    # valida se POST é do tipo alarme esperado
    try:
        if content['alarm']=="distance-bot":
            
            imagem=""

            # texto que veio do alarme
            try:
                txt_alarm=content['data']['message']
            except:
                print ("Nenhuma mensagem identificada")
            
            # lista de pessoas (emails) separados por virgulas
            try:
                pessoas=list(content['data']['who'].split(','))
            except:
                print ('Nenhum destinatario identificado')
                pessoas=()
            
            # tenta identificar imagem (opcional)
            try:
                imagem=content['data']['image']
            except:
                print ('Imagem não identificada')
                imagem="None"
            

            # tipo de alarme
            # 00 = mensagem para individuo(s), 01 = mensagem para admin(s)
            tipo_alarme=content['data']['type']
            print (f'msg={txt_alarm} avisar={pessoas} imagem={imagem}')
                        

            if tipo_alarme=="00":
                # Alarme para individuos
                # pessoas pode conter um email ou uma lista de emails 
                try:
                    for b in pessoas:
                        webexmsgUser(b,txt_alarm)
                except:
                    print ("Envio individual falhou")
                    

            elif tipo_alarme=="01":
                # Alarme do tipo aviso para admin
                # Envia nota para Sala dos Admins/Facility manager
                try:
                    sala=getwebexRoomID(admins_room)
                    webexmsgRoomviaID(sala,txt_alarm,imagem)
                except:
                    print("Falha para enviar msg ao grupo admin")
            
            else:
                print ('Nenhum cod de alarme conhecido')

    except:
        print ("não é alarme esperado")
