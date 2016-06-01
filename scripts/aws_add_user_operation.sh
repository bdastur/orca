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
force_password=

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

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

while getopts "a:cdf:g:lp:ru:h" option; do
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



