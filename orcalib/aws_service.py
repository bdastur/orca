#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import os
#import yaml
#from ConfigParser import SafeConfigParser
from orcalib.s3_service import AwsServiceS3
from orcalib.ec2_service import AwsServiceEC2


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
        if service == "s3":
            self.service = AwsServiceS3(profile_names=profile_names,
                                        access_key_id=access_key_id,
                                        secret_access_key=secret_access_key)
        elif service == "ec2":
            self.service = AwsServiceEC2(profile_names=profile_names,
                                         access_key_id=access_key_id,
                                         secret_access_key=secret_access_key)
        else:
            print "ERROR: Servicename [%s] not valid"
            return



