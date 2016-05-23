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
import botocore

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



@app.route("/rundeck/iam/groups/")
def rundeck_list_groups():
    '''
    Return the list of groups from all available profiles
    '''
    resp_obj = {}

    awsconfig = aws_config.AwsConfig()
    profiles = awsconfig.get_profiles()
    for profile in profiles:
        session = boto3.Session(profile_name=profile)
        iamclient = session.client('iam')

        try:
            groupinfo = iamclient.list_groups()
        except botocore.exceptions.ClientError:
            groupinfo['Groups'] = []

        for group in groupinfo['Groups']:
            grouptext = "(%s) %s" % (profile, group['GroupName'])
            resp_obj[grouptext] = group['GroupName']

    return jsonify(resp_obj)


@app.route("/rundeck/iam/policies/")
def rundeck_list_iam_policies():
    '''
    Return the list of profiles from all available profiles
    '''
    resp_obj = {}

    awsconfig = aws_config.AwsConfig()
    profiles = awsconfig.get_profiles()

    for profile in profiles:
        session = boto3.Session(profile_name=profile)
        iamclient = session.client('iam')

        try:
            policyinfo = iamclient.list_policies()
        except botocore.exceptions.ClientError:
            policyinfo['Policies'] = []

        for policy in policyinfo['Policies']:
            policytext = "(%s) %s" % (profile, policy['PolicyName'])
            resp_obj[policytext] = policy['PolicyName']

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

    try:
        groupinfo = iamclient.list_groups()
    except botocore.exceptions.ClientError:
        groupinfo['Groups'] = []

    groups = []
    for group in groupinfo['Groups']:
        groups.append(group['GroupName'])

    resp_obj['groups'] = groups

    return jsonify(resp_obj)



def main():
    app.run(debug=True, host="0.0.0.0", port=5001)


if __name__ == '__main__':
    main()
