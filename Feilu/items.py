# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FeiluItem(scrapy.Item):
    # 定义图片字段
    image_urls = scrapy.Field()  # 图片URL列表
    images = scrapy.Field()      # 下载后的图片信息
    
    # 其他字段
    title = scrapy.Field()
    author = scrapy.Field()
    monthly_clicks = scrapy.Field()
    word_count = scrapy.Field()
    summary = scrapy.Field()
    tags = scrapy.Field()
    book_url = scrapy.Field()
    flowers = scrapy.Field()
    rating = scrapy.Field()  # 评分
    rewards = scrapy.Field()  # 打赏
