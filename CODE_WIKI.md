# 🧬 基因表达调控分析与预测平台 - Code Wiki

## 目录

1. [项目概述](#项目概述)
2. [项目架构](#项目架构)
3. [核心模块详解](#核心模块详解)
4. [关键类与函数说明](#关键类与函数说明)
5. [依赖关系图](#依赖关系图)
6. [数据流程](#数据流程)
7. [技术栈](#技术栈)
8. [项目运行方式](#项目运行方式)
9. [配置管理](#配置管理)
10. [示例数据说明](#示例数据说明)
11. [开发指南](#开发指南)

---

## 项目概述

### 项目定位

这是一个**功能完整的基因表达数据分析平台**，集成了生物信息学分析的核心功能，为研究人员提供从数据读取到结果可视化的完整解决方案。

### 核心功能

| 功能模块 | 描述 | 应用场景 |
|---------|------|---------|
| 🔬 序列分析 | GC含量计算、核苷酸频率统计、序列长度分布 | 基因组特征分析、物种鉴定 |
| 📊 差异表达分析 | t检验统计、BH-FDR多重校正、上调/下调基因识别 | RNA-seq数据分析、疾病研究 |
| 📈 可视化图表 | 火山图、表达热图、PCA主成分分析、GC含量分布图 | 结果展示、报告生成 |
| 🤖 机器学习 | 随机森林分类、特征重要性分析、模型性能评估 | 基因分类预测、标志物发现 |

### 项目特色

- **双入口设计**：同时支持命令行（main.py）和Web界面（app.py）两种使用方式
- **模块化架构**：各功能模块独立封装，易于维护和扩展
- **完整注释**：代码包含详细的教学级注释，适合学习和教学
- **中文字体支持**：内置字体文件，图表完美支持中文显示
- **云端部署**：支持一键部署到Streamlit Community Cloud

---

## 项目架构

### 目录结构

```
GeneAnalysis/
├── app.py                      # Web应用主入口（Streamlit）
├── main.py                     # 命令行主入口（分析流程）
├── config.py                   # 配置管理类
├── requirements.txt            # Python依赖列表
├── fonts/
│   └── simhei.ttf              # 中文字体文件（黑体）
│
├── data_processing/            # 【模块1】数据处理
│   ├── __init__.py             # 模块初始化，导出公共API
│   ├── fasta_reader.py         # FASTA文件读取器
│   └── data_cleaner.py         # 数据清洗工具
│
├── sequence_analysis/          # 【模块2】序列分析
│   ├── __init__.py
│   └── basic_stats.py          # 序列统计计算（GC含量等）
│
├── expression_analysis/        # 【模块3】表达分析
│   ├── __init__.py
│   └ differential.py           # 差异表达分析器
│
├── visualization/              # 【模块4】可视化
│   ├── __init__.py
│   └ plots.py                  # 图表生成器
│
├── machine_learning/           # 【模块5】机器学习
│   ├── __init__.py
│   └ classifier.py             # 基因分类器
│
├── utils/                      # 【模块6】工具函数
│   ├── __init__.py
│   └ helpers.py                # 通用辅助函数
│
├── tests/                      # 测试模块
│   ├── __init__.py
│   └ test_data.py              # 数据测试
│
├── data/                       # 数据目录
│   ├── simulated_genes.fasta       # 模拟基因序列（示例）
│   ├── simulated_expression.csv    # 模拟表达矩阵（示例）
│   ├── fasta_files/                # 测试FASTA文件
│   │   ├── NM_000546_TP53_test.fasta
│   │   └ NM_001354_GATA1_test.fasta
│   └ expression.csv
│   └ sample.fasta
│   ├── gene_list.txt               # 基因列表
│
├── .streamlit/                 # Streamlit配置
│   └ config.toml               # 应用配置文件
│
├── .devcontainer/              # VS Code开发容器配置
│   └ devcontainer.json
│
├── README.md                   # 项目说明文档
├── CODE_WIKI.md                # 本文档（代码Wiki）
├── module_planning.md          # 模块规划文档
├── .gitignore                  # Git忽略规则
├── start_app.bat               # Windows启动脚本
├── start_app.py                # 启动辅助脚本
├── generate_simulated_data.py  # 模拟数据生成脚本
├── GeneAnalysis.pyproj         # 项目配置文件
├── config.ini                  # INI格式配置
└── config.toml                 # TOML格式配置
```

### 架构设计原则

#### 1. 模块化设计

每个功能模块独立封装，遵循"单一职责原则"：

- **data_processing**: 只负责数据读取和清洗
- **sequence_analysis**: 只负责序列特征计算
- **expression_analysis**: 只负责差异统计分析
- **visualization**: 只负责图表绘制
- **machine_learning**: 只负责模型训练和预测
- **utils**: 提供跨模块的通用工具

#### 2. 分层架构

```
┌─────────────────────────────────────┐
│  应用层 (Application Layer)          │
│  - app.py (Web UI)                   │
│  - main.py (CLI)                     │
└─────────────────────────────────────┘
              ↓ 调用
┌─────────────────────────────────────┐
│  业务逻辑层 (Business Logic Layer)   │
│  - 分析流程控制                      │
│  - 数据流转                          │
└─────────────────────────────────────┘
              ↓ 调用
┌─────────────────────────────────────┐
│  功能模块层 (Module Layer)           │
│  - data_processing                   │
│  - sequence_analysis                 │
│  - expression_analysis               │
│  - visualization                     │
│  - machine_learning                  │
└─────────────────────────────────────┘
              ↓ 调用
┌─────────────────────────────────────┐
│  基础工具层 (Utility Layer)          │
│  - utils/helpers                     │
│  - config                            │
└─────────────────────────────────────┘
```

#### 3. 配置集中化

所有参数集中在 `config.py` 的 `AnalysisConfig` 类中管理，便于：
- 参数调整
- 实验记录
- 结果复现

---

## 核心模块详解

### 模块1: data_processing（数据处理）

#### 职责

负责原始数据的读取和预处理，是整个分析流程的第一步。

#### 核心组件

##### 1. FASTAReader（FASTA文件读取器）

**文件**: [data_processing/fasta_reader.py](data_processing/fasta_reader.py)

**功能**:
- 解析FASTA格式序列文件
- 支持多行序列
- 提供按ID查找功能
- 获取序列统计信息

**关键技术**:
- 使用Biopython的SeqIO模块解析FASTA格式
- 内存高效的迭代器模式读取
- 自动处理标题行和序列行

**示例代码**:
```python
from data_processing.fasta_reader import FASTAReader

# 读取FASTA文件
reader = FASTAReader("data/sample.fasta")
sequences = reader.read_all()

# 查找特定基因
tp53 = reader.read_by_id("gene_001")

# 获取统计信息
stats = reader.get_statistics()
print(f"平均长度: {stats['avg_length']} bp")
```

##### 2. DataCleaner（数据清洗器）

**文件**: [data_processing/data_cleaner.py](data_processing/data_cleaner.py)

**功能**:
- 去除重复数据
- 填补缺失值（均值/中位数/0/向前填充）
- 数据标准化（Z-score / Min-Max）
- 异常值过滤

**清洗策略**:
| 方法 | 适用场景 | 说明 |
|------|---------|------|
| `remove_duplicates()` | 去除重复基因 | 基于ID或序列内容 |
| `fill_missing()` | 处理缺失值 | 多种填充策略可选 |
| `normalize()` | 数据标准化 | Z-score或Min-Max |
| `filter_outliers()` | 去除异常值 | IQR方法或Z-score方法 |

---

### 模块2: sequence_analysis（序列分析）

#### 职责

计算DNA序列的各种统计特征，反映序列的化学和生物学特性。

#### 核心组件

##### SequenceStats（序列统计类）

**文件**: [sequence_analysis/basic_stats.py](sequence_analysis/basic_stats.py)

**主要方法**:

| 方法 | 功能 | 返回值 | 应用场景 |
|------|------|--------|---------|
| `calculate_gc_content()` | 计算GC含量百分比 | List[float] | DNA稳定性分析、物种鉴定 |
| `calculate_nucleotide_frequencies()` | 统计A/T/G/C/N频率 | Dict[str, float] | 碱基组成分析 |
| `calculate_gc_skew()` | 计算GC偏斜值 | List[List[float]] | 复制起始位点预测 |
| `get_summary_statistics()` | 获取汇总统计 | Dict | 快速了解数据特征 |

**GC含量计算原理**:

```
GC含量 = (G数量 + C数量) / 总碱基数 × 100%

意义：
- GC碱基对有3个氢键，AT只有2个 → GC含量高的DNA更稳定
- 不同物种GC含量特征不同 → 可用于物种鉴定
- GC含量高的区域基因密度通常更高
```

**示例代码**:
```python
from sequence_analysis.basic_stats import SequenceStats

stats = SequenceStats(sequences)

# 计算GC含量
gc_contents = stats.calculate_gc_content()
print(f"平均GC含量: {sum(gc_contents)/len(gc_contents):.2f}%")

# 计算核苷酸频率
freq = stats.calculate_nucleotide_frequencies()
print(f"A频率: {freq['A']:.2%}")

# 计算GC偏斜（寻找复制起始位点）
skews = stats.calculate_gc_skew(window_size=100)
```

---

### 模块3: expression_analysis（表达分析）

#### 职责

识别在不同实验条件下表达水平显著差异的基因（差异表达分析）。

#### 核心组件

##### DiffExpAnalyzer（差异表达分析器）

**文件**: [expression_analysis/differential.py](expression_analysis/differential.py)

**分析流程**:

```
┌─────────────────┐
│ 1. 数据过滤     │ 去除低表达基因（减少假阳性）
└─────────────────┘
         ↓
┌─────────────────┐
│ 2. t检验        │ 对每个基因进行两组均值差异检验
└─────────────────┘
         ↓
┌─────────────────┐
│ 3. 计算log2FC   │ 计算倍数变化（变化幅度）
└─────────────────┘
         ↓
┌─────────────────┐
│ 4. 多重检验校正 │ BH-FDR校正（控制假发现率）
└─────────────────┘
         ↓
┌─────────────────┐
│ 5. 标记显著性   │ 同时满足统计显著和生物学显著
└─────────────────┘
```

**关键概念**:

| 概念 | 说明 | 公式/阈值 |
|------|------|----------|
| **P值** | 统计显著性 | p < 0.05通常认为显著 |
| **log2FC** | 倍数变化（log2尺度） | log2(处理组均值/对照组均值) |
| **校正P值** | 多重检验后的P值 | FDR校正控制假阳性率 |
| **显著性判断** | 双重标准 | 校正p值<阈值 且 \|log2FC\|>阈值 |

**多重检验校正必要性**:

```
为什么需要校正？
- 同时检验10000个基因，即使全部无差异，p<0.05的也会有约500个！
- BH-FDR校正控制期望假发现率 < 5%

校正方法：
- Benjamini-Hochberg (BH-FDR): 常用，平衡严格度和灵敏度
- Bonferroni: 最保守，可能漏掉一些真实差异基因
```

**示例代码**:
```python
from expression_analysis.differential import DiffExpAnalyzer

analyzer = DiffExpAnalyzer("data/expression.csv")

# 执行差异分析
deg_results = analyzer.analyze(
    group1_cols=['control_0', 'control_1', 'control_2'],
    group2_cols=['treatment_0', 'treatment_1', 'treatment_2'],
    p_threshold=0.05,
    log2fc_threshold=1.0
)

# 获取显著基因
significant_genes = analyzer.get_significant_genes()
up_genes = analyzer.get_significant_genes(direction='up')
down_genes = analyzer.get_significant_genes(direction='down')

# 导出结果
analyzer.export_results("results/deg_results.csv")
```

---

### 模块4: visualization（可视化）

#### 职责

将分析结果转换为直观的图表，便于理解和交流。

#### 核心组件

##### PlotGenerator（图表生成器）

**文件**: [visualization/plots.py](visualization/plots.py)

**支持的图表类型**:

| 图表类型 | 方法 | 功能说明 | 解读要点 |
|---------|------|---------|---------|
| GC含量分布图 | `plot_gc_distribution()` | 展示序列GC含量分布 | 均值线、中位数线参考 |
| 火山图 | `plot_volcano()` | 差异表达可视化 | 左上=下调，右上=上调 |
| 表达热图 | `plot_heatmap()` | 基因表达模式 | 红=高表达，蓝=低表达 |
| PCA图 | `plot_pca()` | 样本相似性分析 | 相似样本聚集在一起 |

**火山图详解**:

```
火山图是差异表达分析的标准可视化方式：

Y轴: -log10(校正后P值)
     越往上 → 越显著
     -log10(0.05) ≈ 1.3
     -log10(0.01) ≈ 2
     -log10(0.001) ≈ 3

X轴: log2倍数变化
     左边 → 下调基因
     右边 → 上调基因
     中间 → 无变化

四个区域：
左上角: 显著下调基因（红色，统计显著且下调）
右上角: 显著上调基因（蓝色，统计显著且上调）
中间底部: 无显著变化（灰色）
```

**热图标准化**:

```
为什么需要Z-score标准化？
- 不同基因的绝对表达量差异很大（几千到几十万）
- 标准化后关注"表达模式"而非绝对值
- Z-score = (x - μ) / σ
- 使每个基因的均值为0，标准差为1
```

**示例代码**:
```python
from visualization.plots import PlotGenerator

plotter = PlotGenerator()

# 绘制GC含量分布图
fig1 = plotter.plot_gc_distribution(
    gc_contents,
    title="序列GC含量分布",
    output_file="results/gc_distribution.png"
)

# 绘制火山图
fig2 = plotter.plot_volcano(
    deg_results,
    p_threshold=0.05,
    log2fc_threshold=1.0,
    output_file="results/volcano_plot.png"
)

# 绘制热图
fig3 = plotter.plot_heatmap(
    expression_data,
    title="基因表达热图",
    show_labels=True,
    output_file="results/heatmap.png"
)

# 绘制PCA图
fig4 = plotter.plot_pca(
    expression_data.T,  # 注意：需要转置，样本为行
    title="样本PCA分析",
    output_file="results/pca_plot.png"
)
```

---

### 模块5: machine_learning（机器学习）

#### 职责

使用机器学习算法对基因进行分类预测，发现更复杂的模式。

#### 核心组件

##### GeneClassifier（基因分类器）

**文件**: [machine_learning/classifier.py](machine_learning/classifier.py)

**算法选择**: 随机森林（Random Forest）

**为什么选择随机森林**:

| 优点 | 说明 |
|------|------|
| 抗过拟合 | 多棵树投票，避免单棵树的错误 |
| 无需复杂调参 | 默认参数通常表现良好 |
| 处理高维数据 | 很多特征也不怕 |
| 特征重要性 | 能给出哪些特征最关键 |
| 对异常值不敏感 | 随机采样减少异常值影响 |

**训练流程**:

```
┌──────────────────┐
│ 1. 数据准备      │ 选择特征、处理缺失值、生成标签
└──────────────────┘
          ↓
┌──────────────────┐
│ 2. 数据标准化    │ StandardScaler（均值为0，标准差为1）
└──────────────────┘
          ↓
┌──────────────────┐
│ 3. 数据分割      │ 训练集（80%）+ 测试集（20%）
└──────────────────┘
          ↓
┌──────────────────┐
│ 4. 模型训练      │ RandomForestClassifier.fit()
└──────────────────┘
          ↓
┌──────────────────┐
│ 5. 模型评估      │ 准确率、精确率、召回率、F1分数
└──────────────────┘
          ↓
┌──────────────────┐
│ 6. 特征重要性    │ 哪些特征对分类最关键
└──────────────────┘
```

**评估指标**:

| 指标 | 公式 | 说明 |
|------|------|------|
| **准确率** | (TP+TN) / 总数 | 整体正确率 |
| **精确率** | TP / (TP+FP) | 预测为正中真正是正的比例 |
| **召回率** | TP / (TP+FN) | 真正的正例中被找出的比例 |
| **F1分数** | 2×P×R / (P+R) | 精确率和召回率的调和平均 |

**示例代码**:
```python
from machine_learning.classifier import GeneClassifier

# 创建分类器
clf = GeneClassifier(
    model_type='random_forest',
    random_state=42,
    n_estimators=100
)

# 准备数据
X, y = clf.prepare_data(deg_results)

# 训练模型
results = clf.train(X, y, test_size=0.2)

# 查看评估指标
print(f"准确率: {results['accuracy']:.4f}")
print(f"精确率: {results['precision']:.4f}")
print(f"召回率: {results['recall']:.4f}")
print(f"F1分数: {results['f1_score']:.4f}")

# 查看特征重要性
for feat, imp in results['feature_importance'].items():
    print(f"{feat}: {imp:.4f}")

# 预测新基因
predictions = clf.predict(X_new)
probabilities = clf.predict_proba(X_new)
```

---

### 模块6: utils（工具函数）

#### 职责

提供跨模块的通用工具函数，避免代码重复。

#### 核心函数

**文件**: [utils/helpers.py](utils/helpers.py)

| 函数 | 功能 | 应用场景 |
|------|------|---------|
| `ensure_directory()` | 确保目录存在 | 保存结果前创建目录 |
| `calculate_file_hash()` | 计算文件哈希值 | 数据完整性校验 |
| `format_timestamp()` | 格式化时间戳 | 日志记录、结果命名 |
| `validate_file_extension()` | 验证文件扩展名 | 输入验证 |
| `save_json()` / `load_json()` | JSON文件读写 | 配置保存、结果序列化 |
| `chunk_list()` | 列表分块 | 大数据分批处理 |

**示例代码**:
```python
from utils.helpers import ensure_directory, calculate_file_hash, save_json

# 创建目录
output_dir = ensure_directory("results/plots")

# 校验数据完整性
hash_value = calculate_file_hash("data/sample.fasta", algorithm='sha256')
print(f"文件哈希: {hash_value}")

# 保存分析结果元数据
metadata = {
    'analysis_date': '2024-01-01',
    'p_threshold': 0.05,
    'n_significant_genes': 150
}
save_json(metadata, "results/metadata.json")
```

---

## 关键类与函数说明

### 核心类总览

| 类名 | 所在模块 | 主要职责 | 关键方法 |
|------|---------|---------|---------|
| `AnalysisConfig` | config.py | 配置管理 | `validate()`, `save_to_file()`, `load_from_file()` |
| `FASTAReader` | data_processing.fasta_reader.py | FASTA文件读取 | `read_all()`, `read_by_id()`, `get_statistics()` |
| `SequenceStats` | sequence_analysis.basic_stats.py | 序列统计 | `calculate_gc_content()`, `calculate_nucleotide_frequencies()` |
| `DiffExpAnalyzer` | expression_analysis.differential.py | 差异分析 | `analyze()`, `get_significant_genes()`, `export_results()` |
| `PlotGenerator` | visualization.plots.py | 图表生成 | `plot_gc_distribution()`, `plot_volcano()`, `plot_heatmap()`, `plot_pca()` |
| `GeneClassifier` | machine_learning.classifier.py | 机器学习 | `prepare_data()`, `train()`, `predict()` |

### AnalysisConfig（配置类）

**位置**: [config.py](config.py)

**关键属性**:

```python
@dataclass
class AnalysisConfig:
    # 文件路径
    fasta_file: str = "data/simulated_genes.fasta"
    expression_file: str = "data/simulated_expression.csv"
    output_dir: str = "results"
    
    # 分析参数
    gc_window_size: int = 100                # GC分析窗口大小
    p_value_threshold: float = 0.05          # P值阈值
    log2_fold_change_threshold: float = 1.0  # log2FC阈值
    
    # 机器学习参数
    test_size: float = 0.2                   # 测试集比例
    random_state: int = 42                   # 随机种子
    n_estimators: int = 100                  # 随机森林树数
    
    # 可视化参数
    figure_size: tuple = (10, 8)             # 图表尺寸
    color_palette: str = "Set2"              # 调色板
```

**关键方法**:

```python
# 验证配置有效性
if config.validate():
    print("配置有效，可以开始分析")

# 保存配置到文件
config.save_to_file("results/config_backup.txt")

# 从文件加载配置
config = AnalysisConfig.load_from_file("config.txt")

# 转为字典格式
config_dict = config.to_dict()
```

---

## 依赖关系图

### 模块依赖关系

```
┌─────────────┐
│   app.py    │ Web应用入口
│   main.py   │ 命令行入口
└─────┬───────┘
      │
      ├──────────┬──────────┬──────────┬──────────┬─────────
      │          │          │          │          │
      ↓          ↓          ↓          ↓          ↓
┌─────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ config  │ │data_   │ │sequence│ │express │ │visual  │
│         │ │process │ │_analysis│ │_analysis│ │ization │
└────┬────┘ └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘
     │           │          │          │          │
     │           │          │          │          │
     └──────┬────┴──────────┴──────────┴──────────┘
            │
            ↓
     ┌────────────┐
     │   utils    │ 工具函数
     └─────┬──────┘
           │
           ↓
     ┌────────────┐
     │ 外部依赖   │
     │ - pandas   │
     │ - numpy    │
     │ - matplotlib│
     │ - seaborn  │
     │ - biopython│
     │ - sklearn  │
     │ - streamlit│
     └────────────┘
```

### 类依赖关系

```
main.py / app.py
    │
    ├─→ AnalysisConfig
    │       └─→ 提供所有参数配置
    │
    ├─→ FASTAReader
    │       └─→ 读取FASTA序列 → SequenceStats
    │
    ├─→ SequenceStats
    │       └─→ 计算序列统计 → PlotGenerator (GC分布图)
    │
    ├─→ DiffExpAnalyzer
    │       ├─→ 读取表达数据
    │       ├─→ t检验、FDR校正
    │       └─→ 输出差异结果 → GeneClassifier, PlotGenerator
    │
    ├─→ PlotGenerator
    │       ├─→ gc_distribution
    │       ├─→ volcano
    │       ├─→ heatmap
    │       └─→ pca
    │
    └─→ GeneClassifier
            ├─→ prepare_data (使用deg_results)
            ├─→ train
            └─→ predict
```

---

## 数据流程

### 完整分析流程

```
┌────────────────────────────────────────────────────────┐
│ 第一阶段：数据准备                                      │
└────────────────────────────────────────────────────────┘
         │
         ├─→ 加载配置 (config.py)
         │
         ├─→ 读取FASTA序列 (FASTAReader)
         │       输入: FASTA文件
         │       输出: 序列字典列表 [{'id', 'description', 'sequence', 'length'}, ...]
         │
         └─→ 读取表达矩阵 (pd.read_csv)
                 输入: CSV文件
                 输出: DataFrame (行=基因, 列=样本)

┌────────────────────────────────────────────────────────┐
│ 第二阶段：序列分析                                      │
└────────────────────────────────────────────────────────┘
         │
         └─→ 序列统计 (SequenceStats)
                 ├─ calculate_gc_content() → [45.2, 52.1, ...]
                 ├─ calculate_nucleotide_frequencies() → {'A':0.3, 'T':0.3, ...}
                 └─ calculate_gc_skew() → [[0.1, -0.2, ...], ...]

┌────────────────────────────────────────────────────────┐
│ 第三阶段：差异表达分析                                  │
└────────────────────────────────────────────────────────┘
         │
         └─→ 差异分析 (DiffExpAnalyzer.analyze)
                 ├─ 数据过滤（去除低表达）
                 ├─ t检验（每个基因）
                 ├─ 计算log2FC
                 ├─ BH-FDR校正
                 ├─ 标记显著性
                 └─ 输出DataFrame (包含log2FC, p值, 校正p值, 显著性等)

┌────────────────────────────────────────────────────────┐
│ 第四阶段：可视化                                        │
└────────────────────────────────────────────────────────┘
         │
         └─→ 图表生成 (PlotGenerator)
                 ├─ plot_gc_distribution(gc_contents) → PNG
                 ├─ plot_volcano(deg_results) → PNG
                 ├─ plot_heatmap(expression_data) → PNG
                 └─ plot_pca(expression_data.T) → PNG

┌────────────────────────────────────────────────────────┐
│ 第五阶段：机器学习                                      │
└────────────────────────────────────────────────────────┘
         │
         └─→ 基因分类 (GeneClassifier)
                 ├─ prepare_data(deg_results) → X, y
                 ├─ train(X, y) → 模型 + 评估指标
                 ├─ predict(X) → 预测标签
                 └─ 输出特征重要性

┌────────────────────────────────────────────────────────┐
│ 第六阶段：结果输出                                      │
└────────────────────────────────────────────────────────┘
         │
         ├─→ 保存CSV (deg_results.csv)
         ├─→ 保存图表 (PNG, 300 DPI)
         └─→ 保存配置 (config.txt)
```

### Web应用数据流（app.py）

```
用户操作:
    │
    ├─ 上传FASTA文件 → session_state.uploaded_fasta
    │
    ├─ 上传表达矩阵 → session_state.uploaded_expression
    │
    ├─ 配置参数 → session_state.config
    │       - P值阈值
    │       - log2FC阈值
    │       - 样本分组
    │
    ├─ 点击"开始分析" → run_full_analysis()
    │       ├─ 序列分析 → results['seq_results']
    │       ├─ 差异分析 → results['deg_results']
    │       ├─ 可视化 → results['plots']
    │       └─ 机器学习 → results['ml_results']
    │
    └─ 查看结果页面
            ├─ 显示图表 (st.pyplot)
            ├─ 显示表格 (st.dataframe)
            └─ 显示指标 (st.metric)

下载结果:
    ├─ CSV文件 (st.download_button)
    └─ PNG图表 (300 DPI)
```

---

## 技术栈

### Python版本

- **最低要求**: Python 3.8+
- **推荐版本**: Python 3.10+

### 核心依赖库

| 库名 | 版本要求 | 用途 | 关键功能 |
|------|---------|------|---------|
| **streamlit** | >=1.28.0 | Web框架 | 页面渲染、交互组件、状态管理 |
| **pandas** | >=2.0.0 | 数据处理 | DataFrame、CSV读写、数据清洗 |
| **numpy** | >=1.24.0 | 数值计算 | 数组运算、统计函数 |
| **matplotlib** | >=3.7.0 | 绑图基础 | 图表生成、自定义样式 |
| **seaborn** | >=0.12.0 | 高级绑图 | 美化图表、简化绑图代码 |
| **biopython** | >=1.81 | 生物信息学 | FASTA解析、序列操作 |
| **scikit-learn** | >=1.3.0 | 机器学习 | RandomForest、PCA、StandardScaler |

### 可选依赖

```python
# 开发依赖（不在requirements.txt中）
pytest>=7.0.0          # 单元测试
black>=23.0.0          # 代码格式化
flake8>=6.0.0          # 代码检查
ipython>=8.0.0         # 交互式Python
jupyter>=1.0.0         # Jupyter Notebook
```

### 字体资源

- **文件**: [fonts/simhei.ttf](fonts/simhei.ttf)
- **类型**: SimHei（黑体）
- **用途**: 图表中文显示
- **大小**: 约10MB

---

## 项目运行方式

### 方式1: Web应用（推荐）

#### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
streamlit run app.py

# 3. 访问应用
# 浏览器自动打开 http://localhost:8501
```

#### 云端部署（Streamlit Community Cloud）

```bash
# 1. 将代码推送到GitHub
git add .
git commit -m "Initial commit"
git push origin main

# 2. 访问 https://share.streamlit.io/
# 3. 点击 "New app"
# 4. 选择仓库、分支、主文件路径(app.py)
# 5. 点击 "Deploy!"
```

### 方式2: 命令行运行

```bash
# 执行完整分析流程
python main.py

# 输出:
# - results/deg_results.csv
# - results/gc_distribution.png
# - results/volcano_plot.png
# - results/expression_heatmap.png
# - results/pca_plot.png
# - results/deg_results_with_classification.csv
```

### 方式3: 模块化调用

```python
# 只使用特定模块
from data_processing import FASTAReader
from sequence_analysis import SequenceStats

# 读取FASTA文件
reader = FASTAReader("my_data.fasta")
sequences = reader.read_all()

# 计算GC含量
stats = SequenceStats(sequences)
gc_contents = stats.calculate_gc_content()

# 自定义分析流程...
```

### Windows一键启动

```bash
# 双击运行
start_app.bat

# 或使用Python脚本
python start_app.py
```

---

## 配置管理

### 配置类详解

**文件**: [config.py](config.py)

#### 参数分类

**1. 文件路径配置**

```python
fasta_file: str = "data/simulated_genes.fasta"
expression_file: str = "data/simulated_expression.csv"
output_dir: str = "results"
```

**2. 分析参数配置**

```python
# GC分析窗口大小
gc_window_size: int = 100
# 说明: 滑动窗口计算GC含量分布
# 范围: 50-500 bp

# P值阈值（显著性水平）
p_value_threshold: float = 0.05
# 说明: 校正后P值小于此阈值为显著
# 常用: 0.05（5%假阳性）, 0.01（更严格）

# log2倍数变化阈值
log2_fold_change_threshold: float = 1.0
# 说明: |log2FC| > 1.0 对应2倍变化
# 常用: 0.5（1.4倍）, 1.0（2倍）, 2.0（4倍）
```

**3. 机器学习参数**

```python
# 测试集比例
test_size: float = 0.2
# 说明: 20%数据用于测试模型

# 随机种子
random_state: int = 42
# 说明: 固定随机性，保证结果可复现

# 随机森林树数
n_estimators: int = 100
# 说明: 树越多越稳定，但计算越慢
# 范围: 100-500
```

**4. 可视化参数**

```python
# 图表尺寸
figure_size: tuple = (10, 8)  # 宽×高（英寸）

# 调色板
color_palette: str = "Set2"
# 选项: Set1, Set2, Paired, viridis, RdBu_r
```

#### 参数调整建议

| 参数 | 默认值 | 调整场景 | 推荐范围 |
|------|-------|---------|---------|
| `p_value_threshold` | 0.05 | 探索性研究可放宽，验证性研究需严格 | 0.01-0.1 |
| `log2_fold_change_threshold` | 1.0 | 小变化研究可降低，大变化研究可提高 | 0.5-2.0 |
| `n_estimators` | 100 | 数据复杂时可增加 | 100-500 |
| `test_size` | 0.2 | 数据少时可减小 | 0.1-0.3 |

---

## 示例数据说明

### 数据文件

**位置**: [data/](data/)

#### simulated_genes.fasta

**内容**: 模拟的基因序列数据

**格式**:
```
>gene_001 simulated gene 1
ATGAGCCACCCTGAGCCGGCTCCTGATTCCTTTCTTT...
>gene_002 simulated gene 2
ATGCGATCGATCGATCGATCGATCGATCG...
...
```

**用途**:
- 序列分析演示
- GC含量计算
- 核苷酸频率统计

#### simulated_expression.csv

**内容**: 模拟的基因表达矩阵

**格式**:
```csv
gene,control_0,control_1,control_2,treatment_0,treatment_1,treatment_2
gene_001,100,120,110,50,60,55
gene_002,50,55,48,200,210,195
...
```

**结构**:
- 行: 基因（约100个）
- 列: 样本（对照组3个 + 处理组3个）
- 值: 表达量计数

**用途**:
- 差异表达分析演示
- 热图绘制
- PCA分析
- 机器学习训练

### 测试数据

**位置**: [data/fasta_files/](data/fasta_files/)

- **NM_000546_TP53_test.fasta**: TP53基因序列（肿瘤蛋白p53）
- **NM_001354_GATA1_test.fasta**: GATA1基因序列（转录因子）

**用途**:
- 单基因分析测试
- 功能验证

---

## 开发指南

### 代码风格

本项目采用教学级注释风格：

**特点**:
- 每个函数都有详细说明
- 解释"为什么"而非"是什么"
- 包含示例代码
- 使用类比和比喻帮助理解

**示例**:
```python
def calculate_gc_content(self) -> List[float]:
    """
    计算每条序列的GC含量
    
    GC含量 = (G数量 + C数量) / 总碱基数 × 100%
    
    为什么GC含量重要？
    1. DNA热稳定性：GC碱基对有3个氢键，AT只有2个
       GC含量高的生物通常生活在高温环境
    2. 基因组特性：不同物种的GC含量差异很大
       - 人类基因组：约41% GC
       - 拟南芥：约36% GC
    
    Returns:
        List[float]: GC含量百分比列表
    """
```

### 扩展开发

#### 添加新分析模块

**步骤**:

1. 创建新模块目录
```bash
mkdir new_analysis
touch new_analysis/__init__.py
touch new_analysis/analyzer.py
```

2. 实现分析类
```python
# new_analysis/analyzer.py
class NewAnalyzer:
    def __init__(self, data):
        self.data = data
    
    def analyze(self):
        # 实现分析逻辑
        return results
```

3. 在主程序中集成
```python
# main.py 或 app.py
from new_analysis import NewAnalyzer

analyzer = NewAnalyzer(data)
results = analyzer.analyze()
```

#### 添加新图表类型

**步骤**:

1. 在 `PlotGenerator` 类中添加新方法
```python
# visualization/plots.py
def plot_new_chart(self, data, title="新图表"):
    fig, ax = plt.subplots(figsize=(10, 6))
    # 绘图逻辑...
    return fig
```

2. 在主程序中调用
```python
plotter = PlotGenerator()
fig = plotter.plot_new_chart(data)
```

### 测试建议

```python
# tests/test_data.py
import pytest
from data_processing import FASTAReader

def test_fasta_reader():
    reader = FASTAReader("data/sample.fasta")
    sequences = reader.read_all()
    
    assert len(sequences) > 0
    assert sequences[0]['id'] is not None
    assert sequences[0]['length'] > 0
```

### 调试技巧

1. **日志系统**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("调试信息")
```

2. **Streamlit调试**
```python
import streamlit as st
st.write("变量值:", variable)  # 在Web界面显示
```

3. **可视化检查**
```python
# 在分析过程中绘制中间结果
import matplotlib.pyplot as plt
plt.hist(gc_contents)
plt.show()
```

---

## 常见问题与解决方案

### Q1: 中文图表显示乱码

**解决方案**:
```python
# 确保fonts/simhei.ttf存在
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
```

### Q2: Streamlit应用加载慢

**原因**: 首次运行需要安装依赖

**解决方案**: 等待1-3分钟，后续访问会快很多

### Q3: 差异分析结果无显著基因

**可能原因**:
- P值阈值过严格
- 倍数变化阈值过大
- 数据本身差异小

**解决方案**: 在Web界面调整参数，降低阈值

### Q4: 机器学习模型准确率低

**可能原因**:
- 样本数太少
- 特征不够区分
- 类别不平衡严重

**解决方案**:
- 增加数据量
- 调整 `test_size`
- 尝试其他算法（SVM、逻辑回归）

---

## 版本历史

- **v1.0** (2024-01): 初始版本，包含四大核心功能
- **计划**: v1.1 - 添加批量分析功能，支持多个数据集并行处理

---

## 联系方式

- **在线应用**: https://geneanalysis-app.streamlit.app/
- **问题反馈**: GitHub Issues
- **贡献代码**: Pull Requests欢迎

---

**文档生成日期**: 2024-01-01

**最后更新**: 2024-01-01

---

> 本Code Wiki旨在帮助开发者快速理解项目架构和代码逻辑，
> 详细的API文档请参考各模块的源代码注释。