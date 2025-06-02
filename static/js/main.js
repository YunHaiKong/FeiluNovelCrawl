// 飞卢小说数据可视化分析系统 - 主要JavaScript文件

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 加载数据概览
    loadDashboardStats();
    
    // 加载小说列表
    loadBooks(1);
    
    // 加载各种图表
    loadTagDistribution();
    loadRatingDistribution();
    loadTopAuthors();
    loadClicksRatingCorrelation();
});

// 加载数据概览统计信息
function loadDashboardStats() {
    // 获取小说总数
    fetch('/api/books?limit=1')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-books').textContent = data.total.toLocaleString();
        })
        .catch(error => {
            console.error('获取小说总数失败:', error);
            document.getElementById('total-books').textContent = '获取失败';
        });
    
    // 获取标签总数
    fetch('/api/tags/distribution')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-tags').textContent = data.length.toLocaleString();
        })
        .catch(error => {
            console.error('获取标签总数失败:', error);
            document.getElementById('total-tags').textContent = '获取失败';
        });
    
    // 获取平均评分和最高点击量
    fetch('/api/books?limit=100')
        .then(response => response.json())
        .then(data => {
            // 计算平均评分
            let totalRating = 0;
            let ratingCount = 0;
            let maxClicks = 0;
            
            data.books.forEach(book => {
                if (book.rating) {
                    totalRating += parseFloat(book.rating);
                    ratingCount++;
                }
                
                // 处理点击量
                let clicks = book.monthly_clicks;
                if (clicks) {
                    if (typeof clicks === 'string') {
                        if (clicks.includes('万')) {
                            clicks = parseFloat(clicks.replace('万', '')) * 10000;
                        } else if (clicks.includes('千')) {
                            clicks = parseFloat(clicks.replace('千', '')) * 1000;
                        } else {
                            clicks = parseFloat(clicks);
                        }
                    }
                    
                    if (!isNaN(clicks) && clicks > maxClicks) {
                        maxClicks = clicks;
                    }
                }
            });
            
            const avgRating = ratingCount > 0 ? (totalRating / ratingCount).toFixed(1) : '无数据';
            document.getElementById('avg-rating').textContent = avgRating;
            
            // 格式化最高点击量
            if (maxClicks >= 10000) {
                document.getElementById('max-clicks').textContent = (maxClicks / 10000).toFixed(1) + '万';
            } else {
                document.getElementById('max-clicks').textContent = maxClicks.toLocaleString();
            }
        })
        .catch(error => {
            console.error('获取评分和点击量数据失败:', error);
            document.getElementById('avg-rating').textContent = '获取失败';
            document.getElementById('max-clicks').textContent = '获取失败';
        });
}

// 加载小说列表
function loadBooks(page, limit = 10) {
    const offset = (page - 1) * limit;
    
    fetch(`/api/books?limit=${limit}&offset=${offset}`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#books-table tbody');
            tableBody.innerHTML = '';
            
            if (data.books.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="8" class="text-center">没有找到小说数据</td></tr>';
                return;
            }
            
            // 填充表格数据
            data.books.forEach(book => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${book.id}</td>
                    <td>${book.title || '-'}</td>
                    <td>${book.author || '-'}</td>
                    <td>${book.monthly_clicks || '-'}</td>
                    <td>${book.word_count || '-'}</td>
                    <td>${book.flowers || '-'}</td>
                    <td>${book.rating || '-'}</td>
                    <td>${book.rewards || '-'}</td>
                `;
                tableBody.appendChild(row);
            });
            
            // 生成分页控件
            generatePagination(page, Math.ceil(data.total / limit));
        })
        .catch(error => {
            console.error('获取小说列表失败:', error);
            const tableBody = document.querySelector('#books-table tbody');
            tableBody.innerHTML = '<tr><td colspan="8" class="text-center text-danger">获取数据失败</td></tr>';
        });
}

// 生成分页控件
function generatePagination(currentPage, totalPages) {
    const pagination = document.getElementById('books-pagination');
    pagination.innerHTML = '';
    
    // 上一页按钮
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#" ${currentPage > 1 ? `onclick="loadBooks(${currentPage - 1}); return false;"` : ''}>上一页</a>`;
    pagination.appendChild(prevLi);
    
    // 页码按钮
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    
    if (endPage - startPage < 4) {
        startPage = Math.max(1, endPage - 4);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageLi = document.createElement('li');
        pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
        pageLi.innerHTML = `<a class="page-link" href="#" onclick="loadBooks(${i}); return false;">${i}</a>`;
        pagination.appendChild(pageLi);
    }
    
    // 下一页按钮
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#" ${currentPage < totalPages ? `onclick="loadBooks(${currentPage + 1}); return false;"` : ''}>下一页</a>`;
    pagination.appendChild(nextLi);
}

// 加载标签分布图表
function loadTagDistribution() {
    fetch('/api/tags/distribution')
        .then(response => response.json())
        .then(data => {
            const chartDom = document.getElementById('tag-distribution-chart');
            const chart = echarts.init(chartDom);
            
            // 准备图表数据
            const categories = data.map(item => item.name);
            const values = data.map(item => item.book_count);
            
            // 配置图表选项
            const option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: categories,
                    axisLabel: {
                        interval: 0,
                        rotate: 45
                    }
                },
                yAxis: {
                    type: 'value'
                },
                series: [
                    {
                        name: '小说数量',
                        type: 'bar',
                        data: values,
                        itemStyle: {
                            color: function(params) {
                                // 生成渐变色
                                const colorList = [
                                    '#5470c6', '#91cc75', '#fac858', '#ee6666',
                                    '#73c0de', '#3ba272', '#fc8452', '#9a60b4'
                                ];
                                return colorList[params.dataIndex % colorList.length];
                            }
                        }
                    }
                ]
            };
            
            // 渲染图表
            chart.setOption(option);
            
            // 响应窗口大小变化
            window.addEventListener('resize', function() {
                chart.resize();
            });
        })
        .catch(error => {
            console.error('获取标签分布数据失败:', error);
            document.getElementById('tag-distribution-chart').innerHTML = 
                '<div class="text-center text-danger">获取标签分布数据失败</div>';
        });
}

