#!/usr/bin/env python
import sys,time
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

bounce_que = conn.get_queue(que_name)

try:
	rs = bounce_que.get_messages(no_of_messages)
except AttributeError as e:
	print "Error: %s\nIt's possible that you provided an invalid queue name." % e
else:
	print("We are looking at %s messages." % len(rs))

	while True:
		for i in range(len(rs)):
			print(rs[i].get_body())
			conn.delete_message(bounce_que,rs[i])
		time.sleep(1)
