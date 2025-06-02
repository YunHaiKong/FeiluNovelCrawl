# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
from urllib.parse import urlparse
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from itemadapter import ItemAdapter


class FeiluImagesPipeline(ImagesPipeline):
    @classmethod
    def from_settings(cls, settings):
        # 获取图片存储路径
        store_uri = settings['IMAGES_STORE']
        
        # 检查并创建图片存储目录
        if not os.path.exists(store_uri):
            os.makedirs(store_uri, exist_ok=True)
            print(f"创建图片存储目录: {store_uri}")
        else:
            print(f"图片存储目录已存在: {store_uri}")
            
        # 创建full子目录
        full_path = os.path.join(store_uri, 'full')
        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)
            print(f"创建full子目录: {full_path}")
            
        # 创建thumbs子目录（如果启用了缩略图）
        if settings.get('IMAGES_THUMBS'):
            for thumb_name in settings.get('IMAGES_THUMBS', {}):
                thumb_path = os.path.join(store_uri, 'thumbs', thumb_name)
                if not os.path.exists(thumb_path):
                    os.makedirs(thumb_path, exist_ok=True)
                    print(f"创建缩略图目录: {thumb_path}")
        
        return super(FeiluImagesPipeline, cls).from_settings(settings)
        
    def get_media_requests(self, item, info):
        # 从item中获取图片URL并生成请求
        adapter = ItemAdapter(item)
        image_urls = adapter.get('image_urls', [])
        
        # 记录图片URL信息
        title = adapter.get('title', '未知标题')
        info.spider.logger.info(f"处理item: {title}的图片，URL数量: {len(image_urls)}")
        
        if not image_urls:
            info.spider.logger.warning(f"图片URL为空: {title}")
            return
            
        for image_url in image_urls:
            if not image_url:
                info.spider.logger.warning(f"跳过空URL: {title}")
                continue
                
            try:
                # 确保URL格式正确
                if not image_url.startswith(('http://', 'https://')):
                    image_url = 'https:' + image_url if image_url.startswith('//') else 'https://' + image_url
                
                info.spider.logger.info(f"请求图片: {image_url}")
                # 添加请求头，模拟浏览器行为
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Referer': 'https://b.faloo.com/'
                }
                yield scrapy.Request(
                    url=image_url, 
                    headers=headers, 
                    meta={'title': title, 'book_url': adapter.get('book_url', '')},
                    errback=self.handle_error,
                    dont_filter=True  # 避免URL重复过滤
                )
            except Exception as e:
                info.spider.logger.error(f"生成请求时出错: {title}, URL: {image_url}, 错误: {str(e)}")
                continue
    
    def file_path(self, request, response=None, info=None, *, item=None):
        # 自定义文件保存路径
        url = request.url
        title = request.meta.get('title', '未知标题')
        
        # 解析URL获取路径
        path = urlparse(url).path
        # 获取文件名
        filename = os.path.basename(path)
        
        # 提取文件扩展名
        ext = os.path.splitext(filename)[1]
        if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = '.jpg'  # 默认使用jpg扩展名
        
        # 如果文件名为空或没有扩展名，使用标题和URL哈希值生成文件名
        if not filename or '.' not in filename:
            # 清理标题，移除不适合作为文件名的字符
            safe_title = ''.join(c for c in title if c.isalnum() or c in '._- ')
            safe_title = safe_title.strip().replace(' ', '_')[:50]  # 限制长度
            if not safe_title:
                safe_title = 'image'
            filename = f'{safe_title}_{hash(url) % 10000:04d}{ext}'
        
        # 记录文件路径信息
        info.spider.logger.info(f"保存图片: {title}, 文件名: {filename}")
        return f'full/{filename}'
    
    def handle_error(self, failure):
        # 处理请求错误
        request = failure.request
        title = request.meta.get('title', '未知标题')
        book_url = request.meta.get('book_url', '')
        error_type = type(failure.value).__name__
        error_msg = str(failure.value)
        
        # 详细记录错误信息
        self.logger.error(f"图片下载失败: {title}, URL: {request.url}")
        self.logger.error(f"错误类型: {error_type}, 错误信息: {error_msg}")
        self.logger.error(f"相关书籍URL: {book_url}")
        
        # 根据错误类型提供更具体的处理
        if 'TimeoutError' in error_type:
            self.logger.error(f"下载超时，可能需要增加DOWNLOAD_TIMEOUT设置")
        elif 'DNSLookupError' in error_type:
            self.logger.error(f"DNS查找失败，请检查网络连接")
        elif 'ConnectionRefusedError' in error_type:
            self.logger.error(f"连接被拒绝，可能需要使用代理")
        elif 'HttpError' in error_type:
            status = getattr(failure.value, 'status', None)
            self.logger.error(f"HTTP错误状态码: {status}")
            
        # 可以在这里添加重试逻辑或其他恢复策略
    
    def item_completed(self, results, item, info):
        # 处理下载完成后的item
        title = item.get('title', '未知标题')
        
        # 统计成功和失败的下载
        success_count = 0
        failed_count = 0
        image_paths = []
        failed_urls = []
        
        for ok, x in results:
            if ok:
                success_count += 1
                image_paths.append(x['path'])
                info.spider.logger.info(f"图片下载成功: {title}, 路径: {x['path']}")
            else:
                failed_count += 1
                failed_urls.append(x.get('url', '未知URL'))
                info.spider.logger.warning(f"图片下载失败: {title}, URL: {x.get('url', '未知URL')}")
        
        # 记录总体下载结果
        if image_paths:
            info.spider.logger.info(f"图片下载完成: {title}, 成功: {success_count}, 失败: {failed_count}")
        else:
            # 如果没有成功下载的图片，记录详细日志
            info.spider.logger.warning(f"所有图片下载失败: {title}, 原始URL: {item.get('image_urls', [])}")
            info.spider.logger.warning(f"失败URL列表: {failed_urls}")
        
        # 将下载结果保存到item中
        item['images'] = image_paths
        return item


class FeiluPipeline:
    def __init__(self):
        self.success_count = 0
        self.failed_count = 0
        self.total_count = 0
        
    def process_item(self, item, spider):
        # 检查图片下载结果
        image_urls = item.get('image_urls', [])
        images = item.get('images', [])
        title = item.get('title', '未知标题')
        
        # 更新统计信息
        self.total_count += len(image_urls) if image_urls else 0
        self.success_count += len(images) if images else 0
        self.failed_count = self.total_count - self.success_count
        
        # 记录详细信息
        if image_urls and not images:
            spider.logger.warning(f"管道确认: {title} 的所有图片下载失败")
        elif images:
            spider.logger.info(f"管道确认: {title} 的图片下载成功，数量: {len(images)}")
        
        return item
    
    def close_spider(self, spider):
        # 爬虫关闭时输出统计信息
        spider.logger.info("========== 图片下载统计 ==========")
        spider.logger.info(f"总图片数: {self.total_count}")
        spider.logger.info(f"成功下载: {self.success_count}")
        spider.logger.info(f"下载失败: {self.failed_count}")
        if self.total_count > 0:
            success_rate = (self.success_count / self.total_count) * 100
            spider.logger.info(f"成功率: {success_rate:.2f}%")
        spider.logger.info("=================================")



