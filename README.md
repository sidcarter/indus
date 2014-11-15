Indus
=====

A set of tools and configuration files that I end up using too often. My dotfiles and any scripts that I end up creating.

* ami-linux.yml - Ansible playbook to create an AMI Linux Instance.  
  Run ansible-playbook ami-linux.yml -e "instance_name=<your-instance-name> keypair=<your-keypair-name" to create a new EC2 instances. Uses the AMI Linux HVM image. Don't forget to export AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID in your .profile or whatever shell you use.

* aws_sid.py - Set of commands for managing AWS instances. Written using python

* .muttrc - Coming soon
* .fetchmailrc - Coming soon