#!/bin/bash

###################################################
# S3 Operations:
# --------------
####################################################

account=
bucketname=
operation=
debug=false

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

####################################################
# show_help: 
# Display the help for this tool.
# @Arguments: None
####################################################
function show_help() 
{
    echo "`basename $0`  : ORCA - S3 Bucket Operations"
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
source $DIR/aws_common_utils.sh


function validate_input()
{
    local account_valid=false

    if [[ ( -z $account ) || ( -z $bucketname ) ]]; then
        echo "Error: Required Arguments -b <bucketname> and -a <account> not provided."
        echo "For Usage, execute:  `basename $0` -h"
        echo ""
        exit 1
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
        exit 1
    fi

    # Validate if bucket exists.
    buckets=($(aws s3api list-buckets --profile ${account} | awk -F " " '{print $3}'))

    for bucket in "${buckets[@]}"
    do
        if [[ $bucket = $bucketname ]]; then
            echo "Bucket with name $bucketname already exists"
            exit 1
        fi 
    done

    echo "Validations.. Complete"
}


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
        exit 1
    else
        debug "S3 Bucket $bucketname created successfully"
    fi

}


if [[ $# -eq 0 ]]; then
    echo "Error: No options provided"
    echo "For Usage, execute:  `basename $0` -h"
    echo "..."
    exit 1
fi

readonly COMMANDLINE="$*"

#######################################
# Parse the positional arguments first.
# In this case it is the type of operation.
# Once we parse it 'shift' all the command line arguments
# one position to the left.
#######################################
operation=
case $1 in
    create-bucket)
        echo "Create bucket"
        operation="create-bucket"
        ;;
    :) echo "NO option"; show_help;;
    *) echo "Invalid operation"; show_help;;
esac

shift


while getopts "a:b:dh" option; do
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

validate_input
s3_create_bucket $bucketname $account



