# Systems Engineer Homework

## Notes

This was originally meant as the solution for a "homework" assigment for a job for which I had applied.  I don't have the original text of the assignment available, but the gist is to create an instance of [SonarQube](https://www.sonarqube.org) in a new/separate VPC with external access only allowed via some predetermined "office" IP addresses.

## Description of solution

My solution to the Systems Engineer Homework was to deploy the entire stack via CloudFormation.  The CloudFormation stack is created via a JSON based template (SonarQube.json in this repo).  This stack is mostly self-contained as the only item needing to exist prior to deploying is an EC2 Key Pair.  The CloudFormation stack includes its own VPC, Internet Gateway, NAT Gateway, Subnets, and Security Groups.  It was designed to be "mostly" region agnostic, in that it should work in us-{east,west}-[1-2], this limitation is based on mapping the current Amazon Linux AMI on a per region basis.

### Architecture

The subnets in the VPC are configured as such:  A pair of external subnets (one per availability zone) for the ELBs, Internet and NAT Gateways; a pair of "internal web" subnets for the instance running the SonarQube application; and a pair of "internal DB" subnets for the database cluster/instances.  For simplicity sake I only initialized subnets in the first two availability zones in the regions.

Security groups are configured such that only the "internal web" subnets can talk to the "internal DB" subnets on port 3306; only the external subnets can talk to the "internal web" subnets on port 9000 (SonarQube port); and only the provided "office" IP addresses can talk to the external subnets (ELBs) on port 80 (HTTP).

**NOTE:** I would have implemented this solution with HTTPS in place of the HTTP, but that requires a certificate, which would require domain validation.

The SonarQube instance lives in an AutoScaling Group such that it can be recreated if necesseary.  The Launch Configuration for the ASG includes the facility for creating the database and database user if they do not already exist.  It also installs the SolarQube application using a yum repository.

A Dashboard (named SonarQube) is created that consists of two widgets, one for the EC2 instance CPU Utilization and one for the DB Cluster CPU Utilization (specifically the nstance running as the writer role, a.k.a. the active cluster member).

## Launching the CloudFormation stack

### Prerequisistes

In order to deploy the solution you will need the following:

* A valid EC2 Key Pair
* The SonarQube.json CloudFormation stack template contained in this repo

### Parameters

The CloudFormation stack makes use of the following parameters:

* **EC2InstanceType** - Instance type on which SonarQube runs (default: c4.large, limited to EBS optimized instance types)
* **DBInstanceType** - Instance type for the two DB instances in the Aurora DB cluster (default:  db.r4.large, limited to Aurora DB instance types)
* **EC2KeyPair** - EC2 Key Pair for the EC2 instance(s) created to run SonarQube
* **SonarQubeMySQLPassword** - Password for the SonarQube database user
* **MasterMySQLPassword** - "Root" password for the Aurora DB cluster created

### Command Line

Use the following command line to create the CloudFormation stack, substituting values for the parameters as necessary (KEY PAIR NAME, PASSWORD1, and PASSWORD2) and adding parameters for EC2InstanceType and/or DBInstanceType if needing to deviate from the defaults.  If the path to the SonarQube.json template is something other than the current directory, make sure to specify it as well as the exmple below is based on its being in the current directory.

```
aws cloudformation create-stack --stack-name SonarQube --template-body file://SonarQube.json --parameters ParameterKey=EC2KeyPair,ParameterValue=<KEY PAIR NAME> ParameterKey=SonarQubeMySQLPassword,ParameterValue=<PASSWORD1> ParameterKey=MasterMySQLPassword,ParameterValue=<PASSWORD2> --capabilities CAPABILITY_NAMED_IAM --tags "Key=Application,Value=SonarQube”
```

This command should return pretty quickly and You should see output similar to the following.

```
{
    "StackId": "arn:aws:cloudformation:us-west-2:123456789012:stack/SonarQube/27d7cac0-d2fa-11e7-b4c6-503f2a2cee82"
}
```

The creation of all of the resources contained within the stack can take up to 15 minutes to become available, during this time you can check on the current status of the stack by running the following command, using the ARN for the StackId from above.

```
aws cloudformation describe-stacks --stack-name arn:aws:cloudformation:us-west-2:123456789012:stack/SonarQube/27d7cac0-d2fa-11e7-b4c6-503f2a2cee82 --query 'Stacks[*].StackStatus'
[
    "CREATE_IN_PROGRESS"
]
```

If you see a status of "ROLLBACK_IN_PROGRESS" or "ROLLBACK_COMPLETED" then a failure occurred when attempting to create one of the defined resources.  This would require some additional work and I have failed you. :disappointed:

Once all of the resources have been created successfully you should see the following status.
 
```
[
    "CREATE_COMPLETE"
]
```

The template is configured to provied the external URL for the ELB as its output.  To see this output, run the following command.

```
aws cloudformation describe-stacks --stack-name arn:aws:cloudformation:us-west-2:123456789012:stack/SonarQube/27d7cac0-d2fa-11e7-b4c6-503f2a2cee82 --query 'Stacks[*].Outputs'
[
    [
        {
            "Description": "DNS name of the created ELB",
            "OutputKey": "SonarQubeURL",
            "OutputValue": "http://SonarQubeELB-890951963.us-west-2.elb.amazonaws.com/"
        }
    ]
]
```

At this point you should be able to access SonarQube using the URL above.

## Cleaning up

To delete the stack and all of its resources, run the following command.

```
aws cloudformation delete-stack --stack-name arn:aws:cloudformation:us-west-2:123456789012:stack/SonarQube/27d7cac0-d2fa-11e7-b4c6-503f2a2cee82
```

You can then run the same describe-stacks command as above while the delete is occurring, you will see "DELETE_IN_PROGRESS".  Once it completes you should see "DELETE_COMPLETE".

## References

[AWS CloudFormation Template Reference](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html)

[AWS EBS-Optimized Instances](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSOptimized.html)
