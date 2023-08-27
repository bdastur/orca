#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import orcalib.iamService as iamService
import orcalib.orcaLogger as orcaLogger

class IAMServiceUt(unittest.TestCase):
    def test_logger_basic(self):
        print("Test: logger basic")
        ocl = orcaLogger.OrcaLogger(name="TestingBasic", consoleLogLevel="DEBUG")
        ocl.logger.debug("Debug message test")
        ocl.logger.info("Info message test")
        ocl.logger.warning("Warning message test")
        print(orcaLogger.stringc("This is a test colored string", "red"))


    def test_basic_iam(self):
        print("Test: IAM Basic")
        envs = None
        iamHelper = iamService.IamService(envs)
        self.assertEqual(iamHelper.validated, False, 
                         msg="iamHelper's validated flag should be false")

        # Incorrect profile.
        envs = [{"profile_name": "foo", "region_name": "us-east-1"}]
        iamHelper = iamService.IamService(envs)

        # Valid env.
        envs = [{"profile_name": "dev", "region_name": "us-east-1"}]
        iamHelper = iamService.IamService(envs)

        options = {}
        data = iamHelper.executeBotoAPI("list_users", **options)
        print(data)

        data = iamHelper.executeBotoAPI("list_roles", **options)
        print(data)

        options= {"RoleName": "AWSDataLifecycleManagerDefaultRoleForAMIManagement"}
        data = iamHelper.executeBotoAPI("list_attached_role_policies", **options)
        print("Attached role policies: ", data)
