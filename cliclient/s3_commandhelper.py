#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
CLI Interface to Aws Services.
------------------------------

'''

import pprint
import prettytable
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

    def display_s3_summary(self, outputformat='json'):
        '''
        Display S3 summary information

        :type format: String ('json' or 'table')
        :param format:  The output format to display.

        '''
        service_client = aws_service.AwsService('s3')
        bucketlist = service_client.service.list_buckets()
        service_client.service.populate_bucket_location(bucketlist)

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

        if outputformat == "json":
            pprinter = pprint.PrettyPrinter()
            pprinter.pprint(bucket_summary)
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
                  "Total Objects", "Total Size", "Last Modified"]
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
            lastmodified = bucket['LastModified']
            row = [name, profile, location,
                   objcount, obj_totalsize, lastmodified]
            table.add_row(row)

            total_buckets += 1
            total_objects = total_objects + objcount
            total_objectsize = total_objectsize + obj_totalsize

        row = ["-"*20, "-"*20, "-"*17, "-"*17, "-"*17, "-"*20]
        table.add_row(row)

        total_buckets = "Total: " + str(total_buckets)
        if total_objectsize > 10*6:
            total_objectsize = total_objectsize/1024
            total_objectsize = str(total_objectsize) + " KB"

        row = [total_buckets, " - ", " - ",
               total_objects, total_objectsize, " - "]
        table.add_row(row)

        print table

    def display_s3_bucketlist(self, outputformat='json'):
        '''
        Display the List of S3 buckets
        '''
        service_client = aws_service.AwsService('s3')
        bucketlist = service_client.service.list_buckets()
        service_client.service.populate_bucket_location(bucketlist)
        service_client.service.populate_bucket_objects(bucketlist)

        if outputformat == "json":
            pprinter = pprint.PrettyPrinter()
            pprinter.pprint(bucketlist)
        else:
            self.display_s3_buckelist_table(bucketlist)




