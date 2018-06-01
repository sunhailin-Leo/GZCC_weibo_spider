# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GzccWeiboSpiderItem(scrapy.Item):
    weibo = {}

    def __setitem__(self, key, value):
        self.weibo[key] = value
