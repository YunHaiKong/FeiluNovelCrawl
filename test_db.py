import os
import sqlite3
import pandas as pd


def test_database_connection():
    """
    测试数据库连接并显示数据库中的内容
    """
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feilu_books.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        print("请先运行爬虫收集数据")
        return
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        print(f"成功连接到数据库: {db_path}")
        
        # 查询书籍信息
        books_df = pd.read_sql_query("SELECT * FROM books", conn)
        if not books_df.empty:
            print(f"\n共找到 {len(books_df)} 本书籍")
            print("\n书籍信息预览:")
            print(books_df[['id', 'title', 'author', 'rating']].head())
        else:
            print("\n数据库中没有书籍记录")
        
        # 查询标签信息
        tags_df = pd.read_sql_query("SELECT * FROM tags", conn)
        if not tags_df.empty:
            print(f"\n共找到 {len(tags_df)} 个标签")
            print("\n标签预览:")
            print(tags_df.head())
        else:
            print("\n数据库中没有标签记录")
        
        # 查询图片信息
        images_df = pd.read_sql_query("SELECT * FROM images", conn)
        if not images_df.empty:
            print(f"\n共找到 {len(images_df)} 张图片记录")
            print("\n图片记录预览:")
            print(images_df[['id', 'book_id', 'image_path']].head())
        else:
            print("\n数据库中没有图片记录")
        
        # 查询书籍-标签关联
        book_tags_df = pd.read_sql_query("""
            SELECT b.title, t.name as tag_name 
            FROM book_tags bt 
            JOIN books b ON bt.book_id = b.id 
            JOIN tags t ON bt.tag_id = t.id
            LIMIT 10
        """, conn)
        
        if not book_tags_df.empty:
            print("\n书籍-标签关联预览:")
            print(book_tags_df.head(10))
        else:
            print("\n数据库中没有书籍-标签关联记录")
        
        # 关闭连接
        conn.close()
        
    except Exception as e:
        print(f"数据库操作失败: {str(e)}")


if __name__ == "__main__":
    test_database_connection()