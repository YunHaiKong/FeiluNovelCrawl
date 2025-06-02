# Scrapy settings for Feilu project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "Feilu"

SPIDER_MODULES = ["Feilu.spiders"]
NEWSPIDER_MODULE = "Feilu.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "Feilu (+http://www.yourdomain.com)"

# 不遵循robots.txt规则，因为它可能阻止图片下载
ROBOTSTXT_OBEY = False

# 增加重试次数
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 403, 404, 429]

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "Feilu.middlewares.FeiluSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "Feilu.middlewares.FeiluDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# 启用图片下载管道、数据库管道和自定义管道
ITEM_PIPELINES = {
    'Feilu.pipelines.FeiluImagesPipeline': 1,
    'Feilu.pipelines.FeiluPipeline': 300,
    'Feilu.mysql_pipeline.FeiluMySQLPipeline': 400
}

# 设置图片存储路径 - 使用绝对路径
import os
IMAGES_STORE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images')

# 设置用户代理
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# 禁用重定向
REDIRECT_ENABLED = False

# 设置图片下载超时时间
DOWNLOAD_TIMEOUT = 180

# 设置图片缩略图
IMAGES_THUMBS = {
    'small': (50, 50),
    'medium': (100, 100),
}
IMAGES_URLS_FIELD = 'image_urls'

# SQLite数据库设置
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'feilu_books.db')

# MySQL数据库设置
MYSQL_HOST = 'localhost'  # MySQL主机地址
MYSQL_PORT = 3306         # MySQL端口
MYSQL_DATABASE = 'feilu_books'  # 数据库名称
MYSQL_USER = 'root'       # 数据库用户名
MYSQL_PASSWORD = '1234'       # 数据库密码
MYSQL_CHARSET = 'utf8mb4' # 字符集
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
