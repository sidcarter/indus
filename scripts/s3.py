#!/usr/bin/env python
import os,sys
from boto import s3 as s3

conn = s3.connect_to_region("us-east-1")

def list_buckets():
	buckets = conn.get_all_buckets()
	print ("List of buckets:")
	for b in buckets:
		try:
			name=b.name
		except AttributeError:
			name="NoName"
		print ("\t"+name)

def list_files():
	bucketname=raw_input("Which bucket's files you want? ")
	count=0
	if (conn.lookup(bucketname)):
		files=conn.get_bucket(bucketname).get_all_keys()
		print "Files: "
		for k in files:
			count+=1
			print k.name.encode('utf-8')
		print ("\nTotal number of files: "+str(count))
		choice=raw_input("Would you like to download these files? ")
		if (choice=="n"): return
		else:
			print ("Downloading files...")
			for f in files:
				cwd=os.getcwd()
				fname=cwd+"/"
				fname = fname+f.name
				dir = os.path.dirname(fname)
				if not os.path.exists(dir): 
					dir_to_create=cwd
					for dirs in dir.split("/"):
						dir_to_create+="/"+dirs
						#print(dir_to_create)
						if not os.path.exists(dir_to_create): os.mkdir(dir_to_create)
				with open(str(fname),'wb') as fp:
					f.get_contents_to_file(fp)
				#f.get_contents_to_filename(fname)
				#print fname
				#close(fp)
				#print ("f.get_contents_to_filename("+fname+")")
	else:
		print "No such bucket found."
		return

def list_policy():
	bucketname= raw_input("Which bucket's policy you want? ")
	try:
		policy=conn.get_bucket(bucketname).get_policy()
		print ("Policy for Bucket "+bucketname+": ")
		print policy
	except:
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

if ((len(sys.argv) > 1) and(sys.argv[1] == "-p")) :
	list_policy()
elif ((len(sys.argv) > 1) and(sys.argv[1] == "-lf")) :
	list_files()
elif ((len(sys.argv) > 1) and(sys.argv[1] == "-gf")) :
	list_files()
else:
	list_buckets()
