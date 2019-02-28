echo "Creating Directories"

mkdir -p ./unprocessed/doc/
mkdir -p ./unprocessed/docx/
mkdir -p ./unprocessed/pdf/
mkdir -p ./unprocessed/txt/empty
mkdir -p ./unprocessed/txt/blocky/
mkdir -p ./unprocessed/processed/
mkdir -p ./download/

echo "Downloading Documents:"
python ./scraper.py

echo "Sorting Documents (doc/docx/pdf)"
bash ./sort_files.sh

echo "Converting to txt"
bash ./convert_docs.sh

echo "Removing empty text documents"
bash ./remove_empty.sh