// 加载评分分布图表
function loadRatingDistribution() {
    fetch('/api/ratings/distribution')
        .then(response => response.json())
        .then(data => {
            const chartDom = document.getElementById('rating-distribution-chart');
            const chart = echarts.init(chartDom);
            
            // 准备图表数据
            const categories = data.map(item => item.rating_range);
            const values = data.map(item => item.book_count);
            
            // 配置图表选项
            const option = {
                tooltip: {
                    trigger: 'item'
                },
                legend: {
                    orient: 'vertical',
                    left: 'left'
                },
                series: [
                    {
                        name: '小说数量',
                        type: 'pie',
                        radius: '60%',
                        data: data.map(item => ({
                            name: item.rating_range,
                            value: item.book_count
                        })),
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            
            // 渲染图表
            chart.setOption(option);
            
            // 响应窗口大小变化
            window.addEventListener('resize', function() {
                chart.resize();
            });
        })
        .catch(error => {
            console.error('获取评分分布数据失败:', error);
            document.getElementById('rating-distribution-chart').innerHTML = 
                '<div class="text-center text-danger">获取评分分布数据失败</div>';
        });
}

// 加载热门作者图表
function loadTopAuthors() {
    fetch('/api/authors/top')
        .then(response => response.json())
        .then(data => {
            const chartDom = document.getElementById('top-authors-chart');
            const chart = echarts.init(chartDom);
            
            // 准备图表数据
            const authors = data.map(item => item.author);
            const bookCounts = data.map(item => item.book_count);
            const avgRatings = data.map(item => item.avg_rating);
            
            // 配置图表选项
            const option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                legend: {
                    data: ['作品数量', '平均评分']
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: [
                    {
                        type: 'category',
                        data: authors,
                        axisLabel: {
                            interval: 0,
                            rotate: 45
                        }
                    }
                ],
                yAxis: [
                    {
                        type: 'value',
                        name: '作品数量',
                        position: 'left'
                    },
                    {
                        type: 'value',
                        name: '平均评分',
                        position: 'right',
                        min: 0,
                        max: 10
                    }
                ],
                series: [
                    {
                        name: '作品数量',
                        type: 'bar',
                        data: bookCounts
                    },
                    {
                        name: '平均评分',
                        type: 'line',
                        yAxisIndex: 1,
                        data: avgRatings,
                        symbol: 'circle',
                        symbolSize: 8
                    }
                ]
            };
            
            // 渲染图表
            chart.setOption(option);
            
            // 响应窗口大小变化
            window.addEventListener('resize', function() {
                chart.resize();
            });
        })
        .catch(error => {
            console.error('获取热门作者数据失败:', error);
            document.getElementById('top-authors-chart').innerHTML = 
                '<div class="text-center text-danger">获取热门作者数据失败</div>';
        });
}

// 加载点击量与评分关系图表
function loadClicksRatingCorrelation() {
    fetch('/api/correlation/clicks_rating')
        .then(response => response.json())
        .then(data => {
            const chartDom = document.getElementById('clicks-rating-chart');
            const chart = echarts.init(chartDom);
            
            // 准备图表数据
            const scatterData = data.map(item => [
                item.monthly_clicks,
                item.rating,
                item.title
            ]);
            
            // 配置图表选项
            const option = {
                tooltip: {
                    trigger: 'item',
                    formatter: function(params) {
                        return `${params.data[2]}<br/>点击量: ${params.data[0]}<br/>评分: ${params.data[1]}`;
                    }
                },
                xAxis: {
                    type: 'value',
                    name: '月点击量',
                    nameLocation: 'middle',
                    nameGap: 30,
                    scale: true
                },
                yAxis: {
                    type: 'value',
                    name: '评分',
                    scale: true
                },
                series: [
                    {
                        type: 'scatter',
                        data: scatterData,
                        symbolSize: 10,
                        itemStyle: {
                            color: '#5470c6'
                        }
                    }
                ]
            };
            
            // 渲染图表
            chart.setOption(option);
            
            // 响应窗口大小变化
            window.addEventListener('resize', function() {
                chart.resize();
            });
        })
        .catch(error => {
            console.error('获取点击量与评分关系数据失败:', error);
            document.getElementById('clicks-rating-chart').innerHTML = 
                '<div class="text-center text-danger">获取点击量与评分关系数据失败</div>';
        });
}