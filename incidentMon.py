#!/usr/bin/env python3
# A script to monitor the Grafan IRM endpoint and send alerts to a MQTT endpoint
# In this case, an LED on a ESP32
# File    : incidentMon.py
# Author  : Joe McManus josephmc@alumni.cmu.edu
# Version : 0.1 03/15/2025
# Copyright (C) 2025 Joe McManus

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pprint
import time
import configparser
import sys
import os
import argparse
import json
import requests
import paho.mqtt.publish as pub

parser = argparse.ArgumentParser(description='Grafana IRM  Monitor')
parser.add_argument('--debug', help="Turn on debug mode, levels 0-2,0=none, 1=info,2=dumps json", action="store", type=int, default=0)
parser.add_argument('--pid', help="Create a pid file in /var/run/incidentMon.pid",  action="store_true")
parser.add_argument('--config', help="Override config file location, default ./incidentMon.cfg", action="store")
parser.add_argument('--delay', help="Specify delay, default 60s", type=int, default=60, action="store")
args=parser.parse_args()

if args.pid:
	fh=open("/var/run/honeyBotMon.pid", "w")
	fh.write(str(os.getpid()))
	fh.close()

def getIncident(url, token):
	headers={'Authorization': 'Bearer ' + token }
	payload={"query":
			{ "limit": 1,
				"orderDirection": "DESC",
				"orderField": "createdTime",
				"queryString": "isdrill:false"
			 }
		}
	jsonLoad=json.dumps(payload)
	try:
		r=requests.post(url, headers=headers, data=jsonLoad, timeout=30)
		incidentJson=r.json()
		incidentDetails=dict(enumerate(incidentJson["incidentPreviews"]))
		incidentID=int(incidentDetails[0]["incidentID"])
		incidentSev=incidentDetails[0]["severityLabel"]
		incidentStart=incidentDetails[0]["incidentStart"]
		return(incidentID, incidentSev, incidentStart, incidentJson, r.status_code)
	except:
		return(None, None, None, None, None)
        
config=configparser.ConfigParser()
if args.config:
	configFile=args.config
else:
	configFile = 'incidentMon.cfg'
if not os.path.exists(configFile):
	print("ERROR: No config file found %s. The default is ./incidentMon.cfg or can be set with --config" % (configFile))
	sys.exit()

config.read(configFile)
default = config['default']
token=config['default']['token']
url=config['default']['url']
broker=config['default']['broker']

if token == "":
	if os.environ.get('IRM_TOKEN'):
		token=os.environ.get('IRM_TOKEN')
	else:
		print("ERROR: No token defined, use config file or environment var IRM_TOKEN")
		quit()

#store 0 as the last incident id on startup
lastIncident=0
#delay that backs off in case we can't reach the server
backOff=0
#loop forever looking for new alerts
while True:
	incidentID, incidentSev, incidentStart,incidentJson, requestReturnCode=getIncident(url, token)
	if args.debug >= 1:
		if args.debug == 2:
			pprint.pp(incidentJson)
			print("Token : %s " % (token))
		print("Delay : %s " % (args.delay))
		print("Status Code : %s " % (requestReturnCode))
		print("Config : %s " % (configFile))
		print("Last ID : %s " % (lastIncident))
		print("Current ID : %s " % (incidentID))
		print("URL: %s" % (url))
		print("MQTT Broker : %s " % (broker))
	if incidentID == None:
		backOff+=10
		print("ERROR: Unable to connect to server %s" % (url))
		time.sleep(args.delay + backOff)		
		continue
	if incidentID > lastIncident:
		#reset backoff if successful
		backOff=0
		#If we have a new incident, then let the ESP know via mqtt. 
		#I prefer to send digits to the ESP, so change the string to an int. 
		if incidentSev == "Pending":
			sev=1
		elif incidentSev == "Minor":
			sev=2
		elif incidentSev == "Major":
			sev=3
		elif incidentSev == "Critical":
			sev=4
		print("Alert ID: %d Severity %s alert " % (incidentID, incidentSev))
		lastIncident=incidentID
		pub.single('ledOne', sev, hostname=broker)
		counter=0
	elif incidentID == lastIncident:
		counter+=1
		if counter == 60:
			#if 60 minutes(default) hits without a new alert then clear the alert	
			pub.single('ledOne', 0, hostname=broker)
		
	time.sleep(args.delay)
