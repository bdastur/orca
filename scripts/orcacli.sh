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

operation=

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ORCA_LOGFILE="/tmp/orcalog"


#############
# Help Generic
##############
function show_help_generic()
{
    echo "`basename $0`  : ORCA - Operations"
    echo "-------------------------------------------------"
    echo "usage: orcacli <service type> <operation> [ OPTIONS ]"
    echo ""
    echo "Available Services: "
    echo "---------------------"
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
    local options=$2

    echo "AWS Service: $service"
    echo ""

    if [[ $service = "s3" ]]; then
        operations=($s3_operations)
    elif [[ $service = "iam" ]]; then
        operations=($iam_operations)
    elif [[ $service = "ec2" ]]; then
        operations=($ec2_operations)
    fi

    echo "Available Operations for $service:"
    echo "---------------------------------"
    for operation in "${operations[@]}"
    do
        echo "${operation}"
    done

    echo "Example: "
    echo "aws $service ${operations[0]}"

    exit 1
}



# Source helper scripts.
source $DIR/orca_cmdline.sh
source $DIR/aws_common_utils.sh


if [[ $# -eq 0 || $1 = '-h' ]]; then
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

if [[ $# -eq 0 || $1 = '-h' ]]; then
    show_help_service $service_type
fi


operation=$1
validate_operation_type $service_type $operation
shift

# Source Service Specific operation handlers.

if [[ $service_type = "iam" ]]; then
    echo "IAM Service"
    source $DIR/iam_operations.sh
elif [[ $service_type = "s3" ]]; then
    echo "S3 Service"
    source $DIR/s3_operations.sh
elif [[ $service_type = "ec2" ]]; then
    echo "EC2 service"
    source $DIR/ec2_operations.sh
fi

