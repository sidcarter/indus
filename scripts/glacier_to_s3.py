#!/usr/bin/env python

from __future__ import print_function
from pprint import pprint
import boto3
import botocore
from time import sleep
import argparse
import os
import sys
import json
#import logging
#logging.basicConfig(filename="mylog.log", level=logging.DEBUG)

max_retrieval_limit = 80*1024*1024*1024 # 80GB
an_hour=60*60

def list_inventory(client, job_id, vault_name=None, account_id=None):
    archive_files = []
    if get_job_status(client,job_id,vault_name,account_id):
        job_output = client.get_job_output(
            vaultName=vault_name,
            accountId=account_id,
            jobId=job_id)
        output = json.loads(job_output['body'].read())
        for archive in output['ArchiveList']:
            archive_tuple = (archive['ArchiveId'],archive['ArchiveDescription'],archive['Size'])
            archive_files.append(archive_tuple)
    return archive_files


def get_job_status(client, job_id, vault_name=None, account_id=None, verbose=False):
    job_details = client.describe_job(
        vaultName=vault_name,
        jobId=job_id,
        accountId=account_id)
    if verbose:
        pprint(job_details)
    return job_details['Completed']


def retrieve_files_job(client, files, vault_name=None, account_id=None):
    retrieval_size = 0
    file_batch_to_retrieve = []
    for file_id,file_name,size in files:
        try:
            file_exists = open(file_name,'r')
            file_exists.close()
            file_size_on_disk=os.path.getsize(file_name)
            if file_size_on_disk != size:
                raise Exception('file size is incorrect')
            print('^',end="")
        except:
            if (retrieval_size+size)>max_retrieval_limit:
                retrieve_batch_of_files(client,file_batch_to_retrieve,vault_name,account_id)
                print("We finished retrieving a chunk of {}MB ".format((retrieval_size)/(1024*1024)))
                retrieval_size = 0
                file_batch_to_retrieve = []
            elif (retrieval_size+size)<max_retrieval_limit:
                retrieval_size = retrieval_size + size
                file_tuple=(file_name,file_id)
                file_batch_to_retrieve.append(file_tuple)
    if not file_batch_to_retrieve == []:
        retrieve_batch_of_files(client,file_batch_to_retrieve,vault_name,account_id)


def retrieve_batch_of_files(client, file_batch_to_retrieve, vault_name, account_id):
    for file_name,file_id in file_batch_to_retrieve:
        try:
            job_id = get_archive(client,file_name,file_id,vault_name,account_id)
        except botocore.vendored.requests.exceptions.SSLError:
            sleep(20)
            job_id = get_archive(client,file_name,file_id,vault_name,account_id)
        print("{} : {}".format(file_name,job_id))
    sleep(an_hour)


def glacier_to_s3(client, job_id, vault_name=None, account_id=None, s3_bucket=None):
    s3_client = boto3.client('s3')
    path = "LST/WEBHOSE/"
    content_type = "application/zip"
    content_encoding = "zip"
     
    if get_job_status(client,job_id,vault_name,account_id):
        try:
            job_output = client.get_job_output(
                vaultName=vault_name,
                accountId=account_id,
                jobId=job_id)
            try:
                file_name=job_output['archiveDescription']
                
                try:
                    file_exists = open(file_name,'r')
                    file_exists.close()
                except:
                    archive_body=job_output['body'].read()
                    with open(file_name, 'w') as file:
                        file.write(archive_body)

                try:
                    key = "{}{}".format(path,file_name)
                    s3_obj = s3_client.get_object(Bucket=s3_bucket,Key=key)
                    file_size_on_disk=os.path.getsize(file_name)
                    if s3_obj['ContentLength'] != file_size_on_disk:
                        raise Exception('s3 file size is incorrect')
                    print('!', end="")
#                    print("{} exists".format(key))
                except:
                    archive_body = open(file_name,'r')
                    s3_response = s3_client.put_object(
                                Bucket=s3_bucket,
                                Key=key,Body=archive_body,
                                ContentType=content_type,
                                ContentEncoding=content_encoding)
                    if s3_response['ResponseMetadata']['HTTPStatusCode']==200:
                        print('.', end="")
#                        print ("{} uploaded".format(file_name))

            except KeyError:
                pass
        except botocore.exceptions.ClientError as e:
            pass


