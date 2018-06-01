# -*- coding: UTF-8 -*-
"""
Created on 2018年5月20日
@author: Leo
"""
# 系统库
import re
import json
import logging
import urllib.parse as up
from bson import ObjectId
from random import choice
from collections import OrderedDict

# 第三方库
from lxml import etree

# Scrapy库
import scrapy
from scrapy.exceptions import CloseSpider

# 项目内部库
from GZCC_weibo_spider.utils.weibo_login import get_cookies

# 日志系统
logger = logging.getLogger(__name__)

# URL链接
URL = "http://s.weibo.com/user/{}&page={}"

# COOKIE
COOKIE = "SINAGLOBAL=4253625129250.6855.1499336887209; " \
         "UM_distinctid=1607cec7801168-0ce82b60672541-2631506b-2a3000-1607cec78034b9; _s_tentry=-; " \
         "Apache=5245967709285.157.1526627161172; " \
         "ULV=1526627161207:33:3:1:5245967709285.157.1526627161172:1525434261008; " \
         "login_sid_t=13464c6ec83689d64ccec25281c40229; cross_origin_proto=SSL; SWBSSL=usrmdinst_18; " \
         "SSOLoginState=1526663237; wvr=6; UOR=,,ent.ifeng.com; SWB=usrmdinst_5; " \
         "SCF=AlfvGBX_U8E9QHBxFVQfDGbeBLLJiqy6tDjm0rLd9O0YqXQfU4PPMcAxrDcG_vr4m_nF8ZITaWPxUWjgKNVN384.; " \
         "SUB=_2A252Bm7sDeRhGedH6FIY8S3FzzuIHXVVcsckrDV8PUNbmtBeLVXZkW9NUNHC1RD_ZUTiaJyhnsqEyw8mYbclc9-x; " \
         "SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5iUj0WJid4mwqVGV.8z6qq5JpX5KMhUgL.Fo24e054eKe4ShM2dJLoI7_" \
         "-IgfLTH9aMrxLw5tt; SUHB=0btN2Tt2eH4-gp; ALF=1558401594; WBStorage=5548c0baa42e6f3d|undefined "

# USERAGENT-LIST
ua_list = [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.0.2564.82 "
        "Chrome/48.0.2564.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
        "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 "
        "Safari/537.36"
]

# Header
HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": COOKIE,
    "Host": "s.weibo.com",
    "Referer": "",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": choice(ua_list)
}

# 拼接微博用户首页显示全部的URL段
ALL_WEIBO_URL = "&pids=Pl_Official_MyProfileFeed__28&profile_ftype=1&is_all=1#_0"


