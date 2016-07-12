#!/bin/bash

###################################################
# S3 cmdline operations:
# ---------------------
####################################################

account=
bucketname=
debug=false
group=
user=
create_accesskey=false
create_logincredentials=false
delimiter=false
force_password=
outputformat=
resource_actions=
resource_type=
resource_names=
prefix=
expiration_duration=
ia_transition_duration=
glacer_transition_duration=


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ORCA_LOGFILE="/tmp/orcalog"

# Help Functions
function show_help_list-buckets()
{
    echo "S3: List Buckets help"
}

function show_help_create-bucket()
{
    echo "S3: Create Bucket help"
}

function show_help_create-lifecycle-policy()
{
    echo "S3: create lifecycle policy"
}

function show_help_list-summary()
{
    echo "S3: show list summary help"
}

function show_help_list-validations()
{
    echo "S3: show validations help"
}


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


#readonly COMMANDLINE="$*"

CMD_OPTIONS="a:b:dg:u:ho:"


while getopts ${CMD_OPTIONS} option; do
    case $option in
        h)
            help_function="show_help_${service_type}_${operation}" 
            $help_function 
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
        g)
            group=$OPTARG
            ;;
        o)
            outputformat=$OPTARG
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
    s3_list_summary $outputformat
elif [[ $operation = "list-buckets" ]]; then
    s3_list_buckets $outputformat
elif [[ $operation = "list-validations" ]]; then
    s3_list_validations $outputformat
fi


