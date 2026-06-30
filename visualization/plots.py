# -*- coding: utf-8 -*-
"""
可视化图表生成模块
提供多种生物信息学常用的数据可视化方法

可视化是数据分析的关键环节：
- 帮助理解数据分布
- 发现异常和模式
- 验证分析结果
- 向非技术人员传达发现

常用图表类型：
- 直方图：展示单个变量的分布
- 火山图：展示差异表达的统计显著性vs变化幅度
- 热图：展示多个基因在多个样本中的表达模式
- PCA图：降维可视化，展示样本间的相似性
"""
import matplotlib.pyplot as plt    # matplotlib绘图库
import seaborn as sns              # seaborn高级绘图库，基于matplotlib
import pandas as pd                # Pandas数据处理库
import numpy as np                 # NumPy数值计算库
from typing import List, Dict, Optional, Tuple  # 类型提示
import logging                     # 日志模块
import os                          # 操作系统模块，用于路径操作

# 设置matplotlib支持中文字体
# 如果不设置，中文会显示为方框
plt.rcParams['font.sans-serif'] = ['SimHei']
# 解决负号显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False


class PlotGenerator:
    """
    图表生成器类
    
    封装各种生物信息学图表的绘制方法。
    使用seaborn简化绘图代码，自动处理美观样式。
    """
    
    def __init__(self, style: str = 'whitegrid'):
        """
        初始化图表生成器
        
        Args:
            style: seaborn图表样式
                - 'whitegrid': 白色背景+网格线（推荐，清晰易读）
                - 'darkgrid': 深色背景+网格线
                - 'white': 纯白背景
                - 'dark': 纯深色背景
                - 'ticks': 带刻度线的白色背景
        """
        # 设置seaborn的绘图样式
        sns.set_style(style)
        
        # 设置字体支持中文（包含备选字体）
        # 如果SimHei不可用，会尝试Microsoft YaHei等
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 设置全局字体大小
        plt.rcParams['font.size'] = 12
        
        # 设置图片分辨率（DPI：每英寸像素数）
        plt.rcParams['figure.dpi'] = 100
        
        # 获取日志记录器
        self.logger = logging.getLogger(__name__)
    
    def plot_gc_distribution(self, gc_contents: List[float],
                             title: str = "GC含量分布图",
                             output_file: Optional[str] = None) -> plt.Figure:
        """
        绘制GC含量分布直方图
        
        GC含量分布图可以反映：
        1. 样本的GC组成特性
        2. 是否存在污染（如外源DNA通常GC不同）
        3. 是否有多个亚群（如混合物种）
        
        直方图参数说明：
        - bins=30：将数据分为30个区间
        - kde=True：叠加核密度估计曲线（平滑的分布曲线）
        
        Args:
            gc_contents: GC含量百分比列表
            title: 图表标题
            output_file: 保存路径（可选）
            
        Returns:
            plt.Figure: matplotlib图形对象
        """
        # 创建图形对象，设置尺寸（宽10英寸，高6英寸）
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 绘制直方图叠加核密度估计
        # bins=30: 将数据分为30个区间，每个区间一个柱子
        # kde=True: 同时绘制核密度估计曲线
        # color='steelblue': 设置颜色
        sns.histplot(gc_contents, bins=30, kde=True, ax=ax, color='steelblue')
        
        # 计算统计量
        mean_val = np.mean(gc_contents)      # 均值
        median_val = np.median(gc_contents)  # 中位数
        
        # 添加均值参考线（红色虚线）
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2,
                   label=f'均值: {mean_val:.1f}%')
        # 添加中位数参考线（绿色虚线）
        ax.axvline(median_val, color='green', linestyle='--', linewidth=2,
                   label=f'中位数: {median_val:.1f}%')
        
        # 设置标签和标题
        ax.set_title(title, fontsize=16, pad=20)  # pad增加标题与图表的间距
        ax.set_xlabel('GC含量 (%)', fontsize=12)
        ax.set_ylabel('序列数量', fontsize=12)
        ax.legend(fontsize=10)  # 显示图例
        
        # 自动调整布局，防止标签被裁剪
        plt.tight_layout()
        
        # 保存图片
        if output_file:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            # dpi=300满足出版要求
            # bbox_inches='tight'确保所有内容都被保存
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            self.logger.info(f"图表已保存: {output_file}")
        
        return fig
    
    def plot_volcano(self, deg_results: pd.DataFrame,
                     p_threshold: float = 0.05,
                     log2fc_threshold: float = 1.0,
                     title: str = "差异表达火山图",
                     output_file: Optional[str] = None) -> plt.Figure:
        """
        绘制火山图（Volcano Plot）
        
        火山图是差异表达分析的标准可视化方式，
        同时展示变化幅度和统计显著性。
        
        图表解读：
        - X轴：log2倍数变化（-4到4）
          左边的点：下调基因
          右边的点：上调基因
          中间的点：无变化
        - Y轴：-log10(校正后P值)
          越往上：越显著
        - 虚线框出的区域：显著差异基因
        
        位置对应关系：
        - 左上角：显著下调基因（下调且统计显著）
        - 右上角：显著上调基因（上调且统计显著）
        - 中间底部：无显著变化的基因
        
        Args:
            deg_results: 差异表达分析结果DataFrame
            p_threshold: P值阈值
            log2fc_threshold: log2倍数变化阈值
            title: 图表标题
            output_file: 保存路径（可选）
            
        Returns:
            plt.Figure: matplotlib图形对象
        """
        # 创建图形对象
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 计算-log10(校正后P值)，用于Y轴
        # 为什么用-log10？
        # - p值越小，-log10(p)越大，在图上位置越高
        # - -log10(0.05) ≈ 1.3，-log10(0.01) ≈ 2，-log10(0.001) ≈ 3
        neg_log10_p = -np.log10(deg_results['corrected_p_value'])
        
        # 根据显著性和表达方向将数据分为三类
        # 使用布尔索引分离数据
        up_genes = deg_results[(deg_results['is_significant']) & 
                               (deg_results['log2_fold_change'] > 0)]   # 显著上调
        down_genes = deg_results[(deg_results['is_significant']) & 
                                 (deg_results['log2_fold_change'] < 0)] # 显著下调
        ns_genes = deg_results[~deg_results['is_significant']]           # 不显著
        
        # 按三层绘制（不显著的先画，避免遮挡重要的点）
        # 第一层：不显著基因（灰色，半透明alpha=0.5）
        ax.scatter(ns_genes['log2_fold_change'], neg_log10_p[~deg_results['is_significant']],
                   c='grey', alpha=0.5, s=20, label=f'不显著 ({len(ns_genes)})')
        # 第二层：显著上调基因（红色，s=30稍大）
        ax.scatter(up_genes['log2_fold_change'], neg_log10_p[(deg_results['is_significant']) & (deg_results['log2_fold_change'] > 0)],
                   c='red', alpha=0.8, s=30, label=f'上调 ({len(up_genes)})')
        # 第三层：显著下调基因（蓝色）
        ax.scatter(down_genes['log2_fold_change'], neg_log10_p[(deg_results['is_significant']) & (deg_results['log2_fold_change'] < 0)],
                   c='blue', alpha=0.8, s=30, label=f'下调 ({len(down_genes)})')
        
        # 添加阈值参考线（灰色虚线）
        # 水平线：显著性阈值
        ax.axhline(-np.log10(p_threshold), color='grey', linestyle='--', alpha=0.5)
        # 垂直线：倍数变化阈值
        ax.axvline(log2fc_threshold, color='grey', linestyle='--', alpha=0.5)
        ax.axvline(-log2fc_threshold, color='grey', linestyle='--', alpha=0.5)
        
        # 设置标签和标题
        ax.set_xlabel('log2(倍数变化)', fontsize=12)
        ax.set_ylabel('-log10(校正后P值)', fontsize=12)
        ax.set_title(title, fontsize=16, pad=20)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            self.logger.info(f"火山图已保存: {output_file}")
        
        return fig
    
    def plot_heatmap(self, data: pd.DataFrame,
                     title: str = "基因表达热图",
                     cmap: str = 'RdBu_r',
                     show_labels: bool = True,
                     figsize: Optional[tuple] = None,
                     output_file: Optional[str] = None) -> plt.Figure:
        """
        绘制基因表达热图
        
        热图是展示基因表达模式的首选图表：
        - 每一行：一个基因
        - 每一列：一个样本
        - 颜色：表达水平
        
        颜色解读：
        - 红色：高表达（相对于该基因的平均水平）
        - 蓝色：低表达
        - 白色：该基因在样本中的平均表达水平
        
        Z-score标准化：
        - 每个基因单独标准化（减均值，除标准差）
        - 使不同基因的表达量在同一尺度上可比
        - 关注的是表达"模式"而非绝对水平
        
        Args:
            data: 基因表达矩阵（行=基因，列=样本）
            title: 图表标题
            cmap: 颜色映射方案
                - 'RdBu_r': 红-白-蓝（推荐，正负变化）
                - 'coolwarm': 冷暖色
                - 'viridis': 黄-绿-蓝（色盲友好）
            show_labels: 是否显示基因和样本标签
            figsize: 图表尺寸（宽度, 高度），单位英寸
                     不指定则自动计算
            output_file: 保存路径（可选）
            
        Returns:
            plt.Figure: matplotlib图形对象
        """
        # 对每个基因进行Z-score标准化
        # Z-score = (x - μ) / σ，使每个基因的均值为0，标准差为1
        def zscore_row(x):
            std = x.std(ddof=0)  # 使用总体标准差
            if std == 0:
                return pd.Series(0, index=x.index)  # 避免除以零
            return (x - x.mean()) / std
        normalized = data.apply(zscore_row, axis=1)
        
        # 确定图形尺寸
        # 如果指定了figsize就用指定的，否则自动计算
        n_genes, n_samples = data.shape
        if figsize is not None:
            fig_width, fig_height = figsize
        else:
            # 自动计算：根据基因和样本数量
            fig_width = max(8, n_samples * 0.5)
            fig_height = max(6, n_genes * 0.3)
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # 绘制热图
        sns.heatmap(normalized,
                    cmap=cmap,          # 颜色映射
                    center=0,           # 0值显示为白色（中间色）
                    annot=False,        # 不显示数值（避免拥挤）
                    linewidths=0.5,     # 单元格之间的线宽
                    ax=ax,
                    cbar_kws={'label': 'Z-score'})  # 颜色条标签
        
        # 设置标题和轴标签
        ax.set_title(title, fontsize=16, pad=20)
        ax.set_xlabel('样本', fontsize=12)
        ax.set_ylabel('基因', fontsize=12)
        
        # 隐藏行标签（基因名）
        # 当基因太多时，标签会重叠看不清
        # 列标签（样本名）始终显示，因为样本数通常不多
        if not show_labels:
            ax.set_yticklabels([])  # 只隐藏行标签
            ax.set_ylabel('')       # 隐藏Y轴标题
        
        plt.tight_layout()
        
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            self.logger.info(f"热图已保存: {output_file}")
        
        return fig
    
    def plot_pca(self, expression_data: pd.DataFrame,
                 labels: Optional[List[str]] = None,
                 title: str = "PCA主成分分析图",
                 output_file: Optional[str] = None) -> plt.Figure:
        """
        绘制PCA主成分分析图
        
        PCA（Principal Component Analysis，主成分分析）是一种降维方法：
        - 将高维数据（如20000个基因）降到2-3维
        - 同时尽可能保留原始数据的信息
        - 揭示数据的内在结构和模式
        
        PCA结果解读：
        - PC1（第一主成分）：数据最大变异的方向，通常解释最多方差
        - PC2（第二主成分）：与PC1正交（垂直），解释次多方差
        - 每个点代表一个样本
        - 相似的样本会聚在一起
        
        应用场景：
        - 检查批次效应（样本是否按批次聚类）
        - 发现离群样本（远离其他点的样本）
        - 验证实验分组是否合理（对照组和处理组应该分开）
        - 数据质量检查
        
        原理简述：
        1. 找到一条直线，使得所有点到这个直线的距离平方和最小
        2. 这条直线就是PC1
        3. 再找一条与PC1垂直的直线作为PC2
        4. 重复直到所有主成分
        
        Args:
            expression_data: 表达数据（行=样本，列=基因）
            labels: 样本标签（如分组信息），用于着色区分
            title: 图表标题
            output_file: 保存路径（可选）
            
        Returns:
            plt.Figure: matplotlib图形对象
        """
        # 从scikit-learn导入PCA
        from sklearn.decomposition import PCA
        
        # 创建PCA对象，指定提取2个主成分
        pca = PCA(n_components=2)
        
        # 执行PCA降维
        # 输入：样本数 × 基因数
        # 输出：样本数 × 2（PC1和PC2）
        pca_result = pca.fit_transform(expression_data)
        
        # 创建包含PCA结果的DataFrame
        pca_df = pd.DataFrame({
            'PC1': pca_result[:, 0],  # 第一主成分
            'PC2': pca_result[:, 1],  # 第二主成分
        })
        
        # 如果有标签，添加到DataFrame
        if labels:
            pca_df['label'] = labels
        
        # 获取每个主成分的解释方差比例
        # 比例越大，说明该主成分捕获的信息越多
        explained_var = pca.explained_variance_ratio_ * 100
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 绘制散点图
        if labels:
            # 有标签时，根据标签着色
            sns.scatterplot(data=pca_df, x='PC1', y='PC2',
                           hue='label', ax=ax, s=100, palette='Set2')
        else:
            # 无标签时统一颜色
            ax.scatter(pca_df['PC1'], pca_df['PC2'], s=100, alpha=0.7)
        
        # 设置轴标签，显示主成分的解释方差比例
        ax.set_xlabel(f'PC1 ({explained_var[0]:.1f}% 方差)', fontsize=12)
        ax.set_ylabel(f'PC2 ({explained_var[1]:.1f}% 方差)', fontsize=12)
        ax.set_title(title, fontsize=16, pad=20)
        
        # 如果有标签，显示图例
        if labels:
            ax.legend(fontsize=10, title='组别')
        
        plt.tight_layout()
        
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            self.logger.info(f"PCA图已保存: {output_file}")
        
        return fig
