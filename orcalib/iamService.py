#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import jinja2
import boto3
import botocore
from orcalib.aws_config import AwsConfig
import orcalib.orcaLogger as orcaLogger

def get_absolute_path_for_file(file_name, splitdir=None):
    '''
    Return the filename in absolute path for any file
    passed as relative path.
    '''
    base = os.path.basename(__file__)
    if splitdir is not None:
        splitdir = splitdir + "/" + base
    else:
        splitdir = base

    if os.path.isabs(__file__):
        abs_file_path = os.path.join(__file__.split(splitdir)[0],
                                     file_name)
    else:
        abs_file = os.path.abspath(__file__)
        abs_file_path = os.path.join(abs_file.split(splitdir)[0],
                                     file_name)

    return abs_file_path


class IamService(object):
    """
    IAM service handler class.
    """
    def __init__(self, envs):
        self.logger = orcaLogger.OrcaLogger(name="IAMService").logger
        self.validated = False

        if envs is None or len(envs) < 1:
            self.logger.error("atleast one env expected. Cannot be empty or None")
            return

        self.clients = []
        self.envs = envs
        self.getClients()
        self.logger.debug("IAMService Initialized")
        self.validated = True

    def getClients(self):
        for env in self.envs:
            profileName = env["profile_name"]
            regionName = env["region_name"]
            clientInfo = env
            try:
                session = boto3.Session(profile_name=env["profile_name"],
                                        region_name=env["region_name"])
                client = session.client("iam")
                clientInfo["botoClient"] = client
                self.clients.append(clientInfo)
            except botocore.exceptions.ProfileNotFound as err:
                self.logger.error("%s", err)
                clientInfo["botoClient"] = None
                self.clients.append(clientInfo)
                return
            except botocore.exceptions.EndpointConnectionError as err:
                self.logger.error("%s", err)
                clientInfo["botoClient"] = None
                self.clients.append(clientInfo)
                return
            except botocore.exceptions.ClientError as err:
                self.logger.error("%s", err)
                clientInfo["botoClient"] = None
                self.clients.append(clientInfo)

            print(client)

    def executeBotoAPI(self, apiName, **options):
        try:
            apiHandler = getattr(self.clients[0]["botoClient"], apiName)
            data = apiHandler(**options)
        except  AttributeError:
            print("could not find %s" % apiName)
            return None
        except botocore.exceptions.ClientError as err:
            self.logger.error("%s" % err)
            return None

        return data



