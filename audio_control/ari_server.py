import logging
import asyncio
import websockets
import json
import time
import sys

from asyncio import CancelledError
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from pydub import AudioSegment, silence 

from .ari_stasis import ConnectionWizard

#ASR_SOCKET_ADDRESS = 'ws://127.0.0.1:2700'
#FEEDER_SOCKET_ADDRESS = 'ws://127.0.0.1:9007/pub'
#MAX_BUFFER_SIZE = 240000


class Transcriber:

    def __init__(self, ws_address):
        self.queue_in = asyncio.Queue()
        self.queue_out = asyncio.Queue()
        self.buffer_in = b''
        self.buffer_out = b''
        self.prev_record_size = 0
        self.current_record_size = 0
        self.total_payload = 0
        self.record_file_name_in = None
        self.record_file_name_out = None
        self.recognition_source_in = 0
        self.recognition_source_out = 0
        self.transcript_data = {}
        self.buffer_limit = 144000
        self.asr_socket_address = 'ws://127.0.0.1:2700'
        self.feeder_socket_address = ws_address
        
           
    async def produce_chunks(self, record_file_name):
        #with open(record_file_name, 'rb') as record:
            self.record_file_name_in = record_file_name + '-in.wav'            
            self.record_file_name_out = record_file_name + '-out.wav'            
            self.current_record_size = self.get_current_record_size()
            
            with open(self.record_file_name_out, 'rb') as record_out:                             
                with open(self.record_file_name_in, 'rb') as record_in:               
                    while True:                                              
                        await asyncio.sleep(0.1)                        
                        chunk_out = record_out.read(16000)                        
                        chunk_in = record_in.read(16000)
                        self.queue_out.put_nowait(chunk_out)                         
                        self.queue_in.put_nowait(chunk_in)

                                
    async def consume_chunks(self):
        
        while True:
             
            data_out = await self.queue_out.get()
            data_in = await self.queue_in.get()            
            await asyncio.sleep(0.1)
         
            self.buffer_out += data_out
            self.buffer_in += data_in
            self.current_record_size = self.get_current_record_size()
     
            #print('current: ', self.current_record_size)
            #print('prev: ', self.prev_record_size)
            #print('total: ', self.total_payload)
            
            if len(self.buffer_out) >= self.buffer_limit:                  
                self.recognition_source_in = self.buffer_in 
                self.recognition_source_out = self.buffer_out 
                earlierSpeakingParty = self.compareSpeechPeriods(self.recognition_source_in, self.recognition_source_out)                  
                asyncio.ensure_future(self.exec_recognition_task(earlierSpeakingParty, False))                               
                self.total_payload += len(data_out)
                self.buffer_out = b''               
                self.buffer_in = b''
            elif self.current_record_size == self.total_payload and self.current_record_size == self.prev_record_size:
                print('end of call recording\n')
                #self.recognition_source_out = self.buffer_out
                await self.exec_recognition_task(2, True)
                self.buffer_out = b''
                self.buffer_in = b''
                               
                for i in range(self.queue_in.qsize()):
                    self.queue_in.get_nowait()
                for j in range(self.queue_in._unfinished_tasks):
                    self.queue_in.task_done()

                for i in range(self.queue_out.qsize()):
                    self.queue_out.get_nowait()
                for j in range(self.queue_out._unfinished_tasks):
                    self.queue_out.task_done()                
            
                print('recognition service is on wait for a next call response\n')
                self.total_payload = 0
                self.prev_record_size = 0                
                raise Exception('forcing event loop to go asleep for a while')
            elif self.current_record_size == self.total_payload and self.current_record_size != self.prev_record_size:
                self.prev_record_size = self.current_record_size
                await asyncio.sleep(2)                
            else:
                self.total_payload += len(data_out)                

    
    async def exec_recognition_task(self, party, hangupFlag):       

        async with websockets.connect(self.asr_socket_address) as ws:

            if hangupFlag:
                self.transcript_data['party'] = 'You'
                self.transcript_data['text'] = ' (hangup)'
                asyncio.ensure_future(self.publish_new_feed(json.dumps(self.transcript_data)))
                return

            if party == 0:     
                self.transcript_data['party'] = None
                asyncio.ensure_future(self.publish_new_feed(json.dumps(self.transcript_data))) 

            elif party[0] == 1 or party[0] == 3:
                await ws.send(self.recognition_source_in)                                     
                response = await ws.recv()
                try:
                    result = json.loads(response)['partial']
                except KeyError:                        
                    result = json.loads(response)['text'] 
                
                self.transcript_data['party'] = 'Caller'    
                self.transcript_data['text'] = result

                if party[1][0] >= 3 and party[1][1] <= 6:
                    self.transcript_data['split_key'] = 'both'
                elif party[1][0] >= 3:
                    self.transcript_data['split_key'] = 'begin'
                elif party[1][1] <= 6:
                    self.transcript_data['split_key'] = 'end' 
                else:
                    self.transcript_data['split_key'] = None          

                print(self.transcript_data['party'] + ' said: ' + self.transcript_data['text'])
                asyncio.ensure_future(self.publish_new_feed(json.dumps(self.transcript_data)))            
                if party[0] == 3:
                    await ws.send(self.recognition_source_out)                                     
                    response = await ws.recv()
                    try:
                        result = json.loads(response)['partial']
                    except KeyError:                        
                        result = json.loads(response)['text'] 
                    
                    self.transcript_data['party'] = 'You'    
                    self.transcript_data['text'] = result

                    print(self.transcript_data['party'] + ' said: ' + self.transcript_data['text'])
                    asyncio.ensure_future(self.publish_new_feed(json.dumps(self.transcript_data)))
            else:                
                await ws.send(self.recognition_source_out)                                     
                response = await ws.recv()
                try:
                    result = json.loads(response)['partial']
                except KeyError:                        
                    result = json.loads(response)['text']

                self.transcript_data['party'] = 'You'    
                self.transcript_data['text'] = result

                if party[1][0] >= 3 and party[1][1] <= 6:
                    self.transcript_data['split_key'] = 'both'
                elif party[1][0] >= 3:
                    self.transcript_data['split_key'] = 'begin'
                elif party[1][1] <= 6:
                    self.transcript_data['split_key'] = 'end'
                else:
                    self.transcript_data['split_key'] = None    

                print(self.transcript_data['party'] + ' said: ' + self.transcript_data['text'])
                asyncio.ensure_future(self.publish_new_feed(json.dumps(self.transcript_data)))
                if party == 4:
                    await ws.send(self.recognition_source_in)                                     
                    response = await ws.recv()
                    try:
                        result = json.loads(response)['partial']
                    except KeyError:                        
                        result = json.loads(response)['text'] 

                    self.transcript_data['party'] = 'Caller'    
                    self.transcript_data['text'] = result

                    print(self.transcript_data['party'] + ' said: ' + self.transcript_data['text'])
                    asyncio.ensure_future(self.publish_new_feed(json.dumps(self.transcript_data)))
                    
            #print('asr outputs:', response)
            #response = json.loads(await aws.recv())
            #result = ''
            #result = ''                    
            #response = json.loads(await ws.recv())
            #msg = json.dumps(response)
            #await ws.send(msg)
            '''
            try:
                result = json.loads(response)['partial']
            except KeyError:                        
                result = json.loads(response)['text']                

            if len(result) == 0:
                result += ' '
            if hangupFlag:
                result += ' (hangup)'
            self.transcript_data['text'] = result
            #self.transcript_data['text'] = response
            if party == 'you':
                print('you: ', self.transcript_data['text'])
            else:
                print('caller: ', self.transcript_data['text'])    
            #asyncio.ensure_future(self.publish_new_feed(json.dumps(self.transcript_data)))
            '''                        

    async def publish_new_feed(self, data):
        async with websockets.connect(self.feeder_socket_address) as ws:
            await ws.send(data)    
    
    def get_current_record_size(self):
        return Path(self.record_file_name_out).stat().st_size

    def compareSpeechPeriods(self, source_in, source_out):
        segment_in = AudioSegment(data=source_in, sample_width=2, frame_rate=8000, channels=1)
        segment_out = AudioSegment(data=source_out, sample_width=2, frame_rate=8000, channels=1)
        
        speech_period_in = silence.detect_nonsilent(segment_in, min_silence_len=1000, silence_thresh=-32)
        speech_period_out = silence.detect_nonsilent(segment_out, min_silence_len=1000, silence_thresh=-32)
        
        #print('period in: ', speech_period_in)
        #print('period out: ', speech_period_out)

        if len(speech_period_out) == 0 and len(speech_period_in) == 0:
            return 0
        elif len(speech_period_out) == 0 and len(speech_period_in) > 0:
            voiceEdgePoints = [speech_period_in[0][0], speech_period_in[len(speech_period_in)-1][1]]  
            return (1, voiceEdgePoints)
        elif len(speech_period_in) == 0 and len(speech_period_out) > 0:
            voiceEdgePoints = [speech_period_out[0][0], speech_period_out[len(speech_period_out)-1][1]] 
            return (2, voiceEdgePoints)
        elif speech_period_in[0][0] <= speech_period_out[0][0]:
            if speech_period_out[len(speech_period_out)-1][1] >= speech_period_in[len(speech_period_in)-1][1]:
                voiceEdgePoint = speech_period_out[len(speech_period_out)-1][1] 
            else:
                voiceEdgePoint = speech_period_in[len(speech_period_in)-1][1]
            voiceEdgePoints = [speech_period_in[0][0], voiceEdgePoint]
            return (3, voiceEdgePoints) 
        elif speech_period_in[0][0] > speech_period_out[0][0]:
            if speech_period_out[len(speech_period_out)-1][1] >= speech_period_in[len(speech_period_in)-1][1]:
                voiceEdgePoint = speech_period_out[len(speech_period_out)-1][1]  
            else:
                voiceEdgePoint = speech_period_in[len(speech_period_in)-1][1]
            voiceEdgePoints = [speech_period_out[0][0], voiceEdgePoint]
            return (4, voiceEdgePoints)                   

    '''
    async def pick_silence_segments(self):
        #print('point 202')
        #with open('/tmp/dub.wav', 'wb') as record_out:  
        #record = AudioSegment.from_wav(BytesIO(buffer))
        #print('point 204')  
        #record_out.write(buffer)
        #bs = io.BytesIO(buffer)
        #print('point 204')  
        
        fluff = AudioSegment(data=self.buffer_out, sample_width=2, frame_rate=8000, channels=1)
        #.export('/tmp/ddub.wav', format='wav')
        #, sample_width=2, frame_rate=4000, channels=1
        #print('point 224')
        #seg = AudioSegment.from_wav(self.record_file_name_out)
        segments = asyncio.ensure_future(self.detect_voice_activity(fluff)) 
        
        #silence.detect_nonsilent(fluff, min_silence_len=1000, silence_thresh=-32)
        #print('point 205')  
        #silence_ranges = [((begin/1000), (end/1000)) for begin, end in segments]
        #print(silence_ranges)


        if len(await segments) > 0:
                #print('point 12')  
                #self.recognition_input = self.buffer_out 
                #print('point 14')
                asyncio.ensure_future(self.exec_recognition_task(self.buffer_out, False))
                #self.total_payload += len(data_out)
                self.buffer_out = b''
            #else:
                #print('point 15')  
                #self.total_payload += len(data_out)        
        #return []   
        # 
    async def detect_voice_activity(self, data):
        segments = silence.detect_nonsilent(data, min_silence_len=1000, silence_thresh=-32)
        silence_ranges = [((begin/1000), (end/1000)) for begin, end in segments]
        print(silence_ranges)
        return segments
    '''    


