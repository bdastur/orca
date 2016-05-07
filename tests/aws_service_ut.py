#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import orcalib.aws_service as aws_service


class AwsServiceUt(unittest.TestCase):
    def test_service_init_operation(self):
        print "Most basic. Create a client for s3 service"
        service_client = aws_service.AwsService('s3')
        self.failUnless(service_client.clients is not None)

        for client in service_client.clients.keys():
            buckets = service_client.clients[client].list_buckets()
            print "Profile: ", client
            print buckets
