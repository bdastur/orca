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


function show_help_ec2_list-nwinterfaces()
{
    echo "EC2 List nw interfaces"
    exit 1
}

function show_help_ec2_list-secgroups()
{
    echo "HELP: ec2 list security groups"
    exit 1
}

function show_help_ec2_list-summary()
{
    echo "HELP: ec2 list summary"
    exit 1
}

function show_help_ec2_list-tags()
{
    echo "HELP: ec2 list tags"
    exit 1
}

function show_help_ec2_list-vms()
{
    echo "HELP: ec2 list vms"
    exit 1
}


echo "$#"
echo "COMMANDLINE: $COMMANDLINE"

#######################################
# Parse the positional arguments first.
# In this case it is the type of operation.
# Once we parse it 'shift' all the command line arguments
# one position to the left.
#######################################

CMD_OPTIONS="a:F:o:O:h"
echo "Operation in iam operations: $operation"
echo "Service type: $service_type"

while getopts ${CMD_OPTIONS} option; do
    case $option in
        h)
            help_function="show_help_${service_type}_${operation}"
            $help_function
            ;;
        a)
            account=$OPTARG
            ;;
        F)
            filter=$OPTARG
            ;;
        o)
            outputformat=$OPTARG
            ;;
        O)
            output_fields=$OPTARG
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

echo "Now run: $operation"

if [[ $operation = "list-vms" ]]; then
    ec2_list_vms $outputformat
elif [[ $operation = "list-tags" ]]; then
    ec2_list_tags $outputformat
elif [[ $operation = "list-secgroups" ]]; then
    ec2_list_sec_groups $outputformat
elif [[ $operation = "list-nwinterfaces" ]]; then
    ec2_list_nw_interfaces $outputformat
elif [[ $operation = "modify-tag" ]]; then
    ec2_modify_tags
fi


#Log End msg.
exit_log


