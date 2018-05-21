# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo


class MongoDBCli:

    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client["MFW"]

        self.note = db["Note"]
        self.place = db["Place"]
        self.place_score = db["PlaceScore"]


mongo_cli = MongoDBCli()
