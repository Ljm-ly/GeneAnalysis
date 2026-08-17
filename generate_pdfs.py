# -*- coding: utf-8 -*-
"""
为基因分析项目生成《源代码》和《信息手册》两个 PDF。
格式参照飞书中的参考文件：
  - 源代码.pdf：每页页眉为"软件名称（版本号）"，页脚页码，
    各源文件以"N.filename"编号头列出，等宽字体呈现代码。
  - 软件信息指南.pdf：单页结构化字段表单（【字段】：值）。
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.utils import simpleSplit

# ---------------- 字体注册 ----------------
# 中文字体（页眉/信息手册）：使用项目内置 simhei.ttf
CN_FONT = "SimHei"
font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'simhei.ttf')
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont(CN_FONT, font_path))
else:
    # 退回到 reportlab 内置 CID 中文字体
    UnicodeCIDFont('STSong-Light')
    CN_FONT = 'STSong-Light'

# 等宽字体（代码）：使用 Courier
CODE_FONT = "Courier"

# ---------------- 公共参数 ----------------
SOFTWARE_NAME = "基因表达调控分析与预测平台"
VERSION = "V1.0"
HEADER_TEXT = f"{SOFTWARE_NAME}（{VERSION}）"

PAGE_W, PAGE_H = A4
MARGIN_X = 50  # 左右页边距
MARGIN_TOP = 60
MARGIN_BOTTOM = 50


def draw_header_footer(c, page_no):
    """绘制页眉（软件名+版本）和页脚（页码）。"""
    c.setFont(CN_FONT, 11)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 32, HEADER_TEXT)
    c.setFont(CN_FONT, 10)
    c.drawCentredString(PAGE_W / 2, 30, str(page_no))


def is_cjk(ch):
    """判断字符是否为 CJK（中文字符等），需用中文字体渲染。"""
    code = ord(ch)
    return (0x4E00 <= code <= 0x9FFF) or (0x3000 <= code <= 0x303F) or \
           (0xFF00 <= code <= 0xFFEF) or (0x2E80 <= code <= 0x2EFF) or \
           (0x3400 <= code <= 0x4DBF)


def char_width(ch, font_size):
    """估算单字符宽度：CJK 全角，ASCII 半角（Courier 等宽）。"""
    if is_cjk(ch):
        return font_size  # 全角
    return font_size * 0.6  # Courier 近似等宽


def wrap_mixed_line(line, font_size, avail_w):
    """对含中英文的行按可用宽度折行，返回分段列表。"""
    if not line:
        return [""]
    segments = []
    cur = ""
    cur_w = 0.0
    for ch in line:
        w = char_width(ch, font_size)
        if cur_w + w > avail_w and cur:
            segments.append(cur)
            cur = ch
            cur_w = w
        else:
            cur += ch
            cur_w += w
    if cur:
        segments.append(cur)
    return segments if segments else [""]


def draw_mixed_line(c, x, y, text, font_size):
    """绘制一行文本，ASCII 用 Courier、CJK 用中文字体，逐段切换字体。"""
    if not text:
        return
    cx = x
    i = 0
    n = len(text)
    while i < n:
        # 收集连续的同类型字符
        use_cjk = is_cjk(text[i])
        j = i
        while j < n and is_cjk(text[j]) == use_cjk:
            j += 1
        run = text[i:j]
        font = CN_FONT if use_cjk else CODE_FONT
        c.setFont(font, font_size)
        c.drawString(cx, y, run)
        # 推进 x：逐字符累加宽度
        for ch in run:
            cx += char_width(ch, font_size)
        i = j


# =========================================================
# 1. 生成《源代码》PDF
# =========================================================
def generate_source_code_pdf(output_path, file_list):
    """
    file_list: [(display_name, file_path), ...]
    每个文件以 "N.display_name" 作为分节头，代码以等宽字体呈现，自动折行。
    """
    c = canvas.Canvas(output_path, pagesize=A4)
    page_no = 1

    # 代码区域可用宽度与字体
    code_font_size = 8.5
    code_leading = 10.5  # 行高
    avail_w = PAGE_W - 2 * MARGIN_X

    y = PAGE_H - MARGIN_TOP

    def new_page():
        nonlocal page_no, y
        draw_header_footer(c, page_no)
        c.showPage()
        page_no += 1
        y = PAGE_H - MARGIN_TOP

    for idx, (display_name, fpath) in enumerate(file_list, start=1):
        # 文件分节头："N.filename"
        header = f"{idx}.{display_name}"
        if y < MARGIN_BOTTOM + 40:
            new_page()
        c.setFont(CN_FONT, 11)
        c.drawString(MARGIN_X, y, header)
        y -= code_leading * 1.6

        # 读取文件内容
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"# 读取文件失败: {e}"

        # 逐行渲染，超宽自动折行（中英文混排：ASCII 用 Courier，CJK 用中文字体）
        for raw_line in content.splitlines():
            if not raw_line:
                # 空行
                y -= code_leading
                if y < MARGIN_BOTTOM:
                    new_page()
                continue
            # 按可用宽度折行，逐字符测量宽度（CJK 视为全角）
            segments = wrap_mixed_line(raw_line, code_font_size, avail_w)
            for seg in segments:
                if y < MARGIN_BOTTOM:
                    new_page()
                draw_mixed_line(c, MARGIN_X, y, seg, code_font_size)
                y -= code_leading

        # 文件之间留一行空白
        y -= code_leading

    draw_header_footer(c, page_no)
    c.save()
    return page_no


# =========================================================
# 2. 生成《信息手册》PDF
# =========================================================
def generate_info_guide_pdf(output_path, fields):
    """
    fields: [(label, value), ...]
    以单页（或多页）结构化字段表单呈现，格式：【字段】：值
    """
    c = canvas.Canvas(output_path, pagesize=A4)
    page_no = 1

    label_font_size = 11
    value_font_size = 11
    leading = 18
    avail_w = PAGE_W - 2 * MARGIN_X

    y = PAGE_H - MARGIN_TOP

    def ensure_space(needed):
        nonlocal y, page_no
        if y - needed < MARGIN_BOTTOM:
            draw_header_footer(c, page_no)
            c.showPage()
            page_no += 1
            y = PAGE_H - MARGIN_TOP

    for label, value in fields:
        full = f"【{label}】：{value}"
        # 折行
        lines = simpleSplit(full, CN_FONT, label_font_size, avail_w)
        if not lines:
            lines = [full]
        for seg in lines:
            ensure_space(leading)
            c.setFont(CN_FONT, value_font_size)
            c.drawString(MARGIN_X, y, seg)
            y -= leading

    draw_header_footer(c, page_no)
    c.save()
    return page_no


# =========================================================
# 主流程
# =========================================================
if __name__ == "__main__":
    # ---- 源代码 PDF：文件清单（按逻辑顺序） ----
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

    # 统计源程序总行数
    total_lines = 0
    for _, fpath in source_files:
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                total_lines += sum(1 for _ in f)
    print(f"源程序总行数: {total_lines}")

    # ---- 生成源代码 PDF ----
    src_pdf = "源代码.pdf"
    pages = generate_source_code_pdf(src_pdf, source_files)
    print(f"已生成《源代码》PDF: {src_pdf} ({pages} 页)")

    # ---- 信息手册 PDF：字段内容 ----
    info_fields = [
        ("软件全称", "基因表达调控分析与预测平台"),
        ("软件简称", "基因分析平台"),
        ("版本号", "V1.0"),
        ("开发目的",
         "本系统的开发旨在解决生物信息学研究中基因表达数据分析流程分散、"
         "门槛高、可视化不足等问题，通过集成序列分析、差异表达分析、"
         "可视化图表与机器学习预测四大核心功能，提供从原始数据读取到"
         "结果输出的一站式分析平台，助力科研人员高效完成基因表达调控"
         "分析与预测，提升生物信息学研究效率与结果可复现性。"),
        ("面向领域/行业", "生物信息学/生命科学"),
        ("软件的主要功能",
         "本系统提供基因序列分析（GC含量计算、核苷酸频率统计、序列长度分布）、"
         "差异表达分析（t检验统计、BH-FDR多重校正、上调/下调基因识别）、"
         "可视化图表（火山图、表达热图、PCA主成分分析、GC含量分布图）、"
         "机器学习预测（随机森林分类、特征重要性分析、模型性能评估）"
         "等核心功能，支持FASTA序列文件与CSV表达矩阵上传、参数配置、"
         "完整分析流程一键执行及结果（CSV表格、高清PNG图表）导出，"
         "满足基因表达调控分析与预测的科研需求。"),
        ("软件分类", "应用软件"),
        ("开发的硬件环境",
         "13th Gen Intel(R) Core(TM) i7-13700H CPU；Intel(R) UHD Graphics；"
         "内存：16GB；硬盘空间50GB以上"),
        ("运行的硬件环境",
         "Intel(R) Core(TM) i5-10400及以上；Intel(R) UHD Graphics；"
         "内存：8GB；硬盘空间50GB以上"),
        ("开发该软件的操作系统", "Windows 11"),
        ("软件开发环境/开发工具", "Python"),
        ("该软件的运行平台 / 操作系统",
         "Windows 11及更高版本Windows / macOS / Linux（跨平台）"),
        ("软件运行支撑环境 / 支撑软件",
         "Python 3.8及以上；Streamlit Web框架；依赖见requirements.txt"),
        ("编程语言", "Python"),
        ("源程序量", f"{total_lines} 行"),
        ("技术特点",
         "系统采用Python+Streamlit轻量化Web技术架构，集成pandas、numpy"
         "进行数据处理，matplotlib/seaborn实现可视化，biopython处理FASTA"
         "序列，scikit-learn实现机器学习预测。通过模块化设计，解耦序列分析、"
         "差异表达分析、可视化与机器学习四大功能模块；采用dataclass集中"
         "管理分析参数，保障实验可复现；内置中文字体与多字体fallback机制，"
         "支持Streamlit Community Cloud云端一键部署与本地运行。"),
        ("软件参考地址", "https://geneanalysis-app.streamlit.app/"),
        ("软件下载地址（安卓/iOS）", ""),
    ]

    info_pdf = "信息手册.pdf"
    pages = generate_info_guide_pdf(info_pdf, info_fields)
    print(f"已生成《信息手册》PDF: {info_pdf} ({pages} 页)")
