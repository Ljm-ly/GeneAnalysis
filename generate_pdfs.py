# -*- coding: utf-8 -*-
"""
为基因分析项目生成《源代码》和《信息手册》两个 PDF。
使用 fpdf2 库，支持 SMP emoji 字符的自动字体 fallback。

格式严格对齐飞书参考文件：
  - 源代码.pdf：US Letter (612×792pt)、代码字体 10pt、左边距 90pt (~31.8mm)、
    Consolas 等宽字体、页眉左对齐软件名(版本号)+右上角页码、内容从 y=74 开始、
    文件以"N.filename"编号头
  - 信息手册.pdf：A4、字体 12pt、左边距 90pt (~31.8mm)、行距 23.4pt、
    无页眉页脚、内容从 y=78 开始、SimHei 字体、【字段】：值 结构化表单
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

# 参考文件格式标准
MARGIN_LEFT_PT = 90.0   # 参考文件左边距 90pt
MARGIN_RIGHT_PT = 90.0  # 右边距对称 90pt
SRC_MARGIN_TOP_PT = 74.0   # 源代码：内容从 y=74.2 开始（参考文件）
INFO_MARGIN_TOP_PT = 78.0  # 信息手册：内容从 y=77.8 开始（参考文件无页眉）
MARGIN_BOTTOM_PT = 50.0    # 底部页脚预留


# =========================================================
# 1. 源代码 PDF（US Letter, Consolas/DejaVuMono 10pt）
# =========================================================
class SourceCodePDF(FPDF):
    """源代码 PDF，US Letter 格式，页眉左对齐+右上角页码。"""

    def __init__(self):
        # US Letter: 612 x 792 pt = 215.9 x 279.4 mm
        super().__init__(orientation='P', unit='pt', format='Letter')
        self.set_margins(MARGIN_LEFT_PT, SRC_MARGIN_TOP_PT, MARGIN_RIGHT_PT)
        self.set_auto_page_break(True, margin=MARGIN_BOTTOM_PT)
        self.c_margin = 0  # cell 左右内边距设为 0，使文本精确从左边距开始
        # 注册字体
        self.add_font("Consolas", "", DEJAVU_MONO_PATH)
        self.add_font("Consolas", "B", DEJAVU_MONO_PATH)
        self.add_font("SimHei", "", SIMHEI_PATH)
        self.add_font("NotoEmoji", "", NOTOEMOJI_PATH)
        # fallback 字体链：Consolas → SimHei → NotoEmoji
        self.set_fallback_fonts(["SimHei", "NotoEmoji"])

    def header(self):
        # 页眉：左对齐软件名（中文用 SimHei，V1.0 用 Consolas），右上角页码
        y = 37.5
        text = HEADER_TEXT
        cur_x = MARGIN_LEFT_PT
        i = 0
        n = len(text)
        while i < n:
            is_cjk = is_cjk_char(text[i])
            j = i
            while j < n and is_cjk_char(text[j]) == is_cjk:
                j += 1
            run = text[i:j]
            font_name = "SimHei" if is_cjk else "Consolas"
            self.set_xy(cur_x, y)
            self.set_font(font_name, size=10)
            self.cell(0, 10, text=run, new_x=XPos.RIGHT, new_y=YPos.TOP)
            cur_x += self.get_string_width(run)
            i = j
        # 页码：右上角
        page_str = f"{self.page_no()} "
        self.set_font("Consolas", size=10)
        page_w = self.get_string_width(page_str)
        self.set_xy(self.w - MARGIN_RIGHT_PT - page_w, y)
        self.cell(0, 10, text=page_str, new_x=XPos.LEFT, new_y=YPos.TOP)

    def footer(self):
        # 参考文件页脚为空
        pass


def is_cjk_char(ch):
    """判断字符是否为 CJK 或需要 SimHei 字体渲染。"""
    code = ord(ch)
    # ASCII 用 Consolas
    if code < 128:
        return False
    # CJK 统一表意文字、CJK 标点、希腊字母等用 SimHei
    return True


def draw_code_line(pdf, x, y, text, font_size, leading):
    """
    手动逐段渲染一行代码：ASCII 用 Consolas，CJK/emoji 用 SimHei/NotoEmoji。
    绕过 fpdf2 的 fallback 机制 bug，确保每个字符都正确渲染。
    如果行总宽度超过可用宽度，自动缩小字体以适应。
    """
    if not text:
        # 空行：画一个空格占位
        pdf.set_xy(MARGIN_LEFT_PT, y)
        pdf.set_font("Consolas", size=font_size)
        pdf.cell(0, leading, text=" ", new_x=XPos.RIGHT, new_y=YPos.NEXT)
        return

    # 先计算整行宽度，如果超宽则缩小字体
    avail_w = pdf.w - MARGIN_LEFT_PT - MARGIN_RIGHT_PT
    # 分段
    segments = []
    i = 0
    n = len(text)
    while i < n:
        is_cjk = is_cjk_char(text[i])
        j = i
        while j < n and is_cjk_char(text[j]) == is_cjk:
            j += 1
        run = text[i:j]
        if is_cjk:
            has_emoji = any(ord(c) >= 0x1F000 for c in run)
            font_name = "NotoEmoji" if has_emoji else "SimHei"
        else:
            font_name = "Consolas"
        segments.append((run, font_name))
        i = j

    # 计算总宽度
    total_w = 0
    for run, font_name in segments:
        pdf.set_font(font_name, size=font_size)
        total_w += pdf.get_string_width(run)

    # 如果超宽，计算缩放比例
    actual_font_size = font_size
    if total_w > avail_w:
        actual_font_size = font_size * avail_w / total_w * 0.98  # 留 2% 余量

    # 渲染各段
    cur_x = MARGIN_LEFT_PT
    for run, font_name in segments:
        pdf.set_xy(cur_x, y)
        pdf.set_font(font_name, size=actual_font_size)
        pdf.cell(0, leading, text=run, new_x=XPos.RIGHT, new_y=YPos.TOP)
        run_width = pdf.get_string_width(run)
        cur_x += run_width

    # 恢复到下一行起始位置
    pdf.set_xy(MARGIN_LEFT_PT, y + leading)


def generate_source_code_pdf(output_path, file_list):
    pdf = SourceCodePDF()
    pdf.add_page()
    code_font_size = 10.0
    code_leading = 12.0  # 行距 12pt
    pdf.set_xy(MARGIN_LEFT_PT, SRC_MARGIN_TOP_PT)

    for idx, (display_name, fpath) in enumerate(file_list, start=1):
        # 文件分节头（Consolas-Bold）
        header = f"{idx}.{display_name} "
        if pdf.get_y() > pdf.h - MARGIN_BOTTOM_PT - 20:
            pdf.add_page()
        y = pdf.get_y()
        pdf.set_xy(MARGIN_LEFT_PT, y)
        pdf.set_font("Consolas", style="B", size=code_font_size)
        pdf.cell(0, code_leading, text=header, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        y += code_leading

        # 读取文件内容
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"# 读取文件失败: {e}"

        # 逐行渲染
        for raw_line in content.splitlines():
            # 检查是否需要换页
            if y > pdf.h - MARGIN_BOTTOM_PT - 10:
                pdf.add_page()
                y = SRC_MARGIN_TOP_PT
            # 渲染该行
            draw_code_line(pdf, MARGIN_LEFT_PT, y,
                           raw_line if raw_line else "",
                           code_font_size, code_leading)
            y += code_leading

        # 文件之间留一行空白
        y += code_leading

    pdf.output(output_path)
    return pdf.page_no()


# =========================================================
# 2. 信息手册 PDF（A4, SimHei 12pt, 行距 23.4pt）
# =========================================================
class InfoGuidePDF(FPDF):
    """信息手册 PDF，A4 格式，无页眉页脚（参考文件格式）。"""

    def __init__(self):
        # A4: 595.3 x 841.9 pt
        super().__init__(orientation='P', unit='pt', format='A4')
        self.set_margins(MARGIN_LEFT_PT, INFO_MARGIN_TOP_PT, MARGIN_RIGHT_PT)
        self.set_auto_page_break(True, margin=MARGIN_BOTTOM_PT)
        self.c_margin = 0  # cell 左右内边距设为 0
        self.add_font("SimHei", "", SIMHEI_PATH)
        self.add_font("NotoEmoji", "", NOTOEMOJI_PATH)
        self.set_fallback_fonts(["NotoEmoji"])

    def header(self):
        # 参考文件无页眉
        pass

    def footer(self):
        # 参考文件无页脚
        pass


def wrap_field_text(pdf, text, font_size, avail_w):
    """
    将字段文本按可用宽度折行，确保不拆断英文单词/数字/标识符。
    规则：中文可在任意位置换行；连续的 ASCII 字符（英文单词、数字、路径等）
    作为一个整体，放不下时整组移到下一行。
    """
    pdf.set_font("SimHei", size=font_size)
    lines = []
    current_line = ""

    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        # 判断当前字符是否为 ASCII（英文/数字/标点）
        if ord(ch) < 128:
            # 收集连续的 ASCII 字符作为一个 token
            j = i
            while j < n and ord(text[j]) < 128:
                j += 1
            token = text[i:j]
            # 检查 token 加到当前行是否会超宽
            test = current_line + token
            w = pdf.get_string_width(test)
            if w <= avail_w:
                current_line = test
            else:
                # 当前 token 放不下，先保存当前行
                if current_line:
                    lines.append(current_line)
                    current_line = token
                else:
                    # 当前行为空，但 token 本身就超宽，必须强制放入
                    current_line = token
            i = j
        else:
            # CJK 字符，逐个添加
            test = current_line + ch
            w = pdf.get_string_width(test)
            if w <= avail_w:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = ch
                else:
                    current_line = ch
            i += 1

    if current_line:
        lines.append(current_line)

    return lines


def generate_info_guide_pdf(output_path, fields):
    pdf = InfoGuidePDF()
    pdf.add_page()
    font_size = 12.0
    leading = 23.4  # 行距 23.4pt（与参考文件一致）
    pdf.set_font("SimHei", size=font_size)
    pdf.set_xy(MARGIN_LEFT_PT, INFO_MARGIN_TOP_PT)

    avail_w = pdf.w - MARGIN_LEFT_PT - MARGIN_RIGHT_PT  # 可用宽度

    for label, value in fields:
        full = f"【{label}】：{value}"
        # 自定义折行：不拆断英文单词
        lines = wrap_field_text(pdf, full, font_size, avail_w)
        for line in lines:
            if pdf.get_y() > pdf.h - MARGIN_BOTTOM_PT:
                pdf.add_page()
                pdf.set_font("SimHei", size=font_size)
            pdf.set_x(MARGIN_LEFT_PT)
            pdf.set_font("SimHei", size=font_size)
            pdf.cell(0, leading, text=line,
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output(output_path)
    return pdf.page_no()


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
         "双核 x86_64 CPU 及以上；集成显卡；内存：4GB；硬盘空间5GB以上"),
        ("开发该软件的操作系统", "Windows 10"),
        ("软件开发环境/开发工具", "Python + Streamlit"),
        ("该软件的运行平台 / 操作系统",
         "Windows 10及更高版本Windows / macOS / Linux（跨平台，基于Python）"),
        ("软件运行支撑环境 / 支撑软件",
         "Python 3.10及以上；Streamlit>=1.28.0；依赖库包括numpy>=1.24.0、"
         "pandas>=2.0.0、matplotlib>=3.7.0、seaborn>=0.12.0、biopython>=1.81、"
         "scikit-learn>=1.3.0、openpyxl>=3.1.0（详见requirements.txt）"),
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