class GzccWeiboUserSpider(scrapy.Spider):
    name = "Gzcc_weibo_user"

    def __init__(self, **kwargs):
        # 当前页数
        self.current_page = 1

        # 启动url
        self.start_urls = [URL.format(up.quote(up.quote("广州商学院")), self.current_page)]

        # cookies
        self.start_cookies = ""
        self.cookies_list = []
        super().__init__(**kwargs)

    def get_cookie(self):
        """
        获取cookie
        :return:
        """
        # 获取所有cookies
        self.cookies_list = get_cookies()
        logger.info("Cookie池的大小为: {}".format(len(self.cookies_list)))
        # 随机一个cookies
        self.start_cookies = choice(self.cookies_list)
        logger.info("取出一个cookie, cookie池剩余大小为: {}".format(len(self.cookies_list) - 1))
        logger.info("cookie: {}".format(self.start_cookies))
        # 将cookies列表中获取到的cookies移除
        self.cookies_list.pop(self.cookies_list.index(self.start_cookies))
        logger.info("Cookie池的大小为: {}".format(len(self.cookies_list)))
        # 将随机提取出来的cookies转换为json格式
        self.start_cookies = json.loads(self.start_cookies)

    def get_rest_cookie(self):
        """
        获取剩余的cookie
        :return:
        """
        logger.info("Cookie池的大小为: {}".format(len(self.cookies_list)))
        if len(self.cookies_list) > 0:
            cookie = self.cookies_list[-1]
            logger.info("cookie: {}".format(cookie))
            self.cookies_list.pop(self.cookies_list.index(cookie))
            logger.info("Cookie池的大小为: {}".format(len(self.cookies_list)))
            return json.loads(cookie)
        else:
            return None

    def start_requests(self):
        # 获取cookies
        self.get_cookie()

        # 开始请求
        req_url = self.start_urls[0]
        HEADER['Referer'] = req_url
        yield scrapy.Request(url=req_url,
                             method="GET",
                             headers=HEADER,
                             meta={"cp": self.current_page},
                             cookies=self.start_cookies)

    def parse(self, response):
        # 当前页数
        cp = response.meta['cp']
        if int(cp) != 51:
            logger.info("当前页数: 第{}页".format(cp))

            # 存储对象
            weibo_user = OrderedDict()

            # Response的selector对象,解析出网页源代码
            selector = response.selector.xpath('//script/text()').extract()
            try:
                result = [s for s in selector if '"pl_user_feedList"' in s][0]
                result = result.replace("STK && STK.pageletM && STK.pageletM.view(", "").replace("})", "}")
                # 获取微博底部script标签中的HTML代码, 再使用lxml进行解析
                html_code = json.loads(result)['html']
                user_lists = etree.HTML(html_code).xpath('//div[@class="pl_personlist"]/div')
                for user in user_lists:
                    # ID
                    weibo_user['_id'] = ObjectId()
                    # 用户标签(存在多个label)
                    user_label_list = user.xpath('div[@class="person_detail"]/p[@class="person_label"]')
                    label_list = []
                    if len(user_label_list) >= 1:
                        for label in user_label_list:
                            user_label = label.xpath('string(.)')
                            # user_label = re.sub('\s', '', user_label.strip())
                            user_label = user_label.replace("\n", "").replace("\t", "")
                            label_list.append(user_label)
                    else:
                        label_list = []
                    weibo_user['label'] = label_list
                    # 用户名和用户标签
                    username = user.xpath('div[@class="person_detail"]/p[@class="person_name"]/a[1]/@title')[0]
                    # 判断用户是否含有广州商学院(不含有说明不一定属于广州商学院的)
                    if "广州商学院" not in username:
                        # 判断用户的标签系统中是否有广州商学院(含有即为普通用户),不含有则跳过
                        # print(label_list)
                        if "广州商学院" in "".join(label_list):
                            weibo_user['remark'] = "普通用户"
                        else:
                            continue
                    # 是否有大V标志
                    is_auth = user.xpath('div[@class="person_detail"]/p[@class="person_name"]/a[2]')
                    if len(is_auth) != 0:
                        try:
                            weibo_user['remark'] = is_auth[0].xpath('@title')[0]
                        except IndexError:
                            weibo_user['remark'] = is_auth[0].xpath('i/@title')[0]
                    else:
                        weibo_user['remark'] = "普通用户"
                    weibo_user['username'] = username
                    # 用户主页链接
                    user_href = user.xpath('div[@class="person_pic"]/a/@href')[0]
                    user_href = "https:{}{}".format(user_href, ALL_WEIBO_URL)
                    weibo_user['user_href'] = user_href
                    # 用户头像
                    user_img_href = user.xpath('div[@class="person_pic"]/a/img/@src')[0]
                    user_img_href = "https:{}".format(user_img_href)
                    weibo_user['user_img_href'] = user_img_href
                    # 用户性别
                    user_sex = user.xpath('div[@class="person_detail"]/p[@class="person_addr"]/span[1]/@title')[0]
                    weibo_user['sex'] = user_sex
                    # 用户位置
                    user_location = user.xpath('div[@class="person_detail"]/p[@class="person_addr"]/span[2]/text()')[0]
                    user_location = user_location.replace("，", ",")
                    weibo_user['location'] = user_location
                    # 用户主页
                    user_page_href = user.xpath('div[@class="person_detail"]/p[@class="person_addr"]/a/@href')[0]
                    user_page_href = "https:{}".format(user_page_href)
                    weibo_user['user_page_href'] = user_page_href
                    # 用户卡片信息
                    user_card_info = user.xpath('string(div[@class="person_detail"]/p[@class="person_card"])').strip()
                    weibo_user['user_card_info'] = user_card_info
                    # 用户关注人数
                    user_focus_num = \
                        user.xpath('div[@class="person_detail"]/p[@class="person_num"]/span[1]/a/text()')[0]
                    weibo_user['user_focus_num'] = user_focus_num
                    # 用户粉丝数
                    user_funs_num = \
                        user.xpath('div[@class="person_detail"]/p[@class="person_num"]/span[2]/a/text()')[0]
                    weibo_user['user_funs_num'] = user_funs_num
                    # 用户微博数
                    user_publish_num = \
                        user.xpath('div[@class="person_detail"]/p[@class="person_num"]/span[3]/a/text()')[0]
                    weibo_user['user_publish_num'] = user_publish_num
                    # 用户简介
                    user_info = user.xpath('string(div[@class="person_detail"]/div[@class="person_info"]/p)')
                    user_info = re.sub('\s', '', user_info.strip())
                    weibo_user['user_info'] = user_info
                    logger.info(weibo_user)
                    yield weibo_user
                logger.debug("当前cookie为: {}".format(self.start_cookies))
                yield scrapy.Request(url=URL.format(up.quote(up.quote("广州商学院")), cp + 1),
                                     method="GET",
                                     headers=HEADER,
                                     meta={"cp": cp + 1},
                                     callback=self.parse,
                                     cookies=self.start_cookies,
                                     dont_filter=True)
            except IndexError as err:
                logger.error("Error Info: {}".format(err))
                # result = [s for s in selector if '"pl_common_sassfilter"' in s][0]
                # result = result.replace("STK && STK.pageletM && STK.pageletM.view(", "").replace("})", "}")
                # logger.info(result)
                # 再次获取cookie
                cookie = self.get_rest_cookie()
                if cookie is not None:
                    self.start_cookies = cookie
                    HEADER['Cookie'] = cookie
                    yield scrapy.Request(url=URL.format(up.quote(up.quote("广州商学院")), cp),
                                         method="GET",
                                         headers=HEADER,
                                         meta={"cp": cp},
                                         callback=self.parse,
                                         cookies=cookie,
                                         dont_filter=True)
                else:
                    raise CloseSpider("Cookie池已用完!退出爬虫!...")
        else:
            raise CloseSpider("爬虫页数达到上限!退出爬虫!..")
