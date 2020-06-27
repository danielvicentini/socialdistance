# -*- coding: utf-8 -*-
## Variaveis

from influxdb import InfluxDBClient
import json
import time

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

"""
Defintion of measurements currently supported at the SocialDistance DB
General instruction:
When creating a new measurement to the DB, please add an ALIAS for this measurement and
refer to it by this alias (instead of the using an string directly).
"""
MSRMT_RAWPEOPLECOUNT = "RawPeopleCount"


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


  def peopletrace(self, local: str, userid: str, status: str):
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

      # Write data to InfluxDB
      self._client.write_points([json_body])

      #Return True to indicate that data was recorded
      return True


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

# Execucao

banco=DBClient()

lista=("dvicent","maralves","flavio","ana","user1","user3","user4","user5")

def entrou(lista):
    c=0
    for b in lista:
        user= (str(lista[c]))
        status="entrou"
        local="sala"
        c=c+1
        #print (f'{user} {local} {status}\n')
        print ("entrando...")
        banco.peopletrace(local,user,status)


def saiu(lista):
    c=0
    for b in lista:
        user= (str(lista[c]))
        status="saiu"
        local="sala"
        c=c+1
        print ("saindo...")
        banco.peopletrace(local,user,status)

# inicio
# loop infinito
# a cada hora loga, depois desloga lista de users
# a fim de popular tabela Trace

while True:
    
    entrou(lista)
    time.sleep(3600)
    saiu(lista)
    time.sleep(3600)

