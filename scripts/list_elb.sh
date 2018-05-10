#!/bin/bash

# Provide a list of ELBv2 DNS names for sites (assumes a Site tag for the ELB)

export AWS_DEFAULT_OUTPUT="text"

for ARN in $(aws elbv2 describe-load-balancers --query 'LoadBalancers[].LoadBalancerArn')
do
    
    SITE=$(aws elbv2 describe-tags --resource-arns ${ARN} --query 'TagDescriptions[].Tags[?Key==`Site`].Value[] | [0]')
    DNSNAME=$(aws elbv2 describe-load-balancers --query 'LoadBalancers[].DNSName' --load-balancer-arns ${ARN})

    printf "%-36s\t%s\n" ${SITE} ${DNSNAME}
done | sort

