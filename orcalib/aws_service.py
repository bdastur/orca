#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3



class AwsService(object):
    '''
    The class provides a simplified interface on the
    boto3 client library
    '''
    def __init__(self,
                 service,
                 profile_name=None,
                 access_key_id=None,
                 secret_access_key=None):
        '''
        Create a service client by name.

        :type service: string
        :param service: The name of the service ('s3', 'ec2', 'iam', etc.

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

        if profile_name is not None:
            session = boto3.Session(profile_name=profile_name)
            self.client = session.client(service)
        elif access_key_id is not None and secret_access_key is not None:
            self.client = boto3.client(
                service,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key)
        else:
            self.client = boto3.client(service)




