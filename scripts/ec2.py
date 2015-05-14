#!/usr/bin/env python
import sys, traceback
from argparse import ArgumentParser
from boto import ec2 as ec2

def ec2_info(region="us-east-1"):
    conn = ec2.connect_to_region(region)
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
            continue
            #  print ("KeyError: %s tag not set") % ke
        info = '%s %s %s' % (id,name,state)
        if (state=="running"):
            info = '%s %s %s %s' %(info, dns_name, ip_addr, priv_ip)
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
	except Exception as e:
		print (e)
		
def ec2_secgroups(region="us-east-1", file=None,sg=None):
        try:
            conn=ec2.connect_to_region(region)
            rs=conn.get_all_security_groups()
        except Exception as e:
            sys.exit(e)

        if not file:
            for item in rs:
                print "Rules: for %s are:" % item.name
                for rule in item.rules:
                    for grant in rule.grants:
                        if grant.cidr_ip=="0.0.0.0/0":
                            print "\t%s-%s (open)" % (rule.from_port, rule.to_port)
                        elif grant.cidr_ip:
                            print "\t%s-%s (%s)" % (rule.from_port, rule.to_port, grant.cidr_ip)
                        else:
                            print "\t%s-%s (%s)" % (rule.from_port, rule.to_port, grant.name)
                print
        elif file and sg:
            
            # the file should come in a comma separate file - cidr, from_port and to_port
            secgroup=None
            for item in rs:
                if item.name==sg: 
                    secgroup=item
            if secgroup:
                for line in file.read().splitlines():
                    #                print (type(line),line)
                    try:
                        (source_cidr,from_port,to_port) = line.split(",") 
                        print("%s %s %s %s") %(source_cidr, from_port, to_port ,sg)
                        secgroup.authorize(ip_protocol="tcp",from_port=from_port, to_port=to_port, cidr_ip=source_cidr)
                    except:
                        sys.exit(traceback.format_exc())
            else: 
                print "Security Group: %s not found" % sg
            
def main():
    
    parser = ArgumentParser(description='Custom AWS Interface', prog="ec2.py")
    parser.add_argument('-r', '--read-file', nargs=1, required=False, help='input file to be provided')
    parser.add_argument('-sg', '--security-group', nargs=1, required=False, help='security group to be changed or modified')
    parser.add_argument('-l', '--list', nargs=1, choices=['instances','security_groups'], help='list all entities e.g. -l instances')
    args=parser.parse_args()
    
    if args.list:
        if args.list[0]=="instances":
            ec2_info()
        elif args.list[0]=="security_groups":
            ec2_secgroups()
    elif args.read_file:
        if args.security_group:
            filename=args.read_file[0]
            security_group=args.security_group[0]
            try:
                f = open(filename,'r')
                ec2_secgroups(file=f,sg=security_group)
            except Exception as e:
                print(e)
        else:
            print("Please provide a security group to modify.")
    
#    ec2_info("all")
    
main()