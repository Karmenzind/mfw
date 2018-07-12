
- 蚂蜂窝指定关键词爬取游记和景点信息
- 提取文章景点
- 分析、计算热度，绘制图表
- 使用高徳API绘制景点热力图

Spider运行顺序:
>  动态信息爬取依赖[Splash](https://hub.docker.com/r/scrapinghub/splash/)实现

1. note_index
2. travel_notes
3. places

Analysis部分运行顺序：
1. [base_analysis.py](./MFWAnalysis/base_analysis.py)        数据整理
2. [purify_score.py](./MFWAnalysis/purify_score.py)         清洗，导出csv
3. [place_score_sort.ipynb](./MFWAnalysis/place_score_sort.ipynb)  排序，图表
4. [build_heatmap_data.py](./MFWAnalysis/build_heatmap_data.py)   构造热力图数据
5. [start_server.py](./MFWAnalysis/start_server.py)         展示热力图
