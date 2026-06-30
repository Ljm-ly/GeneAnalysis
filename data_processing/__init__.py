# -*- coding: utf-8 -*-
"""
数据处理模块 (data_processing)

本模块负责原始数据的读取、清洗和预处理工作，
是整个分析流程的第一步，也是后续分析的基础。

包含的功能：
    1. FASTA文件读取 (fasta_reader)
       - 解析FASTA格式的序列文件
       - 支持按ID查找序列
       - 获取序列统计信息

    2. 数据清洗 (data_cleaner)
       - 去除重复数据
       - 填补缺失值（均值/中位数/0/向前填充）
       - 数据标准化（Z-score / Min-Max）
       - 异常值过滤

使用方式：
    from data_processing import FASTAReader, DataCleaner

    # 读取FASTA文件
    reader = FASTAReader("data/sample.fasta")
    sequences = reader.read_all()

    # 清洗数据
    cleaner = DataCleaner()
    clean_data = cleaner.remove_duplicates(raw_data)
"""

# 从子模块导入主要类，方便用户直接从包级别导入
from .fasta_reader import FASTAReader
from .data_cleaner import DataCleaner

# __all__ 定义了 "from data_processing import *" 时会导入什么
# 也可以作为包的"公开API"列表
__all__ = ["FASTAReader", "DataCleaner"]
