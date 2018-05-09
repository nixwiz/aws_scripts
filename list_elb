#!/usr/bin/env python

# Provide a list of ELBv2 DNS names for sites (assumes a Site tag for the ELB)

import boto3
from operator import itemgetter

region='us-west-2'

elbv2 = boto3.client('elbv2', region)

lbs = elbv2.describe_load_balancers()

unsorted = []

for lb in lbs['LoadBalancers']:
    lbtag = elbv2.describe_tags(ResourceArns=[lb['LoadBalancerArn']])
    for tag in lbtag['TagDescriptions'][0]['Tags']:
        if tag['Key'] == 'Site':
            unsorted.append({'site':tag['Value'],'dnsname':lb['DNSName']})

# Sort it by the site name
output = sorted(unsorted, key=itemgetter('site'))
for out in output:
    print("{:36}\t{}".format(out['site'], out['dnsname']))
