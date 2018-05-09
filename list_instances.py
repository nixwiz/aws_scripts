#!/usr/bin/env python

# provide a list of instances along with some useful information
# Assumes the use of Tags:  Site and Name

import boto3
from operator import itemgetter

region = 'us-west-2'

ec2 = boto3.client('ec2', region)

instances = ec2.describe_instances()

unsorted = []

print("{:20}\t{:15}\t{:30}\t{:10}\t{:10}\t{:20}".format('Name', 'IP Address', 'Site', 'State', 'Type', 'Instance ID'))
for reservation in instances['Reservations']:
   for instance in reservation['Instances']:
       if instance['State']['Name'] != 'terminated':
           site = 'None'
           name = 'None'
           for tag in instance['Tags']:
               if tag['Key'] == 'Name':
                   name = tag['Value']
               if tag['Key'] == 'Site':
                   site = tag['Value']
           unsorted.append({'name':name,'ip':instance['PrivateIpAddress'],'site':site,'state':instance['State']['Name'],'type':instance['InstanceType'],'id':instance['InstanceId']})

# Sort it by the site name
output = sorted(unsorted, key=itemgetter('site'))
for out in output:
    print("{:20}\t{:15}\t{:30}\t{:10}\t{:10}\t{:20}".format(out['name'], out['ip'], out['site'], out['state'], out['type'], out['id']))
