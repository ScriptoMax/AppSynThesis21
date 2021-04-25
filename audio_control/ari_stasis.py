# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid
import requests 
import ari
import logging
import sys
import signal

from contextlib import contextmanager
from functools import partial

from . import ARI_URL, ARI_USERNAME, ARI_PASSWORD

logging.basicConfig(level=logging.DEBUG)
#record_file_name = '/var/spool/asterisk/monitor/discord.wav'
#ARI_URL = 'http://127.0.0.1:8088'
#ARI_USERNAME = 'demo'
#ARI_PASSWORD = '2b34c141-0ca9-44a7-95ca-570302f069c0'
#APPLICATION = 'stt'


class ConnectionWizard:

    def __init__(self, stasis_control_id):
        self.client = ari.connect(
            base_url=ARI_URL,
            username=ARI_USERNAME,
            password=ARI_PASSWORD,
        )
        self.bridge_id = str(uuid.uuid4())
        self.stt_session_label = stasis_control_id
        self.dialed_extension = None
        self.bridge = None
        signal.signal(signal.SIGTERM, self.apply_bridge_destructor)       


    @contextmanager
    def application_bridge(self, client):
        logging.debug('Building up bridge to mix up multiple channels...')
        self.bridge = self.client.bridges.createWithId(
            bridgeId=self.bridge_id,
            name=self.bridge_id,
            type='mixing',
        )
        try:
            yield self.bridge
    #finally:
        #try:
        #    logging.debug('Destroying our bridge')
        #    client.bridges.destroy(bridgeId=BRIDGE_ID)
        except:
            pass


    def safe_hangup(self, channel):
        """Safely hang up the specified channel"""
        try:
            channel.hangup()
            print ("Hung up {}".format(channel.json.get('name')))
        except requests.HTTPError as e:
            if e.response.status_code != requests.codes.not_found:
                raise e


    def safe_bridge_destroy(self, bridge):
        """Safely destroy the specified bridge"""
        try:
            bridge.destroy()
        except requests.HTTPError as e:
            if e.response.status_code != requests.codes.not_found:
                raise e

    def apply_bridge_destructor(self, signum, frame):
        self.safe_bridge_destroy(self.bridge)
        self.client.close()

    def stasis_start_cb(self, channel_obj, ev, bridge):
        """Handler for StasisStart"""        
        logging.debug('%s', ev)
        #channel_obj['channel'].answer()
        #channel_id = ev['channel']['id']
        #bridge.addChannel(channel=channel_id)
        
        channel = channel_obj.get('channel')
        channel_name = channel.json.get('name')
        channel_id = ev['channel']['id']
        self.dialed_extension = ev['channel']['dialplan']['exten']
        #dialplan = ev.get('channel')['dialplan']
        #exten = 'SIP/' + dialplan['exten']
        #exten = 'SIP/101'
        #args = ['inbound', exten]
        args = ev.get('args')
        bridge.addChannel(channel=channel_id)

        if not args:
            print ("Error: {} didn't provide any arguments".format(channel_name))
            return

        if args and args[0] != 'inbound':
            # Only handle inbound channels here
            return

        if len(args) != 2:
            print ("Error: {} didn't specify an extension to dial".format(channel_name))
            channel.hangup()
            return

        print ("{} entered the Stasis application".format(channel_name))
        channel.ring()

        try:
            print ("Dialing {}".format(args[1]))
            outgoing = self.client.channels.originate(endpoint=args[1],
                                                app=self.stt_session_label,
                                                appArgs='dialed')
        except requests.HTTPError:
            print ("Extension %s is not configured yet" % args[1])
            channel.hangup()
            return

        channel.on_event('StasisEnd', lambda *args: self.safe_hangup(outgoing))
        outgoing.on_event('StasisEnd', lambda *args: self.safe_hangup(channel))

        def outgoing_start_cb(channel_obj, ev):
            """StasisStart handler for our dialed channel"""

            print ("{} answered; bridging with {}".format(outgoing.json.get('name'),
                                                        channel.json.get('name')))
            
            channel.answer()

            #bridge = client.bridges.create(type='mixing')
            bridge.addChannel(channel=[channel.id, outgoing.id])
            #except Exception as exc:
                #print('Failed binding channel with bridge to answer a call')
            #Clean up the bridge when done
            #finally:
            #if self.total_calls > self.calls_until_destroy:
                #channel.on_event('StasisEnd', lambda *args: self.safe_bridge_destroy(bridge))
                #outgoing.on_event('StasisEnd', lambda *args: self.safe_bridge_destroy(bridge))

        logging.debug("called number %s", ev)
        outgoing.on_event('StasisStart', outgoing_start_cb)
        channel.on_event('StasisEnd', lambda *args: self.safe_hangup(outgoing))
        outgoing.on_event('StasisEnd', lambda *args: self.safe_hangup(channel))
    '''
    def on_stasis_start(objects, event, bridge):
        logging.debug('%s', event)
        objects['channel'].answer()
        channel_id = event['channel']['id']
        bridge.addChannel(channel=channel_id)

    def main():
        logging.debug('Starting %s...', sys.argv[0])
        client = ari.connect(
            base_url=ARI_URL,
            username=ARI_USERNAME,
            password=ARI_PASSWORD,
        )

        with application_bridge(client) as bridge:
            client.on_channel_event('StasisStart', partial(on_stasis_start, bridge=bridge))
            client.run(apps=[APPLICATION])
    

    logging.debug('Starting live call transcript app %s...', sys.argv[0])
    client = ari.connect(
        base_url=ARI_URL,
        username=ARI_USERNAME,
        password=ARI_PASSWORD,
    )
    '''

    def start_connection(self):
        logging.basicConfig(level=logging.DEBUG)
        with self.application_bridge(self.client) as bridge: 
            #try:
            self.client.on_channel_event('StasisStart', partial(self.stasis_start_cb, bridge=bridge))
            self.client.run(apps=[self.stt_session_label])