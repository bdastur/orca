#!/bin/bash

services="ec2 iam s3"
s3_operations="create-bucket delete-bucket list-buckets"
iam_operations="create-user delete-user list-policies"


################################################
# validate_service_type:
# Validates the user input service type and make
# sure it is part of the list
# params:
# :$1: Name of the service ('iam', 's3', 'ec2'..)
#################################################
function validate_service_type()
{
    local user_servicetype=$1
    servicearr=($services)

    service_valid=false
    for service in "${servicearr[@]}"
    do
        if [[ $service_type = $service ]]; then
            service_valid=true 
        fi  
    done

    if [[ $service_valid = false ]]; then
        echo "Invalid service $service_type"
        exit 1
    fi
}

function validate_operation_type()
{
    local user_servicetype=$1
    local user_operationtype=$2
    local operation_valid=false

    if [[ $user_servicetype = "s3" ]]; then
        operations=($s3_operations)
        for operation in "${operations[@]}"
        do
            if [[ $operation = $user_operationtype ]]; then
                operation_valid=true
                break
            fi
        done
    elif [[ $user_servicetype = "iam" ]]; then
        operations=($iam_operations)
        for operation in "${operations[@]}"
        do
            if [[ $operation = $user_operationtype ]]; then
                operation_valid=true
                break
            fi
        done

    fi

    if [[ $operation_val = false ]]; then
        echo "Invalid Operation $user_operationtype for $user_servicetype"
        exit 1
    fi

}
