# Admins Session
#---------------------------------------------------------
# Webex Room for admins
admins_room="Distanciamento Piloto"
# Admin list
admins="admin1@domain.com,admin2@admin.com"

# Webex Teams Session
#--------------------------------------------------------
# Webex Bot parameters
bot_webhook="http://address"
bot_token="your bot token"
bot_email="botuser@botdomain.com"
bot_tag='distancebot'

# Meraki Session
#=-------------------------------------------------------
# Meraki Parameters
MERAKI_API_KEY ="Meraki KEY here"
MERAKI_ORG_ID = "<ORD_ID HERE>"
MERAKI_NET_ID = "<NET ID HERE>"


# Servers Session
# influx address
#=-------------------------------------------------------
public_ip=[YOUR PUBLIC IP HERE]
db_server=public_ip
db_server_port=8086
# report code API address
report_server=public_ip
report_server_port=8000
# mask detection API Address
mask_server=public_ip
mask_server_port=10000
# Webex Teams Bot Address
bot_server=public_ip
bot_server_port=7000
# Grafana Dashboard Address
grafana_server=public_ip
grafana_server_port=3000
# Trigger Address
trigger_server=public_ip
trigger_server_port=8080

# BD Session
#--------------------------------------------------------
# BD Variables
INFLUXDB_HOST = db_server
INFLUXDB_PORT = 8086
INFLUXDB_USER = '<superuser>'
INFLUXDB_PASSWORD = '<superpassword>'
INFLUXDB_DBNAME = 'socialdistance'
INFLUXDB_DBUSER = '<user>'
INFLUXDB_DBPASSWORD = '<password>'
TABELA_TRACE="TracePeople"
TABELA_MV="MaskEvents"
TABELA_TOTAL="TotalCount"
