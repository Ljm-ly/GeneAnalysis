# -*- coding: utf-8 -*-
"""
表达分析模块 (expression_analysis)

本模块负责基因表达数据的统计分析，
识别在不同实验条件下表达水平显著变化的基因。

包含的功能：
    1. 差异表达分析 (differential)
       - t检验统计分析
       - 倍数变化计算
       - 多重检验校正（BH-FDR方法）
       - 显著基因筛选

使用方式：
    from expression_analysis import DiffExpAnalyzer

    analyzer = DiffExpAnalyzer("data/expression.csv")
    results = analyzer.analyze(
        group1_cols=['control_0', 'control_1', 'control_2'],
        group2_cols=['treatment_0', 'treatment_1', 'treatment_2'],
        p_threshold=0.05,
        log2fc_threshold=1.0
    )
"""

from .differential import DiffExpAnalyzer

__all__ = ["DiffExpAnalyzer"]
