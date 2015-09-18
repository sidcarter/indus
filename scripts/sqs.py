#!/usr/bin/env python
import sys,time
import json
import boto.sqs
import yaml

# remember to set your AWS_SECRET_ACCESS_KEY & AWS_ACCESS_KEY_ID

def get_args():
    if (len(sys.argv) <= 1):
        sys.exit("Insufficient arguments.\nUsage: sqs.py <queue_name> <no_of_messages>")
    else:
        que_name = sys.argv[1]
        no_of_messages = sys.argv[2] if len(sys.argv)>2 else 10

    return (que_name,no_of_messages)

def process_ques(que_name,no_of_messages):
    try:
        conn = boto.sqs.connect_to_region("us-east-1")
    except Exception as e:
        print("Error connecting to SQS: %s") %e
        sys.exit(1)
    else:
        que = conn.get_queue(que_name)

    try:
	    rs = que.get_messages(no_of_messages)
    except AttributeError as e:
	    print "Error: %s\nInvalid queue name." % e
    else:
        if len(rs)!= 0:
            while True:
                for i in range(len(rs)):
                    message = json.loads(rs[i].get_body())['Message']
                    print(yaml.safe_load(message))['bounce']['bouncedRecipients'][0]['emailAddress']
                    # print(message['bounce'])
                    conn.delete_message(que,rs[i])
                time.sleep(1)
        else:
			sys.exit("No messages to process")

if __name__=="__main__":
    que_name,no_of_messages=get_args()
    process_ques(que_name,no_of_messages)
