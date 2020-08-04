#!/bin/bash
echo "***** Create directories *****"

mkdir -p ./data/raw/doc/
mkdir -p ./data/raw/docx/
mkdir -p ./data/raw/pdf/
mkdir -p ./data/raw/txt/empty
mkdir -p ./data/raw/txt/blocky/
mkdir -p ./data/raw/processed/
mkdir -p ./data/downloads/
mkdir -p ./data/metadata/

echo "***** Download documents *****"

python ./scraper.py

echo "***** Sort documents (doc/docx/pdf) *****"

for file in ./data/downloads/*
do
    if [ -f "$file"  ]
        then
            doc=$( echo "$file" | grep -E "\.doc$" )
            docx=$( echo "$file" | grep -E "\.docx$" )
            pdf=$( echo "$file" | grep -E "\.pdf$" )
            filename=$( basename "$file" )

            if [ "$doc" ] && ! test -f $( echo "./data/raw/doc/$filename")
            then
                echo "Copy $filename to ./data/raw/doc"
                cp $file ./data/raw/doc
            else
                if [ "$docx" ] && ! test -f $( echo "./data/raw/docx/$filename")
                then
                    echo "Copy $filename to ./data/raw/docx"
                    cp $file ./data/raw/docx
                else
                    if [ "$pdf" ] && ! test -f $( echo "./data/raw/pdf/$filename")
                    then
                        echo "Copy $filename to ./data/raw/pdf"
                        cp $file ./data/raw/pdf
                    else
                        echo "Skip copying $file"
                    fi
                fi
            fi
    fi
done

echo "***** Converting to txt *****"

regex="([^/]+)\.(doc|docx|pdf)$"
for file in ./data/raw/doc/*
do
    filename=$( basename "$file" )
    if [[ $file =~ $regex ]] && ! test -f $( echo "./data/raw/txt/$filename" | sed "s/\.doc\$/\.txt/" )
    then
        echo "Converting $filename"
        name="${BASH_REMATCH[1]}"
        soffice --headless --convert-to txt $file --outdir ./data/raw/txt > /dev/null 2>&1
    else
        echo "Skip converting $filename"
    fi
done

echo "***** Remove empty text documents ******"
for file in ./data/raw/txt/*
do
    if [ -f $file ];
    then
        wc -l $file | grep '^0\s\(.*\)' | sed 's/^0\s//g' | xargs -I {} mv {} ./data/raw/txt/empty
    fi
done

echo "***** Done ******"
