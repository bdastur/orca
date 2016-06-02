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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ORCA_LOGFILE="/tmp/orcalog"

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


function deprecated_validate_input()
{
    local account_valid=false

    if [[ ( -z $account ) || ( -z $bucketname ) ]]; then
        echo "Error: Required Arguments -b <bucketname> and -a <account> not provided."
        echo "For Usage, execute:  `basename $0` -h"
        echo ""
        exit_log
    fi

    ##############################################
    # Validate account information.
    ##############################################
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
        exit_log
    fi

    # Validate if bucket exists.
    buckets=($(aws s3api list-buckets --profile ${account} | awk -F " " '{print $3}'))

    for bucket in "${buckets[@]}"
    do
        if [[ $bucket = $bucketname ]]; then
            echo "Bucket with name $bucketname already exists"
            exit_log
        fi 
    done

    echo "Validations.. Complete"
}


if [[ $# -eq 0 ]]; then
    echo "Error: No options provided"
    echo "For Usage, execute:  `basename $0` -h"
    echo "..."
    exit 1
elif [[ $1 = '-h' ]]; then
    echo "BRD. Here"
    show_help
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
echo "Service type: $service_type"
validate_service_type $service_type
shift

echo "options: $*"

operation=$1
validate_operation_type $service_type $operation
shift


CMD_OPTIONS="a:b:dh"

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
        d) 
            debug=true
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
    validate_user_input $service_type $operation 
    s3_create_bucket $bucketname $account
    create_s3_access_managed_policy $account $bucketname 'Allow'
elif [[ $operation = "list-summary" ]]; then
    s3_list_summary
elif [[ $operation = "create-user" ]]; then
    echo "Operation: $operation... NotImplemented"
    #validate_input
    #create_user
    #add_user_to_group
    #attach_user_policies
    #create_access_key
    #create_login_credentials
fi

#Log End msg.
exit_log


