import scrapy
from Feilu.items import FeiluItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["b.faloo.com",'img.faloo.com']
    start_urls = ["https://b.faloo.com/y_0_0_0_0_0_2_1.html"]
    
    # 添加自定义设置
    custom_settings = {
        'DOWNLOAD_DELAY': 10,  # 下载延迟，避免请求过快
        'COOKIES_ENABLED': True,  # 禁用cookies
    }
    
    # 添加命令行参数
    def __init__(self, max_pages=10, *args, **kwargs):
        super(BooksSpider, self).__init__(*args, **kwargs)
        self.max_pages = int(max_pages)  # 最大爬取页数，默认为5页
        self.current_page = 1  # 当前页码

    def parse(self, response):
        # 获取所有小说内容区域（两列布局）
        book_divs = response.xpath('//*[@id="BookContent"]/div')
        
        for div in book_divs:
            # 每个div下有两列小说
            book_columns = div.xpath('./div')
            
            for column in book_columns:
                item = FeiluItem()
                
                # 提取书名
                item['title'] = column.xpath('./div[2]/div[1]/div[1]/h1/a/text()').get()
                
                # 提取作者
                item['author'] = column.xpath('./div[2]/div[1]/div[2]/span/a/text()').get()
                
                # 提取月点击量
                item['monthly_clicks'] = column.xpath('./div[2]/div[2]/span/span[2]/text()').get()
                
                # 提取字数
                item['word_count'] = column.xpath('./div[2]/div[2]/span/span[4]/text()').get()
                
                # 提取图片链接
                img_url = column.xpath('./div[1]/a/img/@src').get()
                # 确保图片URL格式正确
                if img_url:
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = 'https:' + img_url if img_url.startswith('//') else 'https://' + img_url
                    self.logger.info(f"提取到图片URL: {img_url}")
                item['image_urls'] = [img_url] if img_url else []
                
                # 提取书籍详情链接
                book_url = column.xpath('./div[2]/div[1]/div[1]/h1/a/@href').get()
                if book_url and not book_url.startswith('http'):
                    book_url = 'https:' + book_url
                item['book_url'] = book_url
                
                # 请求详情页获取更多信息
                if book_url:
                    yield scrapy.Request(
                        url=item['book_url'],
                        callback=self.parse_detail,
                        meta={'item': item}
                    )
                else:
                    yield item
        
        # 处理翻页 - 通过修改URL参数实现，并限制爬取页数
        current_page = response.url.split('_')[-1].split('.')[0]
        try:
            next_page = int(current_page) + 1
            # 检查是否达到最大页数限制
            if next_page <= self.max_pages:
                self.logger.info(f"爬取下一页: {next_page}/{self.max_pages}")
                next_url = response.url.replace(f'_{current_page}.html', f'_{next_page}.html')
                yield scrapy.Request(next_url, callback=self.parse)
            else:
                self.logger.info(f"已达到最大页数限制: {self.max_pages}，停止爬取")
        except ValueError:
            self.logger.error(f"无法解析页码: {current_page}")
    
    def parse_detail(self, response):
        item = response.meta['item']
        
        # 提取摘要 - 修正XPath选择器，获取所有摘要文本
        summary_div = response.xpath('//div[@class="T-L-T-C-Box1"]')

        summary_texts = summary_div.xpath('.//p/text()').getall()
        item['summary'] = '\n'.join([text.strip() for text in summary_texts if text.strip()])
   
     
        # 提取标签
        tags_div = response.xpath('/html/body/div[3]/div[2]/div[5]/div[1]/div[2]/div[4]')
        tags = tags_div.xpath('./a[@class="LXbq"]/text()').getall()
        item['tags'] = tags if tags else []
        
        # 提取鲜花数
        flowers = response.xpath('/html/body/div[3]/div[3]/div[1]/div[3]/text()').get()
        if flowers:
            item['flowers'] = flowers.strip()
        
        # 提取评分
        rating = response.xpath('/html/body/div[3]/div[3]/div[10]/div[1]/span[1]/text()').get()
        if rating:
            item['rating'] = rating.strip()
        
        # 提取打赏
        rewards = response.xpath('/html/body/div[3]/div[3]/div[5]/div[3]/text()').get()
        if rewards:
            item['rewards'] = rewards.strip()
        
        yield item
