# -*- coding: utf-8 -*-

import re
from urllib.parse import urljoin

from scrapy.conf import settings
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest

from MFWSpider.items import Place
from MFWSpider.pipelines import MfwspiderPipeline

db = MfwspiderPipeline()


class PlacesSpider(CrawlSpider):
    name = 'places'
    allowed_domains = ['www.mafengwo.cn']
    base = 'http://www.mafengwo.cn'

    def start_requests(self):
        spec = {"lat": {"$exists": False}}
        # spec['p_type'] = 'poi'
        gen = db.place.find(spec)

        if settings.get("IS_TEST"):
            gen = gen.limit(10)

        for doc in gen:
            href = doc.get('href')
            if not href:
                continue
            url = urljoin(self.base, href)

            if doc.get('p_type') == 'poi':
                yield SplashRequest(url, 
                                    callback=self.parse_poi, 
                                    meta={"_href": href})
            elif doc.get('p_type') == 'dest':
                yield Request(url, 
                              callback=self.parse_dest,
                              meta={'_href': href})

    def parse_poi(self, response):
        item = Place()
        coord_sel = response.xpath('//div[@class="m-poi"][1]//li[1]')
        item['lat'] = coord_sel.xpath('@data-lat').get()
        item['lng'] = coord_sel.xpath('@data-lng').get()
        if not (item['lat'] and item['lng']):
            self.get_coor_from_js(response, item)
        item['address'] = response.xpath('//div[@class="mhd"]/p/text()').get()
        yield self.check_crawled(item, response)

    def parse_dest(self, response):
        item = Place()
        self.get_coor_from_js(response, item)
        yield self.check_crawled(item, response)

    def check_crawled(self, item: Place, response):
        if item['lat'] and item['lng']:
            item['href'] = response.meta['_href']
            return item
        raise AssertionError("Failed to get coordinates for %s" % response.url)

    def get_coor_from_js(self, response, item):
        coor_js_raw = response.xpath('//script[re:match(text(), "zoom")]/text()').get()
        coor_js = re.sub('[\n\s\t]+', '', str(coor_js_raw))
        item['lat'], item['lng'] = re.search(r"lat':(\d+.\d+),'lng':(\d+.\d+)",
                                             coor_js).groups()
