from pymongo import MongoClient
from block_parser import parse_all

client = MongoClient("mongodb://vladseremet:abc918273645@ds155825.mlab.com:55825/cuc")
db=client.cuc
all_question_objects = parse_all()

for question_objects in all_question_objects:
    for question_object in question_objects:
        db.questions.insert_one(question_object)
