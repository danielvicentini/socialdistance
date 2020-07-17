import sys
import os
#sys.path.append(os.path.abspath('..'))

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config_shared import INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_DBUSER, INFLUXDB_DBPASSWORD, INFLUXDB_DBNAME, INFLUXDB_USER, INFLUXDB_PASSWORD
from config_shared import TABELA_MV, TABELA_TOTAL, TABELA_TRACE
import json


######  MUITO IMPORTANTE: A SER REMOVIDO ##################################
###### Mudando a tabela de Trace para TraceDaniel porque a atual tabela de trace
###### nao tem nenhum dado.  O mesmo foi feito para a tabela de count.
################################################################################
TABELA_TRACE = "TraceDaniel"
TABELA_TOTAL = "RawPeopleCount"


QUERY_TRACE = \
  'targetUser = "%s" \n\
   startTime = %s \n\
   stopTime = %s \n\
   TABELA_TRACE = "%s"  \n\
                        \n\
   t1 = from(bucket:"socialdistance/autogen") \n\
          |> range(start: startTime, stop: stopTime) \n\
          |> filter(fn: (r) => (r._measurement == TABELA_TRACE) and (r._field =~ /(userid)|(state)/)) \n\
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") \n\
          |> drop(columns: ["_start", "_stop", "_measurement"]) \n\
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



QUERY_MAX_OCCUPANCY = \
  'startTime = %s \n\
   TABELA_TOTAL = "%s"  \n\
   TABELA_LOCATION = "%s" \n\
                          \n\
   t1 = from(bucket:"socialdistance/autogen") \
         |> range(start: startTime) \
         |> filter(fn: (r) => (r._measurement == TABELA_TOTAL)) \n\
                                                                \n\
   t2 = from(bucket:"socialdistance/autogen") \
         |> range(start: -1y) \
         |> filter(fn: (r) => (r._measurement == TABELA_LOCATION)) \
         |> last() \
         |> map(fn: (r) => ({location: r.location, max: r._value}))  \n\
                                                                     \n\
   history = join(tables: {count: t1, max: t2}, on:["location"]) \
         |> filter (fn: (r) => (r._value > r.max)) \
         |> map(fn: (r) => ({_time: r._time, location: r.location, count: r._value, max: r.max, origin: r.origin}))  \
         |> yield(name: "history")'


QUERY_BEST_DAY = \
  'import "date" \n\
   startTime = %s \n\
   TABELA_TOTAL = "%s" \n\
                                   \n\
   t1 = from(bucket:"socialdistance/autogen") \
         |> range(start: startTime) \
         |> filter(fn: (r) => (r._measurement == TABELA_TOTAL)) \
         |> window(every: 1h) |> max() \
         |> duplicate(column: "_stop", as: "_time") \
         |> window(every: inf) \
         |> map(fn: (r) => ({r with hour: uint(v: date.hour(t: r._time)),day: uint(v: date.weekDay(t: r._time))})) \
         |> drop(columns: ["_start", "_stop", "_measurement", "origin", "_time"]) \
         |> group(columns: ["location", "hour", "day"]) \
         |> mean() \
         |> yield(name: "t1")'


#---------------------------------------------------------------------------------------
# Trace report
#
# Input:
#    targetUser = userid to be traced
#    startTime = string with initial time for tracing (ex: "2020-07-14T00:00:00Z")
#    stopTime = string with final time for tracing (ex: "2020-07-14T00:00:00Z")
#
# Output: List of dictionaty entries with users that were in contact with targetUser.
#    Dictionary keys:
#    {
#     'local': <local where user was in contact with targetUser>, 
#     'userid': <id of user that was in contact with targerUser>'
#    }
#---------------------------------------------------------------------------------------
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



