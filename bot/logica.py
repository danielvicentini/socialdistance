from config_shared import *
from config import memoria, botmail, webhook_name, configuracao, configa
from webexteams import getwebexMsg, webexmsgRoomviaID, getwebexRoomID, getwebexUserID, webexmsgUser
import json

# ver 1.5 - 11.5.20

#### FUNÇÕES A RESPEITO DAS OPÇÕES/COMANDOS DISPONÍVEIS AO USUÁRIO
#####################################################################

# Funcão para retornar menu com opções ao usuário
# Estas funções são chamadas dentro da logica

def opcoes_para_user():
    
    # acessa cada uma das opcoes da configuracao de opcoes
    # para apresentar a lista de comandos disposniveis ao user
    msg="***Comandos disponiveis que posso fazer***:  \n\n"
    c=0
    for b in novas_opcoes['opcoes']:
        msg=msg+"***"+str(c+1)+") "+novas_opcoes['opcoes'][c]['title']+"***  \n"
        msg=msg+novas_opcoes['opcoes'][c]['desc']+"  \n"
        c+=1
    
    msg=msg+"  \nDigite partes do comando para começarmos nossa conversa.  \n"

    return msg

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


# Função que inicia valores para um usuário conversando com o robo
# iniciar valores = convesarsa começando do zero.

def reinicia_user(usermail):
    
    global aguardando
    global memoria
    global configuracao
    # config nova
    global configa

    # reinicia variavies da memoria par ao usuario
    # robo vai comecar do zero com este usuario
    try:
        var={ 'wait':False, 'option':0, 'req':False, 'params':False, 'typed':'','typing':False}
        memoria[usermail]=var
        aguardando=memoria[usermail]['wait']
    except:
        pass


#### PROGRAMA PRINCIPAL


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

# 1) logica
# É chamado a medida que um comando chega do usuário, seja via console (testes) ou via http (produção)

