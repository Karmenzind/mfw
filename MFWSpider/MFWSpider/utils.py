# !/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import requests
import urllib3
import urllib
from MFWSpider import settings


class LocalProxyService:

    def __init__(self):
        service_url = getattr(settings, 'LOCAL_PROXY_SEVICE_HTTP_URL', None)
        if not service_url:
            raise scrapy.exceptions.NotConfigured
        api = '/proxy?anonymity=anonymous&protocol={scheme}&count=1000'

        self.url = urllib.parse.urljoin(service_url, api)

    def get_proxies(self, scheme):
        """ 可供 RandomHttpProxyMiddleware 使用
        """
        url = self.url.format(scheme=scheme)
        resp = requests.get(url)
        return ["%s://%s:%s" % (scheme, ip, port)
                for ip, port
                in resp.json()]


if __name__ == "__main__":
    res = LocalProxyService().get_proxies('http')
    print(res)
