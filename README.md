# CUC Parse

This program parses documents that contain questions for Who? When? Where? game, commonly known as "Ce? Unde? Când?" or simply CUC.

### Requirements & usage

Requirements:
  - pipenv
  - Python 3

Install:

```bash
# install dependencies
pipenv install

# create directories, download all docs and convert them to text form
./setup.sh
```

### Usage

```bash
# parse all files from 'data/raw/txt' directory & save as JSON to a file
python block_parser.py --all --out output_file

# parse a single file (from 'data/raw/txt' dir) & save as JSON to a file
python block_parser.py --in FILE --out output_file

# get help and more options
python block_parser.py --help
```

