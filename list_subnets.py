#!/usr/bin/env python

# Provide a list of subnets

import boto3
import re

region = 'us-west-2'

ec2 = boto3.client('ec2', region)

subnets = ec2.describe_subnets()

unsorted = []

for subnet in subnets['Subnets']:
    for tag in subnet['Tags']:
        if tag['Key'] == 'Name':
            name = tag['Value']
        unsorted.append({'cidr': subnet['CidrBlock'], 'az': subnet['AvailabilityZone'], 'name': name})

# Sort by subnet IP
output = sorted(unsorted, key=lambda ip:  tuple(map(int, re.split('\.|/', ip['cidr']))))
for out in output:
    print("{:24}{:16}{}".format(out['cidr'], out['az'], out['name']))
