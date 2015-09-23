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
        no_of_messages = sys.argv[2] if len(sys.argv)>2 else 20

    return (que_name,int(no_of_messages))

def process_ques(que_name,no_of_messages):
    try:
        conn = boto.sqs.connect_to_region("us-east-1")
    except Exception as e:
        print("Error connecting to SQS: {}".format(e))
        sys.exit(1)

    que = conn.get_queue(que_name)

    # all_ques = conn.get_all_queues()
    #for queue in all_ques:
    #	print("Queue: %s" % queue)

    try:
        print("Total messages in the {} queue: {}".format(que_name,que.count()))
        max_messages_in_que=10  #minimum is 1, maximum is 10
        rs = que.get_messages(max_messages_in_que)
    except AttributeError as e:
	    print "Error: {}. Likely a non-existent queue.".format(e)
    else:
        print "Information for %s messages" % (no_of_messages)
        count=0
        while count < no_of_messages and len(rs)!=0:
            for que_message in rs:
                count+=1
                message = json.loads(que_message.get_body())['Message']
                bounce_message=yaml.safe_load(message)
                print(bounce_message['mail']['timestamp'] + ' - ' + bounce_message['mail']['destination'][0])
                conn.delete_message(que,que_message)
            time.sleep(1)
            rs = que.get_messages(max_messages_in_que)

    #finally let's purge the queue
    try:
        print("Purging queue: {}...".format(que_name))
        que.purge()
    except boto.exception.SQSError as e:
        print("Purging queue too soon. Try again after a minute. {}".format(e))

if __name__=="__main__":
    que_name,no_of_messages=get_args()
    process_ques(que_name,no_of_messages)
