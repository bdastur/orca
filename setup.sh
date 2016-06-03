#!/bin/bash

curdir=`pwd`
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo $curdir
cmdline_completion="$curdir/scripts/orca_completion.sh"

pythonpath=$curdir
export PYTHONPATH=${PYTHONPATH}:${pythonpath}

# Source the orca cmdline completion script
source ${cmdline_completion}

alias orcacli.sh="$DIR/scripts/orcacli.sh"
