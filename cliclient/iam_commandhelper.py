#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
CLI Interface to Aws Services.
------------------------------

'''

import pprint
import prettytable
import textwrap
import orcalib.aws_service as aws_service
import orcalib.aws_config as aws_config


class IAMCommandHandler(object):
    def __init__(self):
        print("IAM command handler")

    def display_iam_userlist_table(self, userlist):
        '''
        Display user information in tabular format.
        '''
        awsconfig = aws_config.AwsConfig()
        profiles = awsconfig.get_profiles()

        # Setup table.
        header = ["User Name"]
        for profile in profiles:
            header.append(profile)

        table = prettytable.PrettyTable(header)
        table.align["User Name"] = "l"

        userinfo = {}
        for user in userlist:
            username = user['UserName']
            profile = user['profile_name']
            if userinfo.get(username, None) is None:
                # Add an entry first time we see a user.
                userinfo[username] = {}
                userinfo[username]['profile_name'] = {}
                userinfo[username]['profile_name'][profile] = {}
                userinfo[username]['profile_name'][profile]['Groups'] = \
                    user['Groups']
            else:
                userinfo[username]['profile_name'][profile] = {}
                userinfo[username]['profile_name'][profile]['Groups'] = \
                    user['Groups']

        for user in userinfo.keys():
            row = [user]
            for profile in profiles:
                if profile in userinfo[user]['profile_name'].keys():
                    groups = userinfo[user]['profile_name'][profile]['Groups']
                    groupstr = ""
                    for group in groups:
                        groupstr = group['GroupName'] + ", "
                    row.append(groupstr)
                else:
                    row.append('X')

            table.add_row(row)

        print(table)

    def display_iam_userlist(self, outputformat='json'):
        '''
        Display the list of users.
        '''
        service_client = aws_service.AwsService('iam')
        userlist = service_client.service.list_users()
        service_client.service.populate_groups_in_users(userlist)

        if outputformat == "json":
            pprinter = pprint.PrettyPrinter()
            pprinter.pprint(userlist)
        else:
            self.display_iam_userlist_table(userlist)

    def fillstr(self,
                string,
                length):
        '''
        Cap a string to the lenght.
        '''
        if len(string) < length:
            diff = length - len(string)
            string = string + " " * diff
        else:
            mod = len(string) % length
            string = string + " " * mod

        return string

    def display_iam_user_permissions_table(self,
                                           user_name,
                                           profile_perms):
        '''
        Display tabular format
        '''
        table = prettytable.PrettyTable()
        table.add_column("User Name", [user_name])

        for profile in profile_perms.keys():
            if profile_perms[profile] is None:
                continue

            statementstr = ""
            for statement in profile_perms[profile]:
                resources = statement['Resource']
                actions = statement.get('Action', None)
                if not actions:
                    actions = statement.get('NotAction', None)
                effect = statement['Effect']

                #statementstr = statementstr + "-" * 29 + "\n"

                tempstr = "Resources: " + str(resources)
                statementstr = statementstr + self.fillstr(tempstr, 30)

                tempstr = "Actions: " + \
                    str(actions)
                statementstr = statementstr + self.fillstr(tempstr, 30)

                tempstr = "Effect: " + \
                    str(effect)
                statementstr = statementstr + self.fillstr(tempstr, 30)
                statementstr = statementstr + "-" * 29 + "\n"

            statementstr = textwrap.fill(statementstr, 34)
            table.add_column(profile, [statementstr], align="l")

        print(table)

    def display_iam_user_permissions(self, user_name, outputformat='json'):
        '''
        Display Permissions for user
        '''
        awsconfig = aws_config.AwsConfig()
        profiles = awsconfig.get_profiles()

        service_client = aws_service.AwsService('iam')

        profile_perms = {}
        for profile in profiles:
            permissions = service_client.service.get_user_permissions(
                UserName=user_name, profile_name=profile)

            profile_perms[profile] = permissions
            if outputformat == "json":
                print("\n(%s: %s) " % (profile, user_name))
                print("=========================================")
                pprinter = pprint.PrettyPrinter()
                pprinter.pprint(permissions)

        if outputformat == "table":
            self.display_iam_user_permissions_table(user_name,
                                                    profile_perms)

    def display_iam_user_policies_table(self,
                                        user_name,
                                        policyinfo):
        '''
        Display user policy info in tabular format
        '''
        table = prettytable.PrettyTable()
        table.add_column("User Name", [user_name])

        for profile in policyinfo.keys():

            if policyinfo[profile] is None:
                continue

            policystr = ""
            for policy in policyinfo[profile]:
                policyname = policy['PolicyName']
                policy_type = policy['type']

                tempstr = "Name: " + policyname
                policystr = policystr + self.fillstr(tempstr, 30)
                tempstr = "Type: " + policy_type
                policystr = policystr + self.fillstr(tempstr, 30)

            policystr = textwrap.fill(policystr, 34)
            table.add_column(profile, [policystr], align="l")

        print(table)

    def display_iam_user_policies(self,
                                  user_name,
                                  outputformat='json'):
        '''
        Display policies attached to the user.
        '''

        awsconfig = aws_config.AwsConfig()
        profiles = awsconfig.get_profiles()

        service_client = aws_service.AwsService('iam')

        policyinfo = {}
        for profile in profiles:
            policyinfo[profile] = []
            policies = service_client.service.get_user_attached_policies(
                UserName=user_name,
                profile_name=profile)
            policyinfo[profile] = policies

        if outputformat == "json":
            pprinter = pprint.PrettyPrinter()
            pprinter.pprint(policyinfo)

        if outputformat == "table":
            self.display_iam_user_policies_table(user_name,
                                                 policyinfo)


