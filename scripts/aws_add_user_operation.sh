#!/bin/bash

###################################################
# Add a new User.
# --------------
# A new user creation requires the following parameters.
# 1. User name: Name of the user
# 2. Group Name: (optional) If provided the user will be added to that group
# 3. Policy list: Any AWS IAM Policies that need to be applied to the user.
####################################################

account=
group=
user=
debug=false
create_accesskey=false
create_logincredentials=false
delimiter=false


####################################################
# show_help: 
# Display the help for this tool.
# @Arguments: None
####################################################
function show_help() 
{
    echo "`basename $0`  : ORCA - AWS Create User Script"
    echo "-------------------------------------------------"
    echo "usage: aws_add_user_operation -a account-name -u username [-g groupname] [-p policy1,policy2...] "
    echo ""
    echo "-a account   : Specifiy the account name where the new user should be created."
    echo ""
    echo "-u username  : Specify a user name that needs to be created."
    echo ""
    echo "-g groupname : [OPTIONAL] If a group name is provided the user will be added to the specified group."
    echo ""
    echo "-p policies  : [OPTIONAL] List of \"space\"  seperated policies to be applied to the User if specified" 
    echo ""
    echo "-c access_key: [OPTIONAL] If specified create an access key for the user."
    echo ""
    echo "-l login profile: [OPTIONAL] If specified create a login profile with a login password"
    echo ""
    echo "-r delimiter: [OPTIONAL] This flag is set when list arguments like policies are passed with delimiter \":\""
    echo ""
    echo "-h              : To display this help"
    echo ""
    echo "-----------------------------------------------------"
    echo "Requires:"
    echo "-------------"
    echo " 1. AWS CLI"
    echo " 2. ~/.aws/credentials, ~/.aws/config"
    exit 1
}

function debug()
{
    local msg=$1
    local msg2=$2

    if [[ $debug ==  true ]]; then
        if [[ $msg == "-n" ]]; then
            echo -n $msg2
        else
            echo $msg
        fi
    fi
}

function validate_input()
{
    local account_valid=false

    if [[ ( -z $account ) || ( -z $user ) ]]; then
        echo "Error: Required Arguments -u <username> and -a <account> not provided."
        echo "For Usage, execute:  `basename $0` -h"
        echo ""
        exit 1
    fi

    echo "Validations: "
    debug "-------------"
    # Validate account information.
    # Credinfo is an array of the groups.
    credinfo=($(cat ~/.aws/credentials | grep '^\['))
    for profile in "${credinfo[@]}"
    do
        profile=${profile#*[}
        profile=${profile%*]}
        if [[ $account == $profile ]]; then
            account_valid=true
        fi
    done

    debug -n "Validating account.. "
    # Check if the account valid flag is set.
    if [[ $account_valid == true ]]; then
        debug ": Account is valid."
    else
        echo "Error: Invalid Account provided \"$account\""
        echo "Valid values are: ${credinfo[@]}"
        exit 1
    fi

    # Validate groupname.
    debug -n "Validating Groupname.. "
    aws_group=$(aws iam list-groups --profile $account | grep $group)
    if [[ -z $aws_group ]]; then
        echo "Error: Invalid Group provided \"$group\""
        exit 1
    else
        debug ": Group Valid: \"$group\""
    fi

    # Check Policies.
    #aws_policies=($(aws iam list-policies --profile ${account} | awk -F " " '{print $9}'))
    debug "Validating Policies.. "
    if [[ $delimiter == true ]]; then
        OFS=$IFS
        IFS=":"
    fi
    policyarr=($policies)
    for policy in "${policyarr[@]}"
    do
        aws_policy=$(aws iam list-policies --profile ${account} | grep $policy)
        if [[ -z $aws_policy ]]; then
            echo "Error: Invalid Policy provided \"$policy\""
            exit 1
        fi
        debug ": \"$policy\" Valid "
    done

    if [[ $delimiter == true ]]; then
        IFS=$OFS
    fi
    debug ": All policies Valid"
    echo "Validations.. Complete"
}

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


if [[ $# -eq 0 ]]; then
    echo "Error: No options provided"
    echo "For Usage, execute:  `basename $0` -h"
    echo "..."
    exit 1
fi

readonly COMMANDLINE="$*"

while getopts "a:cdg:lp:ru:h" option; do
    case $option in
        h)
            show_help 
            ;;
        a) 
            account=$OPTARG
            ;;
        c)
            create_accesskey=true
            ;;
        d) 
            debug=true
            ;;
        g)
            group=$OPTARG
            ;;
        l)
            create_logincredentials=true
            ;;
        p)
            policies=$OPTARG
            ;;
        r)
            delimiter=true
            ;;
        u)
            user=$OPTARG
            ;;
        :) echo "Error: option \"-$OPTARG\" needs argument"; show_help;;
        *) echo "Error: Invalid option \"-$OPTARG\""; show_help;;
    esac
done

validate_input
create_user
add_user_to_group
attach_user_policies
create_access_key
create_login_credentials



