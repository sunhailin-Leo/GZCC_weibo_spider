# -*- coding: UTF-8 -*-
"""
Created on 2018年5月20日
@author: Leo
"""
# Python内部库
import json
import time
import logging
import requests
import urllib.parse as up
from bson import ObjectId
from random import choice
from collections import OrderedDict

# lxml
from lxml import etree

# Scrapy库
import scrapy
from scrapy.exceptions import CloseSpider

# 项目内部库
from GZCC_weibo_spider.utils.weibo_login import get_cookies

# 日志系统
logger = logging.getLogger(__name__)

# USERAGENT-LIST
ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
        "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 "
        "Safari/537.36"
]

# COOKIE
COOKIE = "SINAGLOBAL=5692607397083.411.1501177931673; " \
         "UOR=www.cnblogs.com,widget.weibo.com,login.sina.com.cn; " \
         "YF-Page-G0=b98b45d9bba85e843a07e69c0880151a; " \
         "_s_tentry=-; " \
         "Apache=8099932421004.072.1527087759340; " \
         "ULV=1527087759372:6:2:1:8099932421004.072.1527087759340:1525370907506; " \
         "YF-Ugrow-G0={}; " \
         "WBtopGlobal_register_version=18ecda104816e044; " \
         "SCF={}; " \
         "SUB={}; " \
         "SUBP={}; " \
         "SUHB={}; " \
         "ALF={}; " \
         "SSOLoginState={}; " \
         "un={}; " \
         "YF-V5-G0=fec5de0eebb24ef556f426c61e53833b; " \
         "wvr=6"

# Header
HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Cookie": COOKIE,
    "Host": "weibo.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": choice(ua_list),
}

# URL Model
URL_MODEL = "https://weibo.com/p/aj/v6/mblog/mbloglist?" \
            "ajwvr=6&" \
            "domain=100206&" \
            "refer_flag=1001030201_&" \
            "pids=Pl_Official_MyProfileFeed__28&" \
            "profile_ftype=1&" \
            "is_all=1&" \
            "pagebar={}&" \
            "pl_name=Pl_Official_MyProfileFeed__28&" \
            "id=1002063381027042&" \
            "script_uri={}&" \
            "feed_type=0&" \
            "page={}&" \
            "pre_page={}&" \
            "domain_op=100206&" \
            "__rnd={}"

# 获取微博链接(用户主页)
URL_MODEL_1 = "https://weibo.com{}?refer_flag=1001030201_&pids=Pl_Official_MyProfileFeed__28&profile_ftype=1&is_all=1"

# 获取全文
URL_MODEL_2 = \
    "https://weibo.com/p/aj/mblog/getlongtext?ajwvr=6&mid={}&is_settop&is_sethot&is_setfanstop&is_setyoudao&__rnd={}"


