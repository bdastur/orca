#!/bin/bash

###################################################
# ORCA CLI Handler:
# ----------------
# orcacli: Is a command line management utility to manage
# AWS cloud.
#
# Where AWS CLI provides a very useful and exhaustive CLI
# to perform various operations, orca CLI provides an encompassing
# functionality.
#
# To illustrate that, consider and example of adding a user account.
# Pretty basic task on one hand which can be accomplished with one
# AWS CLI command, but in reality adding a new user account will require
# several operations like: adding a user, adding a user to a group
# attaching policies. For this would have to figure out correct policy-arn
#
# This is a scenario that can be accomplished with orca CLI with a single
# command.
#
# <TODO: More examples>
####################################################

account=
bucketname=
operation=
debug=false
group=
user=
create_accesskey=false
create_logincredentials=false
delimiter=false
force_password=


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ORCA_LOGFILE="/tmp/orcalog"


#############
# Help Generic
##############
function show_help_generic()
{
    echo "`basename $0`  : ORCA - Operations"
    echo "-------------------------------------------------"
    echo "usage: orcacli <service type> <operation type> [ OPTIONS ]"
    echo "Services: "
    echo ""
    servicearr=($services)
    for service in "${servicearr[@]}"
    do
        echo "${service}"
    done

    exit 1
}

function show_help_service()
{
    local service=$1
    local service_options=($2)
    local optcount=${#service_options}

    if [[ $service = "s3" ]]; then
        operations=($s3_operations)
    elif [[ $service = "iam" ]]; then
        operations=($iam_operations)
    fi

    echo "Available Operations:"
    echo "----------------------"
    for operation in "${operations[@]}"
    do
        echo "${operation}"
    done

    echo "Options:"
    echo "-------------"

    for (( i=0; i<$optcount; i++ )); do
        option=${service_options:$i:1}
        case $option in
            a)
                echo "-a account   : Specifiy the account name where the new user should be created."
                ;;
            b)
                echo "-b bucket    : Specify the bucket name to create."
                ;;
            c)
                echo "-c access_key: [OPTIONAL] If specified create an access key for the user."
                ;;
            d)
                echo "-a account   : Specifiy the account name where the new user should be created."
                ;;
            f)
                echo "-f password  : [OPTIONAL] Instead of randomly generated password. Force the password from CLI"
                ;;
            g)
                echo "-g groupname : [OPTIONAL] If a group name is provided the user will be added to the specified group."
                ;;
            l)
                echo "-l login profile: [OPTIONAL] If specified create a login profile with a login password"
                ;;
            p)
                echo "-p policies  : [OPTIONAL] List of \"space\"  seperated policies to be applied to the User if specified"
                ;; 
            r)
                echo "-r delimiter: [OPTIONAL] This flag is set when list arguments like policies are passed with delimiter \":\""
                ;;
            u)
                echo "-u username  : Specify a username" 
                ;;
            :) ;;
            *);;
        esac
    done

    exit 1
}

####################################################
# show_help:
# Display the help for this tool.
# @Arguments: None
####################################################
function show_help()
{
    echo "`basename $0`  : ORCA - Operations"
    echo "-------------------------------------------------"
    echo "usage: aws_add_user_operation -a account-name -u username [-g groupname] [-p policy1,policy2...] "
    echo ""
    echo "-a account   : Specifiy the account name where the new user should be created."
    echo ""
    echo "-b bucket    : Specify the bucket name to create."
    echo ""
    echo "-g groupname : [OPTIONAL] If a group name is provided the user will be added to the specified group."
    echo ""
    echo "-f password  : [OPTIONAL] Instead of randomly generated password. Force the password from CLI"
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


# Source helper scripts.
source $DIR/orca_cmdline.sh
source $DIR/aws_common_utils.sh

# Create S3 Bucket.
function create_bucket() 
{
    validate_user_input $service_type $operation
    s3_create_bucket $bucketname $account
    s3policyname=$(create_policy_name 's3' $bucketname)
    create_s3_access_managed_policy $account $bucketname 'Allow' $s3policyname
    if [[ ! -z $group ]]; then
        attach_group_policies $account $group $s3policyname
    elif [[ ! -z $user ]]; then
        attach_user_policies $account $user $s3policyname
    fi
}

# Create User.
function create_user_account()
{
    validate_user_input $service_type $operation
    create_user $account $user
    add_user_to_group $account $user $group
    attach_user_policies $account $user $policies
    create_access_key $account $user $create_accesskey
    create_login_credentials $account $user $create_logincredentials
}


if [[ $# -eq 0 ]]; then
    echo "Error: No options provided"
    echo "For Usage, execute:  `basename $0` -h"
    echo "..."
    exit 1
elif [[ $1 = '-h' ]]; then
    show_help_generic
fi

readonly COMMANDLINE="$*"

#######################################
# Parse the positional arguments first.
# In this case it is the type of operation.
# Once we parse it 'shift' all the command line arguments
# one position to the left.
#######################################

# Get service type.
service_type=$1
validate_service_type $service_type
shift

if [[ $service_type = "s3" ]]; then
    CMD_OPTIONS="a:b:dg:u:h"
elif [[ $service_type = "iam" ]]; then
    CMD_OPTIONS="a:cdf:g:lp:ru:h"
fi


if [[ $1 = '-h' ]]; then
    echo "Help for service"
    show_help_service $service_type $CMD_OPTIONS
fi


operation=$1
validate_operation_type $service_type $operation
shift


while getopts ${CMD_OPTIONS} option; do
    case $option in
        h)
            show_help
            ;;
        a)
            account=$OPTARG
            ;;
        b)
            bucketname=$OPTARG
            ;;
        c)
            create_accesskey=true
            ;;
        d)
            debug=true
            ;;
        f)
            force_password=$OPTARG
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
        :) echo "Error: option \"-$OPTARG\" needs argument"; echo "error :";;
        *) echo "Error: Invalid option \"-$OPTARG\""; echo "invalid option error";;
    esac
done

# Log msg
curr_debug=$debug
debug=true
debug "----------------------------------"
debug "[ START: $(date +%D:%H:%M:%S) ]"
debug "[ Service: $service_type| Operation: $operation ]"
debug "[ OPTIONS: Account: $account| Bucket Name: $bucketname ]"
debug "..."
debug=$curr_debug


if [[ $operation = "create-bucket" ]]; then
    create_bucket
elif [[ $operation = "list-summary" ]]; then
    s3_list_summary
elif [[ $operation = "create-user" ]]; then
    create_user_account
fi

#Log End msg.
exit_log


