# -*- coding: utf-8 -*-
## Variaveis

from influxdb import InfluxDBClient
import json
import time

# DB Functions

"""
Definition of paramater that allow connecting to the SocialDistance DB
"""

INFLUXDB_HOST = '159.89.238.176'
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'root'
INFLUXDB_PASSWORD = 'root'
INFLUXDB_DBNAME = 'socialdistance'
INFLUXDB_DBUSER = 'smly'
INFLUXDB_DBPASSWORD = 'my_secret_password'
TABELA_TRACE="TraceDaniel"
TABELA_MV="MVAndrey"
TABELA_TOTAL="TotalDaniel"

"""
Defintion of measurements currently supported at the SocialDistance DB
General instruction:
When creating a new measurement to the DB, please add an ALIAS for this measurement and
refer to it by this alias (instead of the using an string directly).
"""


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
    self._client.close()

  def peopleLog(self, local: str, userid: str, status: str, origem: str):
      """
      Escreve no banco quando user entra ou sai
      """
     
      # Prepare JSON with data to be writte in PeopleCount measurement
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

  def TotalCount(self, local: str, total: int):
      """
      Escreve no banco total de usuarios naquele local
      """
     
      # Prepare JSON with data to be writte in PeopleCount measurement
      json_body = {}
      json_body["measurement"] = TABELA_TOTAL
      json_body["tags"] = {}
      json_body["tags"]["local"] = local
      json_body["fields"] = {}
      json_body["fields"]["total"] = total
      
      # Write data to InfluxDB
      self._client.write_points([json_body])

      #Return True to indicate that data was recorded
      return True

  def SanityMask(self, local: str, network:str, serial:str, url:str, time:str):
      """
      Escreve no banco eventos quando pessoas sem máscara
      """
     
      # Prepare JSON with data to be writte in PeopleCount measurement
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

  def PeopleCountQuery(self, queryFilter=None):
    """
    Query PeopleCount. A filter may be specificified to be used in the WHERE clause.
    """

    # Prepare JSON with data to be writte in PeopleCount measurement
    query = 'SELECT * from ' + TABELA_TRACE
    if queryFilter is not None:
      query = query + " WHERE " + queryFilter
    
    # Query data from InfluxDB
    result = self._client.query(query)
    return result

  def Consulta(self, tabela: str, filtro:str):
      query= 'SELECT LAST(*) from ' + tabela
      result=self._client.query(query)
      return result



# BD report

def bd_consulta(tabela,filtro):

    global TABELA_MV, TABELA_TOTAL, TABELA_TRACE

    banco=DBClient()
    if tabela=="totalcount":
        tabela=TABELA_TOTAL
    elif tabela=="peoplelog":
        tabela=TABELA_TRACE
    elif tabela=="sanityMask":
        tabela=TABELA_MV

    query=banco.Consulta(tabela,filtro)
    banco.Close()

    print (query)
    return f"consulta na tabela {tabela} ok"

    


# BD update via JSON content

def bd_update(json_content):

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
    #    "total":100
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
            banco.TotalCount(json_content["local"],json_content["total"])

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