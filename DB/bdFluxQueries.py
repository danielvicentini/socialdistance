import sys
import os
#sys.path.append(os.path.abspath('..'))

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from influxdb_client import InfluxDBClient
from config_shared import INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_DBUSER, INFLUXDB_DBPASSWORD, INFLUXDB_DBNAME, INFLUXDB_USER, INFLUXDB_PASSWORD
from config_shared import TABELA_MV, TABELA_TOTAL, TABELA_TRACE

######  MUITO IMPORTANTE: A SER REMOVIDO ##################################
###### Mudando a balea de Trace para TraceDaniel porque a atual tabela de trace
###### nao tem nenhum dado
################################################################################

TABELA_TRACE = "TraceDaniel"

LocationInventory = [
  {
   "Location": "Cozinhha",
   "Occupancy": 1
   },
  {
   "Location": "EDU",
   "Occupancy": 2
   },
  {
   "Location": "IND",
   "Occupancy": 2
   },
  {
   "Location": "Quartos",
   "Occupancy": 2
   },
  {
   "Location": "Sala",
   "Occupancy": 2
   },
  {
   "Location": "Sandboz",
   "Occupancy": 3
   }
]



QUERY_TRACE = \
     'targetUser = "%s" \n\
      startTime = %s \n\
      stopTime = %s \n\
      \n\
      t1 = from(bucket:"socialdistance/autogen") \n\
            |> range(start: startTime, stop: stopTime) \n\
            |> filter(fn: (r) => (r._measurement == "%s") and (r._field =~ /(userid)|(state)/)) \n\
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") \n\
            |> drop(columns: ["_start", "_stop", "_measurement"]) \
      \n\
      t2 = t1 \n\
            |> filter(fn: (r) => (r.state=="entrou")) \n\
            |> map(fn: (r) => ({r with entryTime: r._time})) \n\
      t3 = t1 \n\
            |> filter(fn: (r) => (r.state=="saiu")) \n\
      t4 = union(tables: [t2, t3]) \n\
            |> sort(columns:["userid", "_time"]) \n\
            |> fill(column:"entryTime", usePrevious: true) \n\
      \n\
      t5 = t4 \n\
            |> filter(fn: (r) => (r.state=="saiu")) \n\
            |> map(fn: (r) => ({r with exitTime: r._time})) \n\
            |> drop(columns: ["state", "_time"]) \
      \n\
      targetTable = t5 \n\
                     |> filter(fn: (r) => (r.userid == targetUser)) \n\
                     |> drop(columns: ["userid"]) \n\
      othersTable = join(tables: {other: t5, target: targetTable}, on:["local"]) \n\
                     |> filter (fn: (r) => (r.userid != targetUser)) \n\
      suspectTable = othersTable \n\
                       |> filter (fn: (r) => ((r.exitTime_other >= r.entryTime_target) and (r.exitTime_target >= r.entryTime_other))) \n\
                       |> yield(name: "suspectTable")'

#
# Trace report
#
# Input:
#    targetUser = userid to be traced
#    startTime = string with initial time for tracing (ex: "2020-07-14T00:00:00Z")
#    stopTime = string with final time for tracing (ex: "2020-07-14T00:00:00Z")
#
# Output: List of dictionaty entries in the format
#    {
#     'local': <local where user met targetUser>, 
#     'userid': <id of user that met targerUser>'
#    }
#
def TraceReport(targetUser, startTime, stopTime):

  # Connects to the database
  url = "http://{}:{}".format(INFLUXDB_HOST, INFLUXDB_PORT)     
  client = InfluxDBClient(url=url, token="", org="")

  # Build trace query
  query = QUERY_TRACE % (targetUser, startTime, stopTime, TABELA_TRACE)
  tables = client.query_api().query(query)
  client.__del__()

  # Query result is a list of all tables creted in TRACE_QUERY, each of them of type FluxTable
  # see https://github.com/influxdata/influxdb-client-python/blob/master/influxdb_client/client/flux_table.py#L5 for more info

  # Build result as a list of all found records in suspecTable
  result =[]
  for table in tables:
    for record in table.records:
      subdict = {x: record.values[x] for x in ['local','userid']}
      if subdict not in result:
        result.append(subdict)
  return result



#
# Distancing report
#
# Input:
#    startTime = string with initial time for report (ex: "2020-07-14T00:00:00Z")
#
# Output: List of dictionaty entries in the format
#    {
#     'local': <local where user met targetUser>, 
#     'userid': <id of user that met targerUser>'
#    }
#
def OccupancyReport(startTime):

  # Connects to the database
  url = "http://{}:{}".format(INFLUXDB_HOST, INFLUXDB_PORT)     
  client = InfluxDBClient(url=url, token="", org="")

  # Preapre to create a table with maximum occupancy per room 
  TEMP_TABLE = "MaximumOccupancy"
  write_api = client.write_api(write_options=SYNCHRONOUS)

  #Build a record per local
  record = []
  for location in LocationInventory:
    _point = Point(TEMP_TABLE).tag("local", location.Location).field("occupancy", location.Occupancy)
    record.append(_point)

  # Write to temporary table
  write_api.write(bucket=INFLUXDB_DBNAME, record=record)

  # Build trace query
  query = QUERY_TRACE % (targetUser, startTime, stopTime, TABELA_TRACE)
  tables = client.query_api().query(query)
  client.__del__()

  # Query result is a list of all tables creted in TRACE_QUERY, each of them of type FluxTable
  # see https://github.com/influxdata/influxdb-client-python/blob/master/influxdb_client/client/flux_table.py#L5 for more info

  # Build result as a list of all found records in suspecTable
  result =[]
  for table in tables:
    for record in table.records:
      subdict = {x: record.values[x] for x in ['local','userid']}
      if subdict not in result:
        result.append(subdict)
  return result



if __name__ == '__main__':
  result = TraceReport("ana", "2020-07-14T00:00:00Z", "2020-07-14T02:00:00Z")
  print (result)