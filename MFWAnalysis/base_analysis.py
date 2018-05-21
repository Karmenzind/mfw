# !/usr/bin/env python
# -*- coding: utf-8 -*-

# traverse notes

import re
from urllib import parse

import progressbar
from snownlp import SnowNLP as nlp

from utils.db import mongo_cli as db


"""
target:
{
    visit_time
    senti_of_sentences
    senti_of_notes
}
"""


def sentence_contains_brace(sentence):
    return re.search('{.+}', sentence)


class PlaceDataHelper:

    def __init__(self, spec):
        """
        :spec: use to find doc in db.place
        """
        self.place_spec = spec

    @property
    def place_doc(self):
        result = db.place.find_one(self.place_spec)

        if not result:
            print("Cannot find: %s" % self.place_spec)

        return result

    def add_visit(self, num=1):
        self.update({"$inc": {"visit_time": num}})

    def add_note_senti(self, senti):
        self.update({"$push": {"senti_of_notes": senti}})

    def add_sentence_senti(self, senti):
        self.update({"$push": {"senti_of_sentences": senti}})

    @property
    def find_spec(self):
        _id = self.place_doc.get('_id')
        result = {"place_id": _id}

        for key in ('p_type', 'name'):
            value = self.place_doc.get(key)

            if value:
                result[key] = value

        return result

    def update(self, update_spec):
        result = db.place_score.update_one(
            self.find_spec,
            update_spec,
            upsert=True,
        )
        print("spec: %s\n"
              "update: %s\n"
              "matched: %s\n"
              "modified: %s\n"
              "upserted: %s" % (
                  self.find_spec,
                  update_spec,
                  result.matched_count,
                  result.modified_count,
                  result.upserted_id,
              ))


class NoteParseHelper:

    def __init__(self, note_doc):
        self.doc = note_doc
        self._id = self.doc['_id']

        self.text = self.doc.get('text')
        self.dest_hrefs = self.doc.get('related_dest_hrefs', [])
        self.poi_ids = self.doc.get('related_poi_ids', [])
        self.title = self.doc.get('title')

        self.parse_main_dest()

    @property
    def _snow(self):
        return nlp(self.text)

    def parse_main_dest(self):
        _url = self.doc.get('main_dest', {}).get('url')

        if _url:
            href = parse.urlsplit(_url).path

            if href not in self.dest_hrefs:
                self.dest_hrefs.append(href)

    @property
    def whole_senti(self):
        return self._snow.sentiments

    @property
    def sent_senti(self):
        # filtered = filter(sentence_contains_brace, self._snow.sentences)
        sentences = self._snow.sentences

        return {_: nlp(_).sentiments for _ in sentences}

    def __str__(self):
        return '<Note: %s %s>' % (self._id, self.title)


def parse_note(doc):
    note_helper = NoteParseHelper(doc)
    print('Parsing ', note_helper)
    # dest

    for href in note_helper.dest_hrefs:
        spec = {'href': href}
        analysis_single_place(spec, note_helper)
    # poi

    for poi_id in note_helper.poi_ids:
        spec = {'poi_id': poi_id}
        analysis_single_place(spec, note_helper)


def analysis_single_place(place_spec, note_helper, _type=None):
    place_helper = PlaceDataHelper(place_spec)

    if not place_helper.place_doc:
        return

    place_helper.add_visit()

    if note_helper.text:
        place_helper.add_note_senti(note_helper.whole_senti)

        for sent, senti in note_helper.sent_senti.items():
            place_name = place_helper.place_doc.get('name', 'UNKNOWN')

            if place_name in sent:
                place_helper.add_sentence_senti(senti)


def main():
    spec = {"is_crawled": True}

    _gen = db.note.find(spec)
    # _gen = _gen.limit(1)  # test

    # db.place_score.drop()  # !!!

    total = _gen.count()
    parsed = 0

    with progressbar.ProgressBar(max_value=total,
                                 redirect_stdout=True) as bar:

        for doc in _gen:
            parsed += 1

            if parsed < 3307:
                print("Ignore: ", parsed)
                continue

            parse_note(doc)
            bar.update(parsed)


if __name__ == "__main__":
    main()
