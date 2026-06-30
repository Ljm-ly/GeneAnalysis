# -*- coding: utf-8 -*-
"""
数据清洗模块
负责对原始数据进行预处理，包括去重、填补缺失值、标准化等操作

数据清洗是生物信息学分析的第一步，确保数据质量直接影响后续分析的可靠性。
原始数据中常存在：重复测量、缺失值、异常值、量纲不一致等问题。
"""

import pandas as pd          # 数据分析库，提供DataFrame数据结构
import numpy as np           # 数值计算库，用于高效数学运算
from typing import List, Optional  # 类型提示，提高代码可读性
import logging               # 日志模块，记录处理过程


class DataCleaner:
    """
    数据清洗器类
    
    提供多种数据清洗和预处理方法：
    - 去除重复样本/基因
    - 填补缺失值（基因表达数据中常见）
    - 数据标准化（使不同实验的数据可比较）
    - 异常值检测与处理
    """
    
    def __init__(self):
        """初始化清洗器，配置日志记录器"""
        self.logger = logging.getLogger(__name__)
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        去除数据框中的重复行
        
        在RNA-seq数据中，同一个基因可能被测序多次（比对到多个位置），
        或者同一个样本被上机两次。去重可以消除这些人为因素。
        
        Args:
            df: 输入数据框，行代表基因，列代表样本
            
        Returns:
            pd.DataFrame: 去重后的数据框
        """
        # 记录原始数据量（基因数量）
        original_len = len(df)
        
        # drop_duplicates去除完全相同的重复行
        # keep='first': 保留第一次出现的行，删除后续重复
        df_clean = df.drop_duplicates(keep='first')
        
        # 计算被去除的重复行数量
        removed = original_len - len(df_clean)
        self.logger.info(f"去除了 {removed} 行重复数据")
        return df_clean
    
    def fill_missing_values(self, df: pd.DataFrame, 
                           strategy: str = 'mean') -> pd.DataFrame:
        """
        填补数据框中的缺失值
        
        基因表达数据中缺失值很常见，原因包括：
        - 表达量低于检测限
        - 比对失败
        - 测序质量问题
        
        Args:
            df: 输入数据框
            strategy: 填补策略
                - 'mean': 用该基因在所有样本中的均值填充（最常用）
                - 'median': 用中位数填充（对异常值更鲁棒）
                - 'zero': 用0填充（假设基因未表达）
                - 'ffill': 向前填充（用前一个样本的值）
                
        Returns:
            pd.DataFrame: 填补缺失值后的数据框
        """
        # 创建副本，避免修改原始数据
        df_filled = df.copy()
        
        if strategy == 'mean':
            # 对每一列（每个样本），用该列的均值填充缺失值
            # 注意：这里是对列操作（axis=0是默认的）
            for col in df_filled.columns:
                # 检查该列是否有缺失值
                if df_filled[col].isnull().any():
                    mean_val = df_filled[col].mean()
                    # inplace=True直接修改DataFrame，不创建新副本
                    df_filled[col].fillna(mean_val, inplace=True)
                    self.logger.debug(f"列 {col} 用均值 {mean_val:.2f} 填充")
                    
        elif strategy == 'median':
            # 用中位数填充，对偏态分布的数据更合适
            df_filled = df_filled.fillna(df_filled.median())
            
        elif strategy == 'zero':
            # 用0填充，适用于假设缺失意味着不表达的情况
            df_filled = df_filled.fillna(0)
            
        elif strategy == 'ffill':
            # 向前填充：用前一个有效值填充
            # 适用于时间序列或有序样本的数据
            df_filled = df_filled.fillna(method='ffill')
        
        # 记录处理结果
        missing_before = df.isnull().sum().sum()
        missing_after = df_filled.isnull().sum().sum()
        self.logger.info(f"缺失值从 {missing_before} 个减少到 {missing_after} 个")
        
        return df_filled
    
    def normalize_data(self, df: pd.DataFrame, 
                      method: str = 'zscore') -> pd.DataFrame:
        """
        标准化数据，使不同量纲/范围的数据可比较
        
        不同基因的表达量范围差异巨大：
        - housekeeping基因（GAPDH, ACTB）表达量很高
        - 某些转录因子表达量很低
        
        标准化可以消除这种量纲差异，让所有基因在同一个尺度上比较。
        
        Args:
            df: 输入数据框（仅数值列）
            method: 标准化方法
                - 'zscore': Z-score标准化，结果均值为0，标准差为1
                  公式：(x - μ) / σ
                  适用于：假设数据服从正态分布的分析
                - 'minmax': Min-Max归一化，结果缩放到[0,1]区间
                  公式：(x - min) / (max - min)
                  适用于：神经网络、对数值范围敏感的方法
                  
        Returns:
            pd.DataFrame: 标准化后的数据
        """
        # 创建副本
        df_norm = df.copy()
        
        if method == 'zscore':
            # Z-score标准化
            # 处理每个基因（每列）：减去均值，除以标准差
            # 结果：大多数值在[-3, 3]范围内，均值为0
            for col in df_norm.columns:
                mean = df_norm[col].mean()      # 计算该基因的表达均值
                std = df_norm[col].std()        # 计算标准差（反映表达量的变异程度）
                if std > 0:  # 标准差为0说明所有值相同，无需标准化
                    df_norm[col] = (df_norm[col] - mean) / std
                    
        elif method == 'minmax':
            # Min-Max归一化
            # 将数据线性映射到[0,1]区间
            # 公式：(x - min) / (max - min)
            for col in df_norm.columns:
                min_val = df_norm[col].min()    # 该基因的最小表达量
                max_val = df_norm[col].max()    # 该基因的最大表达量
                if max_val > min_val:  # 避免除以零
                    df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
        
        self.logger.info(f"数据标准化完成，方法: {method}")
        return df_norm
    
    def filter_outliers(self, df: pd.DataFrame, 
                       threshold: float = 3.0) -> pd.DataFrame:
        """
        过滤异常值（基于Z-score方法）
        
        异常值可能来源：
        - 测序错误
        - 样本污染
        - 技术故障（如Flow Cell问题）
        
        Z-score方法：|Z| > threshold 的点视为异常
        通常threshold=3对应3个标准差，覆盖99.7%的正态分布数据
        
        Args:
            df: 输入数据框
            threshold: Z-score阈值，默认3.0
            
        Returns:
            pd.DataFrame: 异常值被替换为中位数后的数据
        """
        # 创建副本
        df_filtered = df.copy()
        
        # 逐列（逐个基因）处理
        for col in df_filtered.columns:
            # 计算该列的均值和标准差
            mean = df_filtered[col].mean()
            std = df_filtered[col].std()
            
            if std == 0:
                continue  # 标准差为0，所有值相同，无需处理
            
            # 计算每个点的Z-score
            # Z-score表示该点距离均值有多少个标准差
            z_scores = (df_filtered[col] - mean) / std
            
            # 找出异常值的位置（|Z-score| > threshold）
            outlier_mask = abs(z_scores) > threshold
            outlier_count = outlier_mask.sum()
            
            if outlier_count > 0:
                # 用中位数替换异常值
                # 中位数对异常值不敏感，是鲁棒的统计量
                median_val = df_filtered[col].median()
                df_filtered.loc[outlier_mask, col] = median_val
                self.logger.debug(f"列 {col} 替换了 {outlier_count} 个异常值")
        
        return df_filtered
