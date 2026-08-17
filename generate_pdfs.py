# -*- coding: utf-8 -*-
"""
为基因分析项目生成《源代码》和《信息手册》两个 PDF。
使用 fpdf2 库，支持 SMP emoji 字符的自动字体 fallback。

格式参照飞书中的参考文件：
  - 源代码.pdf：每页页眉为"软件名称（版本号）"，页脚页码，
    各源文件以"N.filename"编号头列出，等宽字体呈现代码。
  - 软件信息指南.pdf：单页结构化字段表单（【字段】：值）。
"""
import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# ---------------- 字体路径 ----------------
FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts')
SIMHEI_PATH = os.path.join(FONT_DIR, 'simhei.ttf')
NOTOEMOJI_PATH = os.path.join(FONT_DIR, 'NotoEmoji.ttf')
DEJAVU_MONO_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# ---------------- 公共参数 ----------------
SOFTWARE_NAME = "基因表达调控分析与预测平台"
VERSION = "V1.0"
HEADER_TEXT = f"{SOFTWARE_NAME}（{VERSION}）"

PAGE_W, PAGE_H = 210, 297  # A4 mm
MARGIN_X = 10    # mm，缩小左右页边距以容纳长行
MARGIN_TOP = 18
MARGIN_BOTTOM = 15

CODE_FONT_SIZE = 6.5  # pt → mm 需转换; fpdf2 用 mm
CODE_FONT_SIZE_MM = CODE_FONT_SIZE * 0.352778  # pt → mm
CODE_LEADING_MM = CODE_FONT_SIZE_MM * 1.3  # 行高


