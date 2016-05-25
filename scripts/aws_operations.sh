#!/bin/bash

###################################################
# Common AWS CLI operations
# -------------------------
#
# Justification:
# Ok, so why have another CLI wrapper for AWS operations, when we
# already have aws cli.
# 
# I like examples. Adding a new user account. Pretty basic, and you
# can use AWS CLI to do that as simply. But in reality adding a 
# new user account will require several operations like -
#  adding a user, adding the user to a group, attaching policies
# Now you would have to figure out the correct policy-arn for the 
# policy you want to add.
#
# This is the sort of complex scenario that we can solve. Also we 
# can do validation checks beforehand to make sure we perform
# operations.
#
####################################################

# Globals.
account=
group=
user=
debug=false
create_accesskey=false
create_logincredentials=false
delimiter=false
operations=

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


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

# Source helper scripts.
source $DIR/aws_iam_operations.sh

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
    echo "-o operations: Specify the operations to perform"
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


if [[ $# -eq 0 ]]; then
    echo "Error: No options provided"
    echo "For Usage, execute:  `basename $0` -h"
    echo "..."
    exit 1
fi

readonly COMMANDLINE="$*"

while getopts "a:cdg:lo:p:ru:h" option; do
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
        o)
            operations=$OPTARG
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



