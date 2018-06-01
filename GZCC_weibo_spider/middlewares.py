# -*- coding: utf-8 -*-
import scrapy
import urllib.parse as up
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class GzccWeiboSpiderSpiderMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        err_block = "https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url="
        req_url = response.url.replace(err_block, "")
        req_url = up.unquote(req_url)
        yield scrapy.Request(url=req_url, method="GET", callback=self.process_start_requests)

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class GzccWeiboSpiderRetryMiddleware(RetryMiddleware):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        # print(response.body)
        # return response
        try:
            print(response.body.decode("GB2312"))
            return response
        except UnicodeDecodeError:
            print(response.body.decode('UTF-8'))

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