class GzccWeiboSpider(scrapy.Spider):
    name = "Gzcc_weibo"

    def __init__(self, **kwargs):
        # 总页数
        self.max_page = 0

        # URL参数 (第五页有问题)
        self.start_page = 1
        self.pre_page = 1
        self.start_page_bar = 0

        # weibo user ID
        self.user_id = "/gzsxy13667"

        # cookies
        self.start_user = ""
        self.user_list = []
        self.start_cookies = ""
        self.cookies_list = []
        super().__init__(**kwargs)

    def get_cookie(self):
        """
        获取cookie
        :return:
        """
        # 获取所有cookies
        self.cookies_list, self.user_list = get_cookies(is_username=True)
        logger.info("Cookie池的大小为: {}".format(len(self.cookies_list)))
        # 取出用户名和cookie
        self.start_cookies = self.cookies_list[0]
        self.start_user = self.user_list[0]
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

        # 微博链接
        req_url = URL_MODEL.format(self.start_page_bar,
                                   self.user_id,
                                   self.start_page,
                                   self.pre_page,
                                   int(time.time() * 1000))
        self.start_cookies = dict(self.start_cookies)
        HEADER['Cookie'] = COOKIE.format(self.start_cookies['YF-Ugrow-G0'],
                                         self.start_cookies['SCF'],
                                         self.start_cookies['SUB'],
                                         self.start_cookies['SUBP'],
                                         self.start_cookies['SUHB'],
                                         self.start_cookies['ALF'],
                                         int(time.time()),
                                         self.start_user)
        logger.debug(HEADER)
        logger.debug(req_url)
        yield scrapy.Request(url=req_url,
                             callback=self.parse,
                             method="GET",
                             headers=HEADER,
                             cookies=self.start_cookies,
                             dont_filter=True)

    def parse(self, response):
        try:
            # 加载数据
            json_result = json.loads(response.body.decode('UTF-8'))
            # HTML代码
            weibo_html_code = json_result['data']
            # 转换成etree对象
            selector = etree.HTML(weibo_html_code)
            # 获取微博列表
            weibo_list = selector.xpath('//div[@action-type="feed_list_item"]')
            # 存储对象
            each_weibo = OrderedDict()
            # 获取每个微博信息
            for weibo in weibo_list:
                # 每个微博块的父选择器路径
                xpath_for_weibo_detail = 'div[@class="WB_feed_detail clearfix"]/div[@class="WB_detail"]'
                # 数据ID
                each_weibo["_id"] = ObjectId()
                # 微博ID
                weibo_id = weibo.xpath('@mid')[0]
                each_weibo['weibo_id'] = weibo_id
                # 发布时间
                weibo_publish_date = \
                    weibo.xpath('{}/div[@class="WB_from S_txt2"]/a/@title'.format(xpath_for_weibo_detail))
                split_date = weibo_publish_date[0].split(" ")
                # 年月日
                weibo_publish_ymd = split_date[0]
                each_weibo['weibo_ymd'] = weibo_publish_ymd
                # 时分秒
                weibo_publish_hm = split_date[1]
                each_weibo['weibo_hm'] = weibo_publish_hm
                # 发布客户端
                weibo_platform = \
                    weibo.xpath('{}/div[@class="WB_from S_txt2"]/a[2]/text()'.format(xpath_for_weibo_detail))
                weibo_platform = weibo_platform[0]
                each_weibo['weibo_platform'] = weibo_platform
                # 获取转发数
                weibo_forwarding_num = weibo.xpath('string(div[2]/div[1]/ul/li[2]/a[1]/span/span/span/em[2])')
                if weibo_forwarding_num == "转发":
                    each_weibo['weibo_forwarding_num'] = 0
                else:
                    each_weibo['weibo_forwarding_num'] = int(weibo_forwarding_num)
                # 获取评论数
                weibo_comment_num = weibo.xpath('string(div[2]/div[1]/ul/li[3]/a[1]/span/span/span/em[2])')
                if weibo_comment_num == "评论":
                    each_weibo['weibo_comment_num'] = 0
                else:
                    each_weibo['weibo_comment_num'] = int(weibo_comment_num)
                # 获取点赞数
                weibo_like_num = weibo.xpath('string(div[2]/div[1]/ul/li[4]/a[1]/span/span/span/em[2])')
                if weibo_like_num == "赞":
                    each_weibo['weibo_like_num'] = 0
                else:
                    each_weibo['weibo_like_num'] = int(weibo_like_num)
                # 是否为转发微博
                is_forwarding = weibo.xpath('{}/div[@class="WB_feed_expand"]'.format(xpath_for_weibo_detail))
                if len(is_forwarding) == 0:
                    # 是否为图文微博
                    is_pictureText_weibo = \
                        weibo.xpath('{}/div[@class="WB_media_wrap clearfix"]'.format(xpath_for_weibo_detail))
                    if len(is_pictureText_weibo) > 0:
                        yield self.parse_picture_text_weibo(item=each_weibo,
                                                            s_selector=weibo,
                                                            f_selector=xpath_for_weibo_detail)
                    else:
                        # 纯文字微博
                        text_weibo = \
                            weibo.xpath('string({}/div[@class="WB_text W_f14"]'.format(xpath_for_weibo_detail) + ')')
                        text_weibo = text_weibo.strip()
                        if "展开全文" in text_weibo:
                            get_longtext_url = URL_MODEL_2.format(each_weibo['weibo_id'], str(int(time.time() * 1000)))
                            data = requests.get(get_longtext_url, headers=HEADER, cookies=self.start_cookies).json()
                            each_weibo['weibo_content'] = data['data']['html'].strip()
                            each_weibo['weibo_media'] = ""
                        else:
                            each_weibo['weibo_content'] = text_weibo
                            each_weibo['weibo_media'] = ""
                        yield each_weibo
                else:
                    continue
            # 判断退出
            if self.max_page == self.start_page:
                raise CloseSpider("爬取结束")
            else:
                if "pagebar=0" in response.url:
                    # 微博链接
                    req_url = URL_MODEL.format(self.start_page_bar + 1,
                                               self.user_id,
                                               self.start_page,
                                               self.pre_page,
                                               int(time.time() * 1000))
                    yield scrapy.Request(url=req_url,
                                         callback=self.parse,
                                         method="GET",
                                         headers=HEADER,
                                         cookies=self.start_cookies,
                                         dont_filter=True)
                else:
                    if self.max_page == 0:
                        # 最开始不知道上限页码有多少的时候执行的方法
                        max_page = selector.xpath('string(//div[@action-type="feed_list_page_morelist"]/ul/li[1])')
                        max_page = max_page.strip().replace("第", "").replace("页", "").strip()
                        self.max_page = max_page
                        logger.debug(
                            "总共有 {} 页".format(self.max_page) + " --- " + "当前第 {} 页".format(self.start_page)
                        )
                        # 下一页
                        self.start_page += 1
                        self.pre_page += 1
                        req_url = URL_MODEL.format(self.start_page_bar,
                                                   self.user_id,
                                                   self.start_page,
                                                   self.pre_page,
                                                   int(time.time() * 1000))
                        yield scrapy.Request(url=req_url,
                                             callback=self.parse,
                                             method="GET",
                                             headers=HEADER,
                                             cookies=self.start_cookies,
                                             dont_filter=True)
                    else:
                        logger.debug(
                            "总共有 {} 页".format(self.max_page) + " --- " + "当前第 {} 页".format(self.start_page)
                        )
                        # 下一页
                        self.start_page += 1
                        self.pre_page += 1
                        req_url = URL_MODEL.format(self.start_page_bar,
                                                   self.user_id,
                                                   self.start_page,
                                                   self.pre_page,
                                                   int(time.time() * 1000))
                        yield scrapy.Request(url=req_url,
                                             callback=self.parse,
                                             method="GET",
                                             headers=HEADER,
                                             cookies=self.start_cookies,
                                             dont_filter=True)
        except Exception as err:
            logger.debug(err)
            print(err.with_traceback(err))
            raise CloseSpider("有错误, 退出爬虫!")

    def parse_picture_text_weibo(self, item, s_selector, f_selector):
        """
        解析图文微博
        :param item: 数据类目
        :param s_selector: 子选择器
        :param f_selector: 父选择器
        :return: 无返回
        """
        # 获取文字
        text = s_selector.xpath('string({}/div[@class="WB_text W_f14"]'.format(f_selector) + ')')
        text = text.strip()
        if "展开全文" in text:
            get_longtext_url = URL_MODEL_2.format(item['weibo_id'], str(int(time.time() * 1000)))
            data = requests.get(get_longtext_url, headers=HEADER, cookies=self.start_cookies).json()
            item['weibo_content'] = data['data']['html'].strip()
        else:
            item['weibo_content'] = text
        # 获取多媒体
        media_class = s_selector.xpath('{}/div[@class="WB_media_wrap clearfix"]/div/ul/li/@class'.format(f_selector))
        if "WB_pic" in str(media_class):
            images = s_selector.xpath('{}/div[@class="WB_media_wrap clearfix"]/div/ul/li'.format(f_selector))
            try:
                # 普通图片
                item['weibo_media'] = ["https:" + img.xpath('img/@src')[0] for img in images]
            except IndexError:
                try:
                    # 动图
                    item['weibo_media'] = ["https:" + img.xpath('div/img/@src')[0] for img in images]
                except IndexError:
                    # 这里保存的问题主要在于图片和动图素材混杂的时候
                    # 一个li下是img标签一个则是div
                    print(images)
                    logger.error("存在媒体对象混杂现象! 待解决...")
        elif "WB_video" in str(media_class):
            video = \
                s_selector.xpath(
                    '{}/div[@class="WB_media_wrap clearfix"]/div/ul/li/@video-sources'.format(f_selector)
                )
            video = up.unquote(up.unquote(video[0].split("=")[-1]))
            item['weibo_media'] = "https:" + video
        return item
