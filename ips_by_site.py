#!/usr/bin/env python

# Script to provide list of IP's that are in the target group for a site.
#
# This requires that the ELB have a Site tag that contains the site URL
#

import boto3
import sys


def main(argv):

    if len(sys.argv) != 2:
        print("Site name missing.")
        sys.exit(1)

    site = sys.argv[1]

    region = 'us-west-2'

    elbv2 = boto3.client('elbv2', region)

    lbs = elbv2.describe_load_balancers()

    lbarn = ''
    for lb in lbs['LoadBalancers']:
        lbtag = elbv2.describe_tags(ResourceArns=[lb['LoadBalancerArn']])
        for tag in lbtag['TagDescriptions'][0]['Tags']:
            if tag['Key'] == 'Site':
                if tag['Value'] == site:
                    lbarn = lbtag['TagDescriptions'][0]['ResourceArn']

    if len(lbarn) == 0:
        print("Site {} not found.  Does the ELB have the appropriate Site tag?".format(site))
        sys.exit(1)

    tgs = elbv2.describe_target_groups(LoadBalancerArn=lbarn)

    instanceids = []

    for tg in tgs['TargetGroups']:
        targets = elbv2.describe_target_health(TargetGroupArn=tg['TargetGroupArn'])
        for target in targets['TargetHealthDescriptions']:
            if target['Target']['Id'] not in instanceids:
                instanceids.append(target['Target']['Id'])

    if len(instanceids) == 0:
        print("ELB for {} has no instances in its target group.".format(site))
        sys.exit(1)

    ec2 = boto3.client('ec2', region)

    instances = ec2.describe_instances(InstanceIds=instanceids)

    for reservations in instances['Reservations']:
        for instance in reservations['Instances']:
            print(instance['PrivateIpAddress'])

if __name__ == "__main__":
    main(sys.argv[1:])
