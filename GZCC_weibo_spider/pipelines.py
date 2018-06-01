# -*- coding: utf-8 -*-

# Python内置库
import logging

# 第三方库
from pymongo import MongoClient
from scrapy.conf import settings

# 日志系统
logger = logging.getLogger(__name__)


class GzccWeiboSpiderPipeline(object):

    def __init__(self):
        _conn = MongoClient(host=settings['MONGODB_HOST'],
                            port=settings['MONGODB_PORT'])

        # 创建MongoDB数据库名称(数据源)
        self.db = _conn[settings['MONGODB_NAME']]

    def process_item(self, item, spider):
        if spider.name == "Gzcc_weibo_user":
            self.process_user(data=item)
        elif spider.name == "Gzcc_weibo":
            self.process_weibo(data=item)
        return item

    def process_user(self, data):
        # 集合对象
        col = self.db["weibo_user"]
        try:
            col.insert(data)
        except Exception as err:
            logger.error(err)

    def process_weibo(self, data):
        # 集合对象
        col = self.db["weibo_item"]
        try:
            col.insert(data)
        except Exception as err:
            logger.error(err)
