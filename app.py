#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
飞卢小说数据可视化分析系统

此应用程序使用Flask框架创建一个Web界面，用于可视化分析MySQL数据库中的飞卢小说数据。
"""

from flask import Flask, render_template, jsonify, request
import pymysql
import pandas as pd 
import json
import os

app = Flask(__name__)

# 从settings.py中读取MySQL配置
def get_mysql_config():
    try:
        # 尝试从settings.py中导入配置
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
            'password': '1234',
            'charset': 'utf8mb4'
        }

# 数据库连接函数
def get_db_connection():
    config = get_mysql_config()
    connection = pymysql.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        charset=config['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 获取书籍数据API
@app.route('/api/books')
def get_books():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取查询参数
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # 查询书籍数据
        cursor.execute(
            """SELECT id, title, author, monthly_clicks, word_count, 
                      flowers, rating, rewards, created_at 
               FROM books LIMIT %s OFFSET %s""", 
            (limit, offset)
        )
        books = cursor.fetchall()
        
        # 查询总数
        cursor.execute("SELECT COUNT(*) as count FROM books")
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total': total,
            'books': books
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取标签分布数据API
@app.route('/api/tags/distribution')
def get_tag_distribution():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询标签分布
        cursor.execute(
            """SELECT t.name, COUNT(bt.book_id) as book_count 
               FROM tags t 
               JOIN book_tags bt ON t.id = bt.tag_id 
               GROUP BY t.name 
               ORDER BY book_count DESC 
               LIMIT 20"""
        )
        tags = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(tags)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取评分分布数据API
@app.route('/api/ratings/distribution')
def get_rating_distribution():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询评分分布
        cursor.execute(
            """SELECT 
                  CASE 
                    WHEN rating BETWEEN 0 AND 1 THEN '0-1' 
                    WHEN rating BETWEEN 1 AND 2 THEN '1-2' 
                    WHEN rating BETWEEN 2 AND 3 THEN '2-3' 
                    WHEN rating BETWEEN 3 AND 4 THEN '3-4' 
                    WHEN rating BETWEEN 4 AND 5 THEN '4-5' 
                    WHEN rating BETWEEN 5 AND 6 THEN '5-6' 
                    WHEN rating BETWEEN 6 AND 7 THEN '6-7' 
                    WHEN rating BETWEEN 7 AND 8 THEN '7-8' 
                    WHEN rating BETWEEN 8 AND 9 THEN '8-9' 
                    WHEN rating BETWEEN 9 AND 10 THEN '9-10' 
                    ELSE 'Unknown' 
                  END as rating_range, 
                  COUNT(*) as book_count 
               FROM books 
               WHERE rating IS NOT NULL 
               GROUP BY rating_range 
               ORDER BY rating_range"""
        )
        ratings = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(ratings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取热门作者数据API
@app.route('/api/authors/top')
def get_top_authors():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询热门作者
        cursor.execute(
            """SELECT author, COUNT(*) as book_count, 
                      AVG(CAST(rating AS DECIMAL(10,2))) as avg_rating 
               FROM books 
               WHERE author IS NOT NULL AND author != '' 
               GROUP BY author 
               ORDER BY book_count DESC 
               LIMIT 10"""
        )
        authors = cursor.fetchall()
        
        # 处理数据，确保avg_rating是数值类型
        for author in authors:
            if author['avg_rating'] is not None:
                author['avg_rating'] = float(author['avg_rating'])
            else:
                author['avg_rating'] = 0
            
            # 确保book_count是整数
            if author['book_count'] is not None:
                author['book_count'] = int(author['book_count'])
            else:
                author['book_count'] = 0
        
        cursor.close()
        conn.close()
        
        return jsonify(authors)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取点击量与评分关系数据API
@app.route('/api/correlation/clicks_rating')
def get_clicks_rating_correlation():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询点击量与评分数据
        cursor.execute(
            """SELECT title, monthly_clicks, rating 
               FROM books 
               WHERE monthly_clicks IS NOT NULL 
                 AND rating IS NOT NULL 
               LIMIT 200"""
        )
        data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 处理数据，将点击量转换为数值
        for item in data:
            clicks = item['monthly_clicks']
            if isinstance(clicks, str):
                # 处理"月点击：1130542"格式
                if '月点击：' in clicks:
                    clicks = clicks.replace('月点击：', '')
                    
                # 处理带单位的数字
                if '万' in clicks:
                    item['monthly_clicks'] = float(clicks.replace('万', '')) * 10000
                elif '千' in clicks:
                    item['monthly_clicks'] = float(clicks.replace('千', '')) * 1000
                else:
                    try:
                        item['monthly_clicks'] = float(clicks)
                    except:
                        item['monthly_clicks'] = 0
            
            # 确保评分是数值类型
            if item['rating'] is not None:
                try:
                    item['rating'] = float(item['rating'])
                except:
                    item['rating'] = 0
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 启动应用
if __name__ == '__main__':
    # 确保templates目录存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 确保static目录存在
    if not os.path.exists('static'):
        os.makedirs('static')
        os.makedirs('static/js', exist_ok=True)
        os.makedirs('static/css', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)