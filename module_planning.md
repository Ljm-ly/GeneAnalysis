# 基因表达调控分析与预测平台 - 模块规划

## 📂 项目结构

```
GeneAnalysis/
├── main.py                    # 主程序入口 
│   ├── 加载配置
│   ├── 读取FASTA序列
│   ├── 读取表达数据
│   ├── 序列基础统计
│   ├── 差异表达分析
│   ├── 生成可视化图表
│   └── 机器学习分类
│
├── config.py                  # 配置文件 
│   ├── AnalysisConfig类（dataclass）
│   ├── validate() - 配置验证
│   ├── save_to_file() - 保存配置
│   └── load_from_file() - 加载配置
│
├── data/                      # 数据目录
│   ├── sample.fasta          # 示例FASTA序列文件
│   ├── expression.csv         # 基因表达矩阵
│   └── gene_list.txt          # 基因列表
│
├── results/                   # 输出结果目录
│   ├── deg_results.csv        # 差异表达结果
│   ├── deg_results_with_classification.csv  # 分类结果
│   ├── gc_distribution.png    # GC含量分布图
│   ├── volcano_plot.png       # 火山图
│   ├── expression_heatmap.png # 表达热图
│   └── pca_plot.png          # PCA图
│
├── data_processing/           # 数据处理模块 
│   ├── __init__.py
│   ├── fasta_reader.py       # FASTA文件读取
│   │   ├── FASTAReader类
│   │   ├── read_all() - 读取所有序列
│   │   ├── read_by_id() - 按ID查找序列
│   │   └── get_statistics() - 获取统计信息
│   └── data_cleaner.py       # 数据清洗
│       ├── DataCleaner类
│       ├── remove_duplicates() - 去除重复
│       ├── fill_missing_values() - 填补缺失值
│       ├── normalize_data() - 数据标准化
│       └── filter_outliers() - 异常值过滤
│
├── sequence_analysis/         # 序列分析模块 
│   ├── __init__.py
│   └── basic_stats.py         # 基础统计分析
│       ├── SequenceStats类
│       ├── calculate_gc_content() - GC含量计算
│       ├── calculate_nucleotide_frequencies() - 核苷酸频率
│       ├── calculate_gc_skew() - GC偏斜分析
│       └── get_summary_statistics() - 汇总统计
│
├── expression_analysis/       # 表达分析模块 
│   ├── __init__.py
│   └── differential.py        # 差异表达分析
│       ├── DiffExpAnalyzer类
│       ├── analyze() - 执行差异分析
│       ├── get_significant_genes() - 获取显著基因
│       └── export_results() - 导出结果
│
├── machine_learning/          # 机器学习模块 
│   ├── __init__.py
│   └── classifier.py         # 基因分类器
│       ├── GeneClassifier类
│       ├── prepare_data() - 准备训练数据
│       ├── train() - 训练模型
│       ├── predict() - 预测
│       └── predict_proba() - 预测概率
│
├── visualization/             # 可视化模块 
│   ├── __init__.py
│   └── plots.py              # 图表生成器
│       ├── PlotGenerator类
│       ├── plot_gc_distribution() - GC含量分布图
│       ├── plot_volcano() - 火山图
│       ├── plot_heatmap() - 热图
│       └── plot_pca() - PCA图
│
├── utils/                    # 工具函数 
│   ├── __init__.py
│   └── helpers.py            # 通用工具
│       ├── ensure_directory() - 确保目录存在
│       ├── calculate_file_hash() - 文件哈希
│       ├── format_timestamp() - 时间戳格式化
│       ├── validate_file_extension() - 验证文件扩展名
│       ├── save_json() - 保存JSON
│       ├── load_json() - 加载JSON
│       └── chunk_list() - 列表分块
│
└── tests/                    # 测试模块 
    ├── __init__.py
    └── test_data.py          # 数据处理测试
        ├── TestFASTAReader - FASTA读取器测试
        └── TestSequenceStats - 序列统计测试
```

---

## 📊 模块功能说明

### 1. 主程序 (main.py)
作为整个分析流程的入口，按顺序调用各个模块：
1. 配置加载与验证
2. FASTA序列读取
3. 表达数据读取
4. 序列统计分析（GC含量）
5. 差异表达分析（t检验 + BH校正）
6. 可视化图表生成
7. 机器学习基因分类

### 2. 数据处理模块 (data_processing/)
| 类/函数 | 功能 | 状态 |
|---------|------|------|
| FASTAReader | 解析FASTA格式序列文件 
| DataCleaner | 数据清洗：去重、补缺失、标准化、过滤异常值 

### 3. 序列分析模块 (sequence_analysis/)
| 类/函数 | 功能 | 状态 |
|---------|------|------|
| SequenceStats | GC含量、核苷酸频率、GC偏斜 

### 4. 表达分析模块 (expression_analysis/)
| 类/函数 | 功能 | 状态 |
|---------|------|------|
| DiffExpAnalyzer | 差异表达分析：t检验 + FDR校正 

### 5. 机器学习模块 (machine_learning/)
| 类/函数 | 功能 | 状态 |
|---------|------|------|
| GeneClassifier | 随机森林分类：特征工程、训练、预测 

### 6. 可视化模块 (visualization/)
| 类/函数 | 功能 | 状态 |
|---------|------|------|
| PlotGenerator | 4种图表：GC分布、火山图、热图、PCA 

### 7. 工具模块 (utils/)
| 函数 | 功能 | 状态 |
|------|------|------|
| helpers | 文件操作、JSON、日志、哈希等 

---

## 🚧 待开发模块

### 优先级：高
```
expression_analysis/
├── correlation.py         # 相关性分析（基因间表达相关性）
└── clustering.py         # 聚类分析（层次聚类、K-means）

machine_learning/
├── feature_engineering.py # 特征工程（GO富集、KEGG通路特征）
└── model_evaluation.py    # 模型评估（交叉验证、ROC曲线）

visualization/
├── advanced_plots.py      # 高级图表（箱线图、小提琴图、网络图）
└── interactive_plots.py   # 交互式图表（Plotly）
```

### 优先级：中
```
sequence_analysis/
├── motif_finder.py       # 序列基序发现（正则表达式、频率矩阵）
└── alignment.py          # 序列比对（BLAST、Smith-Waterman）

utils/
├── logger.py             # 日志模块（统一日志配置）
└── error_handler.py      # 错误处理（自定义异常类）
```

### 优先级：低
```
data_processing/
└── expression_reader.py  # 专用表达数据读取器（支持更多格式）

tests/
├── test_analysis.py      # 分析模块测试
└── test_ml.py           # 机器学习测试

visualization/
└── report_generator.py   # 自动化报告生成
```

---

## 📈 技术栈

| 组件 | 用途 | 版本 |
|------|------|------|
| Python | 编程语言 | 3.10+ |
| pandas | 数据处理 | - |
| numpy | 数值计算 | - |
| scipy | 统计分析 | - |
| matplotlib | 基础绘图 | - |
| seaborn | 高级统计图 | - |
| scikit-learn | 机器学习 | - |
| Biopython | 序列分析 | - |

---

## 🎯 下一步计划

1. **扩展分析模块**：添加相关性分析、聚类分析
2. **完善机器学习**：特征工程、模型评估、模型持久化
3. **增强可视化**：交互式图表、报告自动生成
4. **完善测试**：增加集成测试和性能测试
5. **文档完善**：API文档、用户使用手册

---

*最后更新：2026-06-29*
