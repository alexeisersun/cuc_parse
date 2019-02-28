#!/bin/bash
regex="([^/]+)\.(doc|docx|pdf)$"
for file in ./unprocessed/doc/*
do
    echo $file
    if [[ $file =~ $regex  ]]
    echo $file
    then
        name="${BASH_REMATCH[1]}"
        soffice --headless --convert-to txt $file --outdir ./unprocessed/txt
    fi
done
