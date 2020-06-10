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


"""
Defintion of measurements currently supported at the SocialDistance DB

General instruction:
When creating a new measurement to the DB, please add an ALIAS for this measurement and
refer to it by this alias (instead of the using an string directly).
"""
MSRMT_RAWPEOPLECOUNT = "RawPeopleCount"