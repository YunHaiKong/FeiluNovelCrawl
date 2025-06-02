import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import seaborn as sns
from matplotlib.font_manager import FontProperties
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

# 设置全局风格和参数
plt.style.use('seaborn-v0_8-whitegrid')  # 使用seaborn的白色网格风格

# 设置中文字体
try:
    # 尝试使用微软雅黑字体
    font = FontProperties(fname=r'C:\Windows\Fonts\msyh.ttc')
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    plt.rcParams['figure.facecolor'] = '#f8f9fa'  # 设置图表背景色
    plt.rcParams['axes.facecolor'] = '#f8f9fa'    # 设置坐标区背景色
    plt.rcParams['axes.edgecolor'] = '#333333'    # 设置坐标轴颜色
    plt.rcParams['axes.labelcolor'] = '#333333'   # 设置坐标轴标签颜色
    plt.rcParams['xtick.color'] = '#333333'       # 设置x轴刻度颜色
    plt.rcParams['ytick.color'] = '#333333'       # 设置y轴刻度颜色
    plt.rcParams['grid.color'] = '#dddddd'        # 设置网格线颜色
    plt.rcParams['grid.linestyle'] = '--'         # 设置网格线样式
    plt.rcParams['grid.alpha'] = 0.7              # 设置网格线透明度
except:
    print("无法加载中文字体，图表中文可能显示为乱码")

# 自定义颜色方案
color_palette = ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f', '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab']
sns.set_palette(color_palette)

# 读取CSV文件
df = pd.read_csv('book.csv')

# 数据清洗
def clean_data(df):
    # 复制数据框以避免警告
    df_clean = df.copy()
    
    # 处理月点击量
    def extract_clicks(click_str):
        if pd.isna(click_str):
            return np.nan
        match = re.search(r'\d+', str(click_str))
        return float(match.group()) if match else np.nan
    
    df_clean['monthly_clicks_num'] = df_clean['monthly_clicks'].apply(extract_clicks)
    
    # 处理字数
    def extract_word_count(word_str):
        if pd.isna(word_str):
            return np.nan
        match = re.search(r'\d+', str(word_str))
        if match:
            count = float(match.group())
            if '万' in str(word_str):
                count *= 10000
            return count
        return np.nan
    
    df_clean['word_count_num'] = df_clean['word_count'].apply(extract_word_count)
    
    # 处理评分
    df_clean['rating'] = pd.to_numeric(df_clean['rating'], errors='coerce')
    
    # 处理鲜花数和打赏
    for col in ['flowers', 'rewards']:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # 处理标签
    def split_tags(tag_str):
        if pd.isna(tag_str):
            return []
        return [tag.strip() for tag in str(tag_str).split(',')]
    
    df_clean['tags_list'] = df_clean['tags'].apply(split_tags)
    
    return df_clean

# 清洗数据
df_clean = clean_data(df)

# 创建输出目录
output_dir = 'visualizations'
os.makedirs(output_dir, exist_ok=True)

# 1. 月点击量与评分的关系
fig, ax = plt.subplots(figsize=(10, 6))
# 使用渐变色散点图
scatter = ax.scatter(df_clean['monthly_clicks_num'], df_clean['rating'], 
                   c=df_clean['monthly_clicks_num'], cmap='viridis', 
                   alpha=0.7, s=120, edgecolor='white', linewidth=0.5)

# 添加趋势线
sns.regplot(x='monthly_clicks_num', y='rating', data=df_clean, 
           scatter=False, ci=None, line_kws={'color': '#e15759', 'linewidth': 2}, ax=ax)

# 美化标题和标签
ax.set_title('月点击量与评分的关系', fontproperties=font, fontsize=18, pad=20, color='#333333', fontweight='bold')
ax.set_xlabel('月点击量', fontproperties=font, fontsize=14, labelpad=10, color='#333333')
ax.set_ylabel('评分', fontproperties=font, fontsize=14, labelpad=10, color='#333333')

# 添加网格线
ax.grid(True, linestyle='--', alpha=0.3, color='#cccccc')

# 美化边框
for spine in ax.spines.values():
    spine.set_linewidth(0.5)
    spine.set_color('#333333')

# 添加颜色条
cbar = plt.colorbar(scatter, ax=ax, pad=0.01)
cbar.set_label('月点击量', fontproperties=font, size=12, labelpad=10)
cbar.outline.set_linewidth(0.5)
cbar.outline.set_edgecolor('#333333')

