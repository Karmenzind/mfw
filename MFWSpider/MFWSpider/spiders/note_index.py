# -*- coding: utf-8 -*-
import datetime
import logging
import re

import scrapy
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.spiders import CrawlSpider, Rule

from MFWSpider.items import Note

date_pattern = re.compile('(\d+).+?(\d+).+?(\d+)')


class NoteIndexSpider(CrawlSpider):
    name = 'note_index'
    allowed_domains = ['www.mafengwo.cn']

    # rules = (
    #    # 自动翻页
    #    Rule(LinkExtractor(allow=r'/'), callback='parse_index', follow=True),
    # )

    def start_requests(self):
        base_url = 'http://www.mafengwo.cn/search/s.php?q={keyword}&t=info'
        keywords = self.settings.get('NOTE_KEYWORDS')

        for kw in keywords:
            for page in range(50):
                url = base_url.format(keyword=kw)

                if page:
                    p = page + 1
                    url += '&p={pn}&kt=1'.format(pn=p)
                yield Request(url, callback=self.parse_index)

    def parse_index(self, response):
        for selector in response.xpath('//div[@class="att-list"]/ul/li'):
            item = Note()

            item['url'] = selector.xpath(
                './/div[@class="ct-text "]/h3//@href').get()
            item['from_url'] = response.url
            #item['is_crawled'] = False
            dest_sel = selector.xpath('.//div[@class="ct-text "]/ul/li[1]')
            item['main_dest'] = {
                "name": dest_sel.xpath('./a/text()').get(),
                "url": dest_sel.xpath('./a/@href').get(),
            }
            date_str = selector.xpath(
                './/div[@class="ct-text "]/ul/li[5]/text()').get()
            try:
                search_res = date_pattern.search(date_str.strip())
                item['date'] = datetime.datetime(
                    *map(int, search_res.groups()))
            except Exception:
                self.logger.exception(
                    'Failed to fetch date from: %s' % date_str)
            yield item
