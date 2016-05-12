#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from orcalib.aws_config import AwsConfig
from orcalib.aws_config import OrcaConfig


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
            awsconfig = AwsConfig()
            profiles = awsconfig.get_profiles()

            for profile in profiles:
                session = boto3.Session(profile_name=profile)
                self.clients[profile] = {}
                for region in self.regions:
                    self.clients[profile][region] = \
                        session.client(service,
                                       region_name=region)

    def list_vms(self, profile_names=None, regions=None):
        '''
        Return all the buckets.

        :type profile_names: List of Strings
        :param profile_names: List of profiles. If Not set then get list
            of buckets from all profiles/environments.

        '''
        vm_list = []
        for profile in self.clients.keys():
            if profile_names is not None and \
                    profile not in profile_names:
                continue
            for region in self.regions:
                if regions is not None and \
                        region not in regions:
                    continue

                vms = self.clients[profile][region].describe_instances()
                for vm in vms['Reservations']:
                    vm['profile_name'] = []
                    vm_present = False
                    for savedvm in vm_list:
                        if vm['ReservationId'] == savedvm['ReservationId']:
                            savedvm['profile_name'].append(profile)
                            vm_present = True
                            break
                    if vm_present is False:
                        vm['region'] = region
                        vm['profile_name'].append(profile)
                        vm_list.append(vm)

        return vm_list






