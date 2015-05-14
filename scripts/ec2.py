#!/usr/bin/env python
# Ensure you set AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID
# environment variables before you execute the script


import sys
import traceback
from argparse import ArgumentParser
from boto import ec2
from boto import rds2
from boto import ses


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


def ec2_instance_update(region="us-east-1", filename=None,sg=None):
    # the file should be a comma separate file - instance name and id
    # if we can't split a file we throw an error
    secgroup=None
    for item in sgs:
        if item.id==sg: 
            secgroup=item.id
    if secgroup:
        for line in file.read().splitlines():
            try:
                (hostname,instance_id) = line.split(",")
                instance_sg = conn.get_instance_attribute(instance_id,"groupSet")["groupSet"][0].id
                conn.modify_instance_attribute(instance_id,"groupSet",[instance_sg,sg])
                instance_groups = conn.get_instance_attribute(instance_id,"groupSet")["groupSet"]
                print("Updated %s (%s): now has %d groups") % (hostname,instance_id, len(instance_groups))
                #print("%s %s %s %s") %(hostname, instance_id, secgroup, instance_sg)

            except ValueError:
                sys.exit(traceback.format_exc())
            finally:
                file.close()
    else:
        print "Security Group: %s not found" % sg


def get_conn(region):
    try:
        return ec2.connect_to_region(region)
    except Exception as e:
        sys.exit(e)

def secgroups_add(security_group,filename,region="us-east-1"):
    conn=get_conn(region)
    sgs=conn.get_all_security_groups()
    try:
        file = open(filename,'r')
    except Exception as e:
        sys.exit(e)

    secgroup=None
    for item in sgs:
        if item.id==security_group:
            secgroup=item
    if secgroup:
        for line in file.read().splitlines():
#       print (type(line),line)
            try:
                # the file should be a comma separate file - cidr, from_port and to_port
                # if we can't split a file we throw an error
                (source_cidr,from_port,to_port) = line.split(",")
                print("%s %s %s %s") %(source_cidr, from_port, to_port ,security_group) 
                secgroup.authorize(ip_protocol="tcp",from_port=from_port, to_port=to_port, cidr_ip=source_cidr)
            except ValueError:
                sys.exit(traceback.format_exc())
            finally:
                file.close()
    else:
        print "Security Group: %s not found" % security_group


def security_groups_info(region="us-east-1"):
    conn=get_conn(region)
    sgs=conn.get_all_security_groups()

    print("Security groups and rules in region %s:\n") % region
    for item in sgs:
        print "Rules for %s: " % item.name
        for rule in item.rules:
            for grant in rule.grants:
                if grant.cidr_ip=="0.0.0.0/0":
                    print "\t%s-%s (open)" % (rule.from_port, rule.to_port)
                elif grant.cidr_ip:
                    print "\t%s-%s (%s)" % (rule.from_port, rule.to_port, grant.cidr_ip)
                else:
                    print "\t%s-%s (%s)" % (rule.from_port, rule.to_port, grant.name)
        print


def clear_sg_rules(security_group,region="us-east-1"):
    conn=get_conn(region)
    sgs=conn.get_all_security_groups()

    secgroup=None
    for group in sgs:
        if group.id == security_group:
            secgroup = group

    if secgroup:
#        print secgroup.rules
        for rule in secgroup.rules:
            for grant in rule.grants:
                print("%s %s %s %s") % (rule.ip_protocol,rule.from_port,rule.to_port,grant.cidr_ip)
                secgroup.revoke(rule.ip_protocol,rule.from_port,rule.to_port,grant.cidr_ip)
    else:
        print("Security group %s not found") % security_group


def s3_info():
    s3=boto.connect_s3()
    allBuckets = s3.get_all_buckets()
    for bucket in allBuckets:
        print bucket


def ses_alerts():
    ses_conn=ses.connect_to_region(default_region)
    ses_send_quota= ses_conn.get_send_quota()
    max_quota=float(ses_send_quota['GetSendQuotaResponse']['GetSendQuotaResult']['Max24HourSend'])
    current_usage=float(ses_send_quota['GetSendQuotaResponse']['GetSendQuotaResult']['SentLast24Hours'])
    send_stat=(current_usage/max_quota)*100
    ses_stats=ses_conn.get_send_statistics()
    print("Your current send rate is %.0f%% of your max quota.") % send_stat

def act_on_args():
    
    parser = ArgumentParser(description='Custom AWS Interface', prog="ec2.py")
    parser.add_argument('-i', '--input-file', nargs=1, required=False, help='input file to be provided')
    parser.add_argument('-a', '--add', nargs=1, help='add rules to a security group. e.g. -a sg-88basdfa')
    parser.add_argument('-c', '--clear', nargs=1, help='clear all the rules in a security group. ')
    parser.add_argument('-l', '--list', nargs=1, choices=['instances','security_groups'], help='list all entities e.g. -l instances')
    args=parser.parse_args()
    
    if args.list:
        if args.list[0]=="instances":
            ec2_info()
        elif args.list[0]=="security_groups":
            security_groups_info()
    elif args.add and args.input_file:
        filename=args.input_file[0]
        security_group=args.add[0]
        secgroups_add(security_group,filename)
    elif args.clear:
        security_group=args.clear[0]
        clear_sg_rules(security_group)
    else:
        print("Maybe you didn't provide a file? Check your arguments.")
    
if __name__=="__main__":
    act_on_args()