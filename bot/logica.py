# -*- coding: utf-8 -*-

# This code was originaly Documented in Portuguese Language
# Daniel 6.26.2020

# Webex Teams rooms from config_shared
from config_shared import admins_room
# Bot config
from config import memoria, botmail, webhook_name, configuracao
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

def opcoes_para_user():
    
    # acessa cada uma das opcoes da configuracao de opcoes
    # para apresentar a lista de comandos disposniveis ao user
    msg="***Commands that I understand***:  \n\n"
    c=0
    for b in novas_opcoes['opcoes']:
        msg=msg+"***"+str(c+1)+") "+novas_opcoes['opcoes'][c]['title']+"***  \n"
        msg=msg+novas_opcoes['opcoes'][c]['desc']+"  \n"
        c+=1
    
    msg=msg+"  \nType keywords so we can start our chat.  \n"

    return msg


# This function returns data from an specific user option

# Função que retorna dados a respeito de cada opção
# Ex: se requer parametros, quais as tags

def optparam(codigo,item):
    
    # investiga nas opcoes existentes para o user
    # devolve o valor do item conforme o codigo da opcao
    c=0
    for b in novas_opcoes['opcoes']:
        if novas_opcoes['opcoes'][c]['option']==codigo:
            try:
                dado=novas_opcoes['opcoes'][c][item]
                
            except:
                dado = "erro"
        c+=1

    return dado

# This function try to understand the best match for an available option for the user based on keywords sent.

# Função que sugere melhor comando de acordo com o entendimento do usuário
# Entendimento é feito comparando o que o usuário escreveu com o valor da "tag" da opção    

def sugere_opcao(comando):

    # recebe o comando, procura qual a melhor opcao mais proxima a este comando e devolve o código

    #variável para entencer qual a opcao da lista de comandos qu é mais parecido com o comando digitado
    score=0.0
    # loop para cada um das opções conhecidos
    # variavel c usada para procurar na lista de opcoes
    c=0
    for b in novas_opcoes['opcoes']:
        #
        txtnow=novas_opcoes['opcoes'][c]['tag'].lower()
        opcao_cod=novas_opcoes['opcoes'][c]['option']
        c+=1    

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
    if score>=.3:
        return opescolhido
    else:
        return 0


# Initiates memory for a user - used by the robot to chat with the user

# Função que inicia valores para um usuário conversando com o robo
# iniciar valores = convesarsa começando do zero.

def reinicia_user(usermail):
    
    global aguardando
    global memoria
    global configuracao
    # config nova
    # global configa
    
    # reinicia variavies da memoria par ao usuario
    # robo vai comecar do zero com este usuario
    try:
        var={ 'wait':False, 'option':0, 'req':False, 'params':False, 'typed':'','typing':False}
        memoria[usermail]=var
        aguardando=memoria[usermail]['wait']
    except:
        pass

### Main Code


#### PROGRAMA PRINCIPAL


### Step 0 - Ready options available from options.json
#################################################################

# 0) Inicio
# leitura do arquivo de opcoes

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



### Part 1 - Logic - main function - this function is called whenever a text arrives for the bot
#################################################################


# 1) logica
# É chamado a medida que um comando chega do usuário, seja via console (testes) ou via http (produção)