class SourceCodePDF(FPDF):
    """源代码 PDF，带页眉页脚。"""

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_margins(MARGIN_X, MARGIN_TOP, MARGIN_X)
        self.set_auto_page_break(True, margin=MARGIN_BOTTOM)
        # 注册字体
        self.add_font("DejaVuMono", "", DEJAVU_MONO_PATH)
        self.add_font("SimHei", "", SIMHEI_PATH)
        self.add_font("NotoEmoji", "", NOTOEMOJI_PATH)
        # 设置 fallback 字体链：DejaVuMono → SimHei → NotoEmoji
        self.set_fallback_fonts(["SimHei", "NotoEmoji"])

    def header(self):
        self.set_font("SimHei", size=11)
        self.set_y(8)
        self.cell(0, 8, text=HEADER_TEXT, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def footer(self):
        self.set_font("SimHei", size=10)
        self.set_y(-12)
        self.cell(0, 8, text=str(self.page_no()), align='C')


def generate_source_code_pdf(output_path, file_list):
    pdf = SourceCodePDF()
    pdf.add_page()
    pdf.set_font("DejaVuMono", size=CODE_FONT_SIZE)
    pdf.set_xy(MARGIN_X, MARGIN_TOP)

    avail_w = PAGE_W - 2 * MARGIN_X  # 可用宽度 mm

    for idx, (display_name, fpath) in enumerate(file_list, start=1):
        # 文件分节头
        header = f"{idx}.{display_name}"
        # 检查是否需要换页
        if pdf.get_y() > PAGE_H - MARGIN_BOTTOM - 10:
            pdf.add_page()
            pdf.set_font("DejaVuMono", size=CODE_FONT_SIZE)
        pdf.set_font("SimHei", size=10)
        pdf.set_x(MARGIN_X)
        pdf.cell(0, 6, text=header, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("DejaVuMono", size=CODE_FONT_SIZE)
        pdf.ln(2)

        # 读取文件内容
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"# 读取文件失败: {e}"

        # 逐行渲染
        for raw_line in content.splitlines():
            if pdf.get_y() > PAGE_H - MARGIN_BOTTOM - 5:
                pdf.add_page()
                pdf.set_font("DejaVuMono", size=CODE_FONT_SIZE)
            pdf.set_x(MARGIN_X)
            # 空行也要渲染（画一个空格），确保文本提取保留空行
            line_text = raw_line if raw_line else " "
            pdf.cell(0, CODE_LEADING_MM, text=line_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # 文件之间留空
        pdf.ln(2)

    pdf.output(output_path)
    return pdf.page_no


# =========================================================
# 信息手册 PDF
# =========================================================
class InfoGuidePDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_margins(15, MARGIN_TOP, 15)
        self.set_auto_page_break(True, margin=MARGIN_BOTTOM)
        self.add_font("SimHei", "", SIMHEI_PATH)
        self.add_font("NotoEmoji", "", NOTOEMOJI_PATH)
        self.set_fallback_fonts(["NotoEmoji"])

    def header(self):
        self.set_font("SimHei", size=11)
        self.set_y(8)
        self.cell(0, 8, text=HEADER_TEXT, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def footer(self):
        self.set_font("SimHei", size=10)
        self.set_y(-12)
        self.cell(0, 8, text=str(self.page_no()), align='C')


def generate_info_guide_pdf(output_path, fields):
    pdf = InfoGuidePDF()
    pdf.add_page()
    pdf.set_font("SimHei", size=11)
    pdf.set_xy(15, MARGIN_TOP)

    leading = 7  # mm
    avail_w = PAGE_W - 30  # 左右各 15mm

    for label, value in fields:
        full = f"【{label}】：{value}"
        # 使用 multi_cell 自动折行
        pdf.multi_cell(avail_w, leading, text=full, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output(output_path)
    return pdf.page_no


# =========================================================
# 主流程
# =========================================================
if __name__ == "__main__":
    source_files = [
        ("app.py", "app.py"),
        ("main.py", "main.py"),
        ("config.py", "config.py"),
        ("generate_simulated_data.py", "generate_simulated_data.py"),
        ("start_app.py", "start_app.py"),
        ("data_processing/__init__.py", "data_processing/__init__.py"),
        ("data_processing/fasta_reader.py", "data_processing/fasta_reader.py"),
        ("data_processing/data_cleaner.py", "data_processing/data_cleaner.py"),
        ("sequence_analysis/__init__.py", "sequence_analysis/__init__.py"),
        ("sequence_analysis/basic_stats.py", "sequence_analysis/basic_stats.py"),
        ("expression_analysis/__init__.py", "expression_analysis/__init__.py"),
        ("expression_analysis/differential.py", "expression_analysis/differential.py"),
        ("machine_learning/__init__.py", "machine_learning/__init__.py"),
        ("machine_learning/classifier.py", "machine_learning/classifier.py"),
        ("visualization/__init__.py", "visualization/__init__.py"),
        ("visualization/plots.py", "visualization/plots.py"),
        ("utils/__init__.py", "utils/__init__.py"),
        ("utils/helpers.py", "utils/helpers.py"),
        ("tests/__init__.py", "tests/__init__.py"),
        ("tests/test_data.py", "tests/test_data.py"),
    ]

    total_lines = 0
    for _, fpath in source_files:
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                total_lines += sum(1 for _ in f)
    print(f"源程序总行数: {total_lines}")

    # 生成源代码 PDF
    src_pdf = "源代码.pdf"
    pages = generate_source_code_pdf(src_pdf, source_files)
    print(f"已生成《源代码》PDF: {src_pdf} ({pages} 页)")

    # 信息手册字段
    info_fields = [
        ("软件全称", "基因表达调控分析与预测平台"),
        ("软件简称", "基因分析平台"),
        ("版本号", "V1.0"),
        ("开发目的",
         "本系统的开发旨在解决生物信息学研究中基因表达数据分析流程分散、"
         "门槛高、可视化不足等问题，通过集成DNA序列分析、差异表达分析、"
         "可视化图表与机器学习预测四大核心功能，提供从原始FASTA序列和"
         "CSV表达矩阵读取、参数配置、统计检验、图表生成到结果导出的"
         "一站式Web分析平台，助力科研人员高效完成基因表达调控分析与"
         "预测，提升生物信息学研究效率与实验结果可复现性。"),
        ("面向领域/行业", "生物信息学/生命科学"),
        ("软件的主要功能",
         "本系统基于Streamlit构建5页面Web应用（首页、数据配置、运行分析、"
         "结果展示、下载结果），提供四大核心功能：①序列分析——基于"
         "Biopython SeqIO解析FASTA，计算GC含量、核苷酸频率（A/T/G/C）、"
         "序列长度分布；②差异表达分析——读取CSV表达矩阵，按对照组/"
         "处理组执行SciPy t检验，采用BH-FDR多重检验校正，结合log2倍数"
         "变化识别上调/下调基因；③可视化——matplotlib+seaborn生成火山图、"
         "表达热图、PCA主成分分析图、GC含量分布图；④机器学习预测——"
         "scikit-learn随机森林分类，输出特征重要性、准确率/精确率/召回率/"
         "F1/AUC等性能指标，并支持CSV表格与高清PNG图表（300 DPI）导出。"),
        ("软件分类", "应用软件"),
        ("开发的硬件环境",
         "13th Gen Intel(R) Core(TM) i7-13700H CPU；Intel(R) UHD Graphics；"
         "内存：16GB；硬盘空间50GB以上"),
        ("运行的硬件环境",
         "Intel(R) Core(TM) i5-10400及以上；Intel(R) UHD Graphics；"
         "内存：8GB；硬盘空间50GB以上"),
        ("开发该软件的操作系统", "Windows 11"),
        ("软件开发环境/开发工具", "Python + Streamlit"),
        ("该软件的运行平台 / 操作系统",
         "Windows 11及更高版本Windows / macOS / Linux（跨平台，基于Python）"),
        ("软件运行支撑环境 / 支撑软件",
         "Python 3.8及以上；Streamlit>=1.28.0；依赖库包括numpy、pandas、"
         "matplotlib、seaborn、biopython、scikit-learn、scipy、openpyxl"
         "（详见requirements.txt）"),
        ("编程语言", "Python"),
        ("源程序量", f"{total_lines} 行"),
        ("技术特点",
         "系统采用Python+Streamlit轻量化Web技术架构，模块化设计六大功能"
         "包（data_processing、sequence_analysis、expression_analysis、"
         "machine_learning、visualization、utils）；使用dataclass集中管理"
         "分析参数（P值阈值、log2FC、随机森林超参数等）保障实验可复现；"
         "通过Streamlit Session State实现页面间数据共享与状态保持；"
         "matplotlib配置Agg非交互式后端与内嵌simhei.ttf中文字体+多字体"
         "fallback机制，解决Linux云端中文乱码问题；支持本地运行"
         "（streamlit run app.py）与Streamlit Community Cloud一键部署。"),
        ("软件参考地址", "https://geneanalysis-app.streamlit.app/"),
        ("软件下载地址（安卓/iOS）", ""),
    ]

    info_pdf = "信息手册.pdf"
    pages = generate_info_guide_pdf(info_pdf, info_fields)
    print(f"已生成《信息手册》PDF: {info_pdf} ({pages} 页)")
