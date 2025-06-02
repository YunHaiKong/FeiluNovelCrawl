import pymysql
import os
from itemadapter import ItemAdapter

class FeiluMySQLPipeline:
    """
    将爬取的小说数据保存到MySQL数据库中
    """
    def __init__(self, mysql_host, mysql_port, mysql_db, mysql_user, mysql_password, mysql_charset):
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_db = mysql_db
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_charset = mysql_charset
        self.conn = None
        self.cursor = None
        self.success_count = 0
        self.failed_count = 0
        
    @classmethod
    def from_crawler(cls, crawler):
        # 从设置中获取MySQL连接参数
        return cls(
            mysql_host=crawler.settings.get('MYSQL_HOST', 'localhost'),
            mysql_port=crawler.settings.get('MYSQL_PORT', 3306),
            mysql_db=crawler.settings.get('MYSQL_DATABASE', 'feilu_books'),
            mysql_user=crawler.settings.get('MYSQL_USER', 'root'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD', ''),
            mysql_charset=crawler.settings.get('MYSQL_CHARSET', 'utf8mb4')
        )
    
    def open_spider(self, spider):
        # 爬虫启动时连接数据库
        try:
            self.conn = pymysql.connect(
                host=self.mysql_host,
                port=self.mysql_port,
                user=self.mysql_user,
                password=self.mysql_password,
                charset=self.mysql_charset
            )
            self.cursor = self.conn.cursor()
            
            # 创建数据库（如果不存在）
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.mysql_db}` CHARACTER SET {self.mysql_charset}")
            self.cursor.execute(f"USE `{self.mysql_db}`")
            
            spider.logger.info(f"MySQL数据库连接成功: {self.mysql_host}:{self.mysql_port}/{self.mysql_db}")
            
            # 创建表结构
            self.create_tables()
            spider.logger.info("MySQL数据库表结构初始化完成")
        except Exception as e:
            spider.logger.error(f"MySQL数据库连接失败: {str(e)}")
            raise e
    
    def create_tables(self):
        # 创建小说信息表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS `books` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `title` VARCHAR(255) NOT NULL,
            `author` VARCHAR(100),
            `monthly_clicks` VARCHAR(50),
            `word_count` VARCHAR(50),
            `summary` TEXT,
            `book_url` VARCHAR(255) UNIQUE,
            `flowers` VARCHAR(50),
            `rating` VARCHAR(20),
            `rewards` VARCHAR(50),
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建标签表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS `tags` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(50) UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建小说-标签关联表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS `book_tags` (
            `book_id` INT,
            `tag_id` INT,
            PRIMARY KEY (`book_id`, `tag_id`),
            FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE,
            FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建图片表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS `images` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `book_id` INT,
            `image_url` VARCHAR(255),
            `image_path` VARCHAR(255),
            FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        self.conn.commit()
    
    def process_item(self, item, spider):
        try:
            adapter = ItemAdapter(item)
            
            # 开始事务
            self.conn.begin()
            
            # 1. 插入小说基本信息
            self.cursor.execute('''
            INSERT INTO `books` 
            (`title`, `author`, `monthly_clicks`, `word_count`, `summary`, `book_url`, `flowers`, `rating`, `rewards`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            `title`=%s, `author`=%s, `monthly_clicks`=%s, `word_count`=%s, `summary`=%s,
            `flowers`=%s, `rating`=%s, `rewards`=%s
            ''', (
                adapter.get('title', ''),
                adapter.get('author', ''),
                adapter.get('monthly_clicks', ''),
                adapter.get('word_count', ''),
                adapter.get('summary', ''),
                adapter.get('book_url', ''),
                adapter.get('flowers', ''),
                adapter.get('rating', ''),
                adapter.get('rewards', ''),
                # 用于ON DUPLICATE KEY UPDATE的值
                adapter.get('title', ''),
                adapter.get('author', ''),
                adapter.get('monthly_clicks', ''),
                adapter.get('word_count', ''),
                adapter.get('summary', ''),
                adapter.get('flowers', ''),
                adapter.get('rating', ''),
                adapter.get('rewards', '')
            ))
            
            # 获取插入的书籍ID
            if self.cursor.rowcount > 0:
                book_id = self.cursor.lastrowid
            else:
                # 如果书籍已存在，获取其ID
                self.cursor.execute('SELECT `id` FROM `books` WHERE `book_url` = %s', (adapter.get('book_url', ''),))
                book_id = self.cursor.fetchone()[0]
            
            # 2. 处理标签
            tags = adapter.get('tags', [])
            if tags:
                for tag in tags:
                    # 插入标签（如果不存在）
                    self.cursor.execute('INSERT IGNORE INTO `tags` (`name`) VALUES (%s)', (tag,))
                    
                    # 获取标签ID
                    self.cursor.execute('SELECT `id` FROM `tags` WHERE `name` = %s', (tag,))
                    tag_id = self.cursor.fetchone()[0]
                    
                    # 建立书籍和标签的关联
                    self.cursor.execute('INSERT IGNORE INTO `book_tags` (`book_id`, `tag_id`) VALUES (%s, %s)', 
                                       (book_id, tag_id))
            
            # 3. 处理图片
            image_urls = adapter.get('image_urls', [])
            images = adapter.get('images', [])
            
            if image_urls and images:
                for i, image_info in enumerate(images):
                    image_url = image_urls[i] if i < len(image_urls) else ''
                    image_path = image_info.get('path', '') if isinstance(image_info, dict) else ''
                    
                    self.cursor.execute('''
                    INSERT INTO `images` (`book_id`, `image_url`, `image_path`) VALUES (%s, %s, %s)
                    ''', (book_id, image_url, image_path))
            
            # 提交事务
            self.conn.commit()
            self.success_count += 1
            spider.logger.info(f"成功保存到MySQL数据库: {adapter.get('title', '')}")
            
        except Exception as e:
            self.failed_count += 1
            spider.logger.error(f"保存到MySQL数据库失败: {str(e)}, item: {item}")
            # 回滚事务
            self.conn.rollback()
        
        return item
    
    def close_spider(self, spider):
        # 爬虫关闭时关闭数据库连接
        if self.conn:
            spider.logger.info("========== MySQL数据库存储统计 ==========")
            spider.logger.info(f"成功存储记录: {self.success_count}")
            spider.logger.info(f"存储失败记录: {self.failed_count}")
            spider.logger.info("========================================")
            
            self.conn.close()
            spider.logger.info("MySQL数据库连接已关闭")