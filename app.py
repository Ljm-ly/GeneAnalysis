# -*- coding: utf-8 -*-
"""
基因表达调控分析与预测平台 - Streamlit Web应用

什么是Streamlit？
    Streamlit是一个Python的Web应用框架，专门用于数据科学和机器学习。
    它的特点是：
    - 不需要懂HTML/CSS/JavaScript，纯Python就能写网页
    - 自动处理UI组件（按钮、滑块、表格、图表等）
    - 自动刷新页面（交互响应式）
    - 非常适合快速搭建数据分析工具的原型

这个文件是Web应用的主入口，负责：
1. 页面整体布局和侧边栏导航
2. 全局状态管理（Session State，页面间共享数据）
3. 5个功能页面的切换和渲染

应用包含5个页面：
    🏠 首页      - 欢迎界面和功能介绍
    ⚙️ 数据配置  - 上传数据、设置分析参数、配置样本分组
    🚀 运行分析  - 一键执行完整分析流程，实时显示进度
    📊 结果展示  - 查看图表、表格、机器学习结果
    📥 下载结果  - 导出CSV表格和高清PNG图表

运行方式：
    streamlit run app.py
    然后浏览器会自动打开应用界面
"""

# ==================== 标准库导入 ====================
# os模块：操作系统接口，用于文件路径、目录操作
import os
# sys模块：系统相关功能，用于修改Python搜索路径、退出程序等
import sys
# tempfile模块：临时文件管理，用于处理用户上传的文件
import tempfile
# io模块：内存中的IO操作，用于在内存中读写数据（不写入磁盘）
import io
# base64模块：Base64编码，用于将图片转成字符串在网页中显示
import base64

# ==================== 第三方库导入 ====================
# streamlit：Web应用框架，所有的网页UI都通过这个库实现
# 约定俗成的别名是 st，这样写代码更简洁
import streamlit as st
# pandas：数据分析库，提供DataFrame（类似Excel表格）数据结构
import pandas as pd
# numpy：数值计算基础库，提供高效的数组运算
import numpy as np
# matplotlib.pyplot：绘图库，pyplot是其命令式接口
import matplotlib.pyplot as plt
# matplotlib的顶层模块，用于设置后端（backend）
import matplotlib
# font_manager：字体管理模块，用于动态加载自定义字体文件
import matplotlib.font_manager as fm

# 设置matplotlib使用非交互式后端（Agg）
# 什么是后端？
#   后端决定了图表在哪里渲染（显示窗口/保存文件/网页等）
# 为什么用'Agg'？
#   Streamlit运行在服务器上，没有图形界面
#   Agg后端可以生成图片文件，但不会弹出显示窗口
#   如果用默认后端，在服务器上可能会报错
matplotlib.use('Agg')

# 设置matplotlib中文字体，防止中文显示为方框（豆腐块）
# 问题原因：Streamlit Cloud服务器是Linux系统，默认没有中文字体
# 解决方案：使用内嵌字体文件（打包在项目中），动态加载

# 获取字体文件路径
# __file__是当前文件（app.py）的路径
# os.path.dirname获取目录路径
# os.path.join拼接路径
font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'simhei.ttf')

# 检查字体文件是否存在
if os.path.exists(font_path):
    # 动态加载字体文件到matplotlib
    # addfont()会把字体添加到matplotlib的字体管理器中
    fm.fontManager.addfont(font_path)
    # 获取字体属性
    font_prop = fm.FontProperties(fname=font_path)
    # 设置字体名称（使用字体的family name）
    plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
    # 设置默认字体
    plt.rcParams['font.family'] = font_prop.get_name()
    print(f"✅ 成功加载内嵌字体: {font_prop.get_name()}")
else:
    # 如果字体文件不存在，使用系统字体作为备选
    plt.rcParams['font.sans-serif'] = [
        'Noto Sans CJK SC',      # Google开源中文字体
        'Noto Sans CJK',          # Noto Sans CJK通用
        'WenQuanYi Micro Hei',    # 文泉驿微米黑
        'DejaVu Sans',            # 支持Unicode的通用字体
        'SimHei',                 # 黑体（Windows）
        'Microsoft YaHei',        # 微软雅黑（Windows）
        'Arial Unicode MS',       # Mac系统
        'PingFang SC'             # Mac系统
    ]
    print(f"⚠️ 字体文件不存在({font_path})，使用系统字体")

# axes.unicode_minus：解决负号"-"显示为方块的问题
#   False表示使用Unicode负号，可以正常显示
plt.rcParams['axes.unicode_minus'] = False

# ==================== 项目自定义模块导入 ====================
# 将当前文件所在目录添加到Python搜索路径的最前面
# 作用：确保能正确导入项目中的其他模块（config、data_processing等）
# 为什么需要这行？
#   因为Streamlit运行时的工作目录可能和项目目录不同
#   显式添加路径可以避免导入失败
#
# 解释一下这一串：
#   __file__                    : 当前文件的路径（app.py）
#   os.path.abspath(__file__)   : 转成绝对路径
#   os.path.dirname(...)        : 获取所在目录（去掉文件名）
#   sys.path.insert(0, ...)     : 插到搜索路径最前面
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入项目的各个功能模块
from config import AnalysisConfig                     # 配置管理类
from data_processing.fasta_reader import FASTAReader   # FASTA文件读取器
from sequence_analysis.basic_stats import SequenceStats  # 序列统计分析
from expression_analysis.differential import DiffExpAnalyzer  # 差异表达分析
from machine_learning.classifier import GeneClassifier  # 机器学习分类器
from visualization.plots import PlotGenerator          # 图表生成器


# ==================================================
# 页面全局配置（必须是第一个Streamlit命令！）
# ==================================================
# st.set_page_config() 必须在所有其他Streamlit命令之前调用
# 否则会报错。它设置网页的基本属性。
st.set_page_config(
    # 浏览器标签页上显示的标题
    page_title="基因表达调控分析与预测平台",
    # 标签页图标（可以用emoji，也可以用图片路径）
    # 🧬 是DNA双螺旋的emoji，很适合基因分析项目
    page_icon="🧬",
    # 页面布局模式：
    #   "centered" - 居中布局，内容区域较窄（默认）
    #   "wide" - 宽屏布局，充分利用屏幕宽度
    # 数据分析类应用推荐用wide，因为图表和表格需要更多空间
    layout="wide",
    # 侧边栏初始状态：
    #   "expanded" - 默认展开（显示菜单）
    #   "collapsed" - 默认收起
    #   "auto" - 自动根据屏幕宽度决定
    initial_sidebar_state="expanded"
)


