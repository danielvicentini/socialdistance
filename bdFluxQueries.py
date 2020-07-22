import sys
import os
#sys.path.append(os.path.abspath('..'))

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from influxdb_client import InfluxDBClient as IF, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config_shared import INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_DBUSER, INFLUXDB_DBPASSWORD, INFLUXDB_DBNAME, INFLUXDB_USER, INFLUXDB_PASSWORD
from config_shared import TABELA_MV, TABELA_TOTAL, TABELA_TRACE
import json
import pandas as pd


######  MUITO IMPORTANTE: A SER REMOVIDO ##################################
###### Mudando a tabela de Trace para TraceDaniel porque a atual tabela de trace
###### nao tem nenhum dado.  O mesmo foi feito para a tabela de count.
################################################################################


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
  'import "date" \n\
   startTime = %s \n\
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
   t3 = join(tables: {count: t1, max: t2}, on:["location"]) \
         |> filter (fn: (r) => (r._value > r.max)) \
         |> map(fn: (r) => ({_time: r._time, location: r.location, _field: r._field, _value: r._value, max: r.max})) \n\
                                                                                                                    \n\
   t4 = t3 |> window(every: 1h) |> max() \
         |> duplicate(column: "_start", as: "_time") \
         |> window(every: inf) \
         |> map(fn: (r) => ({r with year: uint(v: date.year(t: r._time)), \
                                    month: uint(v: date.month(t: r._time)), \
                                    day: uint(v: date.monthDay(t: r._time)), \
                                    hour: uint(v: date.hour(t: r._time))})) \
         |> map(fn: (r) => ({r with shift: if (r.hour <=5) then "dawn" else \
                                           if (r.hour <=12) then "morning" else \
                                           if (r.hour <=19) then "afternoon" else "night"})) \
         |> drop(columns: ["_start", "_stop", "_time", "_measurement"])  \n\
                              \n\
   historyHour = t4 \
         |> group(columns: ["location", "year", "month", "day", "hour"]) \
         |> max() \
         |> yield(name: "historyHour")\n\
                              \n\
   historyShift = t4 \
         |> group(columns: ["location", "year", "month", "day", "shift"]) \
         |> max() \
         |> yield(name: "historyShift")'


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
  client = IF(url=url, token="", org="")

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
# Output: Dictionary with history list per location/day/hour and per location/day/shift.
#    Dictionaty format:
#
#    {'PerHourHistory': [<list of occurrences per location/day/hour>],
#     'PerShiftHistory': [<list of occurrence per location/day/shift]}
#
#    Example:
#
#    {'PerHourHistory': 
#       [{'location': 'Sala', '_value': 3, 'max': 2, 'year': 2020, 'month': 6, 'day': 17, 'hour': 11},  
#        ...], 
#     'PerShiftHistory': 
#       [{'location': 'Sala', '_value': 3, 'max': 2, 'year': 2020, 'month': 6, 'day': 17, 'shift': 'afternoon'}, 
#        ...] }
#
#     PS:
#     'location': room where event occurred
#     '_value'  : maximum number of people detect at this room at this date/hour or date/shift
#     'max'     : maximum number of peopple allowed in this room
#     'year', 'month', 'day': date that event was detected
#     'hour'    : hour on which event occurred
#     'shift'   : shift on which event occurred (dawn, morning, afternnon ou night)
#
#---------------------------------------------------------------------------------------
def OccupancyReport(LocationInventory, startTime):

  # Connects to the database
  url = "http://{}:{}".format(INFLUXDB_HOST, INFLUXDB_PORT)     
  client = IF(url=url, token="", org="")

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
  result = {"PerHourHistory" :[], "PerShiftHistory": []}
  for table in tables:
    for record in table.records:
      if  (record.values['result'] == 'historyHour'): 
        subdict = {x: record.values[x] for x in ['location', '_value', 'max', 'year', 'month', 'day', 'hour']}
        result["PerHourHistory"].append(subdict)
      elif  (record.values['result'] == 'historyShift'): 
        subdict = {x: record.values[x] for x in ['location', '_value', 'max', 'year', 'month', 'day', 'shift']}
        result["PerShiftHistory"].append(subdict)
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
#
#---------------------------------------------------------------------------------------
def BestDayReport(startTime):

  # Connects to the database
  url = "http://{}:{}".format(INFLUXDB_HOST, INFLUXDB_PORT)     
  client = IF(url=url, token="", org="")

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




#---------------------------------------------------------------------------------------
# Best day 
#
# Description:
# Parse BestDayReport output in order to infer which are the best days 
#
# Input:
#    report = output of BestDayReport
#    hour1, hour2 = begin and end of time rang of interest (ex: 9,12)
#
# Output: List of dictionaty entries with information for each location
#    Dictionary keys:
#    {
#     'location': id of location 
#     'bestday': list of best days to work considering the provided time range in this location
#     'report': average of maximum allocation for each day in this location considering the provided time range
#    }
#
# Example:
#   [{'location': 'Cozinha', 
#     'bestday': ['Mo', 'Tu'], 
#     'report': {'Mo': 0.0, 'Tu': 0.0, 'We': 2.5, 'Th': 2.0, 'Fr': 1.0}
#    },
#    ...]
#---------------------------------------------------------------------------------------
def BestDay (report, hour1, hour2):
  # Convert report from a list of dictionaries to a Panda Data Frame
  df = pd.DataFrame(report)

  # Select only the rows which hours are in the provided range
  df = df.loc[df['hour'].isin(range(hour1,hour2+1))]

  #Exclude 'hour' column
  df = df[df.columns.difference(['hour'])]

  # Group by location/day, selecting the maximum count epr location/day
  df = df.groupby(['location','day']).agg({'_value': ['max']})
  df.columns=['max']
  df = df.reset_index()

  # Create an auxiliar dataframe with days 1 to 5 (Mon to Fri) fro each existing location
  data = []
  weekdays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
  for location in df.location.unique():
    for day in range(1,6):
      data.append({'location': location, 'day': day, 'weekday':weekdays[day]})
  days = pd.DataFrame(data)

  # Merge result with this auxiliar dataframe so that there is a row for all location/weekday  
  df = df.merge(how='right', right=days, on=['location', 'day'])

  # Fill all NA (not available) values with 0
  df = df.fillna(value=0)

  # Sort result by location/max/day
  df = df.sort_values(['location', 'day'])

  #Build best day dictionary per location
  result = []
  for location in df.location.unique():  # For each unique location
    #select only rows of this location
    df1 = df.loc[df['location'] == location] 
    #build a dataframe withh maximum avarage occupancy per weekday
    max = df1['max']
    max.index=df1['weekday'] 
    #obtem a menor média de ocupação dessa localidade
    min_occupancy = min(max.tolist())
    #build dictionary entry for this location
    dict = {}  #initialize dict as a dictionary
    dict['location'] = location  
    df2 = df1.reset_index()
    dict['bestday'] = df2.loc[df2['max'] == min_occupancy]['weekday'].tolist()
    dict['report'] = max.to_dict()    
    result.append(dict)

  return(result)




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
  result4 = BestDay (result3, 9, 12)
  print(result4)