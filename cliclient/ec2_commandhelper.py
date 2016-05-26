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
                  "PublicDNS", "PublicIP", "PrivateDNS", "PrivateIP", 'VpcId', 'Zone']

        table = prettytable.PrettyTable(header)

        for vm in vmlist:
            for i in range (len(vm['Instances'])):
                instance_id = vm['Instances'][i]['InstanceId']
                instance_type = vm['Instances'][i]['InstanceType']
                if 'KeyName' in vm['Instances'][i]:
                    key_name = vm['Instances'][i]['KeyName']

                if 'VpcId' in vm['Instances'][i]:
                    vpc_id = vm['Instances'][i]['VpcId']
                if 'Placement' in vm['Instances'][i]:
                    zone = vm['Instances'][i]['Placement']['AvailabilityZone']

                for j in range (len(vm['Instances'][i]['NetworkInterfaces'])):
                    if 'Association' in vm['Instances'][i]['NetworkInterfaces'][j]:
                        public_dnsname = vm['Instances'][i]['NetworkInterfaces'][j]['Association']['PublicDnsName']
                        public_ip = vm['Instances'][i]['NetworkInterfaces'][j]['Association']['PublicIp']
                    if 'PrivateDnsName' in vm['Instances'][i]['NetworkInterfaces'][j]:
                        private_dnsname = vm['Instances'][i]['NetworkInterfaces'][j]['PrivateDnsName']
                    if 'PrivateIPAddress' in vm['Instances'][i]['NetworkInterfaces'][j]:
                        private_ip = vm['Instances'][i]['NetworkInterfaces'][j]['PrivateIpAddress']

                    row = [instance_id, instance_type, key_name, public_dnsname, public_ip, private_dnsname, private_ip, vpc_id, zone]
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



