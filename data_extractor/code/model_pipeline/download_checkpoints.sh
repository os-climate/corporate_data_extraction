#!/bin/bash

# if directory doesn't exist, create it
if [ ! -d $1 ]
then
    mkdir -p $1
else
    echo "$1 exists, not mkdir."
fi

# if checkpoint zip file doesn't exist, download it
if [ ! -f $1/$2 ]
then
    gdown_path=$(which gdown)

    while true; do
        ls $2 2> /dev/null
        EC=$?
        if [ $EC -eq 0 ]; then
          break
        fi
        $gdown_path $3
    done

    # move downloaded zip file to appropriate folder
    mv $2 $1
else
    echo "$2 exists, not downloading."
fi
