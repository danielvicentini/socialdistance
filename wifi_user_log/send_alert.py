import user_settings
from pprint import pprint
import json
import requests

def send_alert():
	
	if 2 > int(user_settings.PEOPLE_LIMIT):

		url = "https://webexapis.com/v1/messages"
		
		message = "The max number of users in the room XYZ has reached its limits"
		payload = {"text": message, "roomId": user_settings.WT_ROOM_ID}

		headers = {
			'Authorization': 'Bearer ' + user_settings.WT_ACCESS_TOKEN,
			'Content-Type': 'application/json'
		}

		response = requests.request(
			"POST", 
			url, 
			headers=headers, 
			json = payload
		)

		print(response.text.encode('utf8'))

def main ():
    try:
		with open('wifi_count.log') as f:
			while True:
				#
	except (IOError, SystemExit):
		raise
	except KeyboardInterrupt:
		print ("Crtl+C Pressed. Shutting down.")

if __name__ == '__main__':
    main()