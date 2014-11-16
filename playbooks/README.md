playbooks
=========

* ec2-simple.yml - Ansible playbook to create an AMI Linux Instance, all in a single file.  
  Run ansible-playbook ec2-simple.yml -e "instance_name=#instance-name# keypair=#keypair-name# group=#security-group-name# username=#username#" to create a new EC2 instance.  
  Uses the AMI Linux HVM image.  
  Don't forget to export AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID in your .profile or whatever shell you use.