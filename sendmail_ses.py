#!/usr/bin/python3.6

# Quick, dirty, ugly script to mimic use of sendmail -i -t but to send the email via SES
# Mainly meant to be used by superlance/crashmail for notifications from supervisord which
# assumes the above functionality
#
# This keeps from having the email show up from a random EC2 instance and having to add
# the NAT gateway to the SPF record, having to run sendmail locally, etc.

import sys
import boto3
import getopt
import sys


def main(argv):

    # Get the list of mail recipients. Yes this seems redundant since the -m option of crashmail itself
    # provides this, but it doesn't support multiple recipients.  We need to also be able to add some of
    # the devs as recipients.
    mailto = ''

    try:
        opts, args = getopt.getopt(argv,"m:",["mailto="])
    except getopt.GetoptError:
        print ('sendmail_ses.py -m <comma seperated list of email addresses, without spaces>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-m':
            mailto = arg

    mailtolist = mailto.split(",")

    # Read in the message and parse out the headers. superlance/crashmail seems to only send
    # the following based on this example so it is all we care about:
    #
    # To: devops@riskproadvisor.com
    # Subject:  filewatcher crashed at 2018-04-04 14:46:23,031
    # 
    # Process filewatcher in group filewatcher exited unexpectedly (pid 5296) from state RUNNING

    lines = sys.stdin.readlines()

    headers_done = 0
    body = ""

    for line in lines:
        if headers_done == 1:
            body = body + line
        elif line.startswith('\n'):
            headers_done = 1
        elif line.startswith('To: '):
            recipient = line[4:].rstrip()
        elif line.startswith('Subject: '):
            subject = line[9:].rstrip().lstrip(' ')

    # if crashmail defined recipient is not in list, add it
    if recipient not in mailtolist:
        mailtolist.append(recipient)

    # Now send the message via SES
    client = boto3.client('ses')

    response = client.send_email(
        Destination={
            'BccAddresses': [
            ],
            'CcAddresses': [
            ],
            'ToAddresses': mailtolist,
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': body,
                },
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': body,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject,
            },
        },
        Source='devops@riskproadvisor.com',
    )

    # print(response)

if __name__ == "__main__":
   main(sys.argv[1:])

