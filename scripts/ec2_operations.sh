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
    echo "Usage: orcacli ec2 list-secgroups [-o <json|table>] [-F <filter>]"
    echo "---------------------------------------"
    echo "List all tags"
    echo "-o <outputformat>: Specify output format. (json|table). Default: table"
    echo "-F <filter>: {Json format}"
    echo ""
    echo "Examples:"
    echo "==========="
    echo "List security groups in all regions and all accounts as specified in your .aws/credentials file"
    echo "orcacli ec2 list-secgroups"
    echo ""

    echo "List security groups with output as json"
    echo "orcacli ec2 list-secgroups -o json"
    echo ""

    echo "List security groups in region us-west-1:"
    echo "orcacli ec2 list-secgroups -F '[{\\\"Name\\\": \\\"region\\\", \\\"Values\\\": [\\\"us-west-1\\\"]}]'"
    echo ""

    echo "List sec groups in region us-west-1 or us-west-2 or us-east-1 and with tag Project == Openshift"
    echo "orcacli ec2 list-secgroups -F '[{\\\"Name\\\": \\\"region\\\", \\\"Values\\\": [\\\"us-west-1\\\","\
         "\\\"us-west-2\\\", \\\"us-east-1\\\"]}, {\\\"Name\\\": \\\"Tags.Project\\\", \\\"Values\\\": [\\\"Openshift\\\"]}]'"
    echo ""

    echo "List sec groups in regions us-west-1 or us-east-1 and Where Cidr IP is 0.0.0.0/0 for port 22. NOTE: replace . with : for ip addr"
    echo "orcacli ec2 list-secgroups -F '[{\\\"Name\\\": \\\"region\\\"," \
         " \\\"Values\\\": [\\\"us-west-1\\\", \\\"us-east-1\\\"]}, {\\\"Name\\\": \\\"IpPermissions.22.IpRanges.0:0:0:0/0\\\", \\\"Values\\\": [1]}]'"
    echo ""

    echo "List sec groups whose GroupName starts with _CPE_"
    echo "orcacli ec2 list-secgroups -F '[{\\\"Name\\\": \\\"GroupName\\\", \\\"Values\\\": [\\\"_CPE_*\\\"], \\\"regex\\\": \\\"True\\\"}]'"
    echo ""
    exit 1

}

function show_help_ec2_list-summary()
{
    echo "HELP: ec2 list summary"
    exit 1
}

function show_help_ec2_list-tags()
{
    echo "Usage: orcacli ec2 list-tags [-o <json|table>] [-F <filter>]"
    echo "---------------------------------------"
    echo "List all tags"
    echo "-o <outputformat>: Specify output format. (json|table). Default: table"
    echo "-F <filter>: {Json format}"
    echo ""
    echo "Examples:"
    echo "==========="
    echo "orcacli ec2 list-tags"
    echo "orcacli ec2 list-tags -o json"
    echo "orcacli ec2 list-tags -F '[{\\\"Name\\\": \\\"ResourceType\\\", \\\"Values\\\": [\\\"vpc\\\"]}]'"
    exit 1
}

function show_help_ec2_list-vms()
{
    echo "HELP: ec2 list vms"
    exit 1
}


#######################################
# Parse the positional arguments first.
# In this case it is the type of operation.
# Once we parse it 'shift' all the command line arguments
# one position to the left.
#######################################

CMD_OPTIONS="a:F:o:O:h"

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


