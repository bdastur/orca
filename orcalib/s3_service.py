#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import boto3
import botocore
from orcalib.aws_config import AwsConfig
from orcalib.aws_config import OrcaConfig


class AwsServiceS3(object):
    '''
    The class provides a simpler abstraction to the AWS boto3
    S3 client interface
    '''
    def __init__(self,
                 profile_names=None,
                 access_key_id=None,
                 secret_access_key=None):
        '''
        Create a S3 service client to one ore more environments by name.
        '''
        service = 's3'
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
            try:
                buckets = self.clients[profile].list_buckets()
            except botocore.exceptions.ClientError as clienterr:
                print "Client Error: [%s] [%s] " % (profile, clienterr)
                continue


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
        :param bucketlist: List of buckets

        '''

        for bucket in bucketlist:
            profile = bucket['profile_name'][0]
            try:
                policydata = self.clients[profile].get_bucket_policy(
                    Bucket=bucket['Name'])
                bucket['Policy'] = policydata['Policy']
            except botocore.exceptions.ClientError:
                bucket['Policy'] = None

    def populate_bucket_objects(self, bucketlist):
        '''
        Update the buckets information with list of objects.

        :type bucketlist: List of buckets (list of dictionaries)
        :param bucketlist: List of buckets

        '''

        for bucket in bucketlist:
            profile = bucket['profile_name'][0]
            objectdata = self.clients[profile].list_objects(
                Bucket=bucket['Name'])
            bucket['objects'] = []

            try:
                contents = objectdata['Contents']
            except KeyError:
                bucket['objects'] = None
                bucket['object_count'] = 0
                bucket['object_size'] = 0
                bucket['LastModified'] = 0
                continue

            objcount = 0
            objsize = 0
            lastmodified = -1
            for content in contents:
                objinfo = {}
                objcount += 1
                objsize = objsize + content['Size']
                objinfo['Key'] = content['Key']
                objinfo['Size'] = content['Size']
                objinfo['LastModified'] = content['LastModified']
                if lastmodified == -1:
                    lastmodified = objinfo['LastModified']
                else:
                    if lastmodified < objinfo['LastModified']:
                        lastmodified = objinfo['LastModified']
                bucket['objects'].append(objinfo)
            bucket['object_count'] = objcount
            bucket['object_size'] = objsize
            bucket['LastModified'] = lastmodified

    def populate_bucket_tagging(self, bucketlist):
        '''
        Update the buckets information with tagging info.

        :type bucketlist: List of buckets (List of dictionaries)
        :param bucketlist: List of buckets
        '''
        for bucket in bucketlist:
            profile = bucket['profile_name'][0]
            try:
                tagdata = self.clients[profile].get_bucket_tagging(
                    Bucket=bucket['Name'])
            except botocore.exceptions.ClientError:
                # In case there are no tags for the bucket,
                # an exception is thrown.
                bucket['TagSet'] = None
                continue

            bucket['TagSet'] = tagdata['TagSet']

    def populate_bucket_validation(self, bucketlist):
        '''
        The API will validate the buckets  by looking at the
        bucket naming convention and the available tags. It will save
        the result in a dict object which can be later retrieved.

        Note: Make sure to populate bucket tagging before invoking
        this API.

        :type bucketlist: List of buckets (list of dictionaries)
        :param bucketlist: List of buckets
        '''
        orca_config = OrcaConfig()
        tagset = set(orca_config.get_tagset())
        name_pattern = orca_config.get_s3_bucket_naming_policy()

        for bucket in bucketlist:
            bucket['validations'] = {}
            bucket_taglist = []
            try:
                if bucket['TagSet'] is None:
                    bucket_tagset = None
                    bucket['validations']['result'] = 'FAIL'
                    bucket['validations']['tagresult'] = "No Tags Found"
                else:
                    for obj in bucket['TagSet']:
                        bucket_taglist.append(obj['Key'])
                    bucket_tagset = set(bucket_taglist)
                    difference = tagset.difference(bucket_tagset)
                    if len(difference) != 0:
                        bucket['validations']['tagresult'] = "Tags Missing: " \
                            + str(difference)
                        bucket['validations']['result'] = 'FAIL'
            except KeyError:
                bucket['validations']['result'] = 'FAIL'
                bucket['validations']['tagresult'] = "No Tags Found"

            # Validate bucket naming convention.
            if not re.match(name_pattern, bucket['Name']):
                bucket['validations']['nameresult'] = "Invalid Bucket Name"
                bucket['validations']['result'] = 'FAIL'
            else:
                bucket['validations']['nameresult'] = "Bucket Name Valid"

            if bucket['validations'].get('result', None) is None:
                bucket['validations']['result'] = 'PASS'

    def create_bucket(self, bucket_name):
        '''
        test
        '''

