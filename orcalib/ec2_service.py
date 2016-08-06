#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import botocore
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
                 secret_access_key=None,
                 iam_role_discover=False):
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
            if iam_role_discover:
                session = boto3.Session()
                self.clients['default'] = {}
                for region in self.regions:
                    self.clients['default'][region] = \
                        session.client(service, region_name=region)
            else:
                self.awsconfig = AwsConfig()
                profiles = self.awsconfig.get_profiles()

                for profile in profiles:
                    session = boto3.Session(profile_name=profile)
                    self.clients[profile] = {}
                    for region in self.regions:
                        self.clients[profile][region] = \
                            session.client(service, region_name=region)

    def list_vms(self, profile_names=None, regions=None):
        '''
        Return all the vms.

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

                try:
                    vms = self.clients[profile][region].describe_instances()
                except botocore.exceptions.ClientError as botoerr:
                    print "List VMS Failed: Account: %s, Region: %s [%s]" % \
                        (profile, region, botoerr)
                    continue

                for vm in vms['Reservations']:
                    vm['region'] = region
                    vm['profile_name'] = profile
                    vm_list.append(vm)

                for vm in vm_list:
                    for instance in vm['Instances']:
                        # Flatten Tags.
                        if instance.get('Tags', None) is not None:
                            if type(instance['Tags']) == list:
                                tags = instance['Tags']
                                instance['Tags'] = {}
                                for tag in tags:
                                    instance['Tags'][tag['Key']] = tag['Value']

                        # Flatten Security Groups
                        if instance.get('SecurityGroups', None) is not None:
                            if type(instance['SecurityGroups']) == list:
                                secgroups = instance['SecurityGroups']
                                instance['SecurityGroups'] = {}
                                for secgroup in secgroups:
                                    instance['SecurityGroups'][secgroup['GroupId']] = \
                                        secgroup['GroupName']

                        # Flatten NetworkInterfaces
                        if instance.get('NetworkInterfaces', None) is not None:
                            if type(instance['NetworkInterfaces']) == list:
                                nw_intfs = instance['NetworkInterfaces']
                                instance['NetworkInterfaces'] = {}
                                instobj = instance['NetworkInterfaces']
                                for nw_intf in nw_intfs:
                                    instobj[nw_intf['NetworkInterfaceId']] = \
                                                    nw_intf



        return vm_list

    def list_reserved_vms(self, profile_names=None, regions=None):
        '''
        Return reserved vms.

        :type profile_names: List of Strings
        :param profile_names: List of profiles. If Not set then get list
            of reserved vms from all profiles/environments.

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

                vms = self.clients[profile][region].\
                    describe_reserved_instances()
                for vm in vms['ReservedInstances']:
                    vm['region'] = region
                    vm['profile_name'] = profile
                    vm_list.append(vm)

        return vm_list

    def list_network_interfaces(self, profile_names=None, regions=None):
        '''
        :param profile_names: List of Strings
        :param regions: List of profiles
        :return:
        '''

        nw_list = []
        for profile in self.clients.keys():
            if profile_names is not None and \
                    profile not in profile_names:
                continue
            for region in self.regions:
                if regions is not None and \
                        region not in regions:
                    continue
                nws = self.clients[profile][region].\
                    describe_network_interfaces()
                for nw in nws['NetworkInterfaces']:
                    nw['region'] = region
                    nw['profile_name'] = profile
                    nw_list.append(nw)

        return nw_list

    def list_images(self, profile_names=None, regions=None):

        '''

        :param profile_names: List of Strings
        :param regions: List of profiles
        :return:
        '''

        image_list = []
        for profile in self.clients.keys():
            if profile_names is not None and \
                    profile not in profile_names:
                continue
            ownerid = self.awsconfig.get_aws_owner_id(profile)
            for region in self.regions:
                if regions is not None and \
                        region not in regions:
                    continue
                images = self.clients[profile][region].\
                    describe_images(Owners=[ownerid])
                for image in images['Images']:
                    image['region'] = region
                    image['profile_name'] = profile
                    image_list.append(image)

        return image_list

    def list_volumes(self, profile_names=None, regions=None):
        vol_list = []
        for profile in self.clients.keys():
            if profile_names is not None and profile not in profile_names:
                continue
            for region in self.regions:
                if regions is not None and region not in regions:
                    continue

                vols = self.clients[profile][region].describe_volumes()

                for vol in vols['Volumes']:
                    vol['region'] = region
                    vol['profile_name'] = profile
                    vol_list.append(vol)

        return vol_list

    def list_snapshots(self, profile_names=None, regions=None):
        snapshots = list()
        for profile in self.clients.keys():
            if profile_names is not None and profile not in profile_names:
                continue

            ownerid = self.awsconfig.get_aws_owner_id(profile)
            for region in self.regions:
                if regions is not None and region not in regions:
                    continue

                snaps = self.clients[profile][region].describe_snapshots(
                    OwnerIds=[ownerid])

                for s in snaps['Snapshots']:
                    s['region'] = region
                    s['profile_name'] = profile
                    snapshots.append(s)

        return snapshots

    def list_security_groups(self,
                             profile_names=None,
                             regions=None,
                             dict_type=False):

        if dict_type:
            security_groups = {}
        else:
            security_groups = list()

        for profile in self.clients.keys():
            if profile_names is not None and profile not in profile_names:
                continue
            for region in self.regions:
                if regions is not None and region not in regions:
                    continue

                client = self.clients[profile][region]
                groups = client.describe_security_groups()
                for group in groups['SecurityGroups']:
                    group_id = group['GroupId']
                    # Format IpPermissions.
                    group_ip_permissions = group['IpPermissions']
                    group['IpPermissions'] = {}
                    for permission in group_ip_permissions:
                        try:
                            from_port = permission['FromPort']
                        except KeyError:
                            from_port = "-1"
                        ip_ranges = permission['IpRanges']
                        permission['IpRanges'] = {}
                        for range in ip_ranges:
                            cidr = range['CidrIp']
                            permission['IpRanges'][cidr] = 1

                        group['IpPermissions'][from_port] = permission

                    # Format IpPermissionsEgress
                    egress_ip_permissions = group['IpPermissionsEgress']
                    group['IpPermissionsEgress'] = {}
                    for permission in egress_ip_permissions:
                        try:
                            from_port = permission['FromPort']
                        except KeyError:
                            from_port = "-1"
                        ip_ranges = permission['IpRanges']
                        permission['IpRanges'] = {}
                        for range in ip_ranges:
                            cidr = range['CidrIp']
                            permission['IpRanges'][cidr] = 1
                        group['IpPermissionsEgress'][from_port] = permission

                    # Format Tags.
                    try:
                        tags = group['Tags']
                    except KeyError:
                        tags = []
                    group['Tags'] = {}
                    for tag in tags:
                        tag_key = tag['Key']
                        group['Tags'][tag_key] = tag['Value']

                    if dict_type:
                        security_groups[group_id] = group
                        security_groups[group_id]['region'] = region
                        security_groups[group_id]['profile_name'] = \
                            profile
                    else:
                        group['region'] = region
                        group['profile_name'] = profile
                        security_groups.append(group)

        return security_groups

    def list_tags(self, profile_names=None, regions=None):

        tagsobj = {}
        for profile in self.clients.keys():
            if profile_names is not None and profile not in profile_names:
                continue
            for region in self.regions:
                if regions is not None and region not in regions:
                    continue

                tags_ = self.clients[profile][region].describe_tags()

                for tag in tags_['Tags']:
                    if tagsobj.get(tag['ResourceId'], None) is None:
                        tagsobj[tag['ResourceId']] = {}

                    obj = tagsobj[tag['ResourceId']]

                    obj['region'] = region
                    obj['profile_name'] = profile
                    obj['ResourceType'] = tag['ResourceType']
                    tagname = "tag_" + tag['Key']
                    obj[tagname] = tag['Value']

        return tagsobj
