# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from MFWSpider.items import Note, Place


class MfwspiderPipeline(object):

    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client["MFW"]

        self.note = db["Note"]
        self.place = db["Place"]

    def process_item(self, item, spider):
        if isinstance(item, Note):
            spec = {"url": item.get('url')}
            result = self._update_many(item, self.note, spec)
        if isinstance(item, Place):
            spec = {"href": item.get('href')}
            result = self._upsert_one(item, self.place, spec)
        spider.log('matched: %s modified: %s' % (result.matched_count,
                                                 result.modified_count))
        spider.log(item)

    def process_update_spec(self, item):
        update_spec = dict(item)
        update_spec.pop('_id', 'ignore')
        for key, value in item.items():
            if not value:
                update_spec.pop(key)
        return {"$set": update_spec}

    def _upsert_one(self, item, collection, spec=None):
        update_spec = self.process_update_spec(item)

        return collection.update_one(
            spec,
            update_spec,
            upsert=True,
        )

    def _update_many(self, item, collection, spec=None):
        update_spec = self.process_update_spec(item)

        return collection.update_many(
            spec,
            update_spec,
        )

