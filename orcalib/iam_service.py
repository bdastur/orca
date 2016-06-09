#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import botocore
from orcalib.aws_config import AwsConfig


class AwsServiceIAM(object):
    '''
    The class provides a simpler abstraction to the AWS boto3
    iam client interface
    '''
    def __init__(self,
                 profile_names=None,
                 access_key_id=None,
                 secret_access_key=None):
        '''
        Create a iam service client to one ore more environments by name.
        '''
        service = 'iam'
        self.clients = {}

        if profile_names is not None:
            for profile_name in profile_names:
                session = boto3.Session(profile_name=profile_name)
                self.clients[profile_name] = session.client(service)
        elif access_key_id is not None and secret_access_key is not None:
            self.clients['default'] = boto3.client(
                service,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key)
        else:
            awsconfig = AwsConfig()
            profiles = awsconfig.get_profiles()

            for profile in profiles:
                session = boto3.Session(profile_name=profile)
                self.clients[profile] = session.client(service)

    def list_users(self, profile_names=None):
        '''
        Return all the users

        :type profile_names: List of Strings
        :param profile_names: List of profiles. If Not set then get list
            of buckets from all profiles/environments.

        '''
        userlist = []
        for profile in self.clients.keys():
            if profile_names is not None and \
                    profile not in profile_names:
                continue

            users = self.clients[profile].list_users()
            for user in users['Users']:
                user['profile_name'] = profile
                userlist.append(user)

        return userlist

    def populate_groups_in_users(self, userlist):
        '''
        Populate the user information with group membership
        '''
        for user in userlist:
            profile = user['profile_name']
            groupdata = self.clients[profile].list_groups_for_user(
                UserName=user['UserName'])
            user['Groups'] = groupdata['Groups']

    def get_user_attached_policies(self,
                                   UserName=None,
                                   profile_name=None):
        '''
        Return all policies attached to user or a group to which
        the user belongs.
        '''
        if UserName is None or profile_name is None:
            print "Error: Expected UserName and profile_name"
            return None

        client = self.clients[profile_name]

        try:
            client.get_user(UserName=UserName)
        except botocore.exceptions.ClientError as clienterr:
            print "[%s: %s] User not found [%s]" % \
                (profile_name, UserName, clienterr)

        user_groups = client.list_groups_for_user(UserName=UserName)

        policies = []
        # Get policies attached to groups
        for group in user_groups['Groups']:
            group_policies = client.list_attached_group_policies(
                GroupName=group['GroupName'])
            for policy in group_policies['AttachedPolicies']:
                policies.append(policy)


        # Get policies attached to user
        user_policies = client.list_attached_user_policies(
            UserName=UserName)
        for policy in user_policies['AttachedPolicies']:
            policies.append(policy)

        return policies

    def get_user_permissions(self,
                             UserName=None,
                             profile_name=None):
        '''
        Return all the permissions information for a given user
        '''
        if UserName is None or profile_name is None:
            print "Error: Expected UserName and profile_name"
            return None

        client = self.clients[profile_name]

        try:
            client.get_user(UserName=UserName)
        except botocore.exceptions.ClientError as clienterr:
            print "[%s : %s ] User not found [%s]" % \
                (profile_name, UserName, clienterr)
            return None

        policies = self.get_user_attached_policies(UserName=UserName,
                                                   profile_name=profile_name)

        statements = []
        for policy in policies:
            policy_version_info = client.list_policy_versions(
                PolicyArn=policy['PolicyArn'])
            # Now that we have version info, select only
            # the policy that is default.
            for version in policy_version_info['Versions']:
                if version['IsDefaultVersion'] is True:
                    policy_data = client.get_policy_version(
                        PolicyArn=policy['PolicyArn'],
                        VersionId=version['VersionId'])
                    policy_statements = \
                        policy_data['PolicyVersion']['Document']['Statement']
                    for statement in policy_statements:
                        statements.append(statement)

        return statements

    def get_user_groups(self,user):
        profile = user['profile_name']
        groupdata = self.clients[profile].list_groups_for_user(
                        UserName=user['UserName'])
        return groupdata['Groups']







