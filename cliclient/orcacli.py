#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
CLI Interface to Aws Services.
------------------------------

'''

import pprint
import prettytable
import argparse
import orcalib.aws_service as aws_service


class S3CommandHandler(object):
    def __init__(self):
        print "S3command handler"

    def display_s3_summary_table(self, bucket_summary):
        '''
        Display S3 Summary in Tabular output.
        '''
        # Setup table header.
        header = ["Profile", "Total Bucket Count"]
        table = prettytable.PrettyTable(header)

        for profile in bucket_summary.keys():
            row = [profile, bucket_summary[profile]['total_count']]
            table.add_row(row)

        print table

        # Setup table header (loc constraint)
        header = ["Location", "Bucket Count"]
        table = prettytable.PrettyTable(header)

        for profile in bucket_summary.keys():
            row = ["-"*40, "-"*20]
            table.add_row(row)
            row = [profile, " "]
            table.add_row(row)
            row = ["-"*40, "-"*20]
            table.add_row(row)

            locs = bucket_summary[profile]['locs']
            for loc in locs.keys():
                row = [loc, bucket_summary[profile]['locs'][loc]]
                table.add_row(row)
            row = [" ", " "]
            table.add_row(row)

        print table

    def display_s3_summary(self, format='json'):
        '''
        Display S3 summary information

        :type format: String ('json' or 'table')
        :param format:  The output format to display.

        '''
        service_client = aws_service.AwsService('s3')
        bucketlist = service_client.list_buckets()
        service_client.populate_bucket_location(bucketlist)

        bucket_summary = {}
        for bucket in bucketlist:
            profile_name = bucket['profile_name'][0]
            location_constraint = bucket['LocationConstraint']
            if location_constraint is None:
                location_constraint = "global"

            if bucket_summary.get(profile_name, None) is None:
                bucket_summary[profile_name] = {}
                bucket_summary[profile_name]['total_count'] = 1
            else:
                bucket_summary[profile_name]['total_count'] += 1

            if bucket_summary[profile_name].get('locs', None) is None:
                bucket_summary[profile_name]['locs'] = {}

            if not bucket_summary[profile_name]['locs'].get(location_constraint, None):
                bucket_summary[profile_name]['locs'][location_constraint] = 1
            else:
                bucket_summary[profile_name]['locs'][location_constraint] += 1

        if format == "json":
            pp = pprint.PrettyPrinter()
            pp.pprint(bucket_summary)
        else:
            self.display_s3_summary_table(bucket_summary)

    def display_s3_buckelist_table(self, bucketlist):
        '''
        List the buckets in tabular form

        :type bucketlist: List of buckets (list of dicts)
        :param bucketlist: List of buckets.

        '''
        # Setup table
        header = ["Bucket Name", "Profile", "Location",
                  "Total Objects", "Total Size"]
        table = prettytable.PrettyTable(header)

        total_buckets = 0
        total_objects = 0
        total_objectsize = 0
        for bucket in bucketlist:
            name = bucket['Name']
            profile = bucket['profile_name'][0]
            location = bucket['LocationConstraint']
            if location is None:
                location = "Global"
            objcount = bucket['object_count']
            obj_totalsize = bucket['object_size']
            row = [name, profile, location, objcount, obj_totalsize]
            table.add_row(row)

            total_buckets += 1
            total_objects = total_objects + objcount
            total_objectsize = total_objectsize + obj_totalsize

        row = ["-"*20, "-"*20, "-"*20, "-"*20, "-"*20]
        table.add_row(row)

        total_buckets = "Total: " + str(total_buckets)
        if total_objectsize > 10*6:
            total_objectsize = total_objectsize/1024
            total_objectsize = str(total_objectsize) + " KB"

        row = [total_buckets, " - ", " - ",
               total_objects, total_objectsize]
        table.add_row(row)

        print table

    def display_s3_bucketlist(self, format='json'):
        '''
        Display the List of S3 buckets
        '''
        service_client = aws_service.AwsService('s3')
        bucketlist = service_client.list_buckets()
        service_client.populate_bucket_location(bucketlist)
        service_client.populate_bucket_objects(bucketlist)

        if format == "json":
            pp = pprint.PrettyPrinter()
            pp.pprint(bucketlist)
        else:
            self.display_s3_buckelist_table(bucketlist)



class OrcaCli(object):
    def __init__(self):
        self.namespace = self.__parse_arguments()
        print "Namespace: ", self.namespace
        if self.namespace.output is None:
            self.namespace.output = "table"
        if self.namespace.service == "s3":
            self.perform_s3_operations(self.namespace)

    def perform_s3_operations(self, namespace):
        '''
        Perform S3 operations
        '''
        print "s3 operations"
        s3cmdhandler = S3CommandHandler()

        if namespace.summary is True:
            s3cmdhandler.display_s3_summary(format=namespace.output)
        elif namespace.list_buckets is True:
            s3cmdhandler.display_s3_bucketlist(format=namespace.output)

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
        s3parser.add_argument("--output",
                              help = "Output format {json, table}")

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


        return namespace


def main():
    orcacli = OrcaCli()


if __name__ == '__main__':
    main()
