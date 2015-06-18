scripts
=======

**BEWARE** - scripts always changing. check before you use them.

* ec2.py - Set of commands for managing AWS instances.  
  Remember to export AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID before you use this script.  
  ./ec2.py - lists all available instances  
  -t - terminates instances

* s3.py - Set of commands for managing S3 buckets.  
  Remember to export AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID before you use this script.   
  ./s3.py - lists all available buckets  
  -lf - lists all files in a bucket  
  -p - lists the policy for a bucket  

* aws_usage.py - Code to download your aws usage reports.  
  Originally from - https://github.com/kzahel/awsbill  

* emr.py - Set of commands for mapreduce tasks
  Coming soon...   

* wordfunc.py - Set of functions which use nltk module.  
  Something to use when creating doing anything with words.

* setup_ansible.sh - a quick script I created to setup ansible for 200+ servers
  Uses ec2.py and ec2.ini dynamic inventory scripts

* get_syllables.py - plan to use this to create poems and shit.  
  Need to figure out how to strip duplicates.
  Need to figure try and use hadoop/scala.
  Python is clearly slow.
