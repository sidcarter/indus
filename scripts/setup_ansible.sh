#!/bin/bash
HOSTSFILE=/tmp/ec2hosts
REACHABLE_HOSTSFILE=/tmp/hosts-reachable.txt
ANSIBLE_PLAYBOOK=/tmp/ansible.yml

function setup() {
	[ ! -f $REACHABLE_HOSTSFILE ] && check_hosts
	create_setup_playbook
	for HOST in `grep -v unreachable $REACHABLE_HOSTSFILE | awk '{print $1}'`
	do
		KEYNAME=$(grep $HOST /tmp/ec2hosts | awk '{print $3}')
		USER=$(grep $HOST /tmp/hosts-reachable.txt | awk '{print $NF}')
	#	ansible $i --private-key=~/.ssh/${KEYNAME}.pem -m shell -u ${USER} -a "sudo grep wheel /etc/sudoers"
		ansible-playbook -u ${USER} --private-key=~/.ssh/${KEYNAME}.pem $ANSIBLE_PLAYBOOK -e "hostname=$HOST " >/dev/null 2>&1
		FINALRESULT=$?
		[ $FINALRESULT -ne 0 ] && echo "Failed setup: $HOST"
	done
}

function create_setup_playbook() {
	cat > $ANSIBLE_PLAYBOOK << ANSIBLE
---
- hosts: "{{hostname}}"
  gather_facts: no
  sudo: yes

  tasks:
    - name: install sudo for centos servers
      yum: name=sudo state=present
      register: pl_yum
      ignore_errors: yes

    - name: install sudo for ubuntu servers
      apt: name={{item}} state=present update_cache=yes
      when: pl_yum|failed
      with_items:
        - sudo
        - apt-transport-https
      ignore_errors: yes

    - name: create group devops
      group: name=devops gid=1337
      register: pl_group
      ignore_errors: yes

    - name: create ansible user
      user: name=ansible state=present comment='Ansible User' uid=1337 group=devops
      when: pl_group|success
      register: pl_user

    - name: get ansible user home directory
      command: "cut -d: -f6 /etc/passwd"
      register: pl_ansible_homedir
      when: pl_user|success

    - name: ensure .ssh directory for ansible user exists
      file: path="{{pl_ansible_homedir.stdout}}/.ssh" state=directory owner=ansible group=devops mode=0700
      register: pl_ansible_sshdir
      when: pl_ansible_homedir|success

    - name: give ansible user sudo rights
      lineinfile: "dest=/etc/sudoers state=present regexp='^%devops' line='%devops ALL=(ALL) NOPASSWD: ALL'"

    - name: copy public key to authorized_keys
      copy: src=/home/skhader/.ssh/id_rsa.pub dest={{pl_ansible_homedir.stdout}}/.ssh/authorized_keys mode=400 owner=ansible group=devops
      when: pl_user|success
ANSIBLE
}

function check_ping() {
	ansible -m ping $1 --private-key=~/.ssh/$2.pem -u $3 >/dev/null 2>&1
}

function print_usage() {
	echo "Usage: $1 setup"
	exit 1
}

function check_hosts() {
	[ -f $REACHABLE_HOSTSFILE ] && rm -f $REACHABLE_HOSTSFILE
	for HOST in `grep -v stopped /tmp/ec2hosts | awk '{print $2}'`
	do
		KEYNAME=$(grep ${HOST} /tmp/ec2hosts | awk '{print $3}')
		USER="ec2-user"
		check_ping $HOST $KEYNAME $USER
		FIRST_PASS_RESULT=$?
		if [ $FIRST_PASS_RESULT -ne 0 ]
		then
			USER="root"
			check_ping $HOST $KEYNAME $USER
			SECOND_PASS_RESULT=$?
		fi

		if [ $FIRST_PASS_RESULT -eq 0 ] || [ $SECOND_PASS_RESULT -eq 0 ]
		then
			echo "$HOST is reachable as $USER" >> $REACHABLE_HOSTSFILE
		else
			echo "$HOST is unreachable" >> $REACHABLE_HOSTSFILE
		fi
	done
}

ARGS=$#

if [ $ARGS -eq 0 ]
then
	check_hosts
elif [ $1 == "setup" ]
then
	setup
else
	echo "wrong arguments, yo!"
	print_usage $0
fi