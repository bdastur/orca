#!/usr/bin/env python
# -*- codinag: utf-8 -*-

'''
orcaserver:
Orca Server is a simple restful server, that will invoke the orcalib
to return the appropriate information.

The first usecase for this server is with Rundeck Job definitions. Rundeck
can invoke the rest apis to get the correct parameter values rather than
hardcoded values.
'''

from flask import Flask
from flask import jsonify
import orcalib.aws_config as aws_config
import boto3


app = Flask(__name__)


@app.route("/")
def index():
    '''
    Default path to orca server. List all the services available
    '''
    services = ['s3', 'iam', 'ec2']
    resp_obj = {}
    resp_obj['services'] = services
    return jsonify(resp_obj)


@app.route("/<profile>/iam/groups/")
def list_groups(profile):
    '''
    Return all the groups.
    '''
    resp_obj = {}
    resp_obj['status'] = 'OK'
    awsconfig = aws_config.AwsConfig()
    profiles = awsconfig.get_profiles()

    profile_valid = False
    for configuredprofile in profiles:
        if profile == configuredprofile:
            profile_valid = True

    if not profile_valid:
        resp_obj['status'] = 'FAIL'
        return jsonify(resp_obj)

    session = boto3.Session(profile_name=profile)
    iamclient = session.client('iam')

    groupinfo = iamclient.list_groups()
    groups = []
    for group in groupinfo['Groups']:
        groups.append(group['GroupName'])

    resp_obj['groups'] = groups

    return jsonify(resp_obj)




def main():
    app.run(debug=True, host="0.0.0.0", port=5001)


if __name__ == '__main__':
    main()
