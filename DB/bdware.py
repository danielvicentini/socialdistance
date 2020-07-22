# -*- coding: utf-8 -*-
## Variaveis


# 21.07.2020
# DB Functions for DB writes and reports

import sys
import os
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('bot'))

from bdFluxQueries import TraceReport, OccupancyReport, BestDayReport, BestDay
from config import le_config

"""
Definition of paramater that allow connecting to the SocialDistance DB
"""

from config_shared import INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_DBUSER, INFLUXDB_DBPASSWORD, INFLUXDB_DBNAME, INFLUXDB_USER, INFLUXDB_PASSWORD
from config_shared import TABELA_MV, TABELA_TOTAL, TABELA_TRACE

from influxdb import InfluxDBClient
import json
import time


"""TimeSeries DataBase Class."""

# Objeto do banco
# metodo de escrita do trace

class DBClient():
  """
  This class allows to instantiate a handler for the SocialDistance InfluxDB database.
  When a object is instantitated, connection to the database is opened.
  """
  def __init__(self):

    # Connects to the database
    self._host = INFLUXDB_HOST
    self._port = INFLUXDB_PORT
    self._user = INFLUXDB_USER
    self._password = INFLUXDB_PASSWORD
    self._dbname = INFLUXDB_DBNAME      
    self._client = InfluxDBClient(self._host, self._port, self._user, self._password, self._dbname)
    
  def Close(self):
    # Closes DB
    self._client.close()

  def peopleLog(self, local: str, userid: str, status: str, origem: str):
      """
      Escreve no banco quando user entra ou sai
      """
     
      # Prepare JSON with data to be writte in PeopleLog (trace) measurement
      json_body = {}
      json_body["measurement"] = TABELA_TRACE
      json_body["tags"] = {}
      json_body["tags"]["local"] = local
      json_body["fields"] = {}
      json_body["fields"]["userid"] = userid
      json_body["fields"]["state"]=status
      json_body["fields"]["origin"]=origem

      # Write data to InfluxDB
      self._client.write_points([json_body])

      #Return True to indicate that data was recorded
      return True

  def TotalCount(self, local: str, total: int, origem: str, people:list):
      """
      Escreve no banco total de usuarios naquele local
      """
     
      # Prepare JSON with data to be writte in TotalPeopleCount measurement
      json_body = {}
      json_body["measurement"] = TABELA_TOTAL
      json_body["tags"] = {}
      json_body["tags"]["location"] = local
      json_body["tags"]["origin"] = origem
      json_body["tags"]["people"] = people
      json_body["fields"] = {}
      json_body["fields"]["count"] = total
      
      # Write data to InfluxDB
      self._client.write_points([json_body])

      #Return True to indicate that data was recorded
      return True

  def SanityMask(self, local: str, network:str, serial:str, url:str, time:str):
      """
      Escreve no banco eventos quando pessoas sem máscara
      """
     
      # Prepare JSON with data to be writte in SanityMask measurement
      json_body = {}
      json_body["measurement"] = TABELA_MV
      json_body["tags"] = {}
      json_body["tags"]["local"] = local
      json_body["tags"]["network"] = network
      json_body["tags"]["serial"] = serial
      json_body["fields"] = {}
      json_body["fields"]["url"] = url
      json_body["time"]= time
      
      
      # Write data to InfluxDB
      self._client.write_points([json_body])

      #Return True to indicate that data was recorded
      return True


    ### FALTA FUNCOES DE CONSULTA

  def ConsultaMask(self, tabela: str, tempo:str):
      
      # Count qty of events in the Mask table

      query= 'SELECT count(url) from ' + tabela

      # Consulta
      
      # tenta a consulta, do contrário devolve erro
      try:
        consulta=self._client.query(query+" where time > now() - "+tempo)

        
        # trabalha resultado
        resultado=list(consulta.get_points())
        try:
            x=resultado[0]['count']
        except:
            # se chegou aqui, não voltou nenhum resultado, portanto zero.
            x=0    

        texto = f"{x} events in the past {tempo} time."

      except:
          texto = "Error in the query. Try XXd (for past days)"

      msg=texto
      return msg




# BD report

