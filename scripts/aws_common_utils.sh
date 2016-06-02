#!/bin/bash


###################################################
# Common Tasks.
###################################################

function debug()
{
    local msg=$1
    local msg2=$2
    local logfile=$3

    if [[ -z $logfile ]]; then
        logfile=$ORCA_LOGFILE
    fi

    if [[ $debug =  true ]]; then
        if [[ $msg = "-n" ]]; then
            echo -n $msg2 >> $logfile
        else
            echo $msg >> $logfile
        fi
    fi
}

function exit_log()
{
    curr_debug=$debug
    debug=true
    debug " "
    debug "[ END: $(date +%D:%H:%M:%S) ]"
    debug "-----------------------------------"
    debug " "
    exit 1
}

###################################################
# IAM Operations.
###################################################


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
        exit_log
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
        exit_log
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
        exit_log
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
           exit_log
       else
           debug "Login profile for $user created"
       fi 
   fi 
}

#################################
# IAM Policy Creation  Functions.
#################################

function create_policy_statement()
{
    local resource_type=$1
    local resources=$2
    local effect=$3
    local actions=$4
    local tmpfile="/tmp/policystmt-$(date +%s)"

    python - << END
import json
import sys

#statement = [] 
statementobj = {}

statementobj['Resource'] = []
resources = "${resources}".split()

for resource in resources:
    resource_arn = resource
    if "${resource_type}".lower() == 's3':
        resource_arn = "arn:aws:s3:::" + resource 

    statementobj['Resource'].append(resource_arn)

    statementobj['Sid'] = "${resource_type}".upper() + "${effect}".upper() + "$(date +%s)"

if "$effect".lower() == "allow":
    effect="Allow"
else:
    effect="Deny"

statementobj['Effect'] =  effect
statementobj['Action'] = []

for action in "${actions}".split(" "):
    statementobj['Action'].append(action)


#statement.append(statementobj)

with  open("${tmpfile}", "w") as stmtfile:
    jsonobj = json.dumps(statementobj, sort_keys=False, indent=4, ensure_ascii=False)
    stmtfile.write(jsonobj)

END

    if [[ -e $tmpfile ]]; then
        cat $tmpfile
        rm $tmpfile
    fi

}

function create_policy_file()
{
    local resource_type=$1
    local resources=$2
    local effect=$3
    local actions=$4
    tmpfile="/tmp/iampolicy_$(date +%s)"

    policy_stmt=$(create_policy_statement "$resource_type" "$resources" "$effect" "$actions")

    python - << END
import json

policy={}
policy["Version"] = "2012-10-17"
policy["Statement"] = []
policy["Statement"].append(${policy_stmt})

jsonobj = json.dumps(policy, sort_keys=False, indent=4, ensure_ascii=False)

with open("${tmpfile}", "w") as policyfile:
    policyfile.write(jsonobj)

END

    if [[ -e $tmpfile ]]; then
        echo $tmpfile
    fi

}


function create_s3_access_managed_policy()
{
    echo "Create S3 managed policy"
    local account_name=$1
    local bucketname=$2
    local effect=$3

    local resource_type='s3'
    local resources="$bucketname ${bucketname}/*"
    local actions="s3:CreateBucket s3:ListBuckets s3:*"

    policy_file=$(create_policy_file "$resource_type" "$resources" "$effect" "$actions")

    echo "Policy file: $policy_file"
    cat $policy_file
    policy_name="$resource_type-${bucketname}-AccessPolicy"
    echo "Policy name: $policy_name"

    aws iam create-policy --policy-name ${policy_name} --policy-document file://${policy_file} --profile ${account_name}

}

##################################################
# S3 Operations
##################################################

function s3_create_bucket()
{
    echo "Creating bucket"
    local bucketname=$1
    local account_name=$2

    tmpfile="/tmp/s3bucketcreate_err.tmp"

    # Use Python boto3 API to create bucket.
    # Reason for this is aws cli does not return a correct
    # error code when it fails. This results in parsing the
    # output and looking for error.
    python - << END

import boto3
import botocore

session = boto3.Session(profile_name="${account_name}")
s3client = session.client('s3')

try:
    retcode = s3client.create_bucket(Bucket="${bucketname}")
except botocore.exceptions.ClientError as boto_exception:
    print "[%s] " % boto_exception
    fp = open("${tmpfile}", "w")
    fp.close()

END

    if [[ -e $tmpfile ]]; then
        echo "Error: Failed to create bucket $bucketname"
        rm $tmpfile
        exit_log
    else
        debug "S3 Bucket $bucketname created successfully"
    fi

}

