# -*- coding: utf-8 -*-

BOT_NAME = 'GZCC_weibo_spider'

SPIDER_MODULES = ['GZCC_weibo_spider.spiders']
NEWSPIDER_MODULE = 'GZCC_weibo_spider.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'GZCC_weibo_spider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# dupefilters
# dont_filter = True

# UR长度上限
URLLENGTH_LIMIT = 10000

# 数据库配置
# MongoDB数据库地址
MONGODB_HOST = '127.0.0.1'
# MongoDB数据库端口
MONGODB_PORT = 27017
# MongoDB数据库名称
MONGODB_NAME = 'gzcc_weibo'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 4

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 2

# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# SPIDER_MIDDLEWARES = {
#    'GZCC_weibo_spider.middlewares.GzccWeiboSpiderSpiderMiddleware': 100,
# }

# Enable or disable downloader middlewares
# DOWNLOADER_MIDDLEWARES = {
#    'GZCC_weibo_spider.middlewares.GzccWeiboSpiderRetryMiddleware': 100,
# }

# Enable or disable extensions
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

FILES_STORE = '/'

# Configure item pipelines
ITEM_PIPELINES = {
   # 'scrapy.pipelines.files.FilesPipeline': 1,
   'GZCC_weibo_spider.pipelines.GzccWeiboSpiderPipeline': 300,
   # 'GZCC_weibo_spider.pipelines.GzccWeiboSpiderFilePipeline': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
