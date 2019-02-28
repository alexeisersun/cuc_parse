#!/bin/bash
for file in ./unprocessed/txt/*
do
    if [ -f $file ];
    then
        wc -l $file | grep '^0\s\(.*\)' | sed 's/^0\s//g' | xargs -I {} mv {} ./unprocessed/txt/empty
    fi
done
