# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class Note(Item):
    """ 游记
    """
    _id = Field()
    url = Field()    # str
    is_crawled = Field()  # bool
    from_url = Field()
    main_dest = Field()
    date = Field()

    title = Field()
    text = Field()
    related_dest_hrefs = Field()
    related_poi_ids = Field()


class Place(Item):
    """ 地点
    """
    _id = Field()

    # common
    p_type = Field()  # travel
    url = Field()
    href = Field()
    name = Field()
    other_name = Field()

    # for poi
    poi_id = Field()
    poi_type = Field()  # iclass
    # TODO: picture

    is_crawled = Field()  # bool
    lat = Field()
    lng = Field()
    address = Field()  # 文字描述的地址
    # comment_num = Field()  # 评论数
    # popularity = Field()  # 景点人数

