#!/bin/bash

###################################################
# IAM Operations.
# --------------
####################################################



function create_user()
{
    tmpfile="/tmp/ucreate.tmp"

    python - << END
import boto3 
import botocore


session = boto3.Session(profile_name="${account}")
iamclient = session.client('iam')
try:
    iamuser = iamclient.create_user(UserName="$user")
except botocore.exceptions.ClientError as boto_exception:
    print "[%s] " % boto_exception
    fp = open("${tmpfile}", 'w')
    fp.close()

END

    if [[ -e $tmpfile ]]; then
        echo "Error: Failed to create user $user"
        rm $tmpfile
        exit 1
    else
        debug "User $user created."
    fi
}

function add_user_to_group()
{
    tmpfile="/tmp/gadderr.tmp"

    python - << END
import boto3 
import botocore


session = boto3.Session(profile_name="${account}")
iamclient = session.client('iam')
try:
    iamuser = iamclient.add_user_to_group(UserName="$user", GroupName="$group")
except botocore.exceptions.ClientError as boto_exception:
    print "[%s] " % boto_exception
    fp = open("${tmpfile}", 'w')
    fp.close()

END

    if [[ -e $tmpfile ]]; then
        echo "Error: Failed to Add user $user to group $group"
        rm $tmpfile
        exit 1
    else
        debug "User $user added to group $group"
    fi

}

function attach_user_policies()
{
    if [[ -z $policies ]]; then
        echo "No User policies to attach."
        return
    fi

    tmpfile="/tmp/attachpolicyerr.tmp"

    if [[ $delimiter == true ]]; then
        OFS=$IFS
        IFS=":"
    fi

    policyarr=($policies)
    for policy in "${policyarr[@]}"
    do
        policy_arn=$(aws iam list-policies --profile $account | grep $policy | awk -F" " '{print $2}')

    python - << END
import boto3 
import botocore

session = boto3.Session(profile_name="${account}")
iamclient = session.client('iam')
try:
    iamclient.attach_user_policy(UserName="$user", PolicyArn="$policy_arn")
except botocore.exceptions.ClientError as boto_exception:
    print "[%s] " % boto_exception
    fp = open("${tmpfile}", 'w')
    fp.close()

END
    done

    if [[ $delimiter == true ]]; then
        IFS=$OFS
    fi

    if [[ -e $tmpfile ]]; then
        echo "Error: Failed to attach policies to $user"
        rm $tmpfile
        exit 1
    else
        debug "Policies $policies attached to User $user"
    fi
}

function create_access_key()
{
    accesskey_loc="/tmp/${user}_accesskey"
    if [[ $create_accesskey == true ]]; then
        accesskey=$(aws iam create-access-key --user-name  $user --profile $account --output json)
        echo $accesskey >  $accesskey_loc
    fi
}

function create_login_credentials()
{

   tmpfile="/tmp/loginprofilerr.tmp"

   if [[ $create_logincredentials == true ]]; then

    python - << END
import random
import string
import boto3
import botocore


size = 10
chars = string.digits + string.ascii_letters + "[{}]"
user_password = ''.join(random.choice(chars) for _ in range(size))
user_password = user_password + "{"
logincreds_file = "/tmp/$user" + "_logincredentials"

session = boto3.Session(profile_name="${account}")
iamclient = session.client('iam')
try:
    login_profile = iamclient.create_login_profile(UserName="$user", Password=user_password, PasswordResetRequired=True)
    fp = open(logincreds_file, "w")
    fp.write(str(login_profile))
    fp.close()
except botocore.exceptions.ClientError as boto_exception:
    print "[%s] " % boto_exception
    fp = open("${tmpfile}", 'w')
    fp.close()

END

       if [[ -e $tmpfile ]]; then
           echo "Failed to create login profile for $user"
           rm $tmpfile
           exit 1 
       else
           debug "Login profile for $user created"
       fi 

   fi 
}


