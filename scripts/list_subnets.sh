#!/bin/bash

# Provide a list of subnets

aws ec2 describe-subnets --query 'Subnets[].[CidrBlock, AvailabilityZone, Tags[?Key==`Name`].Value[] | [0]]' --output text | sort -n -t . -k 1,1 -k 2,2 -k 3,3 -k 4,4

