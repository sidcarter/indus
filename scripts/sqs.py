#!/usr/bin/env python
import sys,time
import json
import boto.sqs

if (len(sys.argv) <= 1):
	sys.exit("Insufficient arguments.\nUsage: sqs.py <queue_name> <no_of_messages>")
else:
	que_name = sys.argv[1]
	no_of_messages = 10

conn = boto.sqs.connect_to_region("us-east-1")

# all_ques = conn.get_all_queues()
#for queue in all_ques:
#	print("Queue: %s" % queue)

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
				print(message)
#				conn.delete_message(que,rs[i])
			time.sleep(1)
	else:
		sys.exit("No messages to process")
