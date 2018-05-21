# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import json
import random
from collections import defaultdict
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware


class MfwspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MfwspiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomHttpProxyMiddleware(HttpProxyMiddleware):

    def __init__(self, crawler, auth_encoding='latin-l', proxy_list_file=None, local_proxy_type=None):
        if not proxy_list_file:
            raise NotConfigured

        self.crawler = crawler

        self.auth_encoding = auth_encoding
        self.proxies = defaultdict(list)
        self.local_proxy_type = local_proxy_type
        if local_proxy_type == 'http':
            from MFWSpider.utils import LocalProxyService
            service = LocalProxyService()
            for scheme in ['http', 'https']:
                proxies = service.get_proxies(scheme)
                print('Got proxies: %s' % proxies)
                for proxy in proxies:
                    self.proxies[scheme].append(self._get_proxy(proxy, scheme))
        elif local_proxy_type == 'json_file':
            with open(proxy_list_file) as f:
                proxy_list = json.load(f)
                for proxy in proxy_list:
                    scheme = proxy['scheme']
                    url = proxy['proxy']
                    self.proxies[scheme].append(self._get_proxy(url, scheme))

    @classmethod
    def from_crawler(cls, crawler):
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING', 'latin-l')
        proxy_list_file = crawler.settings.get('PROXY_LIST_FILE')
        local_proxy_type = crawler.settings.get('LOCAL_PROXY_SERVICE_TYPE')
        return cls(crawler, auth_encoding, proxy_list_file, local_proxy_type)

    def _set_proxy(self, request, scheme):
        creds, proxy = random.choice(self.proxies[scheme])
        request.meta['proxy'] = proxy
        if creds:
            request.headers['Proxy-Authorization'] = b'Basic' + creds

