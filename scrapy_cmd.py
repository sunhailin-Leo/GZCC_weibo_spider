# -*-coding:utf-8 -*-
# 通过调用命令行进行调试
# 调用execute这个函数可调用scrapy脚本
from scrapy.cmdline import execute

import os
import sys
# 设置工程路径，在cmd 命令更改路径而执行scrapy命令调试
# 获取main文件的父目录，os.path.abspath(__file__) 为__file__文件目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "Gzcc_weibo_user"])
execute(["scrapy", "crawl", "Gzcc_weibo"])
