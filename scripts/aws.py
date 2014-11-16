#!/usr/bin/env python
import sys
from boto import ec2 as ec2
import boto.fps

conn = ec2.connect_to_region("us-east-1")

def ec2_info(status):
	instances = conn.get_only_instances()
	for x in instances:
		try:
			name=x.tags["Name"]
			ip_addr=x.ip_address
			state=x.state
		except TypeError:
			name="NoName"
			ip_addr='none'
			state='none'
		if status=="all":
			print ('Instance ID: '+x.id)
			print ('\tName: '+ name)
			print ('\tState: '+state)
			if (state=="running"):
				print ('\tIP: '+ip_addr)

def ec2_terminate():
	ec2_info("running")
	print ('Which instance do you want to terminate?')
	print ('* for all, instance id or q to quit: ')
	instance_to_terminate = raw_input()
	if instance_to_terminate == "*":
		for i in conn.get_only_instances():
			i.terminate()
			print 'Termination successful'
	elif instance_to_terminate=="q":
		quit()
	else:
		conn.terminate_instances(instance_to_terminate)	
		print 'Termination successful'

def get_bill():
	conn = boto.connect_fps("fps.amazon.com")
	print conn.get_account_balance()

if ((len(sys.argv) > 1) and(sys.argv[1] == "bill")) :
	get_bill()
elif ((len(sys.argv) > 1) and(sys.argv[1] == "term")) :
	ec2_terminate()
else:
	ec2_info("all")
