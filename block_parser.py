# -*- coding: utf-8 -*-
import re
import os
import pickle
import sys
import json
from logging import getLogger, StreamHandler
import argparse

logger = getLogger(__name__)
logger.setLevel("INFO")

question_pattern = re.compile(
    r"^((I|Î)ntrebare(a)?|#)?(:)?(\s)*((de)?\srezev[aă])?\d{1,2}(\s)*(;|\.|\-|:|\)?)?",
    re.I,
)
answer_pattern = re.compile(r"^(((Ră|Ra)spuns)|(R\.S|Rsp|R))\s*(\.|:|-|=)", re.I)
comment_pattern = re.compile(r"^((Comentari[ui]|C)(;|:|-|\.)\s*)", re.I)
source_pattern = re.compile(r"^(surs(ă|a|e))\s*(:|-)\s*", re.I)
author_pattern = re.compile(r"^A(utor)?:\s*", re.I)
hyperlink_pattern = re.compile(r"http(s)?://", re.I | re.M)

map_categories = ["question", "answer", "comment", "source", "author", "unknown"]
raw_txts_path = "./data/raw/txt"
raw_txt_path = "./data/raw/txt/%s"
blocky_txt_path = "./data/raw/txt/blocky/%s"
metadata_path = "./data/metadata/%s"


def add_lines_between_blocks(file_handler):
    lines = file_handler.readlines()
    for i in range(len(lines)):
        lines[i] = re.sub(r"^\s*", "", lines[i])
        if (
            re.match(question_pattern, lines[i])
            or re.match(answer_pattern, lines[i])
            or re.match(comment_pattern, lines[i])
            or re.match(source_pattern, lines[i])
            or re.match(author_pattern, lines[i])
        ):
            lines[i] = "\n" + lines[i]
    return lines


def get_blocks(lines):
    # find empty lines
    empty_indices = []
    for i in range(len(lines)):
        empty_match = re.search(r"^\s+$", lines[i])
        if empty_match:
            empty_indices.append(i)

    # discount empty line that are surrounded by empty lines
    to_delete = []
    if empty_indices[0] == 0:
        to_delete.append(0)
    for i in range(len(empty_indices) - 2, 0, -1):
        if (
            empty_indices[i - 1] == empty_indices[i] - 1
            and empty_indices[i + 1] == empty_indices[i] + 1
        ):
            to_delete.append(i)

    for i in to_delete:
        del empty_indices[i]

    # now empty_indices contains the indices of the lines that separate blocks of text
    empty_indices.insert(0, -1)
    empty_indices.append(len(lines) - 1)
    blocks = []
    for i in range(len(empty_indices) - 1):
        blocks.append(
            "".join(
                [lines[i] for i in range(empty_indices[i] + 1, empty_indices[i + 1])]
            )
        )

    for i in range(len(blocks)):
        blocks[i] = re.sub(r"\n", " ", blocks[i])
    return blocks


def categorize_blocks(blocks):
    """
    0: question
    1: answer
    2: comment
    3: source
    4: author
    5: unknown
    """
    categories = [5 for b in blocks]
    for i in range(len(blocks)):
        if re.match(question_pattern, blocks[i]):
            categories[i] = 0
            blocks[i] = re.sub(question_pattern, "", blocks[i])
        elif re.match(answer_pattern, blocks[i]):
            categories[i] = 1
            blocks[i] = re.sub(answer_pattern, "", blocks[i])
        elif re.match(comment_pattern, blocks[i]):
            categories[i] = 2
            blocks[i] = re.sub(comment_pattern, "", blocks[i])
        elif re.match(source_pattern, blocks[i]) or re.search(
            hyperlink_pattern, blocks[i]
        ):
            categories[i] = 3
            blocks[i] = re.sub(source_pattern, "", blocks[i])
        elif re.match(author_pattern, blocks[i]):
            categories[i] = 4
            blocks[i] = re.sub(author_pattern, "", blocks[i])

    for i in range(len(blocks) - 2, -1, -1):
        if categories[i] == 5:
            if categories[i + 1] == 1 or categories[i + 1] == 0:
                categories[i] = 0
    # merge neighboring blocks of the same category
    i = 0
    while i < len(blocks) - 1:
        while i < len(blocks) - 1 and categories[i + 1] == categories[i]:
            blocks[i] += "\n" + blocks[i + 1]
            del blocks[i + 1]
            del categories[i + 1]
        i += 1

    i = 0
    while i < len(blocks):
        if categories[i] == 5:
            del blocks[i]
            del categories[i]
        i += 1
    return (blocks, categories)