# ==================================================
# 会话状态初始化函数
# ==================================================
def init_session_state():
    """
    初始化Streamlit会话状态（Session State）

    什么是Session State？
        Streamlit的工作原理是：每次用户交互（点击按钮、拖动滑块），
        整个脚本都会从头到尾重新运行一遍。
        这意味着普通变量会在每次重运行时被重置。

        Session State是一个特殊的字典（st.session_state），
        它的数据会在多次运行之间保留，就像"全局变量"一样。

    为什么需要Session State？
        - 保存用户上传的数据（不会因为点了按钮就丢失）
        - 在不同页面之间共享数据
        - 记录分析是否完成的状态
        - 累积日志消息

    存储的内容说明：
        uploaded_fasta      : 上传的FASTA序列数据（列表，每个元素是字典）
        uploaded_expression : 上传的表达矩阵（pandas DataFrame）
        config              : 分析配置对象（AnalysisConfig实例）
        analysis_results    : 所有分析结果的字典
            - sequences       : 序列列表
            - expression_data : 表达数据
            - seq_results     : 序列分析结果（GC含量、核苷酸频率等）
            - deg_results     : 差异表达分析结果（DataFrame）
            - ml_results      : 机器学习训练结果（字典）
            - plots           : 生成的图表字典（key=图表名, value=Figure对象）
        analysis_done       : 分析是否完成的布尔标记
        log_messages        : 日志消息列表（每条是{message, level}字典）
        control_samples     : 对照组样本名列表
        treatment_samples   : 处理组样本名列表
    """
    # 检查每个键是否存在，不存在就设置默认值
    # 用 if ... not in st.session_state 判断，避免重复初始化

    # FASTA序列数据
    if 'uploaded_fasta' not in st.session_state:
        st.session_state.uploaded_fasta = None

    # 表达矩阵数据
    if 'uploaded_expression' not in st.session_state:
        st.session_state.uploaded_expression = None

    # 分析配置
    if 'config' not in st.session_state:
        # 使用默认配置创建一个配置对象
        st.session_state.config = AnalysisConfig()

    # 分析结果集合
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {
            'sequences': None,        # 序列列表
            'expression_data': None,  # 表达数据
            'seq_results': None,      # 序列分析结果
            'deg_results': None,      # 差异表达结果
            'ml_results': None,       # 机器学习结果
            'plots': {}               # 图表（空字典，后续填充）
        }

    # 分析完成标记
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False

    # 日志消息列表
    if 'log_messages' not in st.session_state:
        st.session_state.log_messages = []

    # 对照组样本列表
    if 'control_samples' not in st.session_state:
        st.session_state.control_samples = []

    # 处理组样本列表
    if 'treatment_samples' not in st.session_state:
        st.session_state.treatment_samples = []


# ==================================================
# 工具函数：日志
# ==================================================
def add_log(message: str, level: str = "info"):
    """
    添加一条日志消息到会话状态

    为什么不直接用print()？
        - Streamlit界面中print()只会输出到终端，不会显示在网页上
        - 我们把日志存到session_state里，可以在"运行分析"页面显示

    Args:
        message: 日志消息内容（字符串）
        level: 日志级别，可选值：
            - "info"    : 普通信息（蓝色）
            - "success" : 成功消息（绿色）
            - "warning" : 警告消息（黄色）
            - "error"   : 错误消息（红色）
    """
    # 追加到日志列表中
    # 每条消息是一个字典，包含内容和级别
    st.session_state.log_messages.append({
        'message': message,
        'level': level
    })


# ==================================================
# 工具函数：图片转换
# ==================================================
def fig_to_base64(fig) -> str:
    """
    将matplotlib图表转换为Base64编码的字符串

    什么是Base64？
        一种将二进制数据（如图片）编码成文本字符串的方法。
        编码后可以直接嵌入到HTML中显示，不需要单独的图片文件。

    用途：
        - 可以直接在HTML的<img>标签中显示
        - 可以在页面间传递图片数据
        - 可以保存到session_state中

    Args:
        fig: matplotlib的Figure对象（图表对象）

    Returns:
        str: Base64编码的PNG图片字符串
            可以直接用在 <img src="data:image/png;base64,{字符串}"> 中
    """
    # 创建一个内存中的字节缓冲区
    # BytesIO就像一个虚拟文件，存在内存里而不是磁盘上
    buf = io.BytesIO()

    # 将图表保存到缓冲区，格式为PNG
    # dpi=150：150像素每英寸，网页显示足够清晰
    # bbox_inches='tight'：紧凑布局，去掉多余的白边
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')

    # 将文件指针移动到开头（准备读取）
    # 因为写完之后指针在末尾，需要回到开头才能读
    buf.seek(0)

    # 读取缓冲区的字节内容，并用Base64编码
    # base64.b64encode() 返回的是bytes，需要decode()转成字符串
    img_str = base64.b64encode(buf.read()).decode()

    # 关闭缓冲区（释放内存）
    buf.close()

    # 关闭图表对象，释放内存
    # matplotlib的图表如果不关闭，会占用大量内存
    plt.close(fig)

    return img_str


def fig_to_bytes(fig) -> bytes:
    """
    将matplotlib图表转换为PNG格式的字节数据

    和fig_to_base64的区别：
        - fig_to_base64：返回字符串，用于在网页中显示
        - fig_to_bytes：返回二进制字节，用于下载文件

    用途：
        用于Streamlit的下载按钮（st.download_button），
        让用户可以把图表保存到本地。

    Args:
        fig: matplotlib的Figure对象

    Returns:
        bytes: PNG图片的二进制字节数据
    """
    # 创建内存缓冲区
    buf = io.BytesIO()

    # 保存图表到缓冲区，300 DPI高清（适合打印/论文）
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')

    # 指针移到开头
    buf.seek(0)

    # 读取全部字节
    img_bytes = buf.read()

    # 关闭缓冲区
    buf.close()

    # 关闭图表，释放内存
    plt.close(fig)

    return img_bytes


# ==================================================
# 页面1：🏠 首页
# ==================================================
def show_home_page():
    """
    显示首页 - 欢迎界面和功能介绍

    页面内容：
        1. 主标题和欢迎语
        2. 四大核心功能介绍卡片（四列布局）
        3. 使用流程说明（表格形式）
        4. 快速体验提示

    Streamlit布局技巧：
        - st.title()     : 一级标题
        - st.markdown()  : Markdown格式文本，支持表格、加粗、链接等
        - st.columns()   : 多列布局
        - st.info()      : 蓝色信息框
        - st.success()   : 绿色成功框
        - st.warning()   : 黄色警告框
        - st.error()     : 红色错误框
    """
    # 页面主标题
    st.title("🧬 基因表达调控分析与预测平台")

    # 分隔线（Markdown语法，--- 表示水平线）
    st.markdown("---")

    # ===== 欢迎区域 =====
    st.markdown("""
    ### 👋 欢迎使用

    本平台是一个功能完整的基因表达数据分析工具，集成了**序列分析**、**差异表达分析**、
    **可视化**和**机器学习预测**四大核心功能。无论您是生物信息学研究者还是学生，
    都可以通过简单的几步操作完成专业级的基因表达分析。
    """)

    # ===== 核心功能卡片（四列布局） =====
    st.markdown("### 📦 核心功能")

    # 创建4列，每列放一个功能卡片
    col1, col2, col3, col4 = st.columns(4)

    # 第1列：序列分析
    with col1:
        # st.info() 显示蓝色背景的信息框
        st.info("""
        **🔬 序列分析**
        - GC含量计算
        - 核苷酸频率统计
        - 序列长度分布
        """)

    # 第2列：差异表达分析
    with col2:
        # st.success() 显示绿色背景的成功框
        st.success("""
        **📊 差异表达分析**
        - t检验统计分析
        - BH-FDR多重校正
        - 上调/下调基因识别
        """)

    # 第3列：可视化图表
    with col3:
        # st.warning() 显示黄色背景的警告框
        st.warning("""
        **📈 可视化图表**
        - 火山图
        - 表达热图
        - PCA主成分分析
        - GC含量分布图
        """)

    # 第4列：机器学习
    with col4:
        # st.error() 显示红色背景的错误框
        st.error("""
        **🤖 机器学习**
        - 随机森林分类
        - 特征重要性分析
        - 模型性能评估
        """)

    # ===== 使用流程表格 =====
    st.markdown("### 🚀 使用流程")

    # Markdown表格语法：
    # | 列标题1 | 列标题2 |
    # |---------|---------|  （分隔线，至少3个减号）
    # | 内容1   | 内容2   |
    st.markdown("""
    | 步骤 | 操作 | 说明 |
    |------|------|------|
    | 1️⃣ | **数据配置** | 上传FASTA序列文件和表达矩阵CSV，设置分析参数 |
    | 2️⃣ | **运行分析** | 点击开始按钮，系统自动执行完整分析流程 |
    | 3️⃣ | **查看结果** | 在结果页面浏览各类图表和统计数据 |
    | 4️⃣ | **下载结果** | 导出分析结果表格和高质量图表 |
    """)

    # ===== 快速体验提示 =====
    st.markdown("### 💡 快速体验")
    st.info("""
    系统内置了示例数据，您可以直接在【数据配置】页面选择"使用示例数据"来快速体验完整分析流程！
    """)


