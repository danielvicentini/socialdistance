"""The provided sample code in this repository will reference this file to get the
information needed to connect to your lab backend.  You provide this info here
once and the scripts in this repository will access it as needed by the lab.
Copyright (c) 2019 Cisco and/or its affiliates.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json, requests
import time
import paho.mqtt.client as mqtt
import sys, getopt
import os
from pprint import pprint
from webexteamssdk import WebexTeamsAPI

sys.path.append('/home/mycode/socialdistance/DB')
from DB import *

# Get the absolute path for the directory where this file is located "here"
#here = os.path.abspath(os.path.dirname(__file__))

# Get the absolute path for the project / repository root
#project_root = os.path.abspath(os.path.join(here, ".."))

# Extend the system path to include the project root and import the env files
#sys.path.insert(0, project_root)
#import env_user  # noqa



#Function receives
#Camera SN that is posting on eclipse mqtt
#Time in seconds that the function will report results
#Get detailed reports of just avervage during the report time.

# Camera serial number - DevNet Sandbox
CAMERA_SERIAL = "Q2GV-7HEL-HC6C"
# Home Dev Environment
#CAMERA_SERIAL = "Q2FV-GA8U-S45S"

#By default intervals of count collection = 1 second
#Dont recomend to change it
timestamp_interval_captures = 1

#time in seconds that the function will report results
timestamp_interval_reports = 5

# mqtt setting
MQTT_SERVER = "mqtt.eclipse.org"
MQTT_PORT = 1883
MQTT_TOPIC = "/merakimv/"+ CAMERA_SERIAL + "/0"

camera_results = {}
camera_results["camera_sn" ] = CAMERA_SERIAL
camera_results["counts"] = {}

#start timestamp with counting in zero
ts = time.time()
camera_results["counts"][int(ts)] = 0
print (camera_results)

#List used to calculate average values
count_list = []


def on_connect(client, userdata, flags, rc):
    #Subscribe to MQTT topic
    print("Function On Connect:")
    print("Connected with result code " + str(rc))
    print()
    client.subscribe(MQTT_TOPIC)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode("utf-8"))
    print (payload)
    #Payload raw example
    #{'ts': 1590873673494, 'counts': {'person': 0}}
    ts = payload["ts"]
    #print (ts)
    count = payload["counts"]["person"]
    #print (count)

    #add a new entry in the results dictionary only if count is not 0
    if count > 0:
        camera_results["counts"][ts] = count
    
    publish_results(count, camera_results)


def publish_results(count, camera_results):
    
    #Records the number of times the functions is executed
    publish_results.counter = publish_results.counter + 1
    #print("Iteration #" + str(publish_results.counter))
    
    #each interaction 1 sec interval - defined on timestamp_interval_captures var
    time.sleep(timestamp_interval_captures)
    #print("Dormi {}s".format(timestamp_interval_captures))

    #Add the count value to a list for future average calculation
    count_list.append(count)
    #print(count_list)
    
    #Execution after the configured time for report of the results
    if publish_results.counter == timestamp_interval_reports:
        if count == 0:
            ts = time.time()
            camera_results["counts"][int(ts)] = 0

        #print("Reporting average count interval of {}s".format(timestamp_interval_reports))
        count_average = sum(count_list)/len(count_list)
        camera_results["count_average"] = round(count_average)
        camera_results["count_interval_in_secs"] = timestamp_interval_reports
        #print("Reporting results after interval of {}s".format(timestamp_interval_reports))
        print()
        print ("Results:")
        print (camera_results)
        print()
        results = camera_results
        publish_results.counter = 0

        #posting date on freeboard
        """TODO
        Replace this with a function to post results on database instead
        """
        print(results["count_average"], latest_count)
        print()
        """
        if results["count_average"] == latest_count:
            print("Nothing changed, not updating the DB")
            print()
            latest_count == results["count_average"]
            clear_counters()
        else: write_on_db(results)
        """
        write_on_db(results)

    else:
        #print ("Printing every iteraction:")
        #print (camera_results)
        #print()
        return

def post_data(results):
    url = "https://dweet.io/dweet/for/socialdistance" 
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(results), headers=headers)
    print ("Posting on dweet status {}".format(str(r.status_code)))
    print (json.loads(r.content)["with"]["content"])
    print()

    clear_counters()

def write_on_db(results):
    print("Enteri no write DB")
    print (results)
    #write on DB
    db = DBClient()
        
    device_sn = results["camera_sn"]
    count = results["count_average"]
    print (device_sn, count)
    # Write some data
    db.PeopleCountWrite(device_sn, count)
    #db.PeopleCountWrite("Q2PD-XNUL-RYYQ", 5)
        
    #Get written data
    #result = db.PeopleCountQuery()
    #print()
    #print (result)
    print ("DB updated with {}, {}".format(device_sn, count))
        
    clear_counters()


def clear_counters():
    #print ("Reseting camera_results dict")           
    camera_results["counts"] = {}
    camera_results.pop("count_average")
    camera_results.pop("count_interval_in_secs")
    #print (camera_results)
    #print ("Reseting Count List")           
    count_list.clear()
    #print (count_list)
    #reset counter
    #print ("Resenting Counter to 0")
    wait = 600
    print("Waiting {} seconds..".format(wait))
    print()
    time.sleep(wait)

if __name__ == "__main__":
    
    MQTT_TOPIC = "/merakimv/"+ CAMERA_SERIAL + "/0"
    
    publish_results.counter = 0
    latest_count = 0

    # mqtt
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(MQTT_SERVER, MQTT_PORT, 60)
        client.loop_forever()

    except Exception as ex:
        print("[MQTT]failed to connect or receive msg from mqtt, due to: \n {0}".format(ex))
