#!/bin/bash

###################################################
# ORCA IAM Commands:
# ----------------
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
filter=
output_fields=

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ORCA_LOGFILE="/tmp/orcalog"


function show_help_iam_list-users()
{
    echo "IAM List Users"
    exit 1
}

function show_help_iam_create-user()
{
    echo "Usage: orcacli iam create-user -a <account> -u <user name> <-g group name>  -p <policies> -l -c "
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
    echo "-c access_key: [OPTIONAL] If specified create an access key for the user."
    echo ""
    echo "-p policies  : [OPTIONAL] List of \"space\"  seperated policies to be applied to the User if specified"
    echo ""
    echo "-l login     : [OPTIONAL] If specified create a login profile with a login password"
    echo ""

    exit 1
}

function show_help_iam_delete_user()
{
    echo "HELP: iam delete user"
    exit 1
}

function show_help_iam_grant-access()
{
    echo "HELP: iam grant access"
    exit 1
}

function show_help_iam_list-policies()
{
    echo "HELP: iam list policies"
    exit 1
}

function  show_help_iam_list-user-permissions()
{
    echo "HELP: iam list user permissions"
    exit 1
}

function  show_help_iam_revoke-access()
{
    echo "HELP: iam revoke access"
    exit 1
}



# Create User.
function create_user_account()
{
    # Note: pass policies in quotes ""
    validate_user_input $service_type $operation "$policies"
    create_user $account $user
    add_user_to_group $account $user $group
    attach_user_policies $account $user "$policies"
    create_access_key $account $user $create_accesskey
    create_login_credentials $account $user $create_logincredentials
}

# Grant Access.
function grant_access_to_resource()
{
    echo "user: $user, group: $group type: $resource_type , name: $resource_names, actions: $resource_actions" 
    validate_user_input $service_type $operation 
    create_iam_policy_document $resource_type "$resource_names" "$resource_actions"

}

#echo "$#"
#echo "COMMANDLINE: $COMMANDLINE"

#######################################
# Parse the positional arguments first.
# In this case it is the type of operation.
# Once we parse it 'shift' all the command line arguments
# one position to the left.
#######################################


CMD_OPTIONS="a:cdf:F:g:lo:O:n:p:rt:s:u:h"

while getopts ${CMD_OPTIONS} option; do
    case $option in
        h)
            help_function="show_help_${service_type}_${operation}"
            $help_function
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
        F)
            filter=$OPTARG
            ;;
        g)
            group=$OPTARG
            ;;
        l)
            create_logincredentials=true
            ;;
        n)
            resource_names=$OPTARG
            ;;
        o)
            outputformat=$OPTARG
            ;;
        O)
            output_fields=$OPTARG
            ;;
        p)
            policies=$OPTARG
            ;;
        r)
            delimiter=true
            ;;
        s)
            resource_actions=$OPTARG
            ;;
        t)
            resource_type=$OPTARG
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

if [[ $operation = "create-user" ]]; then
    create_user_account
elif [[ $operation = "list-users" ]]; then
    iam_list_users $outputformat
elif [[ $operation = "list-user-permissions" ]]; then
    iam_list_user_permissions $user $outputformat
elif [[ $operation = "list-policies" ]]; then
    iam_list_user_policies $user $outputformat
elif [[ $operation = "grant-access" ]]; then
    grant_access_to_resource
fi

#Log End msg.
exit_log