def bd_consulta(tabela,filtro):

    
    # 21.7.2020
    # English
    # This function will run reports on the DB
    # Reports use regular influx for (Mask detection) and Flux for complex reports (BestDay, Occupancy/History and TracePeople)
    # Code will call each function basead on a table (tabela) variable and filter (filtro) defined by user
    # Most of cases, filtro is a point in the time where data is collected for the investigation
    # Returns code in JSON format
    
    msg=""

    global TABELA_MV, TABELA_TOTAL, TABELA_TRACE

    
    if tabela=="totalcount":
        
        # Reports Social Distance Out of Compliance in room by shifts
    
        # Chama consulta e retorna os períodos fora de compliance
        # Chama consulta Flux para Coleta da base de dados conforme filtro
        try:
            x=OccupancyReport(le_config(), filtro)
        except:
            #Msg de erro caso filtro venha errado
            msg="Query Error"
            
        
        try:
            #Formata msg de saída do Filtro
            for b in x['PerShiftHistory']:
                msg=msg+f"Room: {b['location']}  Data: {b['day']}-{b['month']}-{b['year']} Shift: {b['shift']}   \n"
                print (msg)
        except:        
            #Msg de erro caso filtro venha errado
            msg="Error in the query. Try XXd (for past days)"
            
        if msg=="":
            msg="No data  \n"

    elif tabela=="peoplelog":

        # Reports tracing of people (who's close to) in a certain period of time
            
        params=filtro.split('&')
        # Checa e só continua se qtde de parametros correta
        if len(params)!=3:
            msg="Trace: Missing parameters. Requires: userid, start time, end time.  \n"
            
        elif len(params)==3:
            # parametros ok, continua

            personid=params[0]
            start=params[1]
            end=params[2]
            print(params)
            try:
                # realiza consulta
                print ("trace")
                x=TraceReport(personid,start,end)
                print (x)
                minhalista=list()
            except:
                #Msg de erro caso filtro venha errado
                msg="Query Error.Format: personid: username, start: YYYY-MM-DD, end: YYYY-MM-dd"
            
            try:
                #montagem da resposta
                for b in x:
                    minhalista.append(b['userid'])
                    minhalista=list(dict.fromkeys(minhalista))    
                    
                msg="List of users close:  \n"
                for b in minhalista:
                    
                    msg=msg+f"{b}  \n"
                if len(minhalista)==0:
                    msg="No data."
            except:
                msg="No Data or Query Error.  \n"
            

            

    elif tabela=="bestday":
        
        
        # Report Best Day to go to the office
        # 
        #try:
        # Massa de dados do periodo informado
        x=BestDayReport(filtro)
        # consolida os melhores dias durante o horário comercial
        y=BestDay(x,9,12)
        print (y)
        # monta a mensagem
        for b in y:
            msg=msg+f"Room: {b['location']} - Best Days: {b['bestday']}  \n"
        print (msg)
        #return msg
        #except:
            #msg="No Data and/or Query Error. \n"
            #return "No Data and/or Query Error. \n"
    
    elif tabela=="sanityMask":

        # Reports qty of events of people not wearing Mask during a certain period of time

        # Chama consulta dos eventos sem mascara
        banco=DBClient()
        tabela=TABELA_MV
        msg=banco.ConsultaMask(tabela,filtro)
        banco.Close()
        
    else:
        msg="Table information not found."

    
    json = { "msg":msg}
    return json


# BD update via JSON content

def bd_update(json_content):

    # 21.7.2020
    # English
    # This function updates DB according to data type and parameters send in format of a JSON content
    # Details bellow of JSON format
    # Code will identify tipo and calls appropiate function to write to the DB


    # initiate DB
    banco=DBClient()
    

    # faz upload do BD conforme JSON POSTADO

    # Tipo 1 - raw de entrada e saida de usuario
    # Type 1 - raw data of login/logoff user
    # {
    #    "type":"peoplelog",
    #    "local":"LOG1",
    #    "origem":"python",
    #    "userid":"dvicenti",
    #    "status":"entrou"
    #}

    # Tipo 2 - Total de pessoas na sala
    # Typo 2 - Total people in a room
    # {
    #    "type":"totalcount",
    #    "local":"SALA_log2",
    #    "origin": "camera"
    #    "total":100
    #    "people":"people1@email,people2@email"
    #}

    # Tipo 3 - Pessoas detectadas sem mascara
    # Type 3 - No Mask detected people
    # {
    #    "type":"sanitymask",
    #    "local":"SALA-Log3"
    #    "network":"XPTO",
    #    "serial":"XPTO",
    #    "url":"http://x.com/foto.png"
    #    "time": "2018-03-28T8:01:00Z"
    #}

    # check if it an expected data
    try:
        tipo = json_content["type"]
    except:
        print ("not a valid json expected")
        print (json_content)
        return "erro"
    # calls BD to write date
    try:
        if tipo == "peoplelog":
            banco.peopleLog(json_content["local"],json_content["userid"],json_content["status"],json_content["origem"])

        elif tipo == "totalcount":
            banco.TotalCount(json_content["location"],json_content["count"],json_content['origin'],json_content['people'])

        elif tipo == "sanitymask":
            banco.SanityMask(json_content["local"],json_content['network'],json_content['serial'],json_content['url'],json_content["time"])

        # returns ok if ok
        banco.Close()
        print (json_content)
        return "ok"

    except:
        # returns error if not ok
        print ("missing fields or BD error")
        print (json_content)
        return "erro"