#!/usr/bin/env python3
# A script to create word clouds out of Grafana IRM data
# File    : incidentCloud.py
# Author  : Joe McManus josephmc@alumni.cmu.edu
# Version : 0.1 2025/07/10
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

import time
import configparser
import os
import argparse
import json
import requests
from datetime import datetime
from wordcloud import WordCloud, STOPWORDS
import matplotlib 
from collections import defaultdict,Counter


parser = argparse.ArgumentParser(description='Grafana IRM Word Cloud')
parser.add_argument('--debug', help="Turn on debug mode, levels 0-2,0=none, 1=info,2=dumps json", action="store", type=int, default=0)
parser.add_argument('--config', help="Override config file location, default ./incidentMon.cfg", action="store")
parser.add_argument('--window', help="Specify YYYY-MM to view, default current month", action="store")
parser.add_argument('--security', help="Only act on Security incidents, ignore everything else",  action="store_true")
parser.add_argument('--outfile', help="output filename, default wordcloud.png",  action="store_true", default='wordcloud.png')
parser.add_argument('--limit', help="# of words to display, default 100", type=int, default=100)
parser.add_argument('--width', help="Width of image, default 1600", type=int, default=1600)
parser.add_argument('--height', help="Height of image, default 1200", type=int, default=1200)

args=parser.parse_args()

if not args.window:
    window=time.strftime("%Y-%m")
else:
    window=args.window
print("Using window: " + str(window))

def getIncident(url, token, window):
    headers={'Authorization': 'Bearer ' + token }
    payload={"query": { "limit": 100, "orderDirection": "DESC", "orderField": "createdTime", "queryString": "isdrill:false" } }
    bulkSummary=""
    text=[]
    if args.security:
        payload={"query": { "limit": 100, "orderDirection": "DESC", "orderField": "createdTime", "queryString": "label:security" } }
    jsonLoad=json.dumps(payload)
    try:
        #ignore some common words 
        excludeList="because all In question from they were being some use not has been no their due we We had could This these The before which but I Its Im bye it its of for this that the and to was its here hey so there in be you on have with are if " 
        r=requests.post(url, headers=headers, data=jsonLoad, timeout=30)
        incidentJson=r.json()
        incidentBulk=dict(enumerate(incidentJson["incidentPreviews"]))
        for incidentID , details in incidentBulk.items():
            if window in str(details["createdTime"]):
                bulkSummary=bulkSummary + details["summary"] + details["title"]
                words=bulkSummary.rstrip("\n")
                for word in words.split():
                    if word not in excludeList: 
                        text.append(word)
        return(text)
    except:
        return(None)

config=configparser.ConfigParser()
if args.config:
    configFile=args.config
else:
    configFile = 'incidentMon.cfg'
if not os.path.exists(configFile):
    print("ERROR: No config file found %s. The default is ./incidentMon.cfg or can be set with --config" % (configFile))
    quit()

config.read(configFile)
default = config['default']
token=config['default']['token']
url=config['default']['url']

if token == "":
    if os.environ.get('IRM_TOKEN'):
        token=os.environ.get('IRM_TOKEN')
    else:
        print("ERROR: No token defined, use config file or environment var IRM_TOKEN")
        quit()

text=getIncident(url, token, window)
if text != None:
    if args.debug >= 1:
            print(text)
            print("Token : %s " % (token))
            print("Config : %s " % (configFile))
            print("URL: %s" % (url))

# Create a count of word occurance 
cnt = Counter()
for word in text:
    cnt[word] += 1

wc = WordCloud(regexp=r'.*\s', max_words=args.limit, colormap='autumn', max_font_size=200, height=args.height, width=args.width).generate_from_frequencies(cnt)
wc.to_file(args.outfile)