# ==================================================
# 页面2：⚙️ 数据配置
# ==================================================
def show_config_page():
    """
    显示数据配置页面

    这是用户使用的第一步，需要完成3件事：
        1. 上传数据（或使用示例数据）
        2. 设置分析参数
        3. 配置样本分组（对照组vs处理组）

    页面分为三个部分（用 st.header() 分隔）：
        第一部分：数据上传
        第二部分：分析参数设置
        第三部分：样本分组配置
    """
    # 页面标题
    st.title("⚙️ 数据配置")
    st.markdown("---")

    # 从session_state获取当前配置
    # 注意：这里取的是引用，对config的修改会直接反映到session_state中
    config = st.session_state.config

    # ============================================================
    # 第一部分：数据上传
    # ============================================================
    st.header("📁 数据上传")

    # 使用示例数据的复选框
    # 勾选后自动加载系统内置的模拟数据，方便用户快速体验
    use_sample_data = st.checkbox(
        "使用内置示例数据（快速体验）",
        value=False,
        help="勾选后将使用系统内置的模拟数据，无需上传文件"
    )

    # 如果勾选了使用示例数据
    if use_sample_data:
        st.success("✅ 已选择使用示例数据")

        # 设置示例数据的文件路径到配置中
        config.fasta_file = "data/simulated_genes.fasta"
        config.expression_file = "data/simulated_expression.csv"

        # 读取示例数据到session_state
        try:
            # 读取FASTA序列
            reader = FASTAReader(config.fasta_file)
            st.session_state.uploaded_fasta = reader.read_all()
            st.info(f"📋 已加载 {len(st.session_state.uploaded_fasta)} 条基因序列")

            # 读取表达矩阵（index_col=0表示第一列是行索引，即基因名）
            expr_data = pd.read_csv(config.expression_file, index_col=0)
            st.session_state.uploaded_expression = expr_data
            st.info(
                f"📊 已加载表达矩阵："
                f"{expr_data.shape[0]} 个基因，"
                f"{expr_data.shape[1]} 个样本"
            )
        except Exception as e:
            # 加载失败时显示错误
            st.error(f"加载示例数据失败：{e}")

    # 没有勾选示例数据，就显示上传组件让用户自己上传
    else:
        # 两列布局：左列上传FASTA，右列上传表达矩阵
        col1, col2 = st.columns(2)

        # ---- 左列：FASTA序列文件上传 ----
        with col1:
            st.subheader("FASTA序列文件")

            # 文件上传组件
            # key参数确保uploader的稳定性，防止重复创建
            fasta_file = st.file_uploader(
                "上传FASTA格式的序列文件",
                type=['fasta', 'fa', 'txt'],
                help="FASTA格式：以>开头的标题行，后跟序列",
                key="fasta_uploader"
            )

            # 如果用户上传了文件（fasta_file不为None）
            if fasta_file is not None:
                try:
                    # 关键修复：检查session_state中是否已经有这个文件的内容
                    # 通过比较文件名和大小来判断是否是新文件
                    current_file_key = f"{fasta_file.name}_{fasta_file.size}"
                    if st.session_state.get('last_fasta_key') != current_file_key:
                        # 步骤1：读取文件内容
                        # 使用getvalue()一次性读取全部内容，避免游标消耗问题
                        # 这是关键修复：getvalue()不会移动文件指针，比read()更安全
                        fasta_content = fasta_file.getvalue().decode('utf-8')

                        # 步骤2：保存到临时文件
                        # 因为FASTAReader需要从文件读取，而不是从字符串
                        with tempfile.NamedTemporaryFile(
                            mode='w',
                            suffix='.fasta',
                            delete=False,
                            encoding='utf-8'
                        ) as f:
                            f.write(fasta_content)
                            temp_fasta_path = f.name

                        # 步骤3：用FASTAReader读取序列
                        reader = FASTAReader(temp_fasta_path)
                        sequences = reader.read_all()

                        # 步骤4：保存到session_state
                        st.session_state.uploaded_fasta = sequences
                        config.fasta_file = temp_fasta_path
                        
                        # 记录当前文件的key，用于判断是否需要重新处理
                        st.session_state.last_fasta_key = current_file_key

                        # 步骤5：显示成功信息
                        st.success(f"✅ 成功读取 {len(sequences)} 条序列")

                        # 显示前3条序列的信息
                        for i, seq in enumerate(sequences[:3]):
                            st.text(f"  {i+1}. {seq['id']} (长度: {seq['length']} bp)")
                        if len(sequences) > 3:
                            st.text(f"  ... 还有 {len(sequences)-3} 条序列")
                    else:
                        # 文件没有变化，显示已加载的信息
                        sequences = st.session_state.uploaded_fasta
                        st.success(f"✅ FASTA数据已加载：{len(sequences)} 条序列")

                except Exception as e:
                    # 读取失败，显示错误信息
                    st.error(f"❌ 读取FASTA文件失败：{e}")
                    # 清除状态，允许重新上传
                    if 'last_fasta_key' in st.session_state:
                        del st.session_state.last_fasta_key

        # ---- 右列：基因表达矩阵上传 ----
        with col2:
            st.subheader("基因表达矩阵")

            # 文件上传组件（只接受CSV格式）
            expr_file = st.file_uploader(
                "上传CSV格式的表达矩阵",
                type=['csv'],
                help="行=基因，列=样本，第一列为基因名",
                key="expr_uploader"
            )

            # 如果用户上传了文件
            if expr_file is not None:
                try:
                    # 关键修复：检查session_state中是否已经有这个文件的内容
                    current_file_key = f"{expr_file.name}_{expr_file.size}"
                    if st.session_state.get('last_expr_key') != current_file_key:
                        # 步骤1：直接用pandas读取CSV
                        # 关键修复：使用read_csv直接从UploadedFile对象读取
                        # 但为了防止游标问题，先读取到内存
                        expr_file.seek(0)  # 重置文件指针到开头
                        expr_data = pd.read_csv(expr_file, index_col=0)

                        # 步骤2：保存到session_state
                        st.session_state.uploaded_expression = expr_data

                        # 步骤3：同时保存到临时文件（供差异分析模块使用）
                        with tempfile.NamedTemporaryFile(
                            mode='w',
                            suffix='.csv',
                            delete=False,
                            encoding='utf-8'
                        ) as f:
                            expr_data.to_csv(f)
                            temp_expr_path = f.name

                        # 保存路径到配置
                        config.expression_file = temp_expr_path
                        
                        # 记录当前文件的key
                        st.session_state.last_expr_key = current_file_key

                        # 步骤4：显示成功信息和数据概况
                        st.success(f"✅ 成功读取表达矩阵")
                        st.info(f"  基因数量：{expr_data.shape[0]} 个")
                        st.info(f"  样本数量：{expr_data.shape[1]} 个")
                        # 显示前5个样本名，太多的话用省略号
                        st.info(
                            f"  样本名称：{', '.join(expr_data.columns.tolist()[:5])} ..."
                        )
                    else:
                        # 文件没有变化，显示已加载的信息
                        expr_data = st.session_state.uploaded_expression
                        st.success(f"✅ 表达数据已加载：{expr_data.shape[0]} 个基因")

                except Exception as e:
                    # 读取失败，显示错误信息
                    st.error(f"❌ 读取表达矩阵失败：{e}")
                    # 清除状态，允许重新上传
                    if 'last_expr_key' in st.session_state:
                        del st.session_state.last_expr_key

    st.markdown("---")

    # ============================================================
    # 第二部分：分析参数设置
    # ============================================================
    st.header("🔬 分析参数设置")

    # 两列布局：左列差异分析参数，右列机器学习参数
    col1, col2 = st.columns(2)

    # ---- 左列：差异表达分析参数 ----
    with col1:
        st.subheader("差异表达分析")

        # P值阈值滑块
        # min_value / max_value：范围
        # value：默认值（从config读取当前值）
        # step：步长
        # format：显示格式（%.3f表示3位小数）
        config.p_value_threshold = st.slider(
            "P值阈值（显著性水平）",
            min_value=0.001,
            max_value=0.1,
            value=float(config.p_value_threshold),
            step=0.001,
            format="%.3f",
            help="校正后P值小于此阈值的基因被认为是显著差异基因"
        )

        # log2倍数变化阈值滑块
        config.log2_fold_change_threshold = st.slider(
            "log2倍数变化阈值",
            min_value=0.0,
            max_value=3.0,
            value=float(config.log2_fold_change_threshold),
            step=0.1,
            format="%.1f",
            help="|log2FC|大于此阈值的基因被认为有生物学意义的变化。1.0对应2倍变化"
        )

        # GC窗口大小（数字输入框）
        # min_value / max_value：范围
        # step：步长
        config.gc_window_size = st.number_input(
            "GC含量分析窗口大小（bp）",
            min_value=10,
            max_value=500,
            value=int(config.gc_window_size),
            step=10,
            help="滑动窗口大小用于计算GC含量分布"
        )

    # ---- 右列：机器学习参数 ----
    with col2:
        st.subheader("机器学习参数")

        # 测试集比例
        config.test_size = st.slider(
            "测试集比例",
            min_value=0.1,
            max_value=0.5,
            value=float(config.test_size),
            step=0.05,
            help="用于测试模型性能的数据比例"
        )

        # 决策树数量
        config.n_estimators = st.slider(
            "随机森林决策树数量",
            min_value=10,
            max_value=500,
            value=int(config.n_estimators),
            step=10,
            help="决策树越多，结果越稳定，但计算越慢"
        )

        # 随机种子
        config.random_state = st.number_input(
            "随机种子",
            min_value=0,
            max_value=9999,
            value=int(config.random_state),
            step=1,
            help="固定随机种子可以保证结果可复现"
        )

    st.markdown("---")

    # ============================================================
    # 第三部分：样本分组配置
    # ============================================================
    st.header("📋 样本分组配置")

    # 只有上传了表达数据，才能配置样本分组
    if st.session_state.uploaded_expression is not None:
        # 获取表达数据
        expr_data = st.session_state.uploaded_expression
        # 获取所有样本名（DataFrame的列名）
        all_samples = expr_data.columns.tolist()

        # 显示检测到的样本信息
        st.info(f"检测到 {len(all_samples)} 个样本：{', '.join(all_samples)}")

        # 两列布局：左列选对照组，右列选处理组
        col1, col2 = st.columns(2)

        # ---- 左列：对照组样本选择 ----
        with col1:
            st.subheader("对照组样本")

            # 自动猜测对照组：列名包含"control"的
            default_control = [s for s in all_samples if 'control' in s.lower()]

            # 多选组件
            # options：可选的选项（所有样本）
            # default：默认选中的
            control_samples = st.multiselect(
                "选择对照组样本",
                options=all_samples,
                default=default_control if default_control else all_samples[:len(all_samples)//2],
                help="对照组（如正常/未处理的样本）"
            )
            # 保存到session_state
            st.session_state.control_samples = control_samples

        # ---- 右列：处理组样本选择 ----
        with col2:
            st.subheader("处理组样本")

            # 自动猜测处理组：不在对照组里的都是处理组
            default_treatment = [s for s in all_samples if s not in default_control]

            treatment_samples = st.multiselect(
                "选择处理组样本",
                options=all_samples,
                default=default_treatment if default_treatment else all_samples[len(all_samples)//2:],
                help="处理组（如疾病/药物处理的样本）"
            )
            # 保存到session_state
            st.session_state.treatment_samples = treatment_samples

        # ---- 分组验证 ----
        # 检查分组是否合法
        if len(control_samples) == 0 or len(treatment_samples) == 0:
            # 至少一组没有样本
            st.warning("⚠️ 请至少为每组选择1个样本")
        elif len(set(control_samples) & set(treatment_samples)) > 0:
            # 两组有重叠的样本（不允许）
            # set() 转成集合后用 & 求交集
            st.error("❌ 对照组和处理组不能有相同的样本")
        else:
            # 分组配置正确
            st.success(
                f"✅ 分组配置完成："
                f"对照组 {len(control_samples)} 个，"
                f"处理组 {len(treatment_samples)} 个"
            )

    else:
        # 还没有上传数据，提示用户
        st.info("💡 请先上传表达矩阵数据，再配置样本分组")

    # ===== 保存配置按钮 =====
    st.markdown("---")

    # type="primary"：主要按钮（蓝色，更醒目）
    # use_container_width=True：按钮占满整列宽度
    if st.button("💾 保存配置并继续", type="primary", use_container_width=True):
        # 点击按钮后验证配置是否完整

        # 检查1：FASTA数据是否上传
        if st.session_state.uploaded_fasta is None:
            st.error("❌ 请先上传FASTA序列文件")
        # 检查2：表达数据是否上传
        elif st.session_state.uploaded_expression is None:
            st.error("❌ 请先上传表达矩阵数据")
        # 检查3：对照组是否配置
        elif len(st.session_state.get('control_samples', [])) == 0:
            st.error("❌ 请配置对照组样本")
        # 检查4：处理组是否配置
        elif len(st.session_state.get('treatment_samples', [])) == 0:
            st.error("❌ 请配置处理组样本")
        else:
            # 所有检查通过
            st.success("✅ 配置已保存！请前往【运行分析】页面开始分析")
            # 放气球动画，增加趣味性
            st.balloons()


# ==================================================
# 页面3：🚀 运行分析
# ==================================================
def show_analysis_page():
    """
    显示运行分析页面

    功能：
        1. 显示当前配置摘要（可折叠展开）
        2. 开始/重新分析按钮
        3. 进度条显示（4个步骤的进度）
        4. 实时日志输出（不同级别不同颜色）

    核心：点击按钮后调用 run_full_analysis() 函数执行分析
    """
    st.title("🚀 运行分析")
    st.markdown("---")

    # 检查是否已配置数据
    # 如果FASTA或表达数据为空，提示用户先去配置
    if st.session_state.uploaded_fasta is None or st.session_state.uploaded_expression is None:
        st.warning("⚠️ 请先在【数据配置】页面上传数据并设置参数")
        # return 直接结束函数，不显示后面的内容
        return

    # 从session_state获取配置和结果
    config = st.session_state.config
    results = st.session_state.analysis_results

    # ===== 配置摘要（可折叠面板） =====
    # st.expander() 创建一个可展开/折叠的区域
    # expanded=True：默认展开
    with st.expander("📋 当前配置摘要", expanded=True):
        # 三列布局显示配置信息
        col1, col2, col3 = st.columns(3)

        # 第1列：数据信息
        with col1:
            st.markdown("**数据信息**")
            # 序列数量（用三元表达式处理None的情况）
            n_seqs = len(st.session_state.uploaded_fasta) if st.session_state.uploaded_fasta else 0
            # 基因数量（shape[0]是行数）
            n_genes = st.session_state.uploaded_expression.shape[0] if st.session_state.uploaded_expression is not None else 0
            # 样本数量（shape[1]是列数）
            n_samples = st.session_state.uploaded_expression.shape[1] if st.session_state.uploaded_expression is not None else 0
            st.write(f"序列数量：{n_seqs} 条")
            st.write(f"基因数量：{n_genes} 个")
            st.write(f"样本数量：{n_samples} 个")

        # 第2列：分析参数
        with col2:
            st.markdown("**分析参数**")
            st.write(f"P值阈值：{config.p_value_threshold}")
            st.write(f"log2FC阈值：{config.log2_fold_change_threshold}")
            st.write(f"GC窗口大小：{config.gc_window_size} bp")

        # 第3列：样本分组
        with col3:
            st.markdown("**样本分组**")
            # 用 .get() 获取，避免键不存在时报错
            control = st.session_state.get('control_samples', [])
            treatment = st.session_state.get('treatment_samples', [])
            st.write(f"对照组：{len(control)} 个")
            st.write(f"处理组：{len(treatment)} 个")

    # ===== 开始分析按钮 =====
    st.markdown("### ▶️ 开始分析")

    # 如果分析还没完成，显示"开始分析"按钮
    if not st.session_state.analysis_done:
        # 点击按钮就执行完整分析
        if st.button("🔬 开始完整分析流程", type="primary", use_container_width=True):
            run_full_analysis()

    # 如果分析已经完成，显示成功提示和"重新运行"按钮
    else:
        st.success("✅ 分析已完成！可以在【结果展示】页面查看结果")
        if st.button("🔄 重新运行分析", use_container_width=True):
            # 重置所有状态
            st.session_state.analysis_done = False
            st.session_state.log_messages = []
            st.session_state.analysis_results = {
                'sequences': None,
                'expression_data': None,
                'seq_results': None,
                'deg_results': None,
                'ml_results': None,
                'plots': {}
            }
            # 强制重新运行脚本（刷新页面）
            st.rerun()

    # ===== 日志输出区域 =====
    st.markdown("### 📝 分析日志")

    # 如果有日志消息，逐条显示
    if st.session_state.log_messages:
        # 创建一个容器来放日志
        log_container = st.container()
        with log_container:
            for log in st.session_state.log_messages:
                # 根据级别用不同的显示方式
                if log['level'] == 'success':
                    st.success(log['message'])
                elif log['level'] == 'error':
                    st.error(log['message'])
                elif log['level'] == 'warning':
                    st.warning(log['message'])
                else:
                    # 默认info级别
                    st.info(log['message'])
    else:
        # 还没有日志
        st.info("💡 点击上方按钮开始分析，日志将显示在这里")


# ==================================================
# 核心分析函数：执行完整分析流程
# ==================================================
def run_full_analysis():
    """
    执行完整的分析流程（4个步骤）

    这是Web版的"main"函数，和命令行版的main.py功能类似，
    但输出方式不同：
    - 命令行版：打印到终端，结果保存到文件
    - Web版：显示到网页，结果存在session_state中

    分析步骤：
        1. 序列基础统计分析（GC含量、核苷酸频率）
        2. 差异表达分析（t检验 + FDR校正）
        3. 生成可视化图表（4种图表）
        4. 机器学习基因分类（随机森林）

    每一步都会：
        - 更新进度条
        - 添加日志消息
        - 保存结果到 session_state
    """
    # 从session_state获取需要的数据
    config = st.session_state.config
    results = st.session_state.analysis_results
    control_samples = st.session_state.get('control_samples', [])
    treatment_samples = st.session_state.get('treatment_samples', [])

    # 清空之前的日志
    st.session_state.log_messages = []
    add_log("🚀 基因表达调控分析与预测平台启动", "info")
    add_log("=" * 50, "info")

    # 创建进度条组件
    # 进度条的值从0到1（0%到100%）
    progress_bar = st.progress(0)

    # 创建一个空的文本占位符，用来显示当前步骤
    # st.empty() 创建一个"槽"，后面可以随时更新它的内容
    status_text = st.empty()

    try:
        # ==================== 步骤1：序列分析 ====================
        status_text.text("步骤 1/4：序列基础统计分析...")
        progress_bar.progress(10)  # 10%进度
        add_log("📊 第一步：序列基础统计分析", "info")

        # 获取序列数据
        sequences = st.session_state.uploaded_fasta
        results['sequences'] = sequences

        # 创建序列统计分析器
        stats = SequenceStats(sequences)

        # 计算GC含量（每条序列一个值）
        gc_contents = stats.calculate_gc_content()
        # 计算核苷酸频率（总体A/T/G/C比例）
        nucleotide_freq = stats.calculate_nucleotide_frequencies()
        # 计算平均GC含量（所有序列的平均值）
        # 用三目运算符处理空列表的情况（避免除以0）
        avg_gc = sum(gc_contents) / len(gc_contents) if gc_contents else 0

        # 保存序列分析结果
        results['seq_results'] = {
            'gc_contents': gc_contents,
            'nucleotide_freq': nucleotide_freq,
            'avg_gc': avg_gc
        }

        add_log(f"✅ 序列统计分析完成", "success")
        add_log(f"   平均GC含量: {avg_gc:.2f}%", "info")

        # ==================== 步骤2：差异表达分析 ====================
        status_text.text("步骤 2/4：差异表达分析...")
        progress_bar.progress(35)  # 35%进度
        add_log("🔬 第二步：差异表达分析", "info")

        # 获取表达数据
        expression_data = st.session_state.uploaded_expression
        results['expression_data'] = expression_data

        # 差异表达分析器需要从文件读取数据
        # 所以先把表达数据保存到临时文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.csv',
            delete=False,
            encoding='utf-8'
        ) as f:
            expression_data.to_csv(f)
            temp_expr_path = f.name

        # 创建差异表达分析器
        analyzer = DiffExpAnalyzer(temp_expr_path)

        # 记录参数信息
        add_log(f"   对照组样本: {control_samples}", "info")
        add_log(f"   处理组样本: {treatment_samples}", "info")
        add_log(f"   P值阈值: {config.p_value_threshold}", "info")
        add_log(f"   log2FC阈值: {config.log2_fold_change_threshold}", "info")

        # 执行差异表达分析（核心步骤）
        deg_results = analyzer.analyze(
            group1_cols=control_samples,
            group2_cols=treatment_samples,
            p_threshold=config.p_value_threshold,
            log2fc_threshold=config.log2_fold_change_threshold
        )

        # 保存结果
        results['deg_results'] = deg_results

        # 统计结果
        n_significant = deg_results['is_significant'].sum()
        n_up = len(deg_results[deg_results['regulation'] == 'up'])
        n_down = len(deg_results[deg_results['regulation'] == 'down'])

        add_log(f"✅ 差异表达分析完成", "success")
        add_log(f"   总基因数: {len(deg_results)}", "info")
        add_log(f"   显著差异基因: {n_significant} 个", "info")
        add_log(f"     上调基因: {n_up} 个", "info")
        add_log(f"     下调基因: {n_down} 个", "info")

        # ==================== 步骤3：生成可视化图表 ====================
        status_text.text("步骤 3/4：生成可视化图表...")
        progress_bar.progress(65)  # 65%进度
        add_log("📈 第三步：生成可视化图表", "info")

        # 创建图表生成器
        plotter = PlotGenerator()
        plot_count = 0  # 计数器

        # ---- 图表1：GC含量分布图 ----
        if results['seq_results'] and results['seq_results'].get('gc_contents'):
            try:
                fig1 = plotter.plot_gc_distribution(
                    results['seq_results']['gc_contents'],
                    title="序列GC含量分布",
                    output_file=None  # output_file=None表示不保存到文件，只返回Figure对象
                )
                results['plots']['gc_distribution'] = fig1
                add_log("✅ GC含量分布图已生成", "success")
                plot_count += 1
            except Exception as e:
                add_log(f"⚠️ 绘制GC含量分布图失败: {e}", "warning")

        # ---- 图表2：火山图 ----
        if results['deg_results'] is not None and len(results['deg_results']) > 0:
            try:
                fig2 = plotter.plot_volcano(
                    results['deg_results'],
                    p_threshold=config.p_value_threshold,
                    log2fc_threshold=config.log2_fold_change_threshold,
                    title="差异表达火山图",
                    output_file=None
                )
                results['plots']['volcano'] = fig2
                add_log("✅ 火山图已生成", "success")
                plot_count += 1
            except Exception as e:
                add_log(f"⚠️ 绘制火山图失败: {e}", "warning")

        # ---- 图表3：热图 ----
        if expression_data is not None and results['deg_results'] is not None:
            try:
                # 获取全部基因列表
                if 'gene' in results['deg_results'].columns:
                    all_genes = results['deg_results']['gene'].tolist()
                else:
                    all_genes = results['deg_results'].index.tolist()

                # 过滤：只保留在表达数据中存在的基因
                available_genes = [g for g in all_genes if g in expression_data.index]

                if len(available_genes) >= 2:
                    # 提取这些基因的表达数据
                    heatmap_data = expression_data.loc[available_genes]
                    n_genes = len(available_genes)

                    # 动态调整显示效果
                    # 基因<=50个显示行标签，否则不显示（避免拥挤）
                    show_row_labels = n_genes <= 50
                    # 动态计算图的高度：基因越多图越高
                    # 公式：min(30, n_genes * 0.15)，最高不超过30英寸
                    fig_height = max(8, min(30, n_genes * 0.15))
                    fig_width = 10

                    fig3 = plotter.plot_heatmap(
                        heatmap_data,
                        title=f"基因表达热图（共{n_genes}个基因）",
                        show_labels=show_row_labels,
                        output_file=None,
                        figsize=(fig_width, fig_height)
                    )
                    results['plots']['heatmap'] = fig3
                    add_log(f"✅ 热图已生成 ({n_genes} 个基因)", "success")
                    plot_count += 1
            except Exception as e:
                add_log(f"⚠️ 绘制热图失败: {e}", "warning")

        # ---- 图表4：PCA图 ----
        if expression_data is not None:
            try:
                # PCA需要样本为行、基因为列
                # 我们的表达矩阵是基因为行、样本为列
                # 所以需要转置：.T 就是转置
                fig4 = plotter.plot_pca(
                    expression_data.T,
                    title="样本PCA主成分分析",
                    output_file=None
                )
                results['plots']['pca'] = fig4
                add_log("✅ PCA图已生成", "success")
                plot_count += 1
            except Exception as e:
                add_log(f"⚠️ 绘制PCA图失败: {e}", "warning")

        add_log(f"📊 共生成 {plot_count} 个图表", "info")

        # ==================== 步骤4：机器学习分类 ====================
        status_text.text("步骤 4/4：机器学习基因分类...")
        progress_bar.progress(90)  # 90%进度
        add_log("🤖 第四步：机器学习基因分类", "info")

        if results['deg_results'] is not None and len(results['deg_results']) > 0:
            try:
                # 定义用于分类的特征列
                feature_columns = [
                    'log2_fold_change',
                    'p_value',
                    'corrected_p_value',
                    'mean_control',
                    'mean_treatment',
                    't_statistic'
                ]

                # 过滤：只保留数据中实际存在的特征列
                available_features = [
                    col for col in feature_columns
                    if col in results['deg_results'].columns
                ]

                if available_features:
                    add_log(f"   使用特征: {available_features}", "info")

                    # 提取特征矩阵 X
                    X = results['deg_results'][available_features].copy()
                    # 提取标签 y：1=显著，0=不显著
                    y = results['deg_results']['is_significant'].astype(int).values

                    add_log(f"   样本数量: {len(y)}", "info")
                    add_log(f"   显著基因(1): {sum(y == 1)} 个", "info")
                    add_log(f"   非显著基因(0): {sum(y == 0)} 个", "info")

                    # 创建分类器，传入随机种子
                    classifier = GeneClassifier(
                        model_type='random_forest',
                        random_state=config.random_state
                    )

                    # 直接设置决策树数量
                    # （目前分类器在train中使用默认100，这里手动修改）
                    classifier.n_estimators = config.n_estimators

                    # 训练模型
                    train_results = classifier.train(
                        X, y,
                        test_size=config.test_size
                    )

                    # 检查是否训练成功
                    if 'error' not in train_results:
                        add_log("✅ 模型训练完成", "success")
                        # 显示各项评估指标
                        if 'accuracy' in train_results:
                            add_log(f"   准确率: {train_results['accuracy']:.4f}", "info")
                        if 'precision' in train_results:
                            add_log(f"   精确率: {train_results['precision']:.4f}", "info")
                        if 'recall' in train_results:
                            add_log(f"   召回率: {train_results['recall']:.4f}", "info")
                        if 'f1_score' in train_results:
                            add_log(f"   F1分数: {train_results['f1_score']:.4f}", "info")

                        # 显示特征重要性排序
                        if 'feature_importance' in train_results and train_results['feature_importance']:
                            add_log("   特征重要性排序:", "info")
                            # 按重要性从高到低排序
                            sorted_features = sorted(
                                train_results['feature_importance'].items(),
                                key=lambda x: x[1],
                                reverse=True
                            )
                            for feat, imp in sorted_features:
                                add_log(f"     {feat}: {imp:.4f}", "info")

                        # 用训练好的模型预测所有基因
                        predictions = classifier.predict(X)
                        # 把预测结果添加到DataFrame中
                        results['deg_results']['prediction'] = predictions

                        n_sig = sum(predictions == 1)
                        n_nonsig = sum(predictions == 0)
                        add_log(
                            f"   预测结果: 显著基因 {n_sig} 个, "
                            f"非显著基因 {n_nonsig} 个",
                            "info"
                        )

                        # 保存机器学习结果
                        results['ml_results'] = train_results
                    else:
                        # 训练失败
                        add_log(
                            f"⚠️ 模型训练失败: {train_results['error']}",
                            "warning"
                        )
                else:
                    # 没有可用的特征列
                    add_log("⚠️ 没有可用的特征列，跳过机器学习", "warning")
            except Exception as e:
                # 捕获其他异常
                add_log(f"⚠️ 机器学习分类失败: {e}", "warning")
        else:
            # 没有差异表达数据
            add_log("⚠️ 无差异表达数据，跳过机器学习", "warning")

        # ==================== 全部完成 ====================
        progress_bar.progress(100)  # 100%进度
        status_text.text("✅ 分析完成！")

        add_log("=" * 50, "info")
        add_log("🎉 所有分析流程完成！", "success")
        add_log("📂 请前往【结果展示】页面查看详细结果", "info")

        # 标记分析完成
        st.session_state.analysis_done = True

        # 强制重绘页面，让"结果展示"等页面能立即看到数据
        st.rerun()

    except Exception as e:
        # 捕获所有异常，显示错误信息
        add_log(f"❌ 分析过程出错: {e}", "error")
        import traceback
        # 打印完整的错误堆栈，方便调试
        add_log(traceback.format_exc(), "error")
        status_text.text("❌ 分析失败")


# ==================================================
# 页面4：📊 结果展示
# ==================================================
def show_results_page():
    """
    显示结果展示页面

    这是用户查看分析成果的主要页面，包含：
        1. 顶部统计摘要卡片（4个metric）
        2. 4种可视化图表（标签页切换）
        3. 差异表达结果表格（可筛选、排序）
        4. 机器学习结果展示（指标 + 特征重要性图）
    """
    st.title("📊 结果展示")
    st.markdown("---")

    # 如果分析还没完成，提示用户
    if not st.session_state.analysis_done:
        st.warning("⚠️ 请先在【运行分析】页面执行分析")
        return

    # 获取结果数据
    results = st.session_state.analysis_results
    config = st.session_state.config

    # ============================================================
    # 第一部分：统计摘要（4个指标卡片）
    # ============================================================
    st.header("📋 分析结果摘要")

    # 四列布局，每列一个指标
    col1, col2, col3, col4 = st.columns(4)

    # 指标1：序列数量
    with col1:
        # 用列表长度，如果None就显示0
        n_seqs = len(results.get('sequences', [])) if results.get('sequences') else 0
        # st.metric() 显示大字号的指标数字
        st.metric("序列数量", f"{n_seqs} 条")

    # 指标2：平均GC含量
    with col2:
        if results.get('seq_results'):
            avg_gc = results['seq_results'].get('avg_gc', 0)
            st.metric("平均GC含量", f"{avg_gc:.2f}%")
        else:
            st.metric("平均GC含量", "-")

    # 指标3：显著差异基因数
    with col3:
        if results.get('deg_results') is not None:
            n_sig = results['deg_results']['is_significant'].sum()
            st.metric("显著差异基因", f"{n_sig} 个")
        else:
            st.metric("显著差异基因", "-")

    # 指标4：模型准确率
    with col4:
        if results.get('ml_results') and 'accuracy' in results['ml_results']:
            acc = results['ml_results']['accuracy']
            # :.2% 格式化为百分比（保留2位小数）
            st.metric("模型准确率", f"{acc:.2%}")
        else:
            st.metric("模型准确率", "-")

    st.markdown("---")

    # ============================================================
    # 第二部分：可视化图表（标签页）
    # ============================================================
    st.header("📈 可视化图表")

    # st.tabs() 创建标签页
    # 每个tab用with语句管理内容
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌋 火山图",
        "🔥 表达热图",
        "📉 PCA分析",
        "📊 GC分布"
    ])

    # ---- 标签页1：火山图 ----
    with tab1:
        st.subheader("差异表达火山图")
        if 'volcano' in results['plots']:
            # st.pyplot() 显示matplotlib图表
            # use_container_width=True：自动适应容器宽度
            st.pyplot(results['plots']['volcano'], use_container_width=True)
            # 图表下方的说明文字（小字号）
            st.caption("""
            **火山图解读**：
            - X轴：log2倍数变化（正值=上调，负值=下调）
            - Y轴：-log10(P值)（越高越显著）
            - 红色点：显著上调基因
            - 蓝色点：显著下调基因
            - 灰色点：无显著变化基因
            """)
        else:
            st.info("火山图未生成")

    # ---- 标签页2：热图 ----
    with tab2:
        st.subheader("基因表达热图")
        if 'heatmap' in results['plots']:
            st.pyplot(results['plots']['heatmap'], use_container_width=True)
            st.caption("""
            **热图解读**：
            - 每一行是一个基因，每一列是一个样本
            - 颜色深浅表示表达量高低（红色=高表达，蓝色=低表达）
            - 基因和样本都经过聚类，表达模式相似的会聚在一起
            """)
        else:
            st.info("热图未生成")

    # ---- 标签页3：PCA图 ----
    with tab3:
        st.subheader("样本PCA主成分分析")
        if 'pca' in results['plots']:
            st.pyplot(results['plots']['pca'], use_container_width=True)
            st.caption("""
            **PCA图解读**：
            - 每个点代表一个样本
            - 点之间的距离表示样本间的相似性（距离越近越相似）
            - 如果对照组和处理组明显分开，说明处理对基因表达有显著影响
            """)
        else:
            st.info("PCA图未生成")

    # ---- 标签页4：GC分布图 ----
    with tab4:
        st.subheader("序列GC含量分布")
        if 'gc_distribution' in results['plots']:
            st.pyplot(results['plots']['gc_distribution'], use_container_width=True)
            st.caption("""
            **GC含量分布图解读**：
            - 展示所有序列的GC含量分布情况
            - GC含量影响DNA稳定性和基因表达调控
            - 不同物种的GC含量特征不同
            """)
        else:
            st.info("GC含量分布图未生成")

    st.markdown("---")

    # ============================================================
    # 第三部分：差异表达结果表格
    # ============================================================
    st.header("📑 差异表达分析结果")

    if results.get('deg_results') is not None:
        deg_df = results['deg_results'].copy()

        # 筛选和排序控件（三列布局）
        col1, col2, col3 = st.columns(3)

        # 列1：筛选显示
        with col1:
            filter_option = st.selectbox(
                "筛选显示",
                options=[
                    "全部基因",
                    "仅显著差异基因",
                    "仅上调基因",
                    "仅下调基因"
                ],
                index=0
            )

        # 列2：排序方式
        with col2:
            sort_by = st.selectbox(
                "排序方式",
                options=[
                    "校正P值（升序）",
                    "log2倍数变化（降序）",
                    "log2倍数变化（升序）"
                ],
                index=0
            )

        # 列3：显示行数
        with col3:
            show_rows = st.slider(
                "显示行数",
                min_value=10,
                max_value=100,
                value=20,
                step=10
            )

        # 应用筛选
        if filter_option == "仅显著差异基因":
            display_df = deg_df[deg_df['is_significant'] == True].copy()
        elif filter_option == "仅上调基因":
            display_df = deg_df[deg_df['regulation'] == 'up'].copy()
        elif filter_option == "仅下调基因":
            display_df = deg_df[deg_df['regulation'] == 'down'].copy()
        else:
            display_df = deg_df.copy()

        # 应用排序
        if sort_by == "校正P值（升序）":
            display_df = display_df.sort_values('corrected_p_value', ascending=True)
        elif sort_by == "log2倍数变化（降序）":
            display_df = display_df.sort_values('log2_fold_change', ascending=False)
        else:
            display_df = display_df.sort_values('log2_fold_change', ascending=True)

        # 显示统计信息
        st.info(f"共显示 {len(display_df)} 个基因（总基因数：{len(deg_df)}）")

        # 选择要显示的列（只显示有意义的列）
        # 用列表推导式，检查列是否存在
        display_cols = [
            col for col in [
                'gene', 'log2_fold_change', 'p_value', 'corrected_p_value',
                'mean_control', 'mean_treatment', 'regulation',
                'is_significant', 'prediction'
            ]
            if col in display_df.columns
        ]

        # 显示表格（前N行）
        # hide_index=True：隐藏行索引
        st.dataframe(
            display_df[display_cols].head(show_rows),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("暂无差异表达分析结果")

    st.markdown("---")

    # ============================================================
    # 第四部分：机器学习结果
    # ============================================================
    st.header("🤖 机器学习分析结果")

    if results.get('ml_results') and 'error' not in results['ml_results']:
        ml_results = results['ml_results']

        # 两列布局：左列指标，右列特征重要性
        col1, col2 = st.columns(2)

        # ---- 左列：性能指标表格 ----
        with col1:
            st.subheader("模型性能指标")
            # 构建指标字典
            metrics_data = {}
            if 'accuracy' in ml_results:
                metrics_data['准确率'] = f"{ml_results['accuracy']:.4f}"
            if 'precision' in ml_results:
                metrics_data['精确率'] = f"{ml_results['precision']:.4f}"
            if 'recall' in ml_results:
                metrics_data['召回率'] = f"{ml_results['recall']:.4f}"
            if 'f1_score' in ml_results:
                metrics_data['F1分数'] = f"{ml_results['f1_score']:.4f}"

            # 显示为表格
            st.dataframe(
                pd.DataFrame({
                    '指标': list(metrics_data.keys()),
                    '数值': list(metrics_data.values())
                }),
                hide_index=True,
                use_container_width=True
            )

        # ---- 右列：特征重要性条形图 ----
        with col2:
            st.subheader("特征重要性")
            if 'feature_importance' in ml_results and ml_results['feature_importance']:
                feat_imp = ml_results['feature_importance']
                # 按重要性排序
                sorted_feats = sorted(feat_imp.items(), key=lambda x: x[1], reverse=True)

                # 转成DataFrame用于绘图
                feat_df = pd.DataFrame({
                    '特征': [f[0] for f in sorted_feats],
                    '重要性': [f[1] for f in sorted_feats]
                })

                # st.bar_chart() 直接画条形图
                st.bar_chart(feat_df.set_index('特征'))

        # 指标说明
        st.markdown("""
        **指标说明**：
        - **准确率**：预测正确的比例
        - **精确率**：预测为显著的基因中，真正显著的比例
        - **召回率**：真正显著的基因中，被成功预测的比例
        - **F1分数**：精确率和召回率的调和平均，综合评价指标
        """)
    else:
        st.info("暂无机器学习分析结果")


# ==================================================
# 页面5：📥 下载结果
# ==================================================
def show_download_page():
    """
    显示下载结果页面

    提供所有分析结果的下载功能：
        1. 表格数据下载（CSV格式）
        2. 图表下载（300 DPI高清PNG）
        3. 使用说明提示
    """
    st.title("📥 下载结果")
    st.markdown("---")

    # 检查是否有结果
    if not st.session_state.analysis_done:
        st.warning("⚠️ 请先在【运行分析】页面执行分析")
        return

    results = st.session_state.analysis_results

    # ============================================================
    # 第一部分：表格数据下载
    # ============================================================
    st.header("📑 表格数据下载")

    col1, col2 = st.columns(2)

    # ---- 左列：差异表达结果 ----
    with col1:
        st.subheader("差异表达分析结果")
        if results.get('deg_results') is not None:
            # 将DataFrame转换为CSV字节
            # StringIO：内存中的文本缓冲区
            csv_buffer = io.StringIO()
            # to_csv()保存到缓冲区
            # encoding='utf-8-sig'：带BOM的UTF-8，Excel打开不会乱码
            results['deg_results'].to_csv(
                csv_buffer,
                index=False,
                encoding='utf-8-sig'
            )
            # 获取字符串内容，再编码成字节
            csv_data = csv_buffer.getvalue().encode('utf-8-sig')

            # 下载按钮
            st.download_button(
                label="📥 下载 deg_results.csv",
                data=csv_data,
                file_name="deg_results.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.caption("包含所有基因的差异表达分析结果（CSV格式）")
        else:
            st.info("暂无数据")

    # ---- 右列：序列统计信息 ----
    with col2:
        st.subheader("序列统计信息")
        if results.get('sequences'):
            # 构建序列信息列表
            seq_info = []
            for seq in results['sequences']:
                seq_info.append({
                    '基因ID': seq['id'],
                    '描述': seq.get('description', ''),
                    '长度(bp)': seq['length']
                })
            seq_df = pd.DataFrame(seq_info)

            # 转成CSV
            csv_buffer = io.StringIO()
            seq_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_data = csv_buffer.getvalue().encode('utf-8-sig')

            st.download_button(
                label="📥 下载 sequence_info.csv",
                data=csv_data,
                file_name="sequence_info.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.caption("包含所有序列的基本信息（CSV格式）")
        else:
            st.info("暂无数据")

    st.markdown("---")

    # ============================================================
    # 第二部分：图表下载
    # ============================================================
    st.header("🖼️ 图表下载（高清PNG）")

    col1, col2 = st.columns(2)

    # ---- 左列：火山图 + 热图 ----
    with col1:
        # 火山图
        st.subheader("差异表达火山图")
        if 'volcano' in results['plots']:
            fig = results['plots']['volcano']
            img_bytes = fig_to_bytes(fig)  # 转成字节用于下载

            st.download_button(
                label="📥 下载 volcano_plot.png",
                data=img_bytes,
                file_name="volcano_plot.png",
                mime="image/png",
                use_container_width=True
            )
            st.caption("高分辨率火山图（300 DPI）")
        else:
            st.info("暂无图表")

        # 热图
        st.subheader("表达热图")
        if 'heatmap' in results['plots']:
            fig = results['plots']['heatmap']
            img_bytes = fig_to_bytes(fig)

            st.download_button(
                label="📥 下载 expression_heatmap.png",
                data=img_bytes,
                file_name="expression_heatmap.png",
                mime="image/png",
                use_container_width=True
            )
            st.caption("高分辨率表达热图（300 DPI）")
        else:
            st.info("暂无图表")

    # ---- 右列：PCA图 + GC分布图 ----
    with col2:
        # PCA图
        st.subheader("PCA分析图")
        if 'pca' in results['plots']:
            fig = results['plots']['pca']
            img_bytes = fig_to_bytes(fig)

            st.download_button(
                label="📥 下载 pca_plot.png",
                data=img_bytes,
                file_name="pca_plot.png",
                mime="image/png",
                use_container_width=True
            )
            st.caption("高分辨率PCA图（300 DPI）")
        else:
            st.info("暂无图表")

        # GC含量分布图
        st.subheader("GC含量分布图")
        if 'gc_distribution' in results['plots']:
            fig = results['plots']['gc_distribution']
            img_bytes = fig_to_bytes(fig)

            st.download_button(
                label="📥 下载 gc_distribution.png",
                data=img_bytes,
                file_name="gc_distribution.png",
                mime="image/png",
                use_container_width=True
            )
            st.caption("高分辨率GC含量分布图（300 DPI）")
        else:
            st.info("暂无图表")

    st.markdown("---")

    # 底部提示信息
    st.info("""
    💡 **提示**：
    - 所有图表均为300 DPI高分辨率PNG格式，适合用于论文和报告
    - CSV文件使用UTF-8 BOM编码，Excel打开不会乱码
    - 如需其他格式或分辨率，请在【数据配置】页面调整参数后重新分析
    """)


# ==================================================
# 侧边栏导航
# ==================================================
def render_sidebar():
    """
    渲染侧边栏导航菜单

    侧边栏内容：
        1. 应用标题
        2. 导航菜单（单选按钮形式）
        3. 数据加载状态（实时显示）
        4. 分析完成状态
        5. 版本信息

    Returns:
        str: 当前选中的页面名称
    """
    # with st.sidebar: 上下文管理器
    # 所有放在这里面的组件都会显示在左侧边栏
    with st.sidebar:
        st.title("🧬 基因分析平台")
        st.markdown("---")

        # 导航菜单（单选按钮）
        # label_visibility="collapsed"：隐藏标签文字（因为有标题了）
        page = st.radio(
            "导航菜单",
            options=[
                "🏠 首页",
                "⚙️ 数据配置",
                "🚀 运行分析",
                "📊 结果展示",
                "📥 下载结果"
            ],
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("---")

        # ===== 状态显示区 =====
        st.subheader("📌 状态")

        # FASTA数据状态
        if st.session_state.uploaded_fasta is not None:
            st.success("✅ FASTA数据已加载")
        else:
            st.warning("⚠️ FASTA数据未加载")

        # 表达数据状态
        if st.session_state.uploaded_expression is not None:
            st.success("✅ 表达数据已加载")
        else:
            st.warning("⚠️ 表达数据未加载")

        # 分析完成状态
        if st.session_state.analysis_done:
            st.success("✅ 分析已完成")
        else:
            st.info("⏳ 等待分析")

        st.markdown("---")
        # 版本信息（小字）
        st.caption("基因表达调控分析与预测平台 v1.0")

        # 返回当前选中的页面名
        return page


# ==================================================
# 主函数
# ==================================================
def main():
    """
    主函数 - Web应用的入口

    执行流程：
        1. 初始化会话状态（确保所有变量都有默认值）
        2. 渲染侧边栏导航
        3. 根据用户选择，调用对应的页面函数
    """
    # 第一步：初始化会话状态
    # 必须在最前面调用，确保所有页面都能访问到状态变量
    init_session_state()

    # 第二步：渲染侧边栏，获取用户选择的页面
    page = render_sidebar()

    # 第三步：根据页面名称调用对应的函数
    # 每个页面对应一个 show_xxx_page() 函数
    if page == "🏠 首页":
        show_home_page()
    elif page == "⚙️ 数据配置":
        show_config_page()
    elif page == "🚀 运行分析":
        show_analysis_page()
    elif page == "📊 结果展示":
        show_results_page()
    elif page == "📥 下载结果":
        show_download_page()


# ==================== 程序入口 ====================
# 当直接运行这个文件时（streamlit run app.py），执行main()
if __name__ == "__main__":
    main()
