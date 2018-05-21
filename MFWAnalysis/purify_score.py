#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import shutil

import progressbar

from utils.db import mongo_cli as db

time_str = str(datetime.datetime.now()).replace(' ', '_').split('.')[0]
result_csv = './output/result_%s.csv' % time_str
common_csv = './output/result.csv'


def add_result(line):
    with open(result_csv, 'a') as f:
        f.write(line)


def wind_up():
    shutil.copyfile(result_csv, common_csv)
    print('DONE:)')


def save_result(lines):
    """output

    :lines: iterable
    """
    with open(result_csv, 'w') as f:
        f.writelines(lines)


def cal_sentis(sentis, weight):
    return sum(_*weight for _ in sentis if _ > 0.5)


def score_of_place(doc):
    visit_times = doc.get('visit_time', 0)
    note_sentis = doc.get('senti_of_notes', [])
    sent_sentis = doc.get('senti_of_sentences', [])

    note_senti_score = cal_sentis(note_sentis, 0.5)
    sent_senti_score = cal_sentis(sent_sentis, 1.5)

    score = visit_times + note_senti_score + sent_senti_score

    return score


if __name__ == "__main__":
    _gen = db.place_score.find({})
    with progressbar.ProgressBar(max_value=_gen.count(),
                                 redirect_stdout=True) as bar:
        count = 0

        for doc in _gen:
            count += 1

            id_str = str(doc.get('place_id'))
            name = doc.get('name', 'unknown')

            p_type = doc.get('p_type')

            if not p_type:
                continue

            score = str(score_of_place(doc))
            items = (id_str, name, p_type, score)
            line = ','.join(items)
            print(line)
            add_result(line + '\n')

            bar.update(count)

    wind_up()
