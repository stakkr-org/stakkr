#!/bin/bash
# This is a stakkr wrapper to run stakkr with abash shell from outside the 
# virtualenv.
# run this as the stakkr user!
# 
POSITIONAL=()
while [[ $# -gt 0 ]] 
do
    key="$1"

    case $key in
        -c|--command)
        COMMAND="$2"
        shift # past argument
        shift # past value
        ;;
        *)    # unknown option
        POSITIONAL+=("$1") # save it in an array for later
        shift # past argument
        ;;
    esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

WDIR=/home/rbindels/Projects/stakkr/stakkr_stakkr
VIRTUALENV_DIR=$WDIR

source $VIRTUALENV_DIR/bin/activate

cd $WDIR
stakkr $COMMAND