#---------------------------------------------------------------------------------------
# Distancing report
#
# Input:
#    LocationInventory: Dictionary with location inventory
#    startTime = string with initial time for report (ex: "-1w")
#
# Output: List of dictionaty entries with rooms with higher occupancy than allowed.
#    Dictionary keys:
#    {
#     '_time'   : time that event was detected
#     'location': room where event occurred
#     'count'   : number of people detect at this room at this time
#     'max'     : maximum number allowed in this room
#     'origin'  : indicates how measurement was made
#    }
#---------------------------------------------------------------------------------------
def OccupancyReport(LocationInventory, startTime):

  # Connects to the database
  url = "http://{}:{}".format(INFLUXDB_HOST, INFLUXDB_PORT)     
  client = InfluxDBClient(url=url, token="", org="")

  # Preapre to create a table with maximum occupancy per room 
  TABELA_LOCATION = "LocationInventory"
  write_api = client.write_api(write_options=SYNCHRONOUS)

  #Build a record per local
  record = []
  #location_dict = json.loads(LocationInventory)
  for key, value in LocationInventory["rooms"].items():
    _point = Point(TABELA_LOCATION).tag("location", key).field("occupancy", value)
    record.append(_point)

  # Write to temporary table
  write_api.write(bucket=INFLUXDB_DBNAME, record=record)

  # Build max occupancy query
  query = QUERY_MAX_OCCUPANCY % (startTime, TABELA_TOTAL, TABELA_LOCATION)
  tables = client.query_api().query(query)
  client.__del__()

  # Query result is a list of all tables creted in TRACE_QUERY, each of them of type FluxTable
  # see https://github.com/influxdata/influxdb-client-python/blob/master/influxdb_client/client/flux_table.py#L5 for more info

  # Build result as a list of all found records in history table
  result =[]
  for table in tables:
    for record in table.records:
      subdict = {x: record.values[x] for x in ['_time','location', 'count', 'max', 'origin']}
      result.append(subdict)
  return result




#---------------------------------------------------------------------------------------
# Best day report
#
# Input:
#    startTime = string with initial time for analyzing best day (ex: "2020-07-14T00:00:00Z")
#
# Output: List of dictionaty entries with highest occupancy per location/weekday/hour
#    Dictionary keys:
#    {
#     '_value': maximum occupancy 
#     'day': 0 to 6, indicating week day 
#     'hour': 0 to 23, indicating hour in the day 
#     'location': location identification 
#    }
#---------------------------------------------------------------------------------------
def BestDayReport(startTime):

  # Connects to the database
  url = "http://{}:{}".format(INFLUXDB_HOST, INFLUXDB_PORT)     
  client = InfluxDBClient(url=url, token="", org="")

  # Build trace query
  query = QUERY_BEST_DAY % (startTime, TABELA_TOTAL)
  tables = client.query_api().query(query)
  csv = client.query_api().query_csv(query)
  client.__del__()

  # Query result is a list of all tables creted in TRACE_QUERY, each of them of type FluxTable
  # see https://github.com/influxdata/influxdb-client-python/blob/master/influxdb_client/client/flux_table.py#L5 for more info

  # Build result as a list of all found records in suspecTable
  result =[]
  for table in tables:
    for record in table.records:
      subdict = {x: record.values[x] for x in ['_value','day', 'hour', 'location']}
      result.append(subdict)
  return result



if __name__ == '__main__':

  # Teste do report de trace
  result1 = TraceReport("ana", "2020-07-14T00:00:00Z", "2020-07-14T02:00:00Z")
  print (result1)

  # Teste do report de histórico
  LocationInventory = {
    "rooms": {
        "Cozinhha": 1,
        "EDU": 2,
        "IND": 2,
        "Quartos": 2,
        "Sala": 2,
        "Sandbox": 3
    },
    "versao": 5
  }

  result2 = OccupancyReport(LocationInventory=LocationInventory, startTime="-1y")
  print (result2)


  # Teste do report de best day
  result3 = BestDayReport (startTime="-1y")
  print (result3)