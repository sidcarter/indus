#!/usr/bin/env python
import sys
from boto import ec2 as ec2
import boto.fps

def ec2_ip():
	conn = ec2.connect_to_region("us-east-1")
	instances = conn.get_only_instances()
	first_instance = instances[0]
	print ('Your EC2 IP is : ' + first_instance.ip_address)

def ec2_terminate():
	conn = ec2.connect_to_region("us-east-1")
	instances = conn.get_only_instances()
	print ('Terminating ' + str(instances[0]))
	instances[0].terminate()

def get_bill():
	conn = boto.connect_fps("fps.amazon.com")
	print conn.get_account_balance()

if ((len(sys.argv) > 1) and(sys.argv[1] == "bill")) :
	get_bill()
elif ((len(sys.argv) > 1) and(sys.argv[1] == "term")) :
	ec2_terminate()
else:
	ec2_ip()

