# -*- coding: utf-8 -*-
"""
机器学习模块 (machine_learning)

本模块提供基于机器学习算法的基因分析功能，
利用统计学习方法从表达数据中发现模式并进行预测。

包含的功能：
    1. 基因分类器 (classifier)
       - 随机森林分类算法
       - 数据标准化与预处理
       - 模型训练与评估
       - 特征重要性分析
       - 新样本预测

使用方式：
    from machine_learning import GeneClassifier

    clf = GeneClassifier(model_type='random_forest')
    results = clf.train(X, y, test_size=0.2)
    predictions = clf.predict(X_new)
"""

from .classifier import GeneClassifier

__all__ = ["GeneClassifier"]
