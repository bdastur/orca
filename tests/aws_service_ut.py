#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import orcalib.aws_service as aws_service
import orcalib.aws_config as aws_config


class AwsServiceUt(unittest.TestCase):
    def test_service_init_operation(self):
        print "Most basic. Create a client for s3 service"
        service_client = aws_service.AwsService('s3')
        self.failUnless(service_client.service is not None)

        for client in service_client.service.clients.keys():
            buckets = service_client.service.clients[client].list_buckets()
            print "Profile: ", client
            print buckets

    def test_list_bucket_in_region(self):
        print "Test the list_bucket_in_region API"
        service_client = aws_service.AwsService('s3')
        self.failUnless(service_client.service is not None)

        bucketlist = service_client.service.list_buckets()
        for bucket in bucketlist:
            print "Bucket: ", bucket

    def test_populate_bucket_location(self):
        print "Test api populate_bucket_location"
        service_client = aws_service.AwsService('s3')
        self.failUnless(service_client.service is not None)

        bucketlist = service_client.service.list_buckets()
        service_client.service.populate_bucket_location(bucketlist)
        for bucket in bucketlist:
            print "Last bucket: ", bucket

    def test_populate_bucket_policy(self):
        print "Test api populate_bucket_location"
        service_client = aws_service.AwsService('s3')
        self.failUnless(service_client.service is not None)

        bucketlist = service_client.service.list_buckets()
        service_client.service.populate_bucket_policy(bucketlist)
        for bucket in bucketlist:
            print "Bucket: ", bucket

    def test_populate_bucket_objects(self):
        print "Test api populate_bucket_location"
        service_client = aws_service.AwsService('s3')
        self.failUnless(service_client.service.clients is not None)

        bucketlist = service_client.service.list_buckets()
        service_client.service.populate_bucket_objects(bucketlist)
        for bucket in bucketlist:
            print "Bucket: ", bucket

    def test_basic_orcaenv(self):
        print "Test handling of the env yaml file"
        service_client = aws_config.OrcaConfig()
        print service_client.parsedyaml

    def test_get_regions(self):
        print "Test the simple api to get regions"
        service_client = aws_config.OrcaConfig()
        regions = service_client.get_regions()
        print regions

    # EC2 testcases.
    def test_list_vms(self):
        print "Test simple usecase to list all ec2 instances"
        service_client = aws_service.AwsService('ec2')
        self.failUnless(service_client.service.clients is not None)

        vmlist = service_client.service.list_vms()
        for vm in vmlist:
            print "VM: ", vm




