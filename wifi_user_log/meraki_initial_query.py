#!/usr/local/bin/python3.7

import wifi_sensor_settings
import meraki

API_KEY = wifi_sensor_settings.MERAKI_API_KEY
NET_ID = wifi_sensor_settings.MERAKI_NET_ID
BASE_URL = "https://api.meraki.com/api/v0/"

def devices():
    dashboard = meraki.DashboardAPI(api_key=API_KEY, base_url=BASE_URL,print_console=False)
    devices = dashboard.devices.getNetworkDevices(NET_ID)
    return devices

def main ():
    print(devices())

if(__name__ == "__main__"):
    main ()
	#starting the dict logs and wifi_count list
