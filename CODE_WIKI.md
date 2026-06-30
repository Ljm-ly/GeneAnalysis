# 基因表达调控分析与预测平台 - Code Wiki

**项目名称**: GeneAnalysis  
**版本**: v1.0  
**最后更新**: 2026-06-30  
**开发语言**: Python 3.10+  
**作者**: LJM  

---

## 目录

1. [项目概述](#1-项目概述)
2. [项目结构](#2-项目结构)
3. [核心模块详解](#3-核心模块详解)
4. [数据流与分析流程](#4-数据流与分析流程)
5. [配置系统](#5-配置系统)
6. [依赖关系](#6-依赖关系)
7. [运行方式](#7-运行方式)
8. [测试系统](#8-测试系统)
9. [输出结果说明](#9-输出结果说明)
10. [扩展开发指南](#10-扩展开发指南)

---

## 1. 项目概述

### 1.1 项目简介

GeneAnalysis是一个完整的**基因表达调控分析与预测平台**,集成了从原始数据读取到最终结果输出的完整生物信息学分析流程。该项目实现了:

- **序列分析**: FASTA文件解析、GC含量计算、核苷酸频率统计
- **差异表达分析**: t检验、Benjamini-Hochberg FDR校正、显著基因识别
- **机器学习**: 随机森林分类器、特征重要性分析
- **可视化**: GC分布图、火山图、表达热图、PCA降维图

### 1.2 核心功能

| 功能模块 | 核心能力 | 生物信息学应用场景 |
|---------|---------|-------------------|
| 数据处理 | FASTA文件解析、数据清洗 | 原始测序数据预处理 |
| 序列分析 | GC含量、核苷酸频率、GC偏斜 | 基因组组成特征分析 |
| 表达分析 | 差异表达识别、统计检验 | RNA-seq数据分析 |
| 机器学习 | 基因分类、特征重要性 | 预测潜在功能基因 |
| 可视化 | 多维度图表生成 | 结果展示与报告 |

### 1.3 技术特点

- **模块化设计**: 各功能模块独立封装,易于维护和扩展
- **详细注释**: 每行代码都有中文注释,便于理解和学习
- **容错性强**: 完善的错误处理和异常捕获机制
- **参数可配置**: 所有分析参数可通过配置文件调整
- **结果可复现**: 固定随机种子,保证每次运行结果一致

---

## 2. 项目结构

### 2.1 目录结构

```
GeneAnalysis/
├── main.py                          # 主程序入口 - 分析流程总指挥
├── config.py                        # 配置管理 - 集中管理所有参数
├── config.ini                       # 配置文件 - 参数配置存储
├── requirements.txt                 # 依赖清单 - Python包列表
├── generate_simulated_data.py       # 数据生成 - 模拟测试数据
│
├── data/                            # 数据目录
│   ├── expression.csv               # 基因表达矩阵(CSV格式)
│   ├── gene_list.txt                # 基因ID列表
│   ├── sample.fasta                 # 示例FASTA序列
│   └── simulated_genes.fasta        # 模拟基因序列数据
│
├── results/                         # 输出目录(自动生成)
│   ├── deg_results.csv              # 差异表达分析结果
│   ├── deg_results_with_classification.csv  # ML分类结果
│   ├── gc_distribution.png          # GC含量分布图
│   ├── volcano_plot.png             # 差异表达火山图
│   ├── expression_heatmap.png       # 基因表达热图
│   └── pca_plot.png                 # PCA主成分分析图
│
├── data_processing/                 # 数据处理模块
│   ├── __init__.py
│   ├── fasta_reader.py              # FASTA文件读取器
│   └── data_cleaner.py              # 数据清洗工具
│
├── sequence_analysis/               # 序列分析模块
│   ├── __init__.py
│   └── basic_stats.py               # 序列基础统计(GC含量等)
│
├── expression_analysis/             # 表达分析模块
│   ├── __init__.py
│   └── differential.py              # 差异表达分析器
│
├── machine_learning/                # 机器学习模块
│   ├── __init__.py
│   └── classifier.py                # 基因分类器(随机森林)
│
├── visualization/                   # 可视化模块
│   ├── __init__.py
│   └── plots.py                     # 图表生成器
│
├── utils/                           # 工具函数模块
│   ├── __init__.py
│   └── helpers.py                   # 通用工具函数
│
└── tests/                           # 单元测试模块
    ├── __init__.py
    └── test_data.py                 # 数据处理功能测试
```

### 2.2 模块职责矩阵

| 模块 | 主要职责 | 关键类/函数 | 输入 | 输出 |
|------|---------|-----------|------|------|
| main.py | 流程控制 | main(), setup_logging() | 无 | 分析报告 |
| config.py | 参数管理 | AnalysisConfig | 无 | 配置对象 |
| data_processing | 数据IO | FASTAReader, DataCleaner | FASTA/CSV | DataFrame/字典列表 |
| sequence_analysis | 序列统计 | SequenceStats | 序列字典列表 | GC含量、频率统计 |
| expression_analysis | 差异分析 | DiffExpAnalyzer | 表达矩阵 | DEG列表 |
| machine_learning | 基因分类 | GeneClassifier | DEG特征 | 预测标签 |
| visualization | 图表生成 | PlotGenerator | 统计结果 | PNG图表 |
| utils | 工具支持 | helpers模块 | 各种 | 标准化输出 |

---

## 3. 核心模块详解

### 3.1 主程序模块 (main.py)

#### 功能概述
主程序是整个分析流程的"总指挥",按照预设顺序依次调用各个功能模块,完成从原始数据读取到最终结果输出的完整流水线。

#### 关键函数

| 函数名 | 功能 | 参数 | 返回值 |
|--------|------|------|--------|
| `main()` | 主流程控制 | 无 | 执行完整分析 |
| `setup_logging()` | 配置日志系统 | log_level | Logger对象 |
| `load_configuration()` | 加载配置 | logger | AnalysisConfig |
| `load_fasta_sequences()` | 读取FASTA | config, logger | 序列列表 |
| `load_expression_data()` | 读取表达矩阵 | config, logger | DataFrame |
| `run_sequence_analysis()` | 序列统计 | sequences, config, logger | 统计结果字典 |
| `run_differential_analysis()` | 差异分析 | config, logger | DEG DataFrame |
| `generate_visualizations()` | 生成图表 | 多个参数 | PNG文件 |
| `run_machine_learning()` | ML分类 | deg_results, config, logger | 分类结果 |

#### 分析流程

```python
main() {
    1. setup_logging()         → 初始化日志系统
    2. load_configuration()    → 加载并验证配置参数
    3. load_fasta_sequences()  → 读取FASTA序列文件
    4. load_expression_data()  → 读取基因表达矩阵
    5. run_sequence_analysis() → 计算GC含量、核苷酸频率
    6. run_differential_analysis() → 执行t检验和FDR校正
    7. generate_visualizations() → 生成4种图表
    8. run_machine_learning()  → 训练随机森林分类器
    9. 输出结果报告
}
```

#### 容错机制
- **配置验证**: 启动前检查文件路径、参数范围
- **异常捕获**: 每个步骤独立try-catch,不影响其他步骤
- **优雅退出**: KeyboardInterrupt捕获,避免强制中断
- **日志记录**: 所有关键步骤记录到日志,便于排查问题

---

### 3.2 配置管理模块 (config.py)

#### 功能概述
使用Python dataclass集中管理所有分析参数,包括文件路径、统计阈值、模型参数等。支持配置验证、保存和加载。

#### 关键类: AnalysisConfig

```python
@dataclass
class AnalysisConfig:
    # 文件路径配置
    fasta_file: str = "data/simulated_genes.fasta"
    expression_file: str = "data/simulated_expression.csv"
    output_dir: str = "results"
    
    # 分析参数
    gc_window_size: int = 100              # GC分析滑动窗口
    p_value_threshold: float = 0.05        # P值显著性阈值
    log2_fold_change_threshold: float = 1.0  # 倍数变化阈值
    
    # 机器学习参数
    test_size: float = 0.2                 # 测试集比例
    random_state: int = 42                 # 随机种子
    n_estimators: int = 100                # 随机森林树数量
    
    # 可视化参数
    figure_size: tuple = (10, 8)           # 图表尺寸(英寸)
    color_palette: str = "Set2"            # 颜色方案
```

#### 核心方法

| 方法 | 功能 | 说明 |
|------|------|------|
| `validate()` | 配置验证 | 检查文件存在性、参数范围合理性 |
| `save_to_file(filepath)` | 保存配置 | 写入文本文件,记录实验参数 |
| `load_from_file(filepath)` | 加载配置 | 从文本文件读取,支持类型自动转换 |
| `to_dict()` | 转为字典 | 方便序列化和传递 |

#### 配置验证逻辑
```python
validate():
    - 检查FASTA文件是否存在
    - 检查P值阈值在(0, 1]范围
    - 检查log2FC阈值非负
    - 自动创建输出目录(如不存在)
    → 返回True/False表示配置有效性
```

---

### 3.3 数据处理模块 (data_processing/)

#### 3.3.1 FASTA读取器 (fasta_reader.py)

**功能**: 解析FASTA格式的序列文件,提取序列ID、描述、碱基序列和长度信息。

**关键类**: `FASTAReader`

```python
class FASTAReader:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.sequences = []  # 序列缓存
    
    def read_all() -> List[Dict]:
        """读取所有序列"""
        # 返回格式: [{'id': 'gene_001', 'sequence': 'ATCG...', 'length': 1000}, ...]
    
    def read_by_id(seq_id: str) -> Optional[Dict]:
        """按ID查找序列"""
        # 在缓存中查找,返回单个序列字典
    
    def get_statistics() -> Dict:
        """获取统计信息"""
        # 返回: {'count': 100, 'min_length': 500, 'max_length': 3000, ...}
```

**技术要点**:
- 使用Biopython的SeqIO.parse解析器
- 自动处理多行序列和不同格式
- 内存高效的迭代器模式
- 缓存机制避免重复读取

#### 3.3.2 数据清洗器 (data_cleaner.py)

**功能**: 对原始数据进行预处理,包括去重、填补缺失值、标准化、异常值处理。

**关键类**: `DataCleaner`

```python
class DataCleaner:
    def remove_duplicates(df) -> DataFrame:
        """去除完全重复的行"""
    
    def fill_missing_values(df, strategy='mean') -> DataFrame:
        """填补缺失值"""
        # strategy: 'mean'(均值), 'median'(中位数), 'zero'(0值), 'ffill'(前向填充)
    
    def normalize_data(df, method='zscore') -> DataFrame:
        """数据标准化"""
        # zscore: (x-μ)/σ → 均值0,标准差1
        # minmax: (x-min)/(max-min) → [0,1]区间
    
    def filter_outliers(df, threshold=3.0) -> DataFrame:
        """过滤异常值"""
        # |Z-score| > threshold 视为异常,用中位数替换
```

**应用场景**:
- RNA-seq数据去重(同一基因比对多次)
- 低表达基因过滤(表达量<10的基因)
- 不同测序深度样本标准化
- 芯片数据异常值处理

---

### 3.4 序列分析模块 (sequence_analysis/)

#### 功能概述
计算DNA序列的基础统计指标,包括GC含量、核苷酸频率、GC偏斜等。

#### 关键类: SequenceStats

```python
class SequenceStats:
    def __init__(self, sequences: List[Dict]):
        self.sequences = sequences
    
    def calculate_gc_content() -> List[float]:
        """计算每条序列的GC含量"""
        # 公式: (G+C)/(总长度) × 100%
        # 返回: [45.2, 52.1, 38.7, ...]
    
    def calculate_nucleotide_frequencies() -> Dict[str, float]:
        """计算核苷酸频率"""
        # 返回: {'A': 0.30, 'T': 0.30, 'G': 0.20, 'C': 0.20, 'N': 0.0}
    
    def calculate_gc_skew(window_size=100) -> List[List[float]]:
        """计算GC偏斜(滑动窗口)"""
        # 公式: (G-C)/(G+C), 范围[-1, 1]
        # 应用: 预测细菌复制起始位点
    
    def get_summary_statistics() -> Dict:
        """汇总统计"""
        # 返回多个统计指标: 总数、平均GC、长度分布等
```

**生物学意义**:
- **GC含量**: DNA热稳定性指标,不同物种特征不同
- **核苷酸频率**: Chargaff规则验证(A≈T, G≈C)
- **GC偏斜**: 细菌基因组复制方向识别

---

### 3.5 表达分析模块 (expression_analysis/)

#### 功能概述
执行差异表达分析(Differential Expression Analysis),识别在不同条件下表达显著变化的基因。

#### 关键类: DiffExpAnalyzer

```python
class DiffExpAnalyzer:
    def __init__(self, expression_file: str):
        self.data = pd.read_csv(expression_file, index_col=0)
    
    def analyze(group1_cols, group2_cols, 
                p_threshold=0.05, log2fc_threshold=1.0) -> DataFrame:
        """执行完整差异分析"""
        流程:
        1. 过滤低表达基因(均值<10)
        2. 对每个基因执行t检验
        3. 计算log2倍数变化
        4. Benjamini-Hochberg FDR校正
        5. 标记显著基因
    
    def get_significant_genes(direction=None) -> List[str]:
        """获取显著基因列表"""
        # direction: 'up'(上调), 'down'(下调), None(全部)
    
    def export_results(output_file: str):
        """导出结果到CSV"""
```

#### 内部方法详解

| 方法 | 功能 | 关键算法 |
|------|------|---------|
| `_remove_low_expression()` | 过滤低表达基因 | 基于均值阈值 |
| `_perform_ttest()` | t检验 | scipy.stats.ttest_ind |
| `_calculate_fold_change()` | 倍数变化计算 | log2(mean2/mean1) |

#### Benjamini-Hochberg FDR校正

```python
# 核心逻辑:
1. 按p值从小到大排序
2. 计算初始校正值: corrected[i] = p[i] × n / rank[i]
3. 保证单调性: 从后往前取累积最小值
4. 限制最大值 ≤ 1.0

# 硬约束(来自project_memory.md):
"必须从后往前取累积最小值以保证单调性"
```

#### 结果DataFrame列说明

| 列名 | 含义 | 示例值 |
|------|------|--------|
| gene | 基因ID | gene_001 |
| log2_fold_change | log2倍数变化 | 2.5 (上调) |
| p_value | 原始P值 | 0.001 |
| corrected_p_value | 校正后P值 | 0.023 |
| is_significant | 是否显著 | True |
| regulation | 调控方向 | 'up'/'down'/'no_change' |
| mean_control | 对照组均值 | 50.2 |
| mean_treatment | 处理组均值 | 150.8 |
| t_statistic | t统计量 | 3.45 |

---

### 3.6 机器学习模块 (machine_learning/)

#### 功能概述
使用随机森林算法对基因进行分类,综合多个特征判断基因是否为差异表达基因。

#### 关键类: GeneClassifier

```python
class GeneClassifier:
    def __init__(self, model_type='random_forest', random_state=42):
        self.model = None
        self.scaler = StandardScaler()
    
    def prepare_data(deg_results, expression_data=None) -> (X, y):
        """准备训练数据"""
        # X: 特征矩阵 [log2FC, p值, 校正p值, mean_control, mean_treatment, t_statistic]
        # y: 标签 [0=无变化, 1=差异基因]
    
    def train(X, y, test_size=0.2) -> Dict:
        """训练模型"""
        # 返回: {'accuracy': 0.85, 'precision': 0.82, 'recall': 0.88, 'f1_score': 0.85, 'feature_importance': {...}}
    
    def predict(X) -> array:
        """预测新基因"""
        # 返回: [0, 1, 1, 0, ...]
    
    def predict_proba(X) -> array:
        """预测概率"""
        # 返回: [[0.9, 0.1], [0.2, 0.8], ...]
```

#### 特征工程

**使用的特征**:
1. `log2_fold_change` - 变化幅度(生物学意义)
2. `p_value` - 原始显著性(统计检验)
3. `corrected_p_value` - 校正后显著性(更严格)
4. `mean_control` - 对照组基础表达水平
5. `mean_treatment` - 处理组基础表达水平
6. `t_statistic` - t统计量(组间差异/组内变异)

**数据标准化**: Z-score标准化,使所有特征在同一尺度。

#### 模型参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| n_estimators | 100 | 决策树数量 |
| max_depth | min(10, 样本数//2) | 最大深度 |
| class_weight | 'balanced'(样本充足时) | 类别权重 |
| random_state | 42 | 随机种子 |

#### 特殊处理(硬约束)

```python
# 样本类别不平衡时的处理(来自project_memory.md):
"当某个类别样本数<2时自动不使用分层抽样"
"当训练集样本数<10时自动关闭类别平衡"
```

#### 评估指标

| 指标 | 公式 | 含义 |
|------|------|------|
| Accuracy | 正确预测/总数 | 整体准确率 |
| Precision | TP/(TP+FP) | 预测为正的可信度 |
| Recall | TP/(TP+FN) | 真正正例的检出率 |
| F1-Score | 2×P×R/(P+R) | 精确率和召回率的平衡 |

---

### 3.7 可视化模块 (visualization/)

#### 功能概述
生成生物信息学常用的四种图表,用于结果展示和报告。

#### 关键类: PlotGenerator

```python
class PlotGenerator:
    def __init__(self, style='whitegrid'):
        sns.set_style(style)
        # 设置中文字体支持
    
    def plot_gc_distribution(gc_contents, title, output_file):
        """GC含量分布直方图"""
        # 绘制直方图+核密度估计曲线
        # 添加均值和中位数参考线
    
    def plot_volcano(deg_results, p_threshold, log2fc_threshold):
        """差异表达火山图"""
        # X轴: log2FC, Y轴: -log10(p值)
        # 红色=上调, 蓝色=下调, 灰色=不显著
    
    def plot_heatmap(data, show_labels=True):
        """基因表达热图"""
        # Z-score标准化每个基因
        # 红色=高表达, 蓝色=低表达
    
    def plot_pca(expression_data, labels=None):
        """PCA降维图"""
        # 降到2维,显示PC1和PC2
        # 相似样本聚集在一起
```

#### 图表详解

**1. GC含量分布图**
- 类型: 直方图+KDE曲线
- 用途: 检查序列组成特征,识别污染
- 关键元素: 均值线(红色)、中位数线(绿色)

**2. 火山图(Volcano Plot)**
- 类型: 散点图
- 解读: 左上=下调显著, 右上=上调显著, 中下=不显著
- 参数: P值阈值线、FC阈值线

**3. 表达热图**
- 类型: 热力图(Heatmap)
- 标准化: Z-score(行标准化)
- 特殊处理: 基因>50时自动隐藏行标签(硬约束)

**4. PCA图**
- 类型: 散点图
- 用途: 样本相似性、批次效应检查
- 显示: PC1/PC2的解释方差比例

#### 热图特殊逻辑(硬约束)

```python
# 来自project_memory.md:
"热图在基因数量超过50个时自动隐藏行标签,样本名(X轴)始终显示"
"热图需动态调整图表尺寸以适应基因数量"

# 实现逻辑:
if n_genes > 50:
    show_row_labels = False  # 隐藏基因名
    logger.info(f"基因数量({n_genes})较多,热图不显示行标签")

# 动态尺寸:
fig_height = max(8, min(30, n_genes * 0.15))
```

---

### 3.8 工具模块 (utils/)

#### 功能概述
提供通用的辅助函数,不依赖生物学逻辑,可在任何Python项目复用。

#### 关键函数

| 函数名 | 功能 | 应用场景 |
|--------|------|---------|
| `ensure_directory(dir)` | 创建目录 | 结果保存前准备 |
| `calculate_file_hash(filepath)` | 计算文件哈希 | 数据完整性验证 |
| `format_timestamp(timestamp)` | 时间格式化 | 日志记录 |
| `validate_file_extension(path, exts)` | 扩展名验证 | 输入文件检查 |
| `save_json(data, filepath)` | 保存JSON | 元数据存储 |
| `load_json(filepath)` | 加载JSON | 配置读取 |
| `chunk_list(list, size)` | 列表分块 | 大数据批处理 |

#### 示例用法

```python
# 创建目录
ensure_directory("results/plots")

# 验证文件完整性
hash_value = calculate_file_hash("data/sample.fasta", algorithm='sha256')

# 保存分析元数据
save_json({
    'analysis_time': '2026-06-30 10:00:00',
    'parameters': {'p_threshold': 0.05},
    'gene_count': 1000
}, "results/analysis_summary.json")

# 大数据分块处理
for batch in chunk_list(large_gene_list, 100):
    process_batch(batch)
```

---

## 4. 数据流与分析流程

### 4.1 数据流图

```
原始数据输入
    │
    ├─→ FASTA文件 ─→ FASTAReader ─→ 序列字典列表
    │                                 ↓
    │                          SequenceStats
    │                                 ↓
    │                          GC含量、频率统计
    │                                 ↓
    │                          plot_gc_distribution()
    │                                 ↓
    │                          GC分布图
    │
    ├─→ CSV表达矩阵 ─→ DiffExpAnalyzer
    │                       │
    │                       ├─→ 低表达过滤
    │                       ├─→ t检验
    │                       ├─→ FDR校正
    │                       ├─→ 显著性标记
    │                       ↓
    │                  DEG DataFrame
    │                       │
    │                       ├─→ plot_volcano() ─→ 火山图
    │                       ├─→ plot_heatmap() ─→ 热图
    │                       ├─→ plot_pca()    ─→ PCA图
    │                       ↓
    │                  GeneClassifier
    │                       │
    │                       ├─→ 数据标准化
    │                       ├─→ 特征提取
    │                       ├─→ 模型训练
    │                       ├─→ 性能评估
    │                       ↓
    │                  分类预测结果
    │                       ↓
    │                  CSV导出 + 特征重要性
    │
    └─→ 配置参数 ─→ AnalysisConfig ─→ 全流程参数传递
```

### 4.2 完整分析流程(7步)

#### 步骤1: 系统初始化
```python
setup_logging()  # 配置日志输出
load_configuration()  # 加载参数,验证有效性
```

**输出**: Logger对象、AnalysisConfig对象

#### 步骤2: 数据读取
```python
sequences = load_fasta_sequences()  # FASTA序列
expression_data = load_expression_data()  # 表达矩阵
```

**输出**: 序列字典列表(每条序列包含id、description、sequence、length)

#### 步骤3: 序列分析
```python
gc_contents = calculate_gc_content()  # 每条序列GC百分比
nucleotide_freq = calculate_nucleotide_frequencies()  # 总体碱基频率
avg_gc = mean(gc_contents)  # 平均GC含量
```

**输出**: 统计结果字典

#### 步骤4: 差异表达分析
```python
deg_results = analyze(
    group1_cols=['control_0', 'control_1', 'control_2'],
    group2_cols=['treatment_0', 'treatment_1', 'treatment_2'],
    p_threshold=0.05,
    log2fc_threshold=1.0
)
```

**关键计算**:
- t检验 → 原始P值
- log2((mean2+0.01)/(mean1+0.01)) → 倍数变化
- BH校正 → 校正P值
- 综合判断 → 显著性标记

**输出**: DataFrame(964行基因×9列指标)

#### 步骤5: 可视化生成
```python
plot_gc_distribution()  # GC分布直方图
plot_volcano()          # 火山图(红蓝灰三色)
plot_heatmap()          # 全基因热图(自动隐藏>50基因标签)
plot_pca()              # PCA降维散点图
```

**输出**: 4个PNG图片文件(300 DPI出版质量)

#### 步骤6: 机器学习分类
```python
features = [log2FC, p_value, corrected_p_value, mean_control, mean_treatment, t_statistic]
X, y = prepare_data(deg_results)
train(X, y, test_size=0.2)
predictions = predict(X)
```

**模型**: RandomForestClassifier(100棵树)

**输出**: 分类预测、特征重要性排序、模型评估指标

#### 步骤7: 结果输出
```python
export_results("deg_results.csv")  # 差异分析结果
save_classification("deg_results_with_classification.csv")  # ML结果
```

**输出**: 2个CSV文件

---

## 5. 配置系统

### 5.1 配置文件格式

#### config.ini格式
```ini
[FASTA]
path = data/sample.fasta

[SETTINGS]
output_dir = results
```

#### AnalysisConfig默认值
```python
fasta_file = "data/simulated_genes.fasta"
expression_file = "data/simulated_expression.csv"
output_dir = "results"

gc_window_size = 100
p_value_threshold = 0.05
log2_fold_change_threshold = 1.0

test_size = 0.2
random_state = 42
n_estimators = 100

figure_size = (10, 8)
color_palette = "Set2"
```

### 5.2 参数详解

#### 文件路径参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| fasta_file | str | data/simulated_genes.fasta | FASTA序列文件路径 |
| expression_file | str | data/simulated_expression.csv | 表达矩阵CSV路径 |
| output_dir | str | results | 结果输出目录 |

#### 分析参数

| 参数 | 类型 | 默认值 | 合理范围 | 说明 |
|------|------|--------|---------|------|
| gc_window_size | int | 100 | 50-500 | GC分析滑动窗口(bp) |
| p_value_threshold | float | 0.05 | 0.01-0.1 | FDR校正后P值阈值 |
| log2_fold_change_threshold | float | 1.0 | 0.5-2.0 | log2倍数变化阈值 |

**生物学意义**:
- `p_value_threshold=0.05`: 控制假发现率<5%
- `log2fc_threshold=1.0`: 要求≥2倍变化才算显著

#### 机器学习参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| test_size | float | 0.2 | 测试集比例(20%) |
| random_state | int | 42 | 随机种子(固定保证可复现) |
| n_estimators | int | 100 | 随机森林树数量 |

#### 可视化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| figure_size | tuple | (10, 8) | 图表尺寸(英寸) |
| color_palette | str | Set2 | seaborn调色板 |

### 5.3 配置修改示例

```python
# 方式1: 直接修改默认值
config = AnalysisConfig()
config.p_value_threshold = 0.01  # 更严格阈值
config.log2_fold_change_threshold = 1.5  # 要求2.8倍变化

# 方式2: 从文件加载
config = AnalysisConfig.load_from_file("config.ini")

# 方式3: 保存配置(用于实验记录)
config.save_to_file("results/config_backup.txt")
```

---

## 6. 依赖关系

### 6.1 Python包依赖

| 包名 | 版本 | 用途 | 关键功能 |
|------|------|------|---------|
| **biopython** | 1.84 | 生物序列处理 | SeqIO.parse(FASTA解析) |
| **pandas** | - | 数据处理 | DataFrame、CSV读写 |
| **numpy** | - | 数值计算 | 数组运算、统计函数 |
| **scipy** | - | 统计分析 | stats.ttest_ind(t检验) |
| **matplotlib** | - | 基础绘图 | plt.savefig、图表配置 |
| **seaborn** | - | 高级绘图 | heatmap、histplot |
| **scikit-learn** | - | 机器学习 | RandomForest、PCA、StandardScaler |

### 6.2 安装方式

```bash
# 方式1: pip安装(推荐)
pip install -r requirements.txt

# 方式2: 手动安装
pip install biopython==1.84 pandas numpy scipy matplotlib seaborn scikit-learn

# 方式3: conda安装(适合科学计算)
conda install -c conda-forge biopython pandas numpy scipy matplotlib seaborn scikit-learn
```

### 6.3 requirements.txt内容

```
biopython==1.84
numpy
pandas
matplotlib
seaborn
scikit-learn
scipy
```

### 6.4 模块内部依赖

```
main.py
  ├─→ config.py (AnalysisConfig)
  ├─→ data_processing.fasta_reader (FASTAReader)
  ├─→ sequence_analysis.basic_stats (SequenceStats)
  ├─→ expression_analysis.differential (DiffExpAnalyzer)
  ├─→ machine_learning.classifier (GeneClassifier)
  └─→ visualization.plots (PlotGenerator)

DiffExpAnalyzer
  └─→ pandas, scipy.stats, numpy

GeneClassifier
  ├─→ sklearn.ensemble.RandomForestClassifier
  ├─→ sklearn.preprocessing.StandardScaler
  └─→ sklearn.model_selection.train_test_split

PlotGenerator
  ├─→ matplotlib.pyplot
  ├─→ seaborn
  └─→ sklearn.decomposition.PCA (for plot_pca)
```

---

## 7. 运行方式

### 7.1 环境准备

#### 步骤1: 安装Python
- **要求版本**: Python 3.10 或更高
- **检查方式**: `python --version`

#### 步骤2: 创建虚拟环境(推荐)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 步骤3: 安装依赖包
```bash
pip install -r requirements.txt
```

#### 步骤4: 验证安装
```bash
python -c "import Bio; import pandas; import sklearn; print('All packages installed successfully')"
```

### 7.2 运行完整分析

```bash
# 进入项目目录
cd GeneAnalysis

# 运行主程序
python main.py
```

**预期输出**:
```
🚀 基因表达调控分析与预测平台启动
============================================================
第一步：加载配置
============================================================
✅ 配置验证通过
   FASTA文件: data/simulated_genes.fasta
   表达数据: data/simulated_expression.csv
   输出目录: results

第二步：读取FASTA序列数据
============================================================
✅ 成功读取 1000 条序列
   序列1: gene_001 (长度: 1500 bp)
   ...

第三步：读取基因表达数据
============================================================
✅ 成功读取表达数据
   基因数量: 964 个
   样本数量: 6 个
   样本名称: control_0, control_1, control_2, treatment_0, treatment_1, treatment_2

第四步：序列基础统计分析
============================================================
✅ 序列统计分析完成
   平均GC含量: 50.23%
   核苷酸频率:
     A: 24.89%
     T: 25.11%
     G: 25.00%
     C: 25.00%

第五步：差异表达分析
============================================================
✅ 差异表达分析完成
   总基因数: 964
   显著差异基因: 245 个
     上调基因: 123 个
     下调基因: 122 个
   结果已保存: results/deg_results.csv

第六步：生成可视化图表
============================================================
✅ GC含量分布图已保存
✅ 火山图已保存
✅ 热图已保存 (964 个基因)
✅ PCA图已保存
   共生成 4 个图表

第七步：机器学习基因分类
============================================================
✅ 模型训练完成
   准确率 (Accuracy): 0.8542
   精确率 (Precision): 0.8623
   召回率 (Recall): 0.8510
   F1分数: 0.8566
   特征重要性排序:
     log2_fold_change: 0.3521
     corrected_p_value: 0.2815
     p_value: 0.1892
     ...
   分类结果已保存: results/deg_results_with_classification.csv

============================================================
🎉 所有分析流程完成！
📂 结果保存在: d:\LJM\Python学习\GeneAnalysis\GeneAnalysis\results
============================================================
```

### 7.3 单独运行测试

```bash
# 运行单元测试
python -m unittest tests.test_data -v

# 或直接运行测试文件
python tests/test_data.py
```

**测试输出示例**:
```
test_gc_content (__main__.TestSequenceStats) ... ok
test_nucleotide_frequencies (__main__.TestSequenceStats) ... ok
test_empty_sequence (__main__.TestSequenceStats) ... ok
test_read_all_sequences (__main__.TestFASTAReader) ... ok
test_read_by_id (__main__.TestFASTAReader) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.023s

OK
```

### 7.4 运行参数调整

#### 方式1: 修改config.py默认值
```python
@dataclass
class AnalysisConfig:
    p_value_threshold: float = 0.01  # 改为更严格阈值
    log2_fold_change_threshold: float = 1.5  # 要求2.8倍变化
```

#### 方式2: 修改config.ini文件
```ini
[SETTINGS]
p_value_threshold = 0.01
log2_fold_change_threshold = 1.5
```

#### 方式3: 命令行临时修改(需要代码改造)
```bash
python main.py --p_threshold 0.01 --log2fc_threshold 1.5
```

### 7.5 生成模拟数据(测试用)

```bash
python generate_simulated_data.py
```

**生成的文件**:
- `data/simulated_genes.fasta` - 1000条模拟基因序列
- `data/simulated_expression.csv` - 模拟表达矩阵(6个样本)

---

## 8. 测试系统

### 8.1 测试文件结构

```
tests/
├── __init__.py
└── test_data.py          # 数据处理功能测试
    ├── TestFASTAReader    # FASTA读取器测试类
    │   ├── test_read_all_sequences()
    │   └ test_read_by_id()
    └── TestSequenceStats  # 序列统计测试类
        ├── test_gc_content()
        ├── test_nucleotide_frequencies()
        ├── test_empty_sequence()
        └ test_gc_content_multiple_sequences()
```

### 8.2 测试覆盖内容

#### FASTA读取器测试 (TestFASTAReader)

| 测试方法 | 测试内容 | 验证点 |
|---------|---------|--------|
| test_read_all_sequences | 读取所有序列 | 序列数量、ID、长度正确性 |
| test_read_by_id | 按ID查找 | 存在ID返回序列,不存在返回None |

#### 序列统计测试 (TestSequenceStats)

| 测试方法 | 测试内容 | 验证点 |
|---------|---------|--------|
| test_gc_content | GC含量计算 | 已知序列"ATCG" → 50% |
| test_nucleotide_frequencies | 核苷酸频率 | "AACCGGTT" → 各0.25 |
| test_empty_sequence | 空序列处理 | GC=0, 频率={} |
| test_gc_content_multiple_sequences | 多序列GC | 3条不同GC含量序列 |

### 8.3 测试框架

**使用的框架**: Python内置unittest

**关键特性**:
- **setUp/tearDown**: 每个测试独立环境
- **临时文件**: tempfile.NamedTemporaryFile
- **断言方法**: assertEqual, assertAlmostEqual, assertIsNone

### 8.4 测试示例代码

```python
class TestSequenceStats(unittest.TestCase):
    def test_gc_content(self):
        """验证GC含量计算正确性"""
        test_sequences = [{'id': 'seq1', 'sequence': 'ATCG', 'length': 4}]
        stats = SequenceStats(test_sequences)
        gc_contents = stats.calculate_gc_content()
        
        # 已知"ATCG"的GC含量是50%
        self.assertAlmostEqual(gc_contents[0], 50.0, places=6)
```

### 8.5 运行测试

```bash
# 详细模式
python -m unittest tests.test_data -v

# 简洁模式
python -m unittest tests.test_data

# 只运行特定测试类
python -m unittest tests.test_data.TestFASTAReader -v
```

### 8.6 测试最佳实践

1. **边界测试**: 包含空序列、极端值测试
2. **独立性**: 每个测试有独立环境(setUp/tearDown)
3. **可读性**: 测试方法名描述清楚测试意图
4. **断言明确**: 使用具体值而非模糊判断

---

## 9. 输出结果说明

### 9.1 输出文件清单

| 文件名 | 类型 | 内容 | 用途 |
|--------|------|------|------|
| deg_results.csv | CSV | 差异表达分析结果 | 显著基因列表 |
| deg_results_with_classification.csv | CSV | ML分类结果 | 预测基因类别 |
| gc_distribution.png | PNG | GC含量分布图 | 序列组成检查 |
| volcano_plot.png | PNG | 差异表达火山图 | DEG可视化 |
| expression_heatmap.png | PNG | 基因表达热图 | 表达模式展示 |
| pca_plot.png | PNG | PCA降维图 | 样本相似性 |

### 9.2 CSV文件详解

#### deg_results.csv (差异表达结果)

**列结构**:
```
gene, log2_fold_change, p_value, corrected_p_value, is_significant, regulation, mean_control, mean_treatment, t_statistic
```

**示例数据**:
```csv
gene_001, 2.5, 0.001, 0.023, True, up, 50.2, 150.8, 3.45
gene_002, -1.8, 0.003, 0.045, True, down, 120.5, 35.2, -2.89
gene_003, 0.2, 0.78, 0.92, False, no_change, 80.1, 85.3, 0.12
```

**解读方法**:
- `is_significant=True`: 满足P值和FC阈值的双重条件
- `regulation='up'`: log2FC>阈值 → 上调
- `regulation='down'`: log2FC<-阈值 → 下调

#### deg_results_with_classification.csv (ML分类结果)

**额外列**:
```
prediction (0=无变化, 1=差异基因)
```

**用途**:
- 对比`is_significant`和`prediction`,验证模型准确性
- 特征重要性排序用于筛选关键指标

### 9.3 图表解读指南

#### GC分布图

**关键元素**:
- **直方图**: GC含量分布(30个区间)
- **KDE曲线**: 平滑的密度估计
- **均值线(红)**: 平均GC含量
- **中位数线(绿)**: GC中位数

**正常表现**: 单峰分布,均值≈中位数

**异常信号**:
- 双峰 → 可能混合物种
- 极端偏斜 → 序列污染

#### 火山图

**坐标轴**:
- **X轴**: log2倍数变化(负=下调,正=上调)
- **Y轴**: -log10(校正P值)(越高越显著)

**颜色编码**:
- **红色点**: 显著上调基因
- **蓝色点**: 显著下调基因
- **灰色点**: 不显著基因

**阈值线**:
- **水平虚线**: P=0.05 → -log10(0.05)=1.3
- **垂直虚线**: log2FC=±1

**理想表现**: 左上和右上区域有密集点群

#### 表达热图

**颜色映射**:
- **红色**: Z-score>0 → 相对该基因高表达
- **蓝色**: Z-score<0 → 相对该基因低表达
- **白色**: Z-score≈0 → 平均水平

**特殊处理**:
- 基因>50时隐藏行标签(避免重叠)
- 样本名(X轴)始终显示

**解读方法**:
- 观察样本聚类 → 处理组与对照组应该分开
- 观察基因模式 → 共表达基因可能功能相似

#### PCA图

**坐标轴**:
- **PC1**: 第一主成分(最大变异方向)
- **PC2**: 第二主成分(次大变异方向)
- **显示**: 各主成分解释方差比例

**理想表现**:
- 对照组样本聚集
- 处理组样本聚集
- 两组分开

**异常信号**:
- 样本离散 → 可能批次效应
- 样本错位 → 分组不合理

---

## 10. 扩展开发指南

### 10.1 添加新分析模块

#### 步骤1: 创建模块目录
```bash
mkdir new_analysis
touch new_analysis/__init__.py
touch new_analysis/new_function.py
```

#### 步骤2: 实现核心类
```python
# new_analysis/new_function.py
class NewAnalyzer:
    def __init__(self, data):
        self.data = data
    
    def analyze(self):
        """实现新分析逻辑"""
        # ...
        return results
```

#### 步骤3: 在main.py中集成
```python
from new_analysis.new_function import NewAnalyzer

def run_new_analysis(data, config, logger):
    analyzer = NewAnalyzer(data)
    results = analyzer.analyze()
    return results

# 在main()函数中调用
def main():
    # ...
    new_results = run_new_analysis(expression_data, config, logger)
```

### 10.2 添加新图表类型

#### 示例: 添加箱线图

```python
# visualization/plots.py

def plot_boxplot(self, data, title="表达量箱线图", output_file=None):
    """绘制样本表达量箱线图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 准备数据(转置:样本作为行)
    data_for_plot = data.T
    
    # 绘制箱线图
    sns.boxplot(data=data_for_plot, ax=ax)
    
    ax.set_title(title)
    ax.set_xlabel('样本')
    ax.set_ylabel('表达量')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    return fig
```

### 10.3 添加新机器学习模型

#### 示例: 添加支持向量机

```python
# machine_learning/classifier.py

from sklearn.svm import SVC

class GeneClassifier:
    def __init__(self, model_type='random_forest'):
        if model_type == 'svm':
            self.model = SVC(kernel='rbf', random_state=42)
        elif model_type == 'random_forest':
            self.model = RandomForestClassifier(...)
```

### 10.4 扩展配置参数

```python
# config.py

@dataclass
class AnalysisConfig:
    # 添加新参数
    new_parameter: float = 0.5
    new_option: str = "option_a"
```

### 10.5 性能优化建议

#### 数据处理优化
- **使用numpy向量化操作**: 避免Python循环
- **分块处理大数据**: 使用utils.chunk_list
- **缓存中间结果**: 保存JSON避免重复计算

#### 并行化改造
```python
from multiprocessing import Pool

def parallel_analysis(gene_list):
    """并行处理基因列表"""
    with Pool(processes=4) as pool:
        results = pool.map(process_gene, gene_list)
    return results
```

#### 内存优化
- **使用生成器**: 避免一次性加载大文件
- **及时释放内存**: del变量、gc.collect()
- **选择合适数据类型**: 使用numpy array而非Python list

### 10.6 待开发功能(参考module_planning.md)

#### 高优先级扩展
```
expression_analysis/
├── correlation.py         # 基因间表达相关性分析
└── clustering.py         # 聚类分析(K-means、层次聚类)

machine_learning/
├── feature_engineering.py # 特征工程(GO富集、KEGG通路)
└── model_evaluation.py    # 模型评估(交叉验证、ROC曲线)

visualization/
├── advanced_plots.py      # 高级图表(箱线图、小提琴图)
└── interactive_plots.py   # 交互式图表(Plotly)
```

#### 中优先级扩展
```
sequence_analysis/
├── motif_finder.py       # 序列基序发现
└── alignment.py          # 序列比对(BLAST接口)

utils/
├── logger.py             # 统一日志配置
└── error_handler.py      # 自定义异常类
```

---

## 附录

### A. 常见问题解答

#### Q1: 程序报错"FASTA文件不存在"
**解决方案**: 检查config.py中fasta_file路径是否正确,确认data目录下有对应文件。

#### Q2: 热图显示为空白
**原因**: 基因数量>50时自动隐藏行标签,这是设计特性而非错误。

#### Q3: 机器学习训练失败
**可能原因**: 样本类别不平衡(某个类<2个样本)。程序会自动处理:关闭分层抽样和类别平衡。

#### Q4: 如何修改分析阈值
**方法**: 编辑config.py或config.ini,调整p_value_threshold和log2_fold_change_threshold。

#### Q5: 如何处理真实数据
**步骤**:
1. 准备FASTA文件(格式:>gene_id\n序列)
2. 准备CSV表达矩阵(行=基因,列=样本)
3. 修改config.py中的文件路径
4. 运行python main.py

### B. 性能参考数据

**测试环境**: Windows 10, Python 3.10, 16GB RAM

| 数据规模 | 序列分析耗时 | 差异分析耗时 | ML训练耗时 | 总耗时 |
|---------|-------------|-------------|-----------|--------|
| 100基因 | 0.5秒 | 1秒 | 2秒 | 5秒 |
| 1000基因 | 2秒 | 5秒 | 10秒 | 20秒 |
| 10000基因 | 15秒 | 30秒 | 60秒 | 120秒 |

### C. 版本更新历史

**v1.0 (2026-06-30)**:
- 完成核心分析流程
- 实现4种可视化图表
- 添加详细中文注释
- 完成单元测试覆盖

---

## 文档维护

**维护者**: LJM  
**联系方式**: 见项目仓库  
**文档位置**: `d:\LJM\Python学习\GeneAnalysis\CODE_WIKI.md`  
**最后修订**: 2026-06-30  

---

**感谢使用GeneAnalysis平台!**

如有问题或建议,欢迎反馈。祝您科研顺利! 🎉