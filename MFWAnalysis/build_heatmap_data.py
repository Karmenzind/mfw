#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

from bson.objectid import ObjectId
from utils.db import mongo_cli

dest_src = './output/dests_sorted.csv'
poi_src = './output/pois_sorted.csv'

output_dir = './heatmap/data'


def get_coordinates(_id):
    result = None
    print(_id)
    doc = mongo_cli.place.find_one({'_id': ObjectId(_id)})
    print(doc)

    if doc and 'lat' in doc and 'lng' in doc:
        result = doc['lat'], doc['lng']

    return result


def data_iter(data_path):
    with open(data_path) as f:
        for idx, line in enumerate(f):
            if not idx:
                continue
            _id, name, score = line.strip().split(',')
            coor = get_coordinates(_id)

            if not coor:
                continue
            lat, lng = coor
            yield name, score, lat, lng


def save_base_heatmap_file(save_name, data: dict):
    json_str = json.dumps(data)
    text = "var heatmapData = %s;" % json_str
    with open(os.path.join(output_dir, save_name), 'w') as f:
        f.write(text)


def build_base_heatmap_js(save_name, data_path, rate=1):
    result = []
    for t in data_iter(data_path):
        _, count, lat, lng = t
        count = float(count * rate)
        result.append(dict(
            lat=float(lat),
            lng=float(lng),
            count=count,
        ))
    save_base_heatmap_file(save_name, result)


def build_district_csv(save_name, data_path, rate=1):
    _f = os.path.join(output_dir, save_name)
    with open(_f, 'w') as f:
        f.write('name,score,coordinates\n')
        for t in data_iter(data_path):
            name, score, lat, lng = t

            coor = '"%s,%s"' % (lng, lat)
            line = '%s,%s,%s\n' % (name, score, coor)
            f.write(line)


if __name__ == "__main__":
    build_base_heatmap_js('base_heatmap_dest.js', dest_src)
    build_base_heatmap_js('base_heatmap_poi.js', poi_src)
    build_district_csv('district_dest.csv', dest_src)
    build_district_csv('district_poi.csv', poi_src)
