# -*- coding: utf-8 -*-
"""
序列分析模块 (sequence_analysis)

本模块提供DNA/RNA序列的各种统计分析功能，
从基础的碱基组成到更高级的序列特征分析。

包含的功能：
    1. 基础统计 (basic_stats)
       - GC含量计算
       - 核苷酸频率分析
       - GC偏斜(GC Skew)分析
       - 序列汇总统计

使用方式：
    from sequence_analysis import SequenceStats

    stats = SequenceStats(sequences)
    gc_contents = stats.calculate_gc_content()
    nucleotide_freq = stats.calculate_nucleotide_frequencies()
"""

from .basic_stats import SequenceStats

__all__ = ["SequenceStats"]
