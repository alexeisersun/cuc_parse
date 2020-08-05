# CUC Parse

This program parses documents that contain questions for Who? When? Where? game, commonly known as "Ce? Unde? Când?" or simply CUC.

### Requirements & usage

Requirements:
  - Python 3

Install:

```bash
# create directories, download all docs and convert them to text form
./setup.sh
```

### Usage

```bash
# parse all files & save as JSON to a file
python block_parser.py --all --out output_file

# parse a single file & save as JSON to a file
python block_parser.py --in FILE --out output_file

# get help
python block_parser.py --help
```