def empty_question_object():
    return {"question": "", "answer": "", "comment": "", "source": "", "authors": ""}


def get_question_objects(blocks, categories):
    question_objects = []
    current_question_object = empty_question_object()
    last_found = 5
    for i in range(len(blocks)):
        if categories[i] == 0:  # question
            if last_found not in [0, 5]:
                question_objects.append(current_question_object)
            current_question_object = empty_question_object()
            current_question_object["question"] = blocks[i].strip()
            last_found = 0
        if categories[i] == 1:  # answer
            if last_found == 0:
                current_question_object["answer"] = blocks[i].strip()
                last_found = 1
            else:
                last_found = 5
                current_question_object = empty_question_object()
        if categories[i] == 2:  # comment
            if last_found in [1, 4]:
                current_question_object["comment"] = blocks[i].strip()
                last_found = 2
            else:
                last_found = 5
                current_question_object = empty_question_object()
        if categories[i] == 3:  # source
            if last_found in [1, 2, 4]:
                current_question_object["source"] = blocks[i].strip()
                last_found = 3
            else:
                last_found = 5
                current_question_object = empty_question_object()
        if categories[i] == 4:  # Author
            if last_found in [0, 1, 2, 3]:
                current_question_object["authors"] = blocks[i].strip()
                last_found = 4
            else:
                last_found = 5
                current_question_object = empty_question_object()
    if last_found != 5:
        question_objects.append(current_question_object)
    return question_objects


def parse_file(filename):
    name = filename.split("/")[-1]

    with open(filename, "r") as file_without_blocks:
        with open(blocky_txt_path % name, "w+") as file_with_blocks:
            lines = add_lines_between_blocks(file_without_blocks)
            file_with_blocks.write("".join(lines))

    with open(blocky_txt_path % name, "r") as file_with_blocks:
        with open(metadata_path % re.sub(r".txt$", ".info", name), "rb") as file_with_metadata:
            info = pickle.load(file_with_metadata)
            num_questions = int(info["number_of_questions"])
            lines = file_with_blocks.readlines()
            blocks = get_blocks(lines)
            (blocks, categories) = categorize_blocks(blocks)
            question_objects = get_question_objects(blocks, categories)
            logger.info("Extracted {} out of {} questions from {}.".format(len(question_objects), num_questions, name))

            return (question_objects, num_questions)


def parse_all():
    total = 0
    successful = 0
    all_question_objects = []
    for filename in os.listdir(raw_txts_path):
        if not filename.endswith(".txt"):
            continue
        (question_objects, num_questions) = parse_file(raw_txt_path % filename)
        all_question_objects.append(question_objects)
        total += num_questions
        successful += len(question_objects)
    logger.info("Extracted %s out of %s questions." % (successful, total))
    return all_question_objects


if __name__ == "__main__":
    logger.addHandler(StreamHandler(sys.stdout))
    parser = argparse.ArgumentParser(description='Parse questions.')
    parser.add_argument('--all', '-a', dest='all_files', action='store_true', help='parse all files.')
    parser.add_argument('--in', nargs="*", type=str, dest='input_files', action='store', help='parse only selected files.')
    parser.add_argument('--out', nargs=1, type=str, dest='output_file', action='store', help='parse only selected files.')

    args = parser.parse_args()

    parsed_data = []
    if args.all_files:
        parsed_data = parse_all()
    elif args.input_files:
        for filename in args.input_files:
            if filename.endswith(".txt"):
                (question_objects, num_questions) = parse_file(filename)
                logger.info("Extracted %d out of %d questions." % (len(question_objects), num_questions))
                parsed_data.append(question_objects)
            else:
                logger.warning("Must be a *.txt file!")
    else:
        logger.warning("Must provide either '--all' or '--in FILE'.")
        exit()

    if args.output_file[0]:
        with open(args.output_file[0], "w") as f:
            json.dump(parsed_data, f)

        logger.info("Saved parsed data to %s" % args.output_file[0])
