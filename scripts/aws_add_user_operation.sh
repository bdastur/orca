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
    echo "-p policies  : [OPTIONAL] List of command seperated policies to be applied to the User if specified" 
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

    # Check if the account valid flag is set.
    if [[ $account_valid == true ]]; then
        echo "Account is valid."
    else
        echo "Error: Invalid Account provided \"$account\""
        echo "Valid values are: ${credinfo[@]}"
    fi


    
}


if [[ $# -eq 0 ]]; then
    echo "Error: No options provided"
    echo "For Usage, execute:  `basename $0` -h"
    echo "..."
    exit 1
fi

readonly COMMANDLINE="$*"

while getopts "a:g:p:u:h" option; do
    case $option in
        h)
            show_help 
            ;;
        a) 
            account=$OPTARG
            ;;
        g)
            group=$OPTARG
            ;;
        u) 
            user=$OPTARG
            ;;
        p)
            policies=$OPTARG
            ;;
        :) echo "Error: option \"-$OPTARG\" needs argument"; show_help;;
        *) echo "Error: Invalid option \"-$OPTARG\""; show_help;;
    esac
done

validate_input


