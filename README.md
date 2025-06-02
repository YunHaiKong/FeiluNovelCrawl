# 飞卢小说网爬虫与数据可视化分析系统

## 项目简介

本项目包含两个主要部分：
1. 基于Scrapy框架开发的飞卢小说网爬虫，用于爬取小说信息和封面图片
2. 基于Flask和ECharts的Web应用程序，用于可视化分析数据库中的飞卢小说数据

系统提供了直观的图表和数据表格，帮助用户了解小说的评分、点击量、标签分布等多维度信息。

## 功能特点

### 爬虫功能

- 爬取小说基本信息（书名、作者、月点击量、字数等）
- 爬取小说详情页信息（摘要、标签、鲜花数等）
- 下载小说封面图片并保存为jpg格式
- 支持控制爬取页数
- 支持数据存储到SQLite或MySQL数据库

### 数据可视化功能

- **数据概览**：展示总小说数、标签数、平均评分和最高点击量等关键指标
- **小说列表**：以表格形式展示所有小说的基本信息，支持分页浏览
- **数据分析**：提供多种可视化图表
  - 标签分布图：展示最常见的小说标签及其数量
  - 评分分布图：展示小说评分的分布情况
  - 热门作者图：展示作品数量最多的作者及其平均评分
  - 点击量与评分关系图：分析月点击量与评分之间的相关性

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 数据库配置

#### SQLite数据库（默认）

无需额外配置，数据库文件会自动创建在项目根目录下的`feilu_books.db`。

#### MySQL数据库（可选）

1. 确保已安装MySQL服务器
2. 在`Feilu/settings.py`中配置MySQL连接参数：

```python
# MySQL数据库设置
MYSQL_HOST = 'localhost'  # MySQL主机地址
MYSQL_PORT = 3306         # MySQL端口
MYSQL_DATABASE = 'feilu_books'  # 数据库名称
MYSQL_USER = 'root'       # 数据库用户名
MYSQL_PASSWORD = ''       # 数据库密码
MYSQL_CHARSET = 'utf8mb4' # 字符集

# 启用MySQL数据库管道
ITEM_PIPELINES = {
    'Feilu.pipelines.FeiluImagesPipeline': 1,
    'Feilu.pipelines.FeiluPipeline': 300,
    # 'Feilu.db_pipeline.FeiluDatabasePipeline': 400,  # SQLite数据库管道（可注释掉）
    'Feilu.mysql_pipeline.FeiluMySQLPipeline': 400,   # MySQL数据库管道
}
```

## 使用方法

### 1. 运行爬虫

基本运行（默认爬取5页）：

```bash
scrapy crawl books
```

指定爬取页数：

```bash
scrapy crawl books -a max_pages=10
```

导出数据为CSV格式：

```bash
scrapy crawl books -o books.csv
```

### 2. 启动数据可视化Web应用

```bash
python app.py
```

在浏览器中访问：
```
http://localhost:5000
```

使用界面：
- 顶部导航栏可以快速跳转到不同的功能区域
- 在"数据概览"部分查看关键统计数据
- 在"小说列表"部分浏览所有小说信息
- 在"数据分析"部分查看各种可视化图表

## 系统架构

- **后端**：Flask框架，提供Web服务和API接口
- **数据库**：MySQL/SQLite，存储飞卢小说爬虫收集的数据
- **前端**：
  - Bootstrap 5：响应式布局和UI组件
  - ECharts：数据可视化图表库
  - jQuery：DOM操作和AJAX请求

## 数据库结构

1. **books表**：存储小说基本信息
   - id: 主键
   - title: 小说标题
   - author: 作者
   - monthly_clicks: 月点击量
   - word_count: 字数
   - summary: 摘要
   - book_url: 书籍URL（唯一）
   - flowers: 鲜花数
   - rating: 评分
   - rewards: 打赏
   - created_at: 创建时间

2. **tags表**：存储标签信息
   - id: 主键
   - name: 标签名称（唯一）

3. **book_tags表**：存储书籍与标签的关联关系
   - book_id: 书籍ID（外键）
   - tag_id: 标签ID（外键）
   - 主键为(book_id, tag_id)组合

4. **images表**：存储图片信息
   - id: 主键
   - book_id: 书籍ID（外键）
   - image_url: 图片URL
   - image_path: 图片保存路径

## 数据API

系统提供以下API接口：

- `/api/books`：获取小说列表数据
- `/api/tags/distribution`：获取标签分布数据
- `/api/ratings/distribution`：获取评分分布数据
- `/api/authors/top`：获取热门作者数据
- `/api/correlation/clicks_rating`：获取点击量与评分关系数据

## 项目结构

- `Feilu/spiders/books.py`: 爬虫主程序
- `Feilu/items.py`: 数据项定义
- `Feilu/pipelines.py`: 数据处理管道，包含图片下载功能
- `Feilu/db_pipeline.py`: SQLite数据库管道
- `Feilu/mysql_pipeline.py`: MySQL数据库管道
- `Feilu/settings.py`: 爬虫配置
- `app.py`: 数据可视化Web应用主程序
- `templates/`: Web应用HTML模板
- `static/`: Web应用静态资源（CSS、JS等）
- `images/`: 下载的图片存储目录
- `visualizations/`: 数据分析图表

## 常见问题

### 爬虫相关

1. **爬虫运行缓慢**
   - 检查网络连接
   - 适当调整下载延迟（DOWNLOAD_DELAY）
   - 考虑使用代理IP

2. **数据库连接失败**
   - 确保数据库服务已启动
   - 检查连接参数是否正确
   - 确认用户权限

### 可视化系统相关

1. **无法连接到数据库**
   - 确保MySQL服务已启动
   - 检查数据库连接参数是否正确
   - 确认数据库用户有足够的访问权限

2. **图表无法显示**
   - 检查浏览器控制台是否有错误信息
   - 确认数据库中有足够的数据用于分析

3. **系统运行缓慢**
   - 考虑优化数据库查询
   - 可以添加数据缓存机制

## 扩展建议

1. 添加用户认证系统，实现多用户管理
2. 增加数据筛选和导出功能
3. 添加更多类型的数据分析图表
4. 实现数据定时更新机制
5. 优化移动端显示效果
6. 添加自然语言处理功能，分析小说内容和评论

## 注意事项

- 请遵守网站的robots.txt规则
- 适当调整下载延迟，避免对目标网站造成过大压力
- 数据库操作使用事务处理，如果某条记录保存失败，会自动回滚，不影响其他记录

## 许可证

本项目采用MIT许可证。详情请参阅LICENSE文件。