plt.tight_layout()
plt.savefig(f'{output_dir}/clicks_vs_rating.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. 字数与月点击量的关系
fig, ax = plt.subplots(figsize=(10, 6))
# 使用渐变色散点图
scatter = ax.scatter(df_clean['word_count_num'], df_clean['monthly_clicks_num'], 
                   c=df_clean['word_count_num'], cmap='plasma', 
                   alpha=0.7, s=120, edgecolor='white', linewidth=0.5)

# 添加趋势线
sns.regplot(x='word_count_num', y='monthly_clicks_num', data=df_clean, 
           scatter=False, ci=None, line_kws={'color': '#59a14f', 'linewidth': 2}, ax=ax)

# 美化标题和标签
ax.set_title('字数与月点击量的关系', fontproperties=font, fontsize=18, pad=20, color='#333333', fontweight='bold')
ax.set_xlabel('字数', fontproperties=font, fontsize=14, labelpad=10, color='#333333')
ax.set_ylabel('月点击量', fontproperties=font, fontsize=14, labelpad=10, color='#333333')

# 添加网格线
ax.grid(True, linestyle='--', alpha=0.3, color='#cccccc')

# 美化边框
for spine in ax.spines.values():
    spine.set_linewidth(0.5)
    spine.set_color('#333333')

# 添加颜色条
cbar = plt.colorbar(scatter, ax=ax, pad=0.01)
cbar.set_label('字数', fontproperties=font, size=12, labelpad=10)
cbar.outline.set_linewidth(0.5)
cbar.outline.set_edgecolor('#333333')

plt.tight_layout()
plt.savefig(f'{output_dir}/wordcount_vs_clicks.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. 字数与评分的关系
fig, ax = plt.subplots(figsize=(10, 6))
# 使用渐变色散点图
scatter = ax.scatter(df_clean['word_count_num'], df_clean['rating'], 
                   c=df_clean['word_count_num'], cmap='magma', 
                   alpha=0.7, s=120, edgecolor='white', linewidth=0.5)

# 添加趋势线
sns.regplot(x='word_count_num', y='rating', data=df_clean, 
           scatter=False, ci=None, line_kws={'color': '#76b7b2', 'linewidth': 2}, ax=ax)

# 美化标题和标签
ax.set_title('字数与评分的关系', fontproperties=font, fontsize=18, pad=20, color='#333333', fontweight='bold')
ax.set_xlabel('字数', fontproperties=font, fontsize=14, labelpad=10, color='#333333')
ax.set_ylabel('评分', fontproperties=font, fontsize=14, labelpad=10, color='#333333')

# 添加网格线
ax.grid(True, linestyle='--', alpha=0.3, color='#cccccc')

# 美化边框
for spine in ax.spines.values():
    spine.set_linewidth(0.5)
    spine.set_color('#333333')

# 添加颜色条
cbar = plt.colorbar(scatter, ax=ax, pad=0.01)
cbar.set_label('字数', fontproperties=font, size=12, labelpad=10)
cbar.outline.set_linewidth(0.5)
cbar.outline.set_edgecolor('#333333')

plt.tight_layout()
plt.savefig(f'{output_dir}/wordcount_vs_rating.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. 标签分布
# 提取所有标签并计数
all_tags = []
for tags in df_clean['tags_list']:
    all_tags.extend(tags)

tag_counts = pd.Series(all_tags).value_counts().head(10)  # 取前10个最常见的标签

fig, ax = plt.subplots(figsize=(12, 6))

# 创建渐变色条形图
bars = ax.bar(tag_counts.index, tag_counts.values, width=0.7, 
             color=color_palette[:len(tag_counts)], 
             edgecolor='white', linewidth=1.5, alpha=0.9)

# 在条形上方添加数值标签
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
            f'{int(height)}',
            ha='center', va='bottom', fontsize=11, fontweight='bold', color='#333333')

# 美化标题和标签
ax.set_title('小说标签分布 (前10名)', fontproperties=font, fontsize=18, pad=20, color='#333333', fontweight='bold')
ax.set_xlabel('标签', fontproperties=font, fontsize=14, labelpad=10, color='#333333')
ax.set_ylabel('数量', fontproperties=font, fontsize=14, labelpad=10, color='#333333')

# 设置x轴标签
plt.xticks(rotation=45, ha='right', fontproperties=font, fontsize=12)

# 添加网格线（仅y轴）
ax.grid(True, linestyle='--', alpha=0.3, color='#cccccc', axis='y')

# 美化边框
for spine in ax.spines.values():
    spine.set_linewidth(0.5)
    spine.set_color('#333333')

# 移除顶部和右侧边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 添加轻微的背景阴影效果
ax.set_facecolor('#f8f9fa')

plt.tight_layout()
plt.savefig(f'{output_dir}/tag_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. 鲜花数与评分的关系
fig, ax = plt.subplots(figsize=(10, 6))

# 使用渐变色散点图
scatter = ax.scatter(df_clean['flowers'], df_clean['rating'], 
                   c=df_clean['flowers'], cmap='YlOrRd', 
                   alpha=0.7, s=120, edgecolor='white', linewidth=0.5)

# 添加趋势线
sns.regplot(x='flowers', y='rating', data=df_clean, 
           scatter=False, ci=None, line_kws={'color': '#af7aa1', 'linewidth': 2}, ax=ax)

# 美化标题和标签
ax.set_title('鲜花数与评分的关系', fontproperties=font, fontsize=18, pad=20, color='#333333', fontweight='bold')
ax.set_xlabel('鲜花数', fontproperties=font, fontsize=14, labelpad=10, color='#333333')
ax.set_ylabel('评分', fontproperties=font, fontsize=14, labelpad=10, color='#333333')

# 添加网格线
ax.grid(True, linestyle='--', alpha=0.3, color='#cccccc')

# 美化边框
for spine in ax.spines.values():
    spine.set_linewidth(0.5)
    spine.set_color('#333333')

# 添加颜色条
cbar = plt.colorbar(scatter, ax=ax, pad=0.01)
cbar.set_label('鲜花数', fontproperties=font, size=12, labelpad=10)
cbar.outline.set_linewidth(0.5)
cbar.outline.set_edgecolor('#333333')

plt.tight_layout()
plt.savefig(f'{output_dir}/flowers_vs_rating.png', dpi=300, bbox_inches='tight')
plt.close()

# 6. 打赏与月点击量的关系
fig, ax = plt.subplots(figsize=(10, 6))

# 使用渐变色散点图
scatter = ax.scatter(df_clean['rewards'], df_clean['monthly_clicks_num'], 
                   c=df_clean['rewards'], cmap='YlGnBu', 
                   alpha=0.7, s=120, edgecolor='white', linewidth=0.5)

# 添加趋势线
sns.regplot(x='rewards', y='monthly_clicks_num', data=df_clean, 
           scatter=False, ci=None, line_kws={'color': '#f28e2c', 'linewidth': 2}, ax=ax)

# 美化标题和标签
ax.set_title('打赏与月点击量的关系', fontproperties=font, fontsize=18, pad=20, color='#333333', fontweight='bold')
ax.set_xlabel('打赏', fontproperties=font, fontsize=14, labelpad=10, color='#333333')
ax.set_ylabel('月点击量', fontproperties=font, fontsize=14, labelpad=10, color='#333333')

# 添加网格线
ax.grid(True, linestyle='--', alpha=0.3, color='#cccccc')

# 美化边框
for spine in ax.spines.values():
    spine.set_linewidth(0.5)
    spine.set_color('#333333')

# 添加颜色条
cbar = plt.colorbar(scatter, ax=ax, pad=0.01)
cbar.set_label('打赏', fontproperties=font, size=12, labelpad=10)
cbar.outline.set_linewidth(0.5)
cbar.outline.set_edgecolor('#333333')

plt.tight_layout()
plt.savefig(f'{output_dir}/rewards_vs_clicks.png', dpi=300, bbox_inches='tight')
plt.close()

# 7. 评分分布
fig, ax = plt.subplots(figsize=(10, 6))

# 使用自定义颜色的直方图
histplot = sns.histplot(df_clean['rating'].dropna(), bins=10, kde=True, 
                      color='#4e79a7', alpha=0.7, edgecolor='white', linewidth=1.5, ax=ax)
# 单独设置kde曲线颜色
kde_line = histplot.lines[0]
kde_line.set_color('#e15759')
kde_line.set_linewidth(2)

# 美化标题和标签
ax.set_title('小说评分分布', fontproperties=font, fontsize=18, pad=20, color='#333333', fontweight='bold')
ax.set_xlabel('评分', fontproperties=font, fontsize=14, labelpad=10, color='#333333')
ax.set_ylabel('数量', fontproperties=font, fontsize=14, labelpad=10, color='#333333')

# 添加网格线
ax.grid(True, linestyle='--', alpha=0.3, color='#cccccc')

# 美化边框
for spine in ax.spines.values():
    spine.set_linewidth(0.5)
    spine.set_color('#333333')

# 移除顶部和右侧边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 添加平均值线
mean_rating = df_clean['rating'].mean()
ax.axvline(x=mean_rating, color='#ff9da7', linestyle='--', linewidth=2)
ax.text(mean_rating + 0.1, ax.get_ylim()[1] * 0.9, 
        f'平均评分: {mean_rating:.2f}', 
        fontproperties=font, fontsize=12, color='#333333')

plt.tight_layout()
plt.savefig(f'{output_dir}/rating_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 8. 热门作者分析 (按作品数量)
author_counts = df_clean['author'].value_counts().head(10)
fig, ax = plt.subplots(figsize=(12, 6))

# 创建水平条形图，更适合展示作者名称
bars = ax.barh(author_counts.index[::-1], author_counts.values[::-1], 
              color=sns.color_palette("viridis", len(author_counts)), 
              edgecolor='white', linewidth=1.5, alpha=0.9, height=0.7)

# 在条形上添加数值标签
for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
            f'{int(width)}', 
            ha='left', va='center', fontsize=11, fontweight='bold', color='#333333')

# 美化标题和标签
ax.set_title('热门作者 (按作品数量)', fontproperties=font, fontsize=18, pad=20, color='#333333', fontweight='bold')
ax.set_xlabel('作品数量', fontproperties=font, fontsize=14, labelpad=10, color='#333333')
ax.set_ylabel('作者', fontproperties=font, fontsize=14, labelpad=10, color='#333333')

# 设置y轴标签
plt.yticks(fontproperties=font, fontsize=12)

# 添加网格线（仅x轴）
ax.grid(True, linestyle='--', alpha=0.3, color='#cccccc', axis='x')

# 美化边框
for spine in ax.spines.values():
    spine.set_linewidth(0.5)
    spine.set_color('#333333')

# 移除顶部和右侧边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 添加轻微的背景阴影效果
ax.set_facecolor('#f8f9fa')

plt.tight_layout()
plt.savefig(f'{output_dir}/top_authors.png', dpi=300, bbox_inches='tight')
plt.close()

# 9. 相关性热图
corr_columns = ['monthly_clicks_num', 'word_count_num', 'rating', 'flowers', 'rewards']
corr_df = df_clean[corr_columns].corr()

# 创建自定义的相关性热图
fig, ax = plt.subplots(figsize=(10, 8))

# 设置中文列名
col_names = {
    'monthly_clicks_num': '月点击量',
    'word_count_num': '字数',
    'rating': '评分',
    'flowers': '鲜花数',
    'rewards': '打赏'
}

# 创建新的DataFrame，使用中文列名
corr_df_cn = corr_df.copy()
corr_df_cn.index = [col_names[col] for col in corr_df.index]
corr_df_cn.columns = [col_names[col] for col in corr_df.columns]

# 创建自定义热图
mask = np.triu(np.ones_like(corr_df_cn, dtype=bool))

# 使用自定义颜色映射
cmap = sns.diverging_palette(220, 10, as_cmap=True)

# 绘制热图
heatmap = sns.heatmap(corr_df_cn, mask=mask, annot=True, cmap=cmap, vmax=1, vmin=-1,
            annot_kws={"size": 12, "weight": "bold"}, fmt='.2f',
            linewidths=1, linecolor='white', cbar_kws={"shrink": .8})

# 美化标题
plt.title('数据相关性热图', fontproperties=font, fontsize=18, pad=20, color='#333333', fontweight='bold')

# 设置字体
for text in heatmap.texts:
    text.set_fontproperties(font)

# 设置坐标轴标签字体
plt.xticks(fontproperties=font, fontsize=12)
plt.yticks(fontproperties=font, fontsize=12)

plt.tight_layout()
plt.savefig(f'{output_dir}/correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"分析完成！可视化结果已保存到 {output_dir} 目录")

# 生成分析报告
with open(f'{output_dir}/分析报告.md', 'w', encoding='utf-8') as f:
    f.write("# 飞卢小说网数据分析报告\n\n")
    
    f.write("## 数据概览\n")
    f.write(f"- 总数据量: {len(df_clean)} 条记录\n")
    f.write(f"- 平均评分: {df_clean['rating'].mean():.2f}\n")
    f.write(f"- 平均月点击量: {df_clean['monthly_clicks_num'].mean():.0f}\n")
    f.write(f"- 平均字数: {df_clean['word_count_num'].mean():.0f}\n\n")
    
    f.write("## 主要发现\n")
    f.write("1. **月点击量与评分关系**: 分析月点击量与评分之间是否存在相关性\n")
    f.write("2. **字数与受欢迎程度**: 探索小说字数是否影响其受欢迎程度\n")
    f.write("3. **标签分布**: 展示最受欢迎的小说类型标签\n")
    f.write("4. **鲜花与评分**: 分析鲜花数量与评分之间的关系\n")
    f.write("5. **打赏与点击量**: 探索打赏与月点击量之间的关联\n")
    f.write("6. **热门作者**: 识别平台上最活跃的作者\n\n")
    
    f.write("## 详细分析\n")
    f.write("请查看生成的可视化图表以获取详细分析结果。\n")

print(f"分析报告已生成: {output_dir}/分析报告.md")