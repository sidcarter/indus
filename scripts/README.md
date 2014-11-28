scripts
=======

**BEWARE** - scripts always changing. check before you use them.

* ec2.py - Set of commands for managing AWS instances.  
  Remember to export AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID before you use this script. 
  ./ec2.py - lists all available instances  
  ./ec2.py term - terminates instances

* s3.py - Set of commands for managing S3 buckets.  
  Remember to export AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID before you use this script. 
  ./s3.py - lists all available buckets
  ./s3.py files - lists all files in a bucket
  ./s3.py policy - lists the policy for a bucket

* wordfunc.py - Set of functions which use nltk module.  
  Something to use when creating doing anything with words.

* get_syllables.py - plan to use this to create poems and shit.  
  Need to figure out how to strip duplicates.
  Need to figure try and use hadoop/scala.
  Python is clearly slow.
