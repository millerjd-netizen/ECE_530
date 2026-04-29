from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["image_pipeline_db"]
collection = db["annotations"]


def save_annotation(annotation):
    collection.insert_one(annotation)


def get_all_annotations():
    return list(collection.find({}, {"_id": 0}))