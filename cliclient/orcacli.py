#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
CLI Interface to Aws Services.
------------------------------

'''

import argparse
import pprint
import prettytable
import orcalib.aws_config as aws_config
from cliclient.ec2_commandhelper import EC2CommandHandler
from cliclient.s3_commandhelper import S3CommandHandler
from cliclient.iam_commandhelper import IAMCommandHandler


class OrcaCli(object):
    def __init__(self):
        self.namespace = self.__parse_arguments()
        print("Namespace: ", self.namespace)
        if self.namespace.output is None:
            self.namespace.output = "table"
        if self.namespace.service == "ec2":
            self.perform_ec2_operations(self.namespace)
        elif self.namespace.service == "s3":
            self.perform_s3_operations(self.namespace)
        elif self.namespace.service == "profile":
            self.perform_profile_operations(self.namespace)
        elif self.namespace.service == "iam":
            self.perform_iam_operations(self.namespace)

    def perform_profile_operations(self, namespace):
        '''
        Handle the profile operations
        '''
        awsconfig = aws_config.AwsConfig()
        profiles = awsconfig.get_profiles()

        profile_summary = {}
        for profile in profiles:
            profile_summary[profile] = {}
            profile_summary[profile]['access_key_id'] = \
                awsconfig.get_aws_access_key_id(profile)
            profile_summary[profile]['secret_access_key'] = \
                awsconfig.get_aws_secret_access_key(profile)

        if namespace.output == "json":
            pprinter = pprint.PrettyPrinter()
            pprinter.pprint(profile_summary)
        else:
            # Setup table.
            header = ["Profile Name", "Access Key ID", "Secret Access Key"]
            table = prettytable.PrettyTable(header)

            for profile in profile_summary.keys():
                row = [profile,
                       profile_summary[profile]['access_key_id'],
                       profile_summary[profile]['secret_access_key']]
                table.add_row(row)

            print(table)

    def perform_ec2_operations(self, namespace):
        '''
        Perform EC2 operations
        '''
        print("ec2 operations")
        ec2cmdhandler = EC2CommandHandler()

        if namespace.summary is True:
            ec2cmdhandler.display_ec2_summary(outputformat=namespace.output)
        elif namespace.list_vms is True:
            ec2cmdhandler.display_ec2_vmlist(outputformat=namespace.output)

    def perform_s3_operations(self, namespace):
        '''
        Perform S3 operations
        '''
        print("s3 operations")
        s3cmdhandler = S3CommandHandler()

        if namespace.summary is True:
            s3cmdhandler.display_s3_summary(outputformat=namespace.output)
        elif namespace.list_buckets is True:
            s3cmdhandler.display_s3_bucketlist(outputformat=namespace.output)

    def perform_iam_operations(self, namespace):
        '''
        Perform iam operations
        '''
        print("iam operations")
        iam_cmdhandler = IAMCommandHandler()

        if namespace.list_users:
            iam_cmdhandler.display_iam_userlist(outputformat=namespace.output)
        elif namespace.list_user_permissions:
            iam_cmdhandler.display_iam_user_permissions(
                namespace.list_user_permissions,
                outputformat=namespace.output)

    def __parse_arguments(self):
        '''
        cmdline parser. Using python argparse.
        '''
        parser = argparse.ArgumentParser(
            prog="orcacli.py",
            formatter_class=argparse.RawTextHelpFormatter,
            description="Orca command line")

        subparser = parser.add_subparsers(dest="service",
                                          help="Service type")

        ec2parser = subparser.add_parser("ec2",
                                        help="AWS Elastic Compute Service")
        s3parser = subparser.add_parser("s3",
                                        help="AWS Simple Storage Service")
        iamparser = subparser.add_parser("iam",
                                         help="AWS IAM ")
        profile_parser = subparser.add_parser(
            "profile",
            help="Aws Configuration (profiles)")

        # Profile group
        profile_parser.add_argument("--output",
                                    help="Output format {json, table}")

        profile_parser.add_argument("--list",
                                    action="store_true",
                                    help="List AWS Profiles (~/.aws/config)")

        # EC2 group
        ec2parser.add_argument("--output",
                              help="Output format {json, table}")

        ec2group = ec2parser.add_mutually_exclusive_group()
        ec2group.add_argument("--list-vms",
                             dest="list_vms",
                             action="store_true")

        ec2group.add_argument("--summary",
                             dest="summary",
                             action="store_true")

        # S3 group.
        s3parser.add_argument("--output",
                              help="Output format {json, table}")

        s3group = s3parser.add_mutually_exclusive_group()
        s3group.add_argument("--summary",
                             dest="summary",
                             action="store_true")
        s3group.add_argument("--list-buckets",
                             dest="list_buckets",
                             action="store_true")
        s3group.add_argument("--create-bucket",
                             action="store_true")

        # iam group.
        iamparser.add_argument("--output",
                               help="Output format {json, table}")
        iamgroup = iamparser.add_mutually_exclusive_group()

        iamgroup.add_argument("--list-users",
                              dest="list_users",
                              action="store_true")

        iamgroup.add_argument("--list-user-permissions",
                              dest="list_user_permissions",
                              help="List permission for specific user")

        namespace = parser.parse_args()


        return namespace


def main():
    OrcaCli()


if __name__ == '__main__':
    main()
