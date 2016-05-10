#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from orcalib.aws_config import AwsConfig


class AwsServiceEC2(object):
    '''
    The class provides a simpler abstraction to the AWS boto3
    EC2 client interface
    '''
    def __init__(self,
                 profile_names=None,
                 access_key_id=None,
                 secret_access_key=None):
        '''
        Create a EC2 service client to one ore more environments by name.
        '''
        service = 'ec2'
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

    def list_vms(self, profile_names=None):
        '''
        Return all the buckets.

        :type profile_names: List of Strings
        :param profile_names: List of profiles. If Not set then get list
            of buckets from all profiles/environments.

        '''
        pass
