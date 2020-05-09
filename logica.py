from config import memoria, botmail, webhook_name, configuracao
from webexteams import getwebexMsg, webexmsgRoomviaID
import json

# ver 1.4 - 7.5.20

# opcoes de comandos
#versao nova

# opçoes
# roadmap: 1) Arquivo JSON DONE, 2) GET num site http
novas_opcoes={
	"opcoes": [{
		"tag": "configura aplica",
		"title": "Aplicar as configurações feitas",
        "desc":"Esta opção vai aplicar as configurações que vc alterou.",
		"option": 11,
		"req": True,
		"params": "salvar"
	}, {
		"tag": "configurar distanc sala",
		"title": "Configurar distanciamento na Sala",
        "desc":"Esta opção vai definir a regra de distanciamento de pessoas numa sala.  \nO número que vc informar para um determinada sala  \nserá o critério aplicado.",
		"option": 12,
		"req": True,
		"params": "Nome da Sala, No. de pessoas por sala"
    }, {
        "tag": "historico uso",
		"title": "Mostrar o historico de uso",
        "desc" : "Esta opção vai informar como esta a política de distaciamento para vc entender se ela está sendo utilizada.",
		"option": 31,
		"req": False
	}, {
        "tag": "inventario invent",
		"title": "Mostrar o inventario",
        "desc": "Esta opção vai mostrar o inventário de equipamentos técnicos sendo usados.",
		"option": 51,
		"req": False	
	}]
}

"""
# não acertei ainda isto no heroku: dificultado para ler o arquivo devido a codificação
novas_opcoes=dict()
# carrega opcoes do arquivo options.json
try:
    with open('options.json') as json_file:
        data=json.load(json_file)
    novas_opcoes=data
except:
    print ("erro na leitura do arquivo de opçoes")
"""

def opcoes_para_user():
    
    # acessa cada uma das opcoes da configuracao de opcoes
    # para apresentar a lista de comandos disposniveis ao user
    msg="***Comandos disponiveis que posso fazer***:  \n\n"
    c=0
    for b in novas_opcoes['opcoes']:
        msg=msg+"***"+str(c+1)+") "+novas_opcoes['opcoes'][c]['title']+"***  \n"
        msg=msg+novas_opcoes['opcoes'][c]['desc']+"  \n"
        c+=1
    
    msg=msg+"  \nDigitel partes do comando para começarmos nossa conversa.  \n"

    return msg

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


def reinicia_user(usermail):
    
    global aguardando
    global memoria
    global configuracao
    
    # reinicia variavies da memoria par ao usuario
    # robo vai comecar do zero com este usuario
    try:
        var={ 'wait':False, 'option':0, 'req':False, 'params':False, 'typed':'','typing':False}
        memoria[usermail]=var
        aguardando=memoria[usermail]['wait']
        #print ('criado variáveis para user')
    except:
        pass


