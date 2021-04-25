#!/usr/bin/env python3

import asyncio
import websockets
import sys
import json
import deeppavlov

from deeppavlov import configs, train_model
from deeppavlov.core.common.file import read_json
from deeppavlov.core.commands.infer import build_model

#FEEDER_SOCKET_HOST = '127.0.0.1'
#FEEDER_SOCKET_PORT = 9007

connections = set()
model_config = read_json(configs.faq.fasttext_avg_autofaq)
intents = build_model(model_config)


class ActiveSpeaker:
    lastActiveSpeaker = None
    agent_speech = []
    caller_speech = []

async def run_feeding_process(websocket, path):    
    
    if path == '/sub':
        connections.add(websocket)
        print('subscriber #' + str(len(connections)) + ' got connected')
        try:
            async for msg in websocket:
                pass
        except websockets.ConnectionClosed:
                pass
        finally:
            print('subscriptions cancelled')
            connections.clear()            
    elif path == '/pub':        

        async for msg in websocket:
            
            text_feed = json.loads(msg)

            if text_feed['party'] == None:
                ActiveSpeaker.lastActiveSpeaker = None            
            elif text_feed['party'] == 'You' and ActiveSpeaker.lastActiveSpeaker == 'You' and text_feed['split_key'] != 'begin' and text_feed['split_key'] != 'both':
                ActiveSpeaker.agent_speech[len(ActiveSpeaker.agent_speech)-1] += (' ' + (text_feed['text']))
                intent_inference = intents([ActiveSpeaker.agent_speech[len(ActiveSpeaker.agent_speech)-1]])
                print('agent said (non-interrupted): ', ActiveSpeaker.agent_speech[len(ActiveSpeaker.agent_speech)-1])
                print('possible intent: ', intent_inference) 
                try:
                    if text_feed['split_key'] == 'end':
                        ActiveSpeaker.lastActiveSpeaker = None
                except KeyError:
                    pass                               
            elif text_feed['party'] == 'You' and (ActiveSpeaker.lastActiveSpeaker != 'You' or text_feed['split_key'] == 'begin' or text_feed['split_key'] == 'both'):
                ActiveSpeaker.agent_speech.append(text_feed['text'])  
                intent_inference = intents([ActiveSpeaker.agent_speech[len(ActiveSpeaker.agent_speech)-1]])
                print('agent said (responding to caller\'s latest words): ', ActiveSpeaker.agent_speech[len(ActiveSpeaker.agent_speech)-1])
                print('possible intent: ', intent_inference)  
                ActiveSpeaker.lastActiveSpeaker = 'You'
                try:
                    if text_feed['split_key'] == 'end':
                        ActiveSpeaker.lastActiveSpeaker = None
                except KeyError:
                    pass        
            elif text_feed['party'] == 'Caller' and ActiveSpeaker.lastActiveSpeaker == 'Caller' and text_feed['split_key'] != 'begin' and text_feed['split_key'] != 'both':
                ActiveSpeaker.caller_speech[len(ActiveSpeaker.caller_speech)-1] += (' ' + (text_feed['text']))
                try:
                    if text_feed['split_key'] == 'end':
                        ActiveSpeaker.lastActiveSpeaker = None
                except KeyError:
                    pass         
            else:                
                ActiveSpeaker.caller_speech.append(text_feed['text']) 
                ActiveSpeaker.lastActiveSpeaker = 'Caller'
                try:
                    if text_feed['split_key'] == 'end':
                        ActiveSpeaker.lastActiveSpeaker = None
                except KeyError:
                    pass  

            if '(hangup)' in text_feed['text']:
                ActiveSpeaker.lastActiveSpeaker = ''
                ActiveSpeaker.caller_speech = []
                ActiveSpeaker.agent_speech = []     
            
            #print('current item:', text_feed)

            for conn in connections:
                asyncio.ensure_future(conn.send(json.dumps(text_feed)))

def main():

    ws_config_joined = sys.argv[1]
    ws_config_divided = ws_config_joined.split(':') 
    
    FEEDER_SOCKET_HOST = ws_config_divided[0]
    FEEDER_SOCKET_PORT = ws_config_divided[1]    

    text_feed_service = websockets.serve(run_feeding_process, FEEDER_SOCKET_HOST, FEEDER_SOCKET_PORT)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(text_feed_service)
    loop.run_forever()

if __name__ == "__main__":    
    main() 