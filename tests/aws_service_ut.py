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

    def test_populate_bucket_tagging(self):
        print "Test api populate_bucket_tagging"
        service_client = aws_service.AwsService('s3')
        self.failUnless(service_client.service.clients is not None)

        bucketlist = service_client.service.list_buckets()
        service_client.service.populate_bucket_tagging(bucketlist)
        for bucket in bucketlist:
            print "Bucket: ", bucket

    def test_populate_bucket_validation(self):
        print "Test api populate_bucket_validation"
        service_client = aws_service.AwsService('s3')
        self.failUnless(service_client.service.clients is not None)

        bucketlist = service_client.service.list_buckets()
        service_client.service.populate_bucket_tagging(bucketlist)
        service_client.service.populate_bucket_validation(bucketlist)
        for bucket in bucketlist:
            print "Bucket:: ", bucket

    def test_basic_orcaenv(self):
        print "Test handling of the env yaml file"
        service_client = aws_config.OrcaConfig()
        print service_client.parsedyaml

    def test_get_regions(self):
        print "Test the simple api to get regions"
        service_client = aws_config.OrcaConfig()
        regions = service_client.get_regions()
        print regions

    def test_generate_new_s3_lifecycle_policy_document(self):
        print "Test generate_new_s3_lifecycle_policy_document API"
        service_client = aws_service.AwsService('s3')
        self.failUnless(service_client.service.clients is not None)

        rule_obj = {}
        rule_obj['prefix'] = "TESTFOLDER/*"
        rule_obj['status'] = "Enabled"
        rule_obj['expire_duration'] = 500
        rule_obj['standard_ia_transition_duration'] = 45
        rule_obj['glacier_transition_duration'] = 60
        rules = []
        rules.append(rule_obj)
        policyobj = {}
        policyobj['rules'] = rules

        policydoc = \
            service_client.service.\
            generate_new_s3_lifecycle_policy_document(policyobj)
        print "Policy doc: ", policydoc


    # IAM testcases.
    def test_list_users(self):
        print "Test the iam api to list users"
        service_client = aws_service.AwsService('iam')
        self.failUnless(service_client.service.clients)

        userlist = service_client.service.list_users()
        print "Users: ", len(userlist)
        print "Users: ", userlist

    def test_populate_groups_in_users(self):
        print "Test populate_groups_in_users"
        service_client = aws_service.AwsService('iam')
        self.failUnless(service_client.service.clients)

        userlist = service_client.service.list_users()
        service_client.service.populate_groups_in_users(userlist)
        print "Users: ", userlist

    def test_get_permissions_info(self):
        print "Test the get permissions info api"
        service_client = aws_service.AwsService('iam')
        self.failUnless(service_client.service.clients)

        statements = service_client.service.get_user_permissions(
            UserName='behzad_dastur', profile_name='default')

        for statement in statements:
            print "Statement: ", statement

    def test_generate_new_iam_policy_document(self):
        print "Test api generate_new_iam_policy_document"
        service_client = aws_service.AwsService('iam')
        self.failUnless(service_client.service.clients)

        actions = ["ec2:*", "s3:*"]
        resources = ["testresource",
                     "testresource/*"]
        effect = "allow"

        policy_doc = service_client.service.generate_new_iam_policy_document(
            's3',
            resources,
            actions,
            effect)
        print "Policy Doc: \n", policy_doc

    def test_get_user_attached_policies(self):
        print "Test the get permissions info api"
        service_client = aws_service.AwsService('iam')
        self.failUnless(service_client.service.clients)

        statements = service_client.service.get_user_attached_policies(
            UserName='behzad_dastur', profile_name='default')

        for statement in statements:
            print "Statement: ", statement

    # EC2 testcases.
    def test_list_vms(self):
        print "Test simple usecase to list all ec2 instances"
        service_client = aws_service.AwsService('ec2')
        self.failUnless(service_client.service.clients is not None)

        vmlist = service_client.service.list_vms()
        for vm in vmlist:
            print "VM: ", vm




