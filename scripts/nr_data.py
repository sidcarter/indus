#!/usr/bin/env python

import os
import sys
import argparse
import requests
import json
from prettytable import PrettyTable

api_key=os.getenv("NEW_RELIC_API_KEY") 
    
if not api_key: 
    exit("Please set environment variable NEW_RELIC_API_KEY. Aborting....")
else:
    header={'x-api-key':api_key}
    v2_endpoint="https://api.newrelic.com/v2"

def get_endpoint(type):
    return "%s/%s.json" % (v2_endpoint,type)
    
def get_entity_endpoint(type,id):
    return "%s/%s/%s.json" %(v2_endpoint,type,id)

def get_entities(type,endpoint=None,entities=None):
    if not endpoint:
        endpoint=get_endpoint(type)
        entities=[]
    r=requests.get(endpoint,headers=header)
    if '0.14' in requests.__version__:
        entities.extend(r.json[type])
    else:
        entities.extend(r.json()[type])
    if not 'next' in r.links:
        return entities
    else:
        return get_entities(type,r.links['next']['url'],entities)

def remove_entity(type,id):
    r=requests.delete(get_entity_endpoint(type,id),headers=header)
    return r.status_code

def get_entity(type,id):
    r=requests.get(get_entity_endpoint(type,id),headers=header)
    return r.json()

def main():
    parser = argparse.ArgumentParser(description='New Relic V2 API Interface')
    parser.add_argument('-l', '--list', nargs=1, required=True, choices=['servers','applications'], help='List all the entities')
    parser.add_argument('-n', '--non-reporting', action='store_true', help='For non-reporting entities')
    parser.add_argument('-d', '--delete', action='store_true', help='Delete non-reporting entities')
    args=parser.parse_args()

    if args.delete or args.list:
        entity_type=args.list[0]
        entities=get_entities(type=entity_type)
    else:
        exit()

    nr_count=0
    if args.list:
        entries = PrettyTable(["Name", "Reporting Status"])
        entries.align["Name"]="l"
        for entity in sorted(entities,key=lambda entity:entity["reporting"],reverse=True):
            entry=[entity['name'], entity['reporting']]
            if not entity['reporting']: nr_count+=1
            entries.add_row(entry)

        print entries
        if nr_count>0: print "{} {} out of {} not reporting".format(nr_count,entity_type,len(entities))

    elif args.delete:
        entities_to_delete=[(entity['id'],entity['name']) for entity in entities if not entity['reporting']]
        if len(entities_to_delete) > 0:
            print "{} non-reporting {} found. Enter y to delete and any other key to skip deletion: " % (len(entities_to_delete), entity_type)
            choice=raw_input()
            if choice=="y":
                for entity in entities_to_delete:
                    print "Removing host %s from NewRelic" % entity[1]
                    try:
                        remove_entity(entity_type,entity[0])
                        nr_count+=1
                    except Exception as e:
                        print "Unable to delete host: {} due to error: {}".format(entity[1],e)
                if nr_count>0: print "{} hosts deleted from New Relic".format(nr_count)
            else: 
                print "Skipping deletion. Goodbye!"
            
if __name__=="__main__":
    main()