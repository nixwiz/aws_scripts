#!/bin/bash

# Provide short list of instances

# Needs re-write for spaces in any of the fields (name?)

aws ec2 describe-instances --query 'Reservations[].Instances[].[Tags[?Key==`Name`].Value[] | [0],PrivateIpAddress,Tags[?Key==`Site`].Value[] | [0],State.Name,InstanceType]' --output text | sort | grep -v "terminated" | awk 'BEGIN {printf("%-20s\tIP Address\tSite\t\t\t\tState\tType\n", "Name")} {printf("%-20s\t%-15s\t%-30s\t%s\t%s\n", $1, $2, $3, $4,$5)}'