def main():

    stasis_call_id = sys.argv[1]
    monitor_file_name = sys.argv[2]
    ws_address = 'ws://' + sys.argv[3] + '/pub'
    connection = ConnectionWizard(stasis_call_id)
    transcriber = Transcriber(ws_address)    
    
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('asyncio').setLevel(logging.ERROR)
    logging.getLogger('asyncio.coroutines').setLevel(logging.ERROR)
    logging.getLogger('websockets.server').setLevel(logging.ERROR)
    logging.getLogger('websockets.client').setLevel(logging.ERROR)
    logging.getLogger('websockets.protocol').setLevel(logging.ERROR)

    loop = asyncio.get_event_loop() 
    executor = ThreadPoolExecutor(2)   
    loop.run_in_executor(executor, connection.start_connection)
    
    while True:

            #monitor_file_name = '/var/spool/asterisk/monitor/discord.wav' if connection.dialed_extension == '101' else None
            #monitor_file_name = '/var/spool/asterisk/monitor/ext1000.wav' if connection.dialed_extension == '101' else None
        
                
        #if not os.path.exists(record_file_name):
         #   file = open(record_file_name, 'x')
        #file_name_specified.set()
        #current_file_size = get_record_size_info(record_file_name)
        #if current_file_size != transcriber._full_record_size:

            #if is_sigterm_raised:
            #    print('forcing process to finish since SIGTERM received')
            #    break 
                        
            if monitor_file_name is not None and connection.dialed_extension is not None:  
                
                
                time.sleep(2)
                                   
                #prod_task = loop.create_task(transcriber.produce_chunks(transcriber.queue, monitor_file_name))
                #consum_task = loop.create_task(transcriber.consume_chunks(transcriber.queue))           
                prod_task = loop.create_task(transcriber.produce_chunks(monitor_file_name))
                consum_task = loop.create_task(transcriber.consume_chunks())
                tasks = [prod_task, consum_task]
                #tasks = [asyncio.async(transcriber.start(transcriber._queue)), asyncio.async(transcriber._transcribe(transcriber._queue))] 
                #tasks = [loop.create_task(transcriber.start(transcriber._queue)), loop.create_task(transcriber._transcribe(transcriber._queue))]
                          
                executed, remaining = loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)) 
                logging.debug('Tasks completed: %s', executed)
                logging.debug('Tasks in progress: %s', remaining)

                for task in remaining:
                    logging.info('Aborting task %s: %s', task, task.cancel())
                try:
                    loop.run_until_complete(asyncio.gather(*remaining))
                except CancelledError:
                    for running_task in remaining:
                        logging.debug('Task aborted %s: %s', running_task, running_task.cancelled())
                print('cleared queue_in size (outside): ', transcriber.queue_in.qsize())
                print('cleared queue_out size (outside): ', transcriber.queue_out.qsize())
                connection.dialed_extension = None          
            else:
                time.sleep(2.5)     
    
    loop.stop()
    print('event loop execution stopped')
    loop.close()
    print('exited event loop')