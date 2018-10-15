from hackernews import HackerNews
import pyphen
import random
from itertools import chain
from datetime import datetime
from pprint import pprint
from pymongo import MongoClient
from threading import Timer
import os


now = datetime.now()

class MongoConnection():

    """
    Establishes a connection to PyMongo
    Returns DB and Collection access
    """

    def __init__(self,db_name, collection_name):

        self.client = MongoClient('mongo', 27017)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_db(self):
        return self.db

    def get_collection(self):
        return self.collection


def load_name_to_mongo():
    """
     Gets data from HN and cleans it
     50 headlines split up into syllables of proper nouns
     """

    dic = pyphen.Pyphen(lang='en')

    hn = HackerNews()

    top_stories = hn.top_stories(limit=50)

    words = [title for story in top_stories for title in filter(str.isalpha,story.title.split(' '))]

    syllables = [syllable for word in words if not word.islower() and not word.isupper() for syllable in
                 dic.inserted(word).split("-")]

    mixed_bag = [syllable for syllable in syllables if len(syllables) > 1]

    return mixed_bag



def load_data():
    """
     Inserts into Mongo DB
     """

    mongo = MongoConnection("hn", "syllables")
    collection = mongo.get_collection()

    inserted = 0

    for syllable in load_name_to_mongo():

        syl= {"text": syllable,
                 "date": datetime.utcnow()}

        collection.insert_one(syl)
        inserted += 1

    print (f"{inserted} records inserted at {now}")


def get_random_doc(collection):
    """
        Generates a 2-syllable string to return to hustlr app
        """


    strings = []

    records = collection.aggregate( [ { "$sample": {"size": 2} } ] )

    for document in records:
        if document['text']:
            strings.append(document['text'])

    return f"{strings[0].upper()}{strings[1].upper()}"

if __name__ == '__main__':
    load_data()





