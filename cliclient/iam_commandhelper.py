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
        print "IAM command handler"

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

        print table

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


    def display_iam_user_permissions_table(self,
                                           user_name,
                                           prof_permissions):

        # Setup table.
        header = ["User Name"]
        for profile in prof_permissions.keys():
            header.append(profile)

        table = prettytable.PrettyTable(header)

        table.align["User Name"] = "l"
        for profile in prof_permissions.keys():
            table.align[profile] = "l"


        count = 0
        done_flag = False
        while not done_flag:
            done_flag = True
            row = []
            row.append(user_name)
            for profile in prof_permissions.keys():
                perm_info = prof_permissions[profile]
                if perm_info is None:
                    row.append("------- NA --------")
                    continue
                try:
                    obj = prof_permissions[profile][count]
                    perm_str = "Actions:" + " "*25
                    try:
                        for action in obj['Action']:
                            perm_str += action + ", "
                    except KeyError:
                        for action in obj['NotAction']:
                            perm_str += "Not: " + action + ","

                    perm_str += "Resources:" + " " * 20
                    for resource in obj['Resource']:
                        perm_str += resource + ", " + "\n"

                    perm_str += "Effect: " + obj['Effect']

                    perm_str = textwrap.fill(perm_str, 35)

                    row.append(perm_str)
                    done_flag = False
                except IndexError:
                    row.append("------- NA --------")
                    continue
            table.add_row(row)

            count += 1


        print table

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
                print "\n(%s: %s) " % (profile, user_name)
                print "========================================="
                pprinter = pprint.PrettyPrinter()
                pprinter.pprint(permissions)

        if outputformat == "table":
            self.display_iam_user_permissions_table(user_name,
                                                    profile_perms)

