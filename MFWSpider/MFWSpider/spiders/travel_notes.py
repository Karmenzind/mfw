# -*- coding: utf-8 -*-
import scrapy
from collections import defaultdict
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose

from MFWSpider.items import Note, Place
from MFWSpider.pipelines import MfwspiderPipeline


class TravelNotesSpider(CrawlSpider):
    name = 'travel_notes'
    allowed_domains = ['www.mafengwo.cn']

    db = MfwspiderPipeline()

    def start_requests(self):
        for doc in self.db.note.find({'is_crawled': False}):
            url = doc.get('url')
            if not url:
                continue
            yield Request(url, callback=self.parse_note)

    def parse_note(self, response):
        self.log("Using proxy: %s" % response.meta.get('proxy'))

        # main body
        _text = response.xpath('//p[re:match(@class, "^_j_note_content")]//text()').extract() #
        text = ''.join(_ for _ in _text if _.strip())
        text = text.replace('\n', ' ')

        note = Note()
        note['url'] = response.url
        note['is_crawled'] = True
        note['text'] = text

        def _get_title():
            result = ''
            for x in ('//div[@class="bread-con"]/a[2]/text()',
                      '//div[@class="post_title clearfix"]/h1/text()'):
                _r = response.xpath(x).get()
                if _r:
                    result = _r.strip()
                    break
            return result

        note['title'] = _get_title()

        note['related_dest_hrefs'], note['related_poi_ids'], places = self.parse_kws(response)
        for place in places:
            yield place

        yield note

    def parse_kws(self, response):
        """
        :returns:
            dest urls
            pois poi_ids
            places Places
        """
        # linked pois and dests
        poi_xpath = '//a[re:match(@data-cs-p, "ginfo.*poi")]'
        dest_xpath = '//p[@class="_j_note_content"]//a[@class="link _j_keyword_mdd"]'
        related_dest_xpath = '//*[@class="_j_mdd_stas"]'

        dests = []
        pois = []
        places = []

        def _parse(_xpath, _type, col):
            for selector in response.xpath(_xpath):
                parsed_kw = self.parse_single_kw(selector, _type)
                if not parsed_kw:
                    continue
                place = Place(parsed_kw)
                if _type == 'poi':
                    tag = place['poi_id']
                else:
                    tag = place['href']
                if tag not in col:
                    col.append(tag)
                if place not in places:
                    places.append(place)

        _parse(poi_xpath, 'poi', pois)
        _parse(dest_xpath, 'dest', dests)
        _parse(related_dest_xpath, 'dest', dests)
        return dests, pois, places

    def parse_single_kw(self, selector, _type):
        result = {}
        name = self.get_place_name(selector)
        if name:
            result['name'] = name
            result['href'] = selector.xpath('@href').get()
            result['p_type'] = _type
            if _type == 'poi':
                result['poi_id'] = selector.xpath('@data-poi_id').get() or selector.xpath('@data-poiid').get()
                if selector.xpath('./i'):
                    result['poi_type'] = selector.xpath('./i/@class').get()
                    result['other_name'] = selector.xpath('./text()[2]').get().strip()
        return result

    def get_place_name(self, selector):
        name = selector.xpath('@data_kw').get()
        if not name:
            t = selector.xpath('.//text()').extract()
            name = ''.join(_.strip() for _ in t if _.strip())
            name = name.replace('\n', '')
        return name

