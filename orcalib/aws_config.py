#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from ConfigParser import SafeConfigParser


class OrcaConfig(object):
    '''
    The class reads/manages the orcaenv.yaml file.
    Ideally the file should be located in the same place as your
    aws config file (~/.aws/orcaenv.yaml).
    '''
    def __init__(self):
        '''
        Initialize.
        '''
        homedir = os.environ.get("HOME", None)
        if homedir is None:
            print "ERROR: Home ENV is not set"
            return
        self.__orca_config = os.path.join(homedir, ".aws/orcaenv.yaml")
        try:
            fp = open(self.__orca_config)
        except IOError as ioerr:
            print "ERROR: Failed to open [%s] [%s]" % \
                (self.__orca_config, ioerr)

        try:
            self.parsedyaml = yaml.safe_load(fp)
        except yaml.error.YAMLError as yamlerr:
            print "ERROR: Yaml parsing failed [file: %s] [%s]" % \
                (self.__orca_config, yamlerr)
            return

    def get_regions(self):
        '''
        Return the region list from the orcaenv config file
        '''
        try:
            return (self.parsedyaml['regions'])
        except KeyError:
            return None


class AwsConfig(object):
    '''
    The class provides functionality to read the was configuration.
    '''
    def __init__(self):
        homedir = os.environ.get('HOME', None)
        if homedir is None:
            print "ERROR: HOME ENV is not set."
            return
        self.__config_file = os.path.join(homedir, ".aws/credentials")

        if not os.path.exists(self.__config_file):
            print "ERROR: No aws credentials/config file present"
            return

        self.cfgparser = SafeConfigParser()
        self.cfgparser.read(self.__config_file)

    def get_profiles(self):
        '''
        Return the profiles configured in the aws configuration file
        '''
        return self.cfgparser.sections()

    def get_aws_access_key_id(self, profilename):
        '''
        Return the aws_access_key_id
        '''
        return self.cfgparser.get(profilename, 'aws_access_key_id')

    def get_aws_secret_access_key(self, profilename):
        '''
        Return the aws_secret_access_key
        '''
        return self.cfgparser.get(profilename, 'aws_secret_access_key')


