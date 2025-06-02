import sqlite3
import os
import json
from itemadapter import ItemAdapter

class FeiluDatabasePipeline:
    """
    将爬取的小说数据保存到SQLite数据库中
    """
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.success_count = 0
        self.failed_count = 0
        
    @classmethod
    def from_crawler(cls, crawler):
        # 从设置中获取数据库路径，如果没有设置则使用默认路径
        db_path = crawler.settings.get('DATABASE_PATH', 
                  os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'feilu_books.db'))
        return cls(db_path)
    
    def open_spider(self, spider):
        # 爬虫启动时连接数据库
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            spider.logger.info(f"数据库连接成功: {self.db_path}")
            
            # 创建表结构
            self.create_tables()
            spider.logger.info("数据库表结构初始化完成")
        except Exception as e:
            spider.logger.error(f"数据库连接失败: {str(e)}")
            raise e
    
    def create_tables(self):
        # 创建小说信息表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            monthly_clicks TEXT,
            word_count TEXT,
            summary TEXT,
            book_url TEXT UNIQUE,
            flowers TEXT,
            rating TEXT,
            rewards TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建标签表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        ''')
        
        # 创建小说-标签关联表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_tags (
            book_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (book_id, tag_id),
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (tag_id) REFERENCES tags (id)
        )
        ''')
        
        # 创建图片表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            image_url TEXT,
            image_path TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
        ''')
        
        self.conn.commit()
    
    def process_item(self, item, spider):
        try:
            adapter = ItemAdapter(item)
            
            # 1. 插入小说基本信息
            self.cursor.execute('''
            INSERT OR IGNORE INTO books 
            (title, author, monthly_clicks, word_count, summary, book_url, flowers, rating, rewards)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                adapter.get('title', ''),
                adapter.get('author', ''),
                adapter.get('monthly_clicks', ''),
                adapter.get('word_count', ''),
                adapter.get('summary', ''),
                adapter.get('book_url', ''),
                adapter.get('flowers', ''),
                adapter.get('rating', ''),
                adapter.get('rewards', '')
            ))
            
            # 获取插入的书籍ID
            if self.cursor.rowcount > 0:
                book_id = self.cursor.lastrowid
            else:
                # 如果书籍已存在，获取其ID
                self.cursor.execute('SELECT id FROM books WHERE book_url = ?', (adapter.get('book_url', ''),))
                book_id = self.cursor.fetchone()[0]
            
            # 2. 处理标签
            tags = adapter.get('tags', [])
            if tags:
                for tag in tags:
                    # 插入标签（如果不存在）
                    self.cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
                    
                    # 获取标签ID
                    self.cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
                    tag_id = self.cursor.fetchone()[0]
                    
                    # 建立书籍和标签的关联
                    self.cursor.execute('INSERT OR IGNORE INTO book_tags (book_id, tag_id) VALUES (?, ?)', 
                                       (book_id, tag_id))
            
            # 3. 处理图片
            image_urls = adapter.get('image_urls', [])
            images = adapter.get('images', [])
            
            if image_urls and images:
                for i, image_info in enumerate(images):
                    image_url = image_urls[i] if i < len(image_urls) else ''
                    image_path = image_info.get('path', '') if isinstance(image_info, dict) else ''
                    
                    self.cursor.execute('''
                    INSERT INTO images (book_id, image_url, image_path) VALUES (?, ?, ?)
                    ''', (book_id, image_url, image_path))
            
            self.conn.commit()
            self.success_count += 1
            spider.logger.info(f"成功保存到数据库: {adapter.get('title', '')}")
            
        except Exception as e:
            self.failed_count += 1
            spider.logger.error(f"保存到数据库失败: {str(e)}, item: {item}")
            # 回滚事务
            self.conn.rollback()
        
        return item
    
    def close_spider(self, spider):
        # 爬虫关闭时关闭数据库连接
        if self.conn:
            spider.logger.info("========== 数据库存储统计 ==========")
            spider.logger.info(f"成功存储记录: {self.success_count}")
            spider.logger.info(f"存储失败记录: {self.failed_count}")
            spider.logger.info("====================================")
            
            self.conn.close()
            spider.logger.info("数据库连接已关闭")