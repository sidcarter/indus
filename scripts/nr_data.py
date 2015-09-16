#!/usr/bin/env python

import os
import sys
import requests
import json

api_key=os.getenv("NEW_RELIC_API_KEY")
    
if not api_key: 
    exit("Please set environment variable NEW_RELIC_API_KEY. Aborting....")
else:
    header={'x-api-key':api_key}
    v2_endpoint="https://api.newrelic.com/v2"

def get_endpoint(type):
    return "%s/%s.json" % (v2_endpoint,type)

def get_entities(type,endpoint=None,entities=None):
    if not endpoint:
        endpoint=get_endpoint(type)
        entities=[]
    r=requests.get(endpoint,headers=header)
    entities.extend(r.json()[type])
    if not 'next' in r.links:
        return entities
    else:
        return get_entities(type,r.links['next']['url'],entities)

print "Fetching info from New Relic....",
sys.stdout.flush()
servers = get_entities('servers')
applications = get_entities('applications')
print "Done."

print "The following hosts are not reporting: "
count=0
for server in servers:
    if not server['reporting']:
        print "%s" % server['name']
        count+=1

print "that's a total of %d servers not reporting" % count
    
print "total servers: %d" % len(servers)

print "total applications: %d" % len(applications)