#!/usr/bin/env python
import boto.sqs

conn = boto.sqs.connect_to_region("us-east-1")

all_ques = conn.get_all_queues()

for queue in all_ques:
	print("Queue: %s" % queue)

bounce_que = conn.get_queue("ses-bounces")

rs = bounce_que.get_messages(5)
print("We are looking at about %s messages." % len(rs))

for i in range(len(rs)):
	print(rs[i].get_body())
