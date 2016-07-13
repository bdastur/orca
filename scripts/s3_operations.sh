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
outputformat="table"
resource_actions=
resource_type=
resource_names=
prefix=
expiration_duration=
ia_transition_duration=
glacer_transition_duration=
filter=
output_fields=

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ORCA_LOGFILE="/tmp/orcalog"

# Help Functions
function show_help_s3_list-buckets()
{
    echo "Usage: orcacli s3 list-buckets [ -o <json|table>]"
    echo "--------------------------------------"
    echo "List All the buckets" 
    echo "-o <outputformat> : Specify the output format. (json or tabular). Default: table"
    echo ""

    exit 1
}

function show_help_s3_create-bucket()
{
    echo "Usage: orcacli s3 create-bucket -a <account> -b <bucket name> <-g <group name> | -u <user name>]"
    echo "--------------------------------------"
    echo "Create a S3 bucket. Create a new IAM Policy to allow access to bucket and attach it to the group or user"
    echo ""
    echo "-a account   : Specifiy the account name where the new user should be created."
    echo ""
    echo "-b bucket    : Specify the bucket name to create."
    echo ""
    echo "-u username  : Specify the IAM User to attach the policy to"
    echo ""
    echo "-g group     : Specify the IAM Group to attach the policy to"
    echo ""

    exit 1
}

function show_help_s3_create-lifecycle-policy()
{
    echo "S3: create lifecycle policy"
    exit 1
}

function show_help_s3_list-summary()
{
    echo "S3: show list summary help"
    exit 1
}

function show_help_s3_list-validations()
{
    echo "S3: show validations help"
    exit 1
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

CMD_OPTIONS="a:b:dF:g:u:ho:O:"


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
        F)
            filter=$OPTARG
            ;;
        g)
            group=$OPTARG
            ;;
        o)
            outputformat=$OPTARG
            ;;
        O)
            output_fields=$OPTARG
            ;;
        u)
            user=$OPTARG
            ;;
        :) echo "Error: option \"-$OPTARG\" needs argument";;
        *) echo "Error: Invalid option \"-$OPTARG\"";;
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