def logica(comando,usermail):
   
    global aguardando
    global memoria
    global configuracao
    global configa

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
        
    # 2) Análise
    # Caso esteja no começa da conversa, este bloco entende o que o usuário quer fazer

    # 2.1 este bloco é para o caso do robo não saber ainda o que o user quer:
    if aguardando==False:
        
        # 2.1a. teste se user pediu ajuda
        if "ajuda" in comando:
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

                msg="Você quiz dizer: "+str(optparam(opescolhido,"title"))+" ?  \n"

                # Se chegou até aqui... na próxima interação robo fica a espera da continuidade da conversa
 
        # 2.1c nada conhecido, então devolve msg padrão

        if msg=="":
            msg="Olá. Digite ***ajuda*** para ver as opçoes disponíveis.  \nVou tentar adivinhar também o que você está procurando :-)  \n"

    # 3) Conversando
    # Caso conversa já iniciado, usa este bloco

    # vai por este caminho se o robo espera resposta do usuario
    if aguardando==True:

        # resgata o código do comando em questão
        codigo=memoria[usermail]['option']
    
        # Textos padrão
        msg_titulo="Bem? Eu tinha entendido: ***"+optparam(memoria[usermail]['option'],'title')+"***.  \n"
        msg_sn="Diga ***sim*** ou ***ok*** para continuar ou digite ***não*** ou ***reinicie*** para recomeçarmos.  \n"   
        msg_ready="Estou pronto para executar seu comando.  \n"

        # Se chegou até aqui, robo aguarda sim ou não para executar o comando
        if memoria[usermail]['params']==True:
            
            # resgata parametros caso comando precise deles
            if memoria[usermail]['req']==True:
                parametros=memoria[usermail]['typed']
                msg_params="Voce digitou os parâmetros : ("+parametros+")  \n"
             
            if "sim" in comando or 'ok' in comando:
            # se chegou aqui no Sim, vai executar se achar funcões para o código desejado
                msg="vou executar o que você me pediu:  \n"

               
                # Os parametros digitados estao na variavel do tipo lista abaixo
                lista_parametros=memoria[usermail]['typed'].split(",")
 
                #---------------------------------------------------------------------------------
                # DIGITE SUA INTERPRETAÇÃO DE CÓDIGOS AQUI
                # codigo = codigo do comando
                # lista_parametros = lista com os parametros digitados pelo usuario, separado por virgulas
                # o resultado do seu código deve ser atribuido a variavel msg

                if codigo==11:
                    pin=lista_parametros[0]
                    # funcao inventario
                    if pin==configa['PIN']:
                        msg=msg+"Executando a aplicacão da config..."
                    else:
                        msg="PIN não autorizado."
                                            
                elif codigo==12:
                    distancia=lista_parametros[0]
                    # funcao configura distancia
                    msg=msg+"Executando a config da distancia... para "+str(distancia)
                    configa['data']['max']=int(distancia)
                             
                elif codigo==13:
                    intervalo=lista_parametros[0]
                    # funcao configura intervalo
                    msg=msg+"Executando a config do intervalo... para "+str(intervalo)
                    configa['data']['interval']=int(intervalo)
                    
                elif codigo==14:
                    parametro = lista_parametros[0]
                    msg=msg+"Executando a monitoria de qtde de pessoas para... "
                    if 'ok' in parametro or 'on' in parametro or 'sim' in parametro:
                        # Ativa monitoria qtde pessoas
                        msg=msg+parametro
                        configa['data']['distance']=True
                    elif 'off' in parametro:
                        # Desativa monitoria qtde pessoas
                        msg=msg+parametro
                        configa['data']['distance']=False
                    else:
                        msg=msg+"Parametro nao compreendido. Não fiz nada."
                
                elif codigo==15:
                    parametro = lista_parametros[0]
                    msg=msg+"Executando a monitoria de mascara para... "
                    if 'ok' in parametro or 'on' in parametro or 'sim' in parametro:
                        # Ativa monitoria de Mascara
                        msg=msg+parametro
                        configa['data']['mask']=True
                    elif 'off' in parametro:
                        # Desativa monitoria de Mascara
                        msg=msg+parametro
                        configa['data']['mask']=False
                    else:
                        msg="Parametro nao compreendido. Não fiz nada."

                elif codigo==16:
                    parametro = lista_parametros[0]
                    msg=msg+"Executando o rastreio de pessoas para... "
                    if 'ok' in parametro or 'on' in parametro or 'sim' in parametro:
                        # Ativa tracing
                        msg=msg+parametro
                        configa['data']['tracing']=True
                    elif 'off' in parametro:
                        # Desativa tracing
                        msg=msg+parametro
                        configa['data']['tracing']=False
                        print (configa['data']['tracing'])
                    else:
                        msg="Parametro nao compreendido. Não fiz nada."


                elif codigo==51:
                    # funcao inventario
                    c=0
                    saida = "  \nSegue o inventário:  \n"
                    for dado in configuracao['inventario']:
                        sala="Sala:**"+str(dado['sala'])+"**  \n"
                        ap="Access-Point:"+str(dado['access-point'])+"  \n"
                        dist="Distancia:"+str(dado['distancia'])+"  \n"
                        saida=saida+"___  \n"+sala+ap+dist+"___  \n"
                        c+=1
                    msg=msg+saida

                    
                elif codigo==52:
                    # config rodando
                    admins=configa['admin']
                    max=configa['data']['max']
                    interval=configa['data']['interval']
                    mask=configa['data']['mask']
                    distance=configa['data']['distance']
                    tracing=configa['data']['tracing']
                    msg=f"Admins: {admins}  \n Monitorando a Distancia: {distance}  \n Max Pessoas: {max}  \n Intervalo de Pesquisa: {interval}  \n Detectar Mascara:{mask}  \n Detectar Tracing:{tracing}  \n"
                    
                    

                elif codigo==31:
                    # funcao historico
                    msg=msg+"  \nO histórico é o seguinte:  \n"
                    msg=msg+"Sala ***Cafeteria***: dentro do distanciamento.  \n"
                    msg=msg+"Sala ***Reunião***: fora do distanciamento na parte da manhã. Estouro em 10 pessoas.  \n"

                
                












                #------------------------------------
                # FIM DO BLOCO PARA INTERPRETAÇÃO DE CÓDGIOS       

                else:
                    msg="Não encontrei um forma de executar o comando que você me pediu devido a um erro na minha programação.  \n"


                msg=msg+"  \nEspero ter atendido sua expectativa.  \n"
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
                    msg=msg+"Parametros digitados: "+texto+ "  \n"
                    msg=msg+msg_sn
                    memoria[usermail]['params']=True
                else:
                    # informa que ainda falta qtde de parametros
                    msg_param="Estou aguardando parametros do seu lado.   \nEles sao: ***" + optparam(memoria[usermail]['option'],"params")+"***  \n"
                    msg_type="Digite os parametros separados por virgulas.  \n"
                    msg=msg_titulo+msg_param+msg_type+msg_sn


               # se chegou aqui, aguarda user dizer se é o comando inicialmente está correto ou não
            else:
                if 'sim' in comando or 'ok' in comando:
                    msg= "Ok. Digite os parametros para completar o comando:"+(optparam(memoria[usermail]['option'],"params"))
                    msg= msg+"  \nLembre-se de separar os comandos por vírgulas.  \n"
                    memoria[usermail]['typing']=True
                    # sendo sim, significa agora que está a espera de parametros
                else:
                    msg=msg_titulo+"Estou aguardando que você responda ***sim*** ou ***ok***. Na dúvida digite ***não*** ou ****reinicie***.  \n"    


        # 4)  Usuário cancelou a conversa  então este bloco recomeça

        # Reinicia conversa se usuario pedir
        if 'reinicie' in comando or "não" in comando or "nao" in comando:
            msg = "Ok, vou reiniciar nossa conversa.  \nDigite ***ajuda*** se quiser saber mais o que posso fazer."
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

    # webhooks aqui
   
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
        print ("não é webhook")


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
            txt_alarm=content['data']['message']
            
            # lista de pessoas (emails) separados por virgulas
            pessoas=list(content['data']['who'].split(','))
            
            # tenta identificar imagem (opcional)
            try:
                imagem=content['data']['image']
            except:
                print ('Imagem não identificada')
            

            # tipo de alarme
            # 00 = mensagem para individuo(s), 01 = mensagem para admin(s)
            tipo_alarme=content['data']['type']
            print (f'msg={txt_alarm} avisar={pessoas} imagem={imagem}')
                        

            if tipo_alarme=="00":
                # Alarme para individuos
                # pessoas pode conter um email ou uma lista de emails 
                for b in pessoas:
                    webexmsgUser(b,txt_alarm)
                    
            elif tipo_alarme=="01":
                # Alarme do tipo aviso para admin
                # Envia nota para Sala dos Admins/Facility manager
                sala=getwebexRoomID(admins_room)
                webexmsgRoomviaID(sala,txt_alarm,imagem)
            else:
                print ('Nenhum cod de alarme conhecido')

    except:
        print ("não é alarme.")


