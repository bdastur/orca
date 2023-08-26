#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import datetime
import jinja2
import json
import multiprocessing as mp
import boto3
import botocore
from orcalib.aws_config import AwsConfig
from orcalib.aws_config import OrcaConfig



def get_absolute_path_for_file(file_name, splitdir=None):
    '''
    Return the filename in absolute path for any file
    passed as relative path.
    '''
    base = os.path.basename(__file__)
    if splitdir is not None:
        splitdir = splitdir + "/" + base
    else:
        splitdir = base

    if os.path.isabs(__file__):
        abs_file_path = os.path.join(__file__.split(splitdir)[0],
                                     file_name)
    else:
        abs_file = os.path.abspath(__file__)
        abs_file_path = os.path.join(abs_file.split(splitdir)[0],
                                     file_name)

    return abs_file_path


class AwsServiceS3(object):
    '''
    The class provides a simpler abstraction to the AWS boto3
    S3 client interface
    '''
    def __init__(self,
                 profile_names=None,
                 access_key_id=None,
                 secret_access_key=None,
                 iam_role_discover=False):
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
            if iam_role_discover:
                session = boto3.Session()
                self.clients['default'] = session.client(service)
            else:
                awsconfig = AwsConfig()
                profiles = awsconfig.get_profiles()

                for profile in profiles:
                    session = boto3.Session(profile_name=profile)
                    self.clients[profile] = session.client(service)

    def list_buckets_fast(self):
        buckets = []
        jobs = []
        for profile in self.clients.keys():
            queue = mp.Queue()
            kwargs = {'profile_names': profile,
                      'queue': queue}

            process = mp.Process(target=self.list_buckets,
                                 kwargs=kwargs)
            process.start()
            jobs.append((process, queue))

        count = 0
        for job in jobs:
            process = job[0]
            queue = job[1]
            process.join()
            profile_buckets = queue.get()
            buckets.extend(profile_buckets)
            count += 1

        for job in jobs:
            process = job[0]
            if process.is_alive():
                process.terminate()

        return buckets

    def list_buckets(self, profile_names=None, queue=None):
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
                print("Client Error: [%s] [%s] " % (profile, clienterr))
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

        if queue is not None:
            queue.put(bucketlist)

        return bucketlist

    def populate_bucket_fast(self, oper, bucketlist):
        '''
        Multiprocess API to populate bucket info
        '''
        batch_size = 10
        jobs = []

        for count in range(0, len(bucketlist), batch_size):
            if oper == "location":
                api = self.populate_bucket_location
            elif oper == "policy":
                api = self.populate_bucket_policy
            elif oper == "objects":
                api = self.populate_bucket_objects
            elif oper == "tagging":
                api = self.populate_bucket_tagging
            elif oper == "validation":
                api = self.populate_bucket_validation
            else:
                api = None
                print("Invalid operation")
                return
            queue = mp.Queue()
            kwargs = {'queue': queue}
            process = mp.Process(target=api,
                                 args=(bucketlist[count:count + batch_size],),
                                 kwargs=kwargs)
            process.start()
            jobs.append((process, queue))

        newbucketlist = []
        for job in jobs:
            process = job[0]
            queue = job[1]
            templist = queue.get()
            newbucketlist.extend(templist)
            process.join()

        for job in jobs:
            if job[0].is_alive():
                job[0].terminate()

        return newbucketlist

    def populate_bucket_location(self, bucketlist, queue=None):
        '''
        Update the bucket information with bucket location.

        :type bucketlist: List of bucket (list of dictionaries)
        :param bucketlist: List of buckets
        '''
        newlist = []
        for bucket in bucketlist:
            profile = bucket['profile_name'][0]
            try:
                locationdata = self.clients[profile].get_bucket_location(
                    Bucket=bucket['Name'])
                bucket['LocationConstraint'] = \
                    locationdata['LocationConstraint']
            except botocore.exceptions.ClientError as botoerr:
                print("Failed: [get bucket location] [%s] [%s] " % \
                    (bucket['Name'], botoerr))
                bucket['LocationConstraint'] = None

        if queue:
            newlist = bucketlist
            queue.put(newlist)

    def populate_bucket_policy(self, bucketlist, queue=None):
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

        if queue:
            queue.put(bucketlist)

    def populate_bucket_objects(self, bucketlist, queue=None):
        '''
        Update the buckets information with list of objects.

        :type bucketlist: List of buckets (list of dictionaries)
        :param bucketlist: List of buckets

        '''
        for bucket in bucketlist:
            profile = bucket['profile_name'][0]
            try:
                objectdata = self.clients[profile].list_objects(
                    Bucket=bucket['Name'])
                bucket['objects'] = []
            except botocore.exceptions.ClientError as botoerr:
                print("Failed: [get bucket objects ] [%s] [%s] " % \
                    (bucket['Name'], botoerr))
                bucket['objects'] = None
                bucket['object_count'] = 0
                bucket['object_size'] = 0
                bucket['LastModified'] = 0
                continue

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

        if queue:
            queue.put(bucketlist)

    def populate_bucket_tagging(self, bucketlist, queue=None):
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

            bucket['TagSet'] = {}
            for tagitem in tagdata['TagSet']:
                bucket['TagSet'][tagitem['Key']] = tagitem['Value']

        if queue:
            queue.put(bucketlist)

    def populate_bucket_validation(self, bucketlist, queue=None):
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
                    for key in bucket['TagSet'].keys():
                        bucket_taglist.append(key)
                    bucket_tagset = set(bucket_taglist)
                    difference = tagset.difference(bucket_tagset)
                    if len(difference) != 0:
                        bucket['validations']['tagresult'] = "Tags Missing: " \
                            + str(difference)
                        bucket['validations']['result'] = 'FAIL'
                    else:
                        bucket['validations']['tagresult'] = "All Tags Found"
                        bucket['validations']['result'] = 'PASS'
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

        if queue:
            queue.put(bucketlist)

    def generate_new_s3_lifecycle_policy_document(self,
                                                  policyobj):
        '''
        Generate a new S3 lifecycle policy document
        '''

        searchpath = get_absolute_path_for_file("./")
        templatefile = "./templates/s3_lifecycle_policy.j2"
        now = datetime.datetime.now()
        timestamp = "%s%s" % (str(now.microsecond), str(now.second))

        for rule in policyobj['rules']:
            if rule.get('id', None):
                rule['id'] = "rule-%s" % str(timestamp)

        print("policyobj: ", policyobj)
        template_loader = jinja2.FileSystemLoader(searchpath=searchpath)
        env = jinja2.Environment(loader=template_loader,
                                 trim_blocks=False,
                                 lstrip_blocks=False)
        template = env.get_template(templatefile)
        data = template.render(policyobj)
        print("data: ", data)

        jdata = json.loads(data)
        return jdata

    def create_bucket(self, bucket_name):
        '''
        test
        '''