def logica(comando,usermail):
   
    global aguardando
    global memoria
    global configuracao

    # faz a logica de entender o comando pedido e a devida resposta para o usuario
    # o parametro usermail e' utilizado para identificar o usuario que solicitou o comando
    # O usuario pode ser uzado como filtro para se executar ou negar o comando
    #
    # Retorna mensagem para ser enviada para console ou Webex teams
    
    #Separa o comando por espacos
    #Primeiro item e'o comando em si, os demais sao parametros deste comando
    #
    comando=comando.lower()
    sp=comando.split(" ")
    
    # comando na variavel box, lower deixa em minusculo para normalizar
    #box=sp[0]
    
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
        #print ('recuperando memoria')
        
    except:
        # se chegamos aqui, usuario esta se comunicando pela primeira vez,
        # protanto variaveis serao criadas
        reinicia_user(usermail)
        aguardando=memoria[usermail]['wait']
        #print ('criado variáveis para user')
    
    #print(aguardando)
    

    # 2) Análise
    # Caso esteja no começa da conversa, este bloco entende o que o usuário quer fazer

    #este bloco é para o caso do robo não saber ainda o que o user quer:
    if aguardando==False:
        
        # 2a. teste se user pediu ajuda
        if "ajuda" in comando:
            # roda as opcaoes disponives
            msg=opcoes_para_user()

            #print (x)

                
        #2b. tenta adivinhar o comando consultando os comandos disponiveis

        # caso ele encontre uma opcao, apresenta e apos isto o robo entra em modo de espera

        if msg=="" and len(sp)>0 and len(comando)>=5:
            # chama função que devolve o cod da opcao mais aproximada
            opescolhido=sugere_opcao(comando)
            if opescolhido != 0:
                # popula variaveis e pergunta se e' a escolhida
                memoria[usermail]['option']=opescolhido
                memoria[usermail]['wait']=True
                memoria[usermail]['req']=optparam(opescolhido,"req")
                msg="Você quiz dizer: "+str(optparam(opescolhido,"title"))+" ?  \n"

                # Se chegou até aqui... na próxima interação robo fica a espera da continuidade da conversa
 
        # 2c nada conhecido, então devolve msg padrão

        if msg=="":
            msg="Olá. Digite ***ajuda*** para ver as opçoes disponíveis.  \nVou tentar adivinhar também o que você está procurando :-)  \n"

    # 3) Aguardando
    # Caso conversa já iniciado, usa este bloco
    # Aqui varios ramos da conversa existe
    # 1o Aguardo o comando

    if aguardando==True:
  
        # vai por este caminho se o comando identificado não precisa de parametros
        # basicamente o robo aguarda um sim ou nao
        if memoria[usermail]['req']==False:

            # mensagem padrão caso não se identifique o que se espera nas próximas condições
            msg="Bem? Eu tinha entendido: ***"+optparam(memoria[usermail]['option'],'title')+"***.  \n"
            msg=msg+"Se é isto digite ***sim***. Na dúvida digite ***não*** e dai vc pode ver o que fazer digitando ***ajuda***."

            if "sim" in comando:
            # se chegou aqui no Sim, vai executar se achar funcões para o código desejado
                msg="vou executar o que você me pediu:  \n"
                
                # executa comandos que não precisa de parametros
                # resgata o código
                codigo=memoria[usermail]['option']

                if codigo==51:
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

                elif codigo==31:
                    # funcao historico
                    msg=msg+"  \nO histórico é o seguinte:  \n"
                    msg=msg+"Sala ***Cafeteria***: dentro do distanciamento.  \n"
                    msg=msg+"Sala ***Reunião***: fora do distanciamento na parte da manhã. Estouro em 10 pessoas.  \n"

                msg=msg+"  \nEspero ter atendido sua expectativa.  \n"
                # uma vez que serviço entregue, zera a memória da conversa
                reinicia_user(usermail)    
            
        
        # vai neste caminho se o comando identificado precisa de parametros
        # o robo aguarda os parametros para dali executar as funcoes


        # Começa aqui se robo está aguardando parametros
        elif memoria[usermail]['req']==True:
            
            # mensgem padrão caso não se identifique o que se espera nas próximas condições
            msg_titulo="Bem? Eu tinha entendido: ***"+optparam(memoria[usermail]['option'],'title')+"***.  \n"
            msg_param="Estou aguardando parametros do seu lado.   \nEles sao: ***" + optparam(memoria[usermail]['option'],"params")+"***  \n"
            msg=msg_titulo+msg_param+"Digite os parametros separados por virgulas.  \nNa dúvida digite ***não*** ou ***reinicie*** para recomeçarmos."

            # trata aqui se parametros estão ok

            # Se chegou aqui é por que parametros estão prontos
            if memoria[usermail]['params']==True:

                # resgata o que foi digitado como parametros
                parametros=memoria[usermail]['typed']

                if "sim" in comando or 'ok' in comando:
                # se chegou aqui no Sim, vai executar se achar funcões para o código desejado
                    msg="Vou executar o que você me pediu:  \n"
                    
                    # executa comandos que não precisa de parametros
                    # resgata o código
                    codigo=memoria[usermail]['option']
                    
                    if codigo==11:
                        # funcao inventario
                        msg=msg+"Executando a aplicacão da config..."
                                                
                    if codigo==12:
                        # funcao inventario
                        msg=msg+"Executando a config da distancia..."

                       
                    msg=msg+"  \nEspero ter atendido sua expectativa.  \n"
                    # uma vez que serviço entregue, zera a memória da conversa
                    reinicia_user(usermail) 

                else:
                    # caso ainda não tenha digitado o sim, então pede o prox passo:
                    msg=msg_titulo+"Voce digitou os parâmetros ("+parametros+") e estou pronto para executar com estes parametros  \n"
                    msg=msg+"Diga ***sim*** ou ***ok*** que eu executo ou digite ***não*** ou ***reinicie*** para recomeçarmos.  \n"   
        
            
            elif memoria[usermail]['params']==False:
            # se chegou aqui, aguarda parametros, mas ainda não estão prontos

            
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
                        msg=msg+"Parametros digitados: "+texto
                        msg=msg+"  \nConfirma? Diga ***sim*** ou ***ok*** para executar. Digite ***não*** ou ***reinicie*** para recomeçar.  \n"
                        memoria[usermail]['params']=True
                    else:
                        # informa que ainda falta qtde de parametros
                        msg="Falta parâmetros para o comando. Tente de novo.  \n"
                        msg=msg+msg_param


               # se chegou aqui, aguarda user dizer se é o comando inicialmente está correto ou não
                if memoria[usermail]['typing']==False:
                    if 'sim' in comando:
                        msg= "Ok. Digite os parametros para completar o comando:"+(optparam(memoria[usermail]['option'],"params"))
                        msg= msg+"  \nLembre-se de separar os comandos por vírgulas.  \n"
                        memoria[usermail]['typing']=True
                        # sendo sim, significa agora que está a espera de parametros
                    else:
                        msg=msg_titulo+"Estou aguardando que você responda ***sim***. Na dúvida digite ***não*** ou ****reinicie***.  \n"    


        # 4)  se usuário cancelou a conversa  então este bloco recomeça

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
            msg,arquivo=logica(mensagem,usermail)
        
            # Envia resposta na sala apropriada
            webexmsgRoomviaID(sala,msg,arquivo)

    except:
            print("POST nao reconhecido")
            pass