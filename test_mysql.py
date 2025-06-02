#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
飞卢小说爬虫 - MySQL数据库测试工具

此脚本用于测试MySQL数据库连接和查询功能。
使用前请确保已安装pymysql库，并且MySQL服务已启动。

使用方法：
    python test_mysql.py
"""

import pymysql
import os
import sys
from prettytable import PrettyTable

# 从settings.py中读取MySQL配置
def get_mysql_config():
    try:
        # 尝试从settings.py中导入配置
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from Feilu.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD, MYSQL_CHARSET
        
        return {
            'host': MYSQL_HOST,
            'port': MYSQL_PORT,
            'database': MYSQL_DATABASE,
            'user': MYSQL_USER,
            'password': MYSQL_PASSWORD,
            'charset': MYSQL_CHARSET
        }
    except ImportError:
        # 如果导入失败，使用默认配置
        return {
            'host': 'localhost',
            'port': 3306,
            'database': 'feilu_books',
            'user': 'root',
            'password': '',
            'charset': 'utf8mb4'
        }

def test_connection(config):
    """
    测试MySQL数据库连接
    """
    try:
        # 尝试连接到MySQL服务器
        conn = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            charset=config['charset']
        )
        print("MySQL服务器连接成功！")
        
        # 检查数据库是否存在
        cursor = conn.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{config['database']}'")
        if cursor.fetchone():
            print(f"数据库 '{config['database']}' 已存在")
            cursor.execute(f"USE `{config['database']}`")
            
            # 检查表是否存在
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if tables:
                print(f"数据库中存在以下表：")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print(f"数据库中没有表")
        else:
            print(f"数据库 '{config['database']}' 不存在")
        
        cursor.close()
        conn.close()
        return True
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1045:  # 访问被拒绝
            print(f"错误：MySQL连接失败 - 访问被拒绝。请检查用户名和密码。")
        elif e.args[0] == 2003:  # 无法连接到服务器
            print(f"错误：无法连接到MySQL服务器。请确保MySQL服务已启动。")
        else:
            print(f"错误：MySQL操作错误 - {str(e)}")
        return False
    except Exception as e:
        print(f"错误：连接测试失败 - {str(e)}")
        return False

def show_database_stats(config):
    """
    显示数据库统计信息
    """
    try:
        # 连接到数据库
        conn = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset=config['charset']
        )
        cursor = conn.cursor()
        
        # 获取各表的记录数
        tables = ['books', 'tags', 'book_tags', 'images']
        stats = PrettyTable()
        stats.field_names = ["表名", "记录数"]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            stats.add_row([table, count])
        
        print("\n数据库统计信息：")
        print(stats)
        
        # 显示书籍预览
        cursor.execute("SELECT id, title, author, monthly_clicks, rating FROM books LIMIT 5")
        books = cursor.fetchall()
        
        if books:
            preview = PrettyTable()
            preview.field_names = ["ID", "书名", "作者", "月点击量", "评分"]
            for book in books:
                preview.add_row(book)
            
            print("\n书籍预览（前5条）：")
            print(preview)
        
        # 显示标签预览
        cursor.execute("SELECT id, name FROM tags LIMIT 10")
        tags = cursor.fetchall()
        
        if tags:
            preview = PrettyTable()
            preview.field_names = ["ID", "标签名"]
            for tag in tags:
                preview.add_row(tag)
            
            print("\n标签预览（前10条）：")
            print(preview)
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"错误：获取数据库统计信息失败 - {str(e)}")
        return False

def main():
    try:
        # 检查是否安装了prettytable
        import prettytable
    except ImportError:
        print("错误：未安装prettytable库。请运行 'pip install prettytable' 安装。")
        return
    
    print("=" * 60)
    print("飞卢小说爬虫 - MySQL数据库测试工具")
    print("=" * 60)
    
    # 获取MySQL配置
    config = get_mysql_config()
    print("\nMySQL配置信息：")
    print(f"主机: {config['host']}")
    print(f"端口: {config['port']}")
    print(f"数据库: {config['database']}")
    print(f"用户: {config['user']}")
    print(f"字符集: {config['charset']}")
    
    # 测试连接
    print("\n正在测试MySQL连接...")
    if test_connection(config):
        # 显示数据库统计信息
        try:
            show_database_stats(config)
        except Exception as e:
            print(f"\n无法显示数据库统计信息: {str(e)}")
            print("可能是因为数据库为空或表结构不完整。请先运行爬虫收集数据。")
    
    print("\n测试完成。如需帮助，请参考 'MySQL数据库使用说明.md' 文件。")

if __name__ == "__main__":
    main()