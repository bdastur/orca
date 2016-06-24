#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from orcalib.aws_config import AwsConfig
from orcalib.aws_config import OrcaConfig

class AwsServiceCloudWatch(object):
    '''
    The class provides a simpler abstraction to the AWS boto3
    cloudwatch client interface
    '''
    def __init__(self,
                 profile_names=None,
                 access_key_id=None,
                 secret_access_key=None,
                 iam_role_discover=False):
        '''
        Create a cloudwatch service client to one ore more environments by name.
        '''
        service = 'cloudwatch'

        orca_config = OrcaConfig()
        self.regions = orca_config.get_regions()
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
                self.clients['default'] = {}
                for region in self.regions:
                    self.clients['default'][region] = \
                        session.client(service, region_name=region)
            else:
                awsconfig = AwsConfig()
                profiles = awsconfig.get_profiles()

                for profile in profiles:
                    session = boto3.Session(profile_name=profile)
                    self.clients[profile] = {}
                    for region in self.regions:
                        self.clients[profile][region] = \
                            session.client(service,
                                           region_name=region)

    def list_alarms(self, profile_names=None, regions=None):
        '''
        Return all the alarms.

        :type profile_names: List of Strings
        :param profile_names: List of profiles.

        '''
        alarm_list = []
        for profile in self.clients.keys():
            if profile_names is not None and \
                    profile not in profile_names:
                continue
            for region in self.regions:
                if regions is not None and \
                        region not in regions:
                    continue

                alarms = self.clients[profile][region].describe_alarms()
                for alarm in alarms['MetricAlarms']:
                    alarm['region'] = region
                    alarm['profile_name'] = profile
                    alarm_list.append(alarm)

        return alarm_list