def get_archive(client, archive_name, archive_id, vault_name=None, account_id=None):
    job_description = "webhose_{}".format(archive_name)
    get_archive_job = client.initiate_job(
        vaultName=vault_name,
        accountId=account_id,
        jobParameters={"Description":job_description,"ArchiveId":archive_id,"Type":"archive-retrieval"}
        )
    return get_archive_job['jobId']


def list_jobs(client, vault_name=None,account_id=None,completed="true",all_jobs=[],next_batch=None):
    if not next_batch:
        jobs_batch = client.list_jobs(vaultName=vault_name,accountId=account_id,completed=completed)
    else:
        jobs_batch = client.list_jobs(vaultName=vault_name,accountId=account_id,completed=completed,marker=next_batch)

    for job in jobs_batch['JobList']:
#        job_data=(job['JobId'],job['JobDescription'],job['CreationDate'])
        job_data=(job['JobId'],job['CreationDate'])
        all_jobs.append(job_data)

    if not "Marker" in jobs_batch:
        return all_jobs
    else:
        next_batch=jobs_batch['Marker']
        list_jobs(client, vault_name,account_id,completed,all_jobs,next_batch)


def get_inventory(client,vault_name=None,account_id=None):
    job = client.initiate_job(
        vaultName=vault_name,
        accountId=account_id,
        jobParameters={"Description":"inventory-job", "Type":"inventory-retrieval", "Format":"JSON"})

    return job['jobId']


def print_retrieval_policy(client,account_id=None):
    policy = client.get_data_retrieval_policy(
            accountId=account_id)

    print(policy)


def main():
    client = boto3.client('glacier')
    args, extra_args = parse_args()

    vault_name = args.vault_name
    account_id = args.account_id
    s3_bucket = args.s3_bucket
    if len(extra_args)!=0:
        job_id = extra_args[0]
    else:
        job_id = None

    if args.in_progress:
        completed = "false"
    else:
        completed = "true"

    if args.new_inventory_job:
        inventory_job_id = get_inventory(client,vault_name,account_id)
        print("Submitted new inventory job with id: {}".format(inventory_job_id))
    elif args.list:
        jobs = []
        list_jobs(client,vault_name,account_id,completed,jobs)
        print("We have a total of {} jobs".format(len(jobs)))
        for job_id,creation_date in sorted(jobs,key=lambda (k,v): (v,k)):
            print(job_id)
    elif job_id:
        if args.retrieve_files:
            files=list_inventory(client,job_id,vault_name,account_id)
            retrieve_files_job(client,files,vault_name,account_id)
        elif args.inventory:
            files=list_inventory(client,job_id,vault_name,account_id)
            print("Archive has {} objects".format(len(files)))
            for file_id,file_name,size in files:
                print("Object Id: {}, Object Name: {}, Object Size: {}".format(file_id,file_name,size))
        elif args.s3_bucket:
            glacier_to_s3(client,job_id,vault_name,account_id,s3_bucket)
        else:
            verbose=True
            get_job_status(client,job_id,vault_name,account_id,verbose)
    elif args.s3_bucket and not job_id:
        jobs = []
        list_jobs(client,vault_name,account_id,completed,jobs)
        for job_id,creation_date in sorted(jobs,key=lambda (k,v): (v,k)):
#            print(job_id,"\n")
            glacier_to_s3(client,job_id,vault_name,account_id,s3_bucket)


def parse_args():
    parser = argparse.ArgumentParser(description='Get the output of a glacier job.')

    parser.add_argument('-v', '--vault-name', required=True, default='webhose',
                        help='The name of the vault to operate on')
    parser.add_argument('-l', '--list', action='store_true',
                        help='List all running jobs on vault')
    parser.add_argument('--in-progress', action='store_true',
                        help='show only jobs in progress')
    parser.add_argument('-i', '--inventory', action='store_true',
                        help='show what is in the inventory')
    parser.add_argument('-r', '--retrieve-files', action='store_true',
                        help='download files')
    parser.add_argument('-n', '--new-inventory-job', action='store_true',
                        help='start a new inventory job')
    parser.add_argument('-s', '--s3-bucket',
                        help='s3 bucket to download file to')
    parser.add_argument('-a', '--account-id',
                        help='the account id to retrieve data from')

    return parser.parse_known_args()


if __name__ == '__main__':
    main()