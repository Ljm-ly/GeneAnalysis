# -*- coding: utf-8 -*-
"""
可视化模块 (visualization)

本模块提供生物信息学常用的数据可视化图表，
帮助直观理解分析结果和数据特征。

包含的功能：
    1. 图表生成器 (plots)
       - GC含量分布直方图
       - 差异表达火山图
       - 基因表达热图
       - PCA主成分分析图

使用方式：
    from visualization import PlotGenerator

    plotter = PlotGenerator()
    plotter.plot_volcano(deg_results, output_file="volcano.png")
    plotter.plot_heatmap(expression_data, output_file="heatmap.png")
"""

from .plots import PlotGenerator

__all__ = ["PlotGenerator"]
