"""
This is a Discord bot for getting NFT sales from OpenSean and posting
the results to Discord. It's very simple to start, but the goal is to 
make this a full social automation bot with what's happening on a
collection of NFTs.

Copyright (C) 2021 John Anthony Mugavero
"""

import os
import requests
import json
import env_vars

from apscheduler.schedulers.blocking import BlockingScheduler

#OpenSea API URLs - https://docs.opensea.io/reference/api-overview
event_url = "https://api.opensea.io/api/v1/events"
asset_url = "https://api.opensea.io/api/v1/assets"

#Load environment variables from env_vars.py
api_key = env_vars.OPENSEA_API_KEY
contract_addr = env_vars.OPENSEA_CONTRACT_ADDRESS
collection = env_vars.OPENSEA_COLLECTION
discord_webhook = env_vars.DISCORD_WEBHOOK

#Global for tracking Panda count. Not elegant.
last_panda_number = 0

def get_opensea_sales():

    # TODO: Add logging to everything.
    # TODO: Break out functions for calling Discord.
    # TODO: Add pricing bot for ARA.
    # TODO: Add twitter integration / auto posting updates to other social networks.
    # TODO: Add more events on Panda transfers, auctions, etc. from OpenSea.
    # TODO: Change prints to logs.
    # TODO: Add analytics capabilities?

    global last_panda_number
        
    try:
        
        #Set headers
        headers = {"Accept": "application/json"}
                
        #Get latest asset from OpenSea - https://docs.opensea.io/reference/api-overview
        assets_querystring = {"order_direction": "desc", "offset": "0", "limit": "1", "collection": collection}
        assets_response = requests.request("GET", asset_url, headers=headers, params=assets_querystring)
        assets_data = assets_response.json()
        
        
        #Event responses. Commented out because it doesn't provide full data
        #on lazy minted items from a collection. Revisit.
        #
        #events_querystring = {'event_type': 'successful', 'asset_contract_address': contract_addr, 'occurred_after': '2021-08-18T00:00:00.000Z', 'X-API-KEY': api_key}    
        #events_response = requests.request("GET", event_url, headers=headers, params=events_querystring)
        #events_data = events_response.json()
        #print(events_data)
        
        print("---------------")        
        print("Latest Panda ID: " + assets_data['assets'][0]['token_id'])
        
        token_id = int(assets_data['assets'][0]['token_id'])
                
        if token_id > last_panda_number:
        
            last_panda_number = token_id
                        
            #Create a post to Discord
            #For all params check https://discordapp.com/developers/docs/resources/webhook#execute-webhook
            data = {
                "content" : "A new Rad Panda was adopted!",
                "username" : "Panda-Adoption-Alert"
            }
           
            #For all params check https://discordapp.com/developers/docs/resources/channel#embed-object
            data["embeds"] = [
                {
                    "title" : "Panda " + assets_data['assets'][0]['token_id'],
                    "url" : assets_data['assets'][0]['permalink'],
                    "image" : {"url": assets_data['assets'][0]['image_original_url'] }
                }
            ]
            
            #Send post to Discord channel
            result = requests.post(discord_webhook, json = data)

            try:
                result.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)
            else:
                print("Payload delivered successfully to Discord, code {}.".format(result.status_code))
                        
        else:
            print("No new pandas adopted.")
        
    except Exception as e:
        print(e)
    
# TODO: Add a ping / uptime capability so we can see on a dashboard somewhere.
scheduler = BlockingScheduler()
scheduler.add_job(get_opensea_sales, 'interval', seconds=30)
scheduler.start()