#!/bin/bash

services="ec2 iam s3"
#s3_operations="create-bucket delete-bucket list-buckets"
#iam_operations="create-user delete-user list-policies"

operations['s3']="create-bucket delete-bucket list-buckets"
operations['iam']="create-user delete-user list-policies"

service_type=

function find_options()
{
    local lastoption=$1
    local stage=$2
    echo "last option: $lastoption, stage: $stage"
    echo ""

    if [[ $stage = 1 ]]; then
        COMPREPLY=($services)
    elif [[ $stage = 2 ]]; then
        # First check if we matched any of the services in
        # services list.
        servicearr=($services)
        service_match=false
        for service in "${servicearr[@]}"
        do
            if [[ $service = $lastoption ]]; then
                # Matched a service.
                COMPREPLY=($operations[$service])
                service_match=true
                service_type=$service
            fi
        done

        if [[ $service_match = false ]]; then
            newarr=""
            for service in "${servicearr[@]}"
            do
                if [[ $service = ${lastoption}* ]]; then
                    echo "service matched: $service"
                    newarr="${newarr} $service"
                fi  
            done 
            COMPREPLY=($newarr)
        fi
    elif [[ $stage = 3 ]]; then
        # Stage 3. We are at service level operations.
        operationarr=($operations[$service_type])
        echo "Operation arr: $operationarr"
        operation_match=false
        for operation in "${operationarr[@]}"
        do
          echo "operation: $operation"
          if [[ $operation = $lastoption ]]; then
              operation_match=true
              break
          fi
        done

        if [[ $operation_match = false ]]; then
            newarr=""
            for operation in "${operationarr[@]}"
            do
                if [[ $operation = ${lastoption}* ]]; then
                    newarr="${newarr} $operation"
                fi
            done
            COMPREPLY=($newarr)
        fi
    fi
}

function _cmdline_complete()
{
    cmd="${1##*/}"
    word=${COMP_WORDS[COMP_CWORD]}
    line=${COMP_LINE}
    option=($line)
    lastoption=${option[${#option[@]}-1]}
    stage=${#option[@]}

    find_options ${lastoption} ${stage}


}

complete -F _cmdline_complete orcacli.sh 

