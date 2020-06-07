"""TimeSeries DataBase Class."""

from influxdb import InfluxDBClient
import DBconst as db
import json

class DBClient():
  """
  This class allows to instantiate a handler for the SocialDistance InfluxDB database.
  When a object is instantitated, connection to the database is opened.
  """
  def __init__(self):

    # Connects to the database
    self._host = db.INFLUXDB_HOST
    self._port = db.INFLUXDB_PORT
    self._user = db.INFLUXDB_USER
    self._password = db.INFLUXDB_PASSWORD
    self._dbname = db.INFLUXDB_DBNAME      
    self._client = InfluxDBClient(self._host, self._port, self._user, self._password, self._dbname)


  def PeopleCountWrite(self, location: str, origin: str, count: int):
      """
      Write a PeopleCount point in the SocialDistance InfluxDB database.

      The following parameters are expected to instantiate a PeopleCount object:

      :param location: Location associated to this count. Type=string. Valid values TBD.
      :param origin: How this measurement was obtained. Type=string. Valid values TBD.
      :count: QUantity of people detected in this location. Type = integer.
      """

      # Prepare JSON with data to be writte in PeopleCount measurement
      json_body = {}
      json_body["measurement"] = db.MSRMT_RAWPEOPLECOUNT
      json_body["tags"] = {}
      json_body["tags"]["location"] = location
      json_body["tags"]["origin"] = origin
      json_body["fields"] = {}
      json_body["fields"]["count"] = count

      # Write data to InfluxDB
      self._client.write_points([json_body])

  def PeopleCountQuery(self, queryFilter=None):
    """
    Query PeopleCount. A filter may be specificified to be used in the WHERE clause.
    """

    # Prepare JSON with data to be writte in PeopleCount measurement
    query = 'SELECT * from ' + db.MSRMT_RAWPEOPLECOUNT
    if queryFilter is not None:
      query = query + " WHERE " + queryFilter
    
    # Query data from InfluxDB
    result = self._client.query(query)
    return result

