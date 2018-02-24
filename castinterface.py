#!/usr/bin/python

import sys
import json
import config

import coloredlogs
import logging
import pychromecast
from logging.handlers import SysLogHandler
from time import sleep
from threading import Thread
import paho.mqtt.client as mqtt

#################################
# LOGOWANIE
#################################

if config.IS_DEBUG:
    loglevel = [logging.DEBUG,'DEBUG']
else:
    loglevel = [logging.INFO,'INFO']


logging.basicConfig(level=loglevel[0], format='%(asctime)s -- %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

logger = logging.getLogger(__name__)
coloredlogs.install(level=loglevel[1], logger=logger)

# SYSLOG
syslog = SysLogHandler(address='/dev/log', facility='user')
formatter = logging.Formatter('%(name)s: %(levelname)s %(module)s %(message)r')
syslog.setFormatter(formatter)
syslog.setLevel(logging.WARNING)

logger.addHandler(syslog)


#################################

def on_connect(client, userdata, flags, rc):
    logger.info('Connected with result code ' + str(rc))
    pass

def get_cc_data(cast,what):
    try:
	sleep(0.1)
        if what == 'status':
            return json.dumps({"online": True, "data": (cast.status.__dict__)})
        else:
            return json.dumps({"online": True, "data": (cast.media_controller.status.__dict__)})
	cast.disconnect()
    except:
        logger.error(sys.exc_info())
	return json.dumps(config.DEAD_FRAME)

def on_message_volume(mqcl, obj, msg):
    logger.debug('Received ' + msg.payload + ' on ' + msg.topic)
    device = [cast for cast in config.CHROMECAST_LIST if cast['name'] == msg.topic.split('/')[0]][0]
    if device['isAlive'] == True :
        if msg.payload.isdigit() and (float(msg.payload) >= 0 and float(msg.payload) <= 100 ) :
            device['castObject'].set_volume(float(msg.payload)/100)
	    logger.info('Volume set to ' + msg.payload + '%')
        else:
            if msg.payload == '?' :
		volumeVal = float(device['castObject'].status.volume_level)*100
                mqcl.publish(device['name'] + '/chromecast/volume', volumeVal)
		logger.debug('Received volume level check, answered ' + str(volumeVal)) 

def on_message_pause(mqcl, obj, msg):
    logger.debug('Received ' + msg.payload + ' on ' + msg.topic)
    device = [cast for cast in config.CHROMECAST_LIST if cast['name'] == msg.topic.split('/')[0]][0]
    if device['isAlive'] == True :
	if msg.payload == 'pause':
            device['castObject'].media_controller.pause()
            logger.info('Chromecast ' + device['name'] + ' paused as requested') 
	if msg.payload == 'play':
            device['castObject'].media_controller.play()
            logger.info('Chromecast ' + device['name'] + ' resumed as requested') 
	

def do_all(mqcl,casts):
    for i in casts:
	if i['isAlive'] == True:
	        mqcl.publish(i['name'] +'/chromecast/status',get_cc_data(i['castObject'],'status'), retain=True)
		logger.debug('Sent '+ i['name'] + ' status packet')
	        mqcl.publish(i['name'] +'/chromecast/playing',get_cc_data(i['castObject'],'media'), retain=True)
		logger.debug('Sent '+ i['name'] + ' media packet')
		mqcl.publish(i['name'] +'/chromecast/volume', float(i['castObject'].status.volume_level)*100, retain=True)
	else:
	        mqcl.publish(i['name'] +'/chromecast/status',json.dumps(config.DEAD_FRAME), retain=True)
		logger.debug('Sent '+ i['name'] + ' dead status packet')
	        mqcl.publish(i['name'] +'/chromecast/playing',json.dumps(config.DEAD_FRAME), retain=True)
		logger.debug('Sent '+ i['name'] + ' dead media packet')


def connect_to(castItem):
    try:
	return pychromecast.Chromecast(castItem['ip'])
	logger.debug('Connected to ' + castItem['name'] + ' successfully')
    except:
	logger.warning('Unable to connect to '+ castItem['name'] +', will try again')
	return None

def execute():
    while True:
        do_all(client,config.CHROMECAST_LIST)
	logger.debug(' sleeping ' + str(config.SLEEP_TIME) + ' seconds')
        sleep(config.SLEEP_TIME)

def control_isAlive():
    while True:
	for cast in config.CHROMECAST_LIST:
		if (cast['castObject']):
			if(cast['castObject'].socket_client.is_connected):
				cast['isAlive'] = True
				logger.debug('Cast ' + cast['name'] + ' is alive')
			else:
				logger.info('Cast ' + cast['name'] + ' was alive, but now its not')
				logger.info('Will try to connect gradually')
				cast['isAlive'] = False
				sleep(10)

		else:
			cast['isAlive'] = False
			logger.debug('Cast ' + cast['name'] + ' is dead')
			logger.debug('Trying to connect')
			cast['castObject'] = connect_to(cast)
			sleep(10)
	sleep(config.SLEEP_TIME)

client = mqtt.Client()
logger.info('Created MQTT client')

client.on_connect = on_connect
logger.info('onConnect callback set')

try:
    client.connect(config.SERVER_ADDRESS, 1883, 60)
    logger.info('Connected to ' + config.SERVER_ADDRESS + ' successfully')
except:
    logger.error('Connecting to ' + config.SERVER_ADDRESS + ' unsuccessful')
    logger.error(sys.exc_info())
    

client.loop_start()
logger.info('Main MQTT loop started')

for cast in config.CHROMECAST_LIST:
	client.message_callback_add(cast['name']+'/chromecast/volume', on_message_volume)
	logger.info('Volume callback for ' + cast['name'] + ' set') 
	client.message_callback_add(cast['name']+'/chromecast/pause', on_message_pause)
	logger.info('Pause callback for ' + cast['name'] + ' set') 
	client.subscribe(cast['name']+"/#")
	logger.info('Subscribed ' + cast['name'] + '/# topic on ' + config.SERVER_ADDRESS) 

Thread(target=control_isAlive).start()
Thread(target=execute).start()
logger.info('isAlive and executive threads started')
logger.info('--- Startup completed, let\'s roll ---')