def logica(comando,usermail):
   
    global aguardando
    global memoria
    global configuracao
    #global configa
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
            msg=opcoes_para_user()
                
        #2.1b. tenta adivinhar o comando consultando os comandos disponiveis
        # caso ele encontre uma opcao, apresenta e apos isto o robo entra em modo de espera

        if msg=="" and len(sp)>0 and len(comando)>=5:
            # chama função que devolve o cod da opcao mais aproximada
            opescolhido=sugere_opcao(comando)
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
            msg_need_params=f"Digite os parametros para completar o comando:{optparam(memoria[usermail]['option'],'params')}  \n"    
            # English
            msg_need_params=f"The following parameters are needed:{optparam(memoria[usermail]['option'],'params')}  \n"   


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

                    #teste admin
                    if usermail not in configuracao['admin']:
                        msg = msg+"I can't execute. You are not an admin.  \n"
                        msg = msg+msg_restart
                        reinicia_user(usermail)
                    else:    
                        # funcao configura distancia Teste
                        maximo=lista_parametros[0].strip()
                        sala=lista_parametros[1].strip()
                        msg=msg+f"Defining max distance of ***{maximo}*** peopleo for room ***{sala}***...ok"
                        configuracao['data']['max']=int(maximo)
                    
                elif codigo==13:
                    # Start Camera for mask detection
                    camera=lista_parametros[0]
                    serial=getDeviceInfoName("SerialNumber",camera)
                    netid=getDeviceInfoName("NetworkID",camera)
                    if serial!="erro" or netid!="erro":
                        msg= (f"Executar: http://{mask_server}:{mask_server_port}/loop?network_id={netid}&mv_serial={serial}&turn=on")
                    else:
                        msg = "Couldn't find the device information you asked."

                elif codigo==14:
                    # Stop camera for mask detection
                    camera=lista_parametros[0]
                    serial=getDeviceInfoName("SerialNumber",camera)
                    netid=getDeviceInfoName("NetworkID",camera)
                    if serial!="erro" or netid!="erro":
                        msg= (f"Executar: http://{mask_server}:{mask_server_port}/loop?network_id={netid}&mv_serial={serial}&turn=off")
                    else:
                        msg = "Couldn't find the device information you asked."


                elif codigo==51:
                    # funcao inventario
                    #c=0
                    saida = "  \nCurrent Inventory:  \n"
                    #for dado in configuracao['inventario']:
                    #    sala="Sala:**"+str(dado['sala'])+"**  \n"
                    #    ap="Access-Point:"+str(dado['access-point'])+"  \n"
                    #    dist="Distancia:"+str(dado['distancia'])+"  \n"
                    #    saida=saida+"___  \n"+sala+ap+dist+"___  \n"
                    #    c+=1
                    #c=0
                    
                    # Read data from inventory.py
                    for dado in DeviceInventory:
                        sala=f"Room: ***{dado['Location']}***  \n"
                        device=f"Device Name:{dado['Nome']} SN:{dado['SerialNumber']} Type:{dado['Device']}   \nNetId:{dado['NetworkID']}  \n"
                        saida=saida+sala+device+"___  \n"
                    msg=msg+saida

                    
                elif codigo==55:
                    # config rodando
                    admins=configuracao['admin']
                    maximo=configuracao['data']['max']
                    msg=msg+f"Current config: Admins: {admins}  \n Max People per room: {maximo}  \n"
                    
                    
                elif codigo==52:
                    # Tracing
                    pessoa=lista_parametros[0]
                    msg=msg+f"Tracing ***{pessoa}***:  \nList of close people in the previous weeks:  \n"
                    msg=msg+f"Week 1: ana, daniel, andrey, adilson  \n"
                    msg=msg+f"Week 2: Ana, Danie, Flávio  \n"

                    # Teste de código para consultar report
                    url = f"http://{report_server}:{report_server_port}/api/v1/consulta/peoplelog/ana"
                    headers = {'Content-Type': "application/json" }
                    response = requests.request("GET", url, headers=headers)
                    msg=msg+response.text

                    
                          
                elif codigo==53:
                    # Best Day
                    msg=msg+f"Best days to go to office:  \n"
                    msg=msg+f"Thursday: ***8h00-9h00***, ***16h00-17h00***  \n"
                    msg=msg+f"Friday: ***8h00-10h00***  \n"

                elif codigo==54:
                    # Mask Detection
                    msg=msg+f"Report of people not wearing mask this week:  \n"
                    msg=msg+f"Monday: 1  \n"
                    msg=msg+f"Tuesday: 15  \n"
                    msg=msg+f"Wednesday: 3  \n"
                    msg=msg+f"Thursday: 0  \n"
                    msg=msg+f"Friday: 7  \n"
                    
                    
                    # Teste de código para consultar report
                    url = f"http://{report_server}:{report_server_port}/api/v1/consulta/sanityMask/1"
                    headers = {'Content-Type': "application/json" }
                    response = requests.request("GET", url, headers=headers)
                    msg=msg+response.text


                elif codigo==55:
                    # config rodando
                    admins=configuracao['admin']
                    maximo=configuracao['data']['max']
                    msg=msg+f"Current config: Admins: {admins}  \n Max People per room: {maximo}  \n"
                    
                        

                elif codigo==31:
                    # funcao historico
                    msg=msg+"  \nO histórico é o seguinte:  \n"
                    msg=msg+"Sala ***Cafeteria***: dentro do distanciamento.  \n"
                    msg=msg+"Sala ***Reunião***: fora do distanciamento na parte da manhã. Estouro em 10 pessoas.  \n"

                
                    # Teste de código para consultar report
                    url = f"http://{report_server}:{report_server_port}/api/v1/consulta/totalcount/hoje"
                    headers = {'Content-Type': "application/json" }
                    response = requests.request("GET", url, headers=headers)
                    msg=msg+response.text

                












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


