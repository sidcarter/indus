playbooks
=========

Don't forget to export AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID before using these playbooks.

* ec2-simple.yml - Ansible playbook to create an AMI Linux Instance, all in a single file.  
  Uses the Debian 8.0 jessie HVM instance for us-east-1 region.  
  Run ansible-playbook ec2-simple.yml -e "instance_name=#instance-name# keypair=#keypair-name# group=#security-group-name# username=#username#" to create a new EC2 instance.  

* ec2-custom.yml - Ansible playbook to create a custom ec2 instance
  Coming soon
