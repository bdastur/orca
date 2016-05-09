#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from ConfigParser import SafeConfigParser
import boto3
import botocore


class AwsConfig(object):
    '''
    The class provides functionality to read the was configuration.
    '''
    def __init__(self):
        homedir = os.environ.get('HOME', None)
        if homedir is None:
            print "ERROR: HOME ENV is not set."
            return
        self.__config_file = os.path.join(homedir, ".aws/credentials")

        if not os.path.exists(self.__config_file):
            print "ERROR: No aws credentials/config file present"
            return

        self.cfgparser = SafeConfigParser()
        self.cfgparser.read(self.__config_file)

    def get_profiles(self):
        '''
        Return the profiles configured in the aws configuration file
        '''
        return self.cfgparser.sections()


class AwsService(object):
    '''
    The class provides a simplified interface on the
    boto3 client library. Also it can handle use case of managing multiple
    environments by reading the aws configuration file and maintaining
    sessions to each environment.
    '''
    def __init__(self,
                 service,
                 profile_names=None,
                 access_key_id=None,
                 secret_access_key=None):
        '''
        Create a service client to one or more environments by name.

        :type service: string
        :param service: The name of the service ('s3', 'ec2', 'iam', etc.

        :type profile_names: list of strings
        :param profile_names: A list of profile names to create create
            client connections.

        :type access_key_id: string
        :param access_key_id: The access key to use when creating the
            client. If a profile_name is provided then it will superceed this
            parameter.

        :type secret_access_key: string
        :param secret_access_key: The secret key used when creating the
            client.

        Note: If none of the optional parameters are provided then
            the default credentials in ~/.aws/config default section will
            be used with the default profile.

        '''
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
            print "Profiles: ", profiles

            for profile in profiles:
                session = boto3.Session(profile_name=profile)
                self.clients[profile] = session.client(service)

    def list_buckets(self, profile_names=None):
        '''
        Return all the buckets.

        :type profile_names: List of Strings
        :param profile_names: List of profiles. If Not set then get list
            of buckets from all profiles/environments.

        '''
        bucketlist = []
        for profile in self.clients.keys():
            if profile_names is not None and \
                    profile not in profile_names:
                continue

            buckets = self.clients[profile].list_buckets()

            for bucket in buckets['Buckets']:
                bucket['profile_name'] = []
                # Before we add the bucket to the list check if it
                # already exist. Since bucket is a global entity it
                # could show up in multiple profiles if there are
                # different profiles for same account/env with different
                # regions
                bucket_present = False
                for savedbucket in bucketlist:
                    if bucket['Name'] == savedbucket['Name']:
                        savedbucket['profile_name'].append(profile)
                        bucket_present = True
                        break
                if bucket_present is False:
                    bucket['profile_name'].append(profile)
                    bucketlist.append(bucket)
                #bucketlist.append(bucket)
        return bucketlist

    def populate_bucket_location(self, bucketlist):
        '''
        Update the bucket information with bucket location.

        :type bucketlist: List of bucket (list of dictionaries)
        :param bucketlist: List of buckets

        '''

        for bucket in bucketlist:
            profile = bucket['profile_name'][0]
            locationdata = self.clients[profile].get_bucket_location(
                Bucket=bucket['Name'])
            bucket['LocationConstraint'] = locationdata['LocationConstraint']

    def populate_bucket_policy(self, bucketlist):
        '''
        Update the bucket information with bucket policy.

        :type bucketlist: List of buckets (list of dictionaries)
        : param bucketlist: List of buckets

        '''

        for bucket in bucketlist:
            profile = bucket['profile_name'][0]
            try:
                policydata = self.clients[profile].get_bucket_policy(
                    Bucket=bucket['Name'])
                bucket['Policy'] = policydata['Policy']
            except botocore.exceptions.ClientError:
                bucket['Policy'] = None

    def create_bucket(self, bucket_name):
        '''
        test
        '''
        pass

