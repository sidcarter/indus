#!/usr/bin/env python
import sys
from boto import ec2 as ec2

try:
	conn = ec2.connect_to_region("us-east-1")
except Exception as e:
	sys.exit(e)

def ec2_info(status):
	instances = conn.get_only_instances()
	for x in instances:
		try:
			name=x.tags["Name"]
			ip_addr=x.ip_address
			priv_ip=x.private_ip_address
			state=x.state
		except AttributeError:
			name="NoName"
			ip_addr='none'
			state='none'
		except KeyError:
			print ("Unknown Key.")
		if status=="all" or status==state:
			info = 'ID: '+x.id+' |Name: '+ name
			info = info+' |State: '+state
			if (state=="running"):
				info = info+' |IP: '+str(ip_addr)
				info = info+' |Private IP:'+str(priv_ip)
			print info

def ec2_terminate():
	ec2_info("running")
	print ('Which instance do you want to terminate?')
	print ('* for all, instance id or q to quit: ')
	instance_to_terminate = raw_input()
	if instance_to_terminate == "*":
		areyousure = raw_input("Are you sure (y/n)? ")
		if areyousure=="n":
			print('No instances terminated.')
			return
		for i in conn.get_only_instances():
			if (i.state=="running"):
				i.terminate()
				print 'Termination successful'
	elif instance_to_terminate=="q":
		quit()
	else:
		conn.terminate_instances(instance_to_terminate)	
		print ('Terminated '+instance_to_terminate+'  successfully')

def ec2_start_stop():
	ec2_info("all")
	instance_to_toggle=raw_input("Which instance do you want to start or stop?")
	try:
		get_state=conn.get_all_instance_status(instance_to_toggle)
		print ("The instance "+instance_to_toggle+" is "+get_state)
	except e:
		print (e)
		

def get_bill():
	conn = boto.connect_fps("fps.amazon.com")
	print conn.get_account_balance()

if ((len(sys.argv) > 1) and(sys.argv[1] == "-t")) :
	ec2_terminate()
if ((len(sys.argv) > 1) and(sys.argv[1] == "-s")) :
	ec2_start_stop()
else:
	ec2_info("all")
