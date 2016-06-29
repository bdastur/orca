#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
CLI Interface to Aws Services.
------------------------------

'''

import pprint
import prettytable
import orcalib.aws_service as aws_service
from collections import defaultdict


class EC2CommandHandler(object):
    def __init__(self):
        print "EC2command handler"

    def display_ec2_summary_table(self, vm_summary):
        '''
        Display EC2 Summary in Tabular output.
        '''
        pass

    def display_ec2_summary(self, outputformat='json'):
        '''
        Display ec2 summary information

        :type format: String ('json' or 'table')
        :param format:  The output format to display.

        '''
        service_client = aws_service.AwsService('ec2')
        vmlist = service_client.service.list_vms()

        # Defaults in case they are not set
        instance_type = 'None'
        vpc_id = 'None'
        zone = 'None'

        type_count = defaultdict(int)
        vpc_count = defaultdict(int)
        zone_count = defaultdict(int)

        # # Setup table
        header = ["Resource", "Count"]

        table = prettytable.PrettyTable(header)

        for vm in vmlist:
            for i in range (len(vm['Instances'])):

                # if 'InstanceType' in vm['Instances'][i]:
                instance_type = vm['Instances'][i]['InstanceType']
                type_count[instance_type] += 1

                if 'VpcId' in vm['Instances'][i]:
                    vpc_id = vm['Instances'][i]['VpcId']
                    vpc_count[vpc_id] += 1

                if 'Placement' in vm['Instances'][i]:
                    zone = vm['Instances'][i]['Placement']['AvailabilityZone']
                    zone_count[zone] += 1

        for itype in type_count:
            row = [itype, type_count[itype]]
            table.add_row(row)
        for vpc in vpc_count:
            row = [vpc, vpc_count[vpc]]
            table.add_row(row)
        for zone in zone_count:
            row = [zone, zone_count[zone]]
            table.add_row(row)

        print table

    def display_ec2_vmlist_table(self, vmlist):
        '''
        List the vms in tabular form

        :type vmlist: List of vms (list of dicts)
        :param vmlist: List of vms.

        '''

        # Defaults in case they are not set
        instance_id = 'None'
        instance_type = 'None'
        key_name = 'None'
        public_dnsname = 'None'
        public_ip = 'None'
        private_dnsname = 'None'
        private_ip = 'None'
        vpc_id = 'None'
        zone = 'None'

        # Setup table
        header = ["Instance-Id", "InstanceType", "KeyName",
                  "PublicDNS", "PublicIP", "PrivateDNS",
                  "PrivateIP", "VpcId", "Zone", "Account"]

        table = prettytable.PrettyTable(header)

        for vm in vmlist:
            profile = vm['profile_name']
            for instance in vm['Instances']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                try:
                    key_name = instance['KeyName']
                except KeyError:
                    key_name = "N/A"

                try:
                    vpc_id = instance['VpcId']
                except KeyError:
                    vpc_id = "NA"

                zone = instance['Placement']['AvailabilityZone']
                public_dnsname = instance['PublicDnsName']
                if len(public_dnsname) == 0:
                    public_dnsname = "NA"

                try:
                    public_ip = instance['PublicIpAddress']
                except KeyError:
                    public_ip = "NA"

                private_dnsname = instance['PrivateDnsName']
                try:
                    private_ip = instance['PrivateIpAddress']
                except KeyError:
                    private_ip = "NA"

                row = [instance_id, instance_type, key_name,
                       public_dnsname, public_ip, private_dnsname,
                       private_ip, vpc_id, zone, profile]
                table.add_row(row)

        print table

    def display_ec2_vmlist(self, outputformat='json'):
        '''
        Display the List of EC2 buckets
        '''
        service_client = aws_service.AwsService('ec2')
        vmlist = service_client.service.list_vms()

        if outputformat == "json":
            pprinter = pprint.PrettyPrinter()
            pprinter.pprint(vmlist)
        else:
            self.display_ec2_vmlist_table(vmlist)

    def display_ec2_tags_table(self, tagsobj):
        '''
        Display List of tags in tabular format
        '''
        header = ["Resource Id", "Resource Type", "Profile", "Tags"]
        table = prettytable.PrettyTable(header)
        table.align['Tags'] = "l"

        for resid in tagsobj.keys():
            resource_id = resid

            obj = tagsobj[resid]
            keys = obj.keys()
            resource_type = obj['ResourceType']
            profile_name = obj['profile_name']

            tags_str = ""
            for key in keys:
                if key.startswith('tag_'):
                    tagname = key.split("tag_")[1]
                    tags_str = tags_str + tagname + ": " + obj[key] + "\n"


            row = [resource_id, resource_type, profile_name, tags_str]
            table.add_row(row)

            row = ["-"*20, "-"*20, "-"*20, "-"*50]
            table.add_row(row)

        print table

    def display_ec2_tags(self, outputformat='json'):
        '''
        Display Tags for all EC2 Resources
        '''
        ec2_client = aws_service.AwsService('ec2')
        tagsobj = ec2_client.service.list_tags()
        if outputformat == "json":
            pprinter = pprint.PrettyPrinter()
            pprinter.pprint(tagsobj)
        else:
            self.display_ec2_tags_table(tagsobj)

    def display_ec2_sec_groups_table(self, secgroups):
        '''
        Display security groups in tabular format
        '''
        print "Sec groups table"
        header = ["Group Id", "Group Name", "Zone", "Account",
                  "Instances", "ELBs"]
        table = prettytable.PrettyTable(header)
        table.align["Instances"] = "l"

        for secgroup in secgroups.keys():
            group_id = secgroup

            obj = secgroups[secgroup]
            group_name = obj['GroupName']
            zone = obj['region']
            account = obj['profile_name']
            try:
                instances = len(obj['vm_list'])
            except KeyError:
                instances = 0
            try:
                elbs = len(obj['elb_list'])
            except KeyError:
                elbs = 0

            row = [group_id, group_name, zone, account, instances, elbs]
            table.add_row(row)

        print table

    def display_ec2_sec_groups(self, outputformat="json"):
        '''
        Display security groups
        '''
        ec2_client = aws_service.AwsService('ec2')
        elb_client = aws_service.AwsService('elb')
        vmlist = ec2_client.service.list_vms()
        elbs = elb_client.service.list_elbs()
        secgroups = ec2_client.service.list_security_groups(dict_type=True)


        for vm in vmlist:
            for instance in vm['Instances']:
                instance_id = instance['InstanceId']
                vm_secgroups = instance['SecurityGroups']
                for vm_secgroup in vm_secgroups:
                    group_id = vm_secgroup['GroupId']
                    if secgroups[group_id].get('vm_list', None) is None:
                        secgroups[group_id]['vm_list'] = []

                    secgroups[group_id]['vm_list'].append(instance_id)

        for elb in elbs:
            elb_name = elb['LoadBalancerName']
            print "elb name: ", elb_name
            elb_secgroups = elb['SecurityGroups']
            for elb_secgroup in elb_secgroups:
                print "elb_secgroup: ", elb_secgroup
                if secgroups[elb_secgroup].get('elb_list', None) is None:
                    secgroups[elb_secgroup]['elb_list'] = []

                secgroups[elb_secgroup]['elb_list'].append(elb_name)

        if outputformat == "json":
            pprinter = pprint.PrettyPrinter()
            pprinter.pprint(secgroups)
        else:
            self.display_ec2_sec_groups_table(secgroups)







