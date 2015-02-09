#!/usr/bin/env python
import sys
from boto import ec2 as ec2

try:
	conn = ec2.connect_to_region("us-east-1")
except Exception as e:
	sys.exit(e)

def ec2_info(status):
	instances = conn.get_only_instances()
	print ("Instance ID\tName\tDNS Name\tState\tPublic IP\tPrivate IP")
	for x in instances:
		try:
			id=x.id
			name=x.tags["Name"]
			dns_name=x.public_dns_name
			ip_addr=x.ip_address
			priv_ip=x.private_ip_address
			state=x.state
		except AttributeError:
			name="NoName"
			ip_addr='none'
			state='none'
		except KeyError as ke:
			print ("KeyError: %s tag not set") % ke
		if status=="all" or status==state:
			info = '%s %s %s' % (id,name,state)
			if (state=="running"):
				info = '%s %s %s' %(info,ip_addr, priv_ip)
			print info

def ec2_terminate():
	ec2_info('running')
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
	ec2_info('all')
	instance_to_toggle=raw_input("Which instance do you want to start or stop?")
	try:
		get_state=conn.get_all_instance_status(instance_to_toggle)
		print ("The instance "+instance_to_toggle+" is "+get_state)
	except e:
		print (e)
		
def ec2_secgroups():
    for region in ec2.regions():
        if not 'us' in region.name or 'gov' in region.name: continue
        print region.name
        try:
            conn=ec2.connect_to_region(region.name)
        except Exception as e:
            sys.exit(e)

        rs=conn.get_all_security_groups()

        for item in rs:
            print "Rules: for %s are:" % item.name
            for rule in item.rules:
                print "rule: %s" % rule
            print
            
if ((len(sys.argv) > 1) and(sys.argv[1] == "-s")) :
	ec2_snapshots()
if ((len(sys.argv) > 1) and(sys.argv[1] == "-r")) :
	ec2_start_stop()
if ((len(sys.argv) > 1) and(sys.argv[1] == "-g")) :
	ec2_secgroups()
else:
	ec2_info("all")
