#!/usr/bin/env python
import sys
from boto import s3 as s3

conn = s3.connect_to_region("us-east-1")

def list_buckets():
	buckets = conn.get_all_buckets()
	for b in buckets:
		try:
			name=b.name
		except AttributeError:
			name="NoName"

		print ('Bucket Name: '+ name)

def list_files():
	bucketname=raw_input("Which bucket's files you want? ")
	if (conn.lookup(bucketname)):
		files=conn.get_bucket(bucketname).get_all_keys()
		print "Files: "
		for k in files:
			print k.name.encode('utf-8')
	else:
		print "No such bucket found."
		return

def list_policy():
	bucketname= raw_input("Which bucket's policy you want? ")
	try:
		policy=conn.get_bucket(bucketname).get_policy()
		print ("Policy for Bucket "+bucketname+": ")
		print policy
	except S3ResponseError:
		print ("Policy or Bucket not found.")
	
def bucket_delete():
	print ('Which bucket do you want to delete?')
	print ('* for all, bucket id or q to quit: ')
	bucket_to_delete= raw_input()
	if bucket_to_delete == "*":
		areyousure = raw_input("Are you sure (y/n)? ")
		if areyousure=="n":
			print('No buckets deleted.')
			return
		for i in conn.get_all_buckets():
			if (i.state=="running"):
				i.delete()
				print 'Bucket deleted successfully.'
	elif bucket_to_delete=="q":
		quit()
	else:
		conn.delete_buckets(bucket_to_delete)	
		print ('Terminated '+bucket_to_delete+'  successfully')

if ((len(sys.argv) > 1) and(sys.argv[1] == "term")) :
	bucket_delete()
elif ((len(sys.argv) > 1) and(sys.argv[1] == "policy")) :
	list_policy()
elif ((len(sys.argv) > 1) and(sys.argv[1] == "files")) :
	list_files()
else:
	list_buckets()
