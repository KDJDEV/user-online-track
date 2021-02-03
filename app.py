
import requests, time, asyncio, threading
import thisrobloxapi as robloxapi
from datetime import datetime
import os
from os import environ
cookie = environ['cookie']
client = robloxapi.Client(cookie)
webhook_url = environ['webhook']
user_id = environ['userid']

def sendMessage(message):
	print(message)
	Message = {
    "content": message
	}
	requests.post(webhook_url, data=Message)

async def StartTrack():
    
        start_timestamp = time.time()
        start_datetime = datetime.now()
        r = await client.get_user_presense(user_id)
        json = r.json()
        
        presense = json['userPresences'][0]['userPresenceType']
        game = json['userPresences'][0]['lastLocation']
        
        if presense == 2:
        	sendMessage(f'Joined game: {game} at {str(start_datetime.hour).zfill(2)}:{str(start_datetime.minute).zfill(2)}')
        	while True:
        		time.sleep(5)
        		r = await client.get_user_presense(user_id)
        		json = r.json()
        		presense = json['userPresences'][0]['userPresenceType']
        		if presense != 2:
        			end_timestamp = time.time()
        			end_datetime = datetime.now()
        			sendMessage(f"Left game: Played {game} from {str(start_datetime.hour).zfill(2)}:{str(start_datetime.minute).zfill(2)} to {str(end_datetime.hour).zfill(2)}:{str(end_datetime.minute).zfill(2)}")
        			break


        

async def start():
    while True:
        await StartTrack()
        time.sleep(5)

asyncio.run(start())





