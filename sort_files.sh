#!/bin/bash

for file in ./download//*
do
    if [ -f "$file"  ]
        then
            doc=$( echo "$file" | grep -E "\.doc$" )
            docx=$( echo "$file" | grep -E "\.docx$" )
            pdf=$( echo "$file" | grep -E "\.pdf$" )
            if [ "$doc" ]
            then
                echo $file
                cp $file ./unprocessed/doc
            fi
            if [ "$docx" ]
            then
                echo $file
                cp $file ./unprocessed/docx
            fi
            if [ "$pdf" ]
            then
                echo $file
                cp $file ./unprocessed/pdf
            fi
    fi
done
