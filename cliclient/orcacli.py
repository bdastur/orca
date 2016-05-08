#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
CLI Interface to Aws Services.
------------------------------

'''

import argparse
import orcalib.aws_service as aws_service


class S3CommandHandler(object):
    def __init__(self):
        print "S3command handler"

    def display_s3_summary(self):
        '''
        Display S3 summary information
        '''
        service_client = aws_service.AwsService('s3')
        bucketlist = service_client.list_buckets()
        for bucket in bucketlist:
            print bucket


class OrcaCli(object):
    def __init__(self):
        self.namespace = self.__parse_arguments()
        print "Namespace: ", self.namespace
        if self.namespace.service == "s3":
            self.perform_s3_operations(self.namespace)

    def perform_s3_operations(self, namespace):
        '''
        Perform S3 operations
        '''
        print "s3 operations"
        s3cmdhandler = S3CommandHandler()
        s3cmdhandler.display_s3_summary()


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

        s3parser = subparser.add_parser("s3",
                                        help="AWS Simple Storage Service")
        iamparser = subparser.add_parser("iam",
                                         help="AWS IAM ")

        # S3 group.
        s3group = s3parser.add_mutually_exclusive_group()
        s3group.add_argument("--summary",
                             dest="summary",
                             action="store_true")
        s3group.add_argument("--list-buckets",
                             dest="list_buckets",
                             action="store_true")
        s3group.add_argument("--create-bucket",
                             action="store_true")


        namespace = parser.parse_args()



        #s3parser.add_argument("list-buckets",
        #                     action="store_true",
        #                     help="Display all buckets")

        # Subparser: 'iam'


        return namespace


def main():
    orcacli = OrcaCli()


if __name__ == '__main__':
    main()
