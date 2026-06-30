# 🧬 基因表达调控分析与预测平台

一个功能完整的基因表达数据分析Web应用，集成了序列分析、差异表达分析、可视化和机器学习预测四大核心功能。

## ✨ 功能特性

- 🔬 **序列分析**：GC含量计算、核苷酸频率统计、序列长度分布
- 📊 **差异表达分析**：t检验统计、BH-FDR多重校正、上调/下调基因识别
- 📈 **可视化图表**：火山图、表达热图、PCA主成分分析、GC含量分布图
- 🤖 **机器学习**：随机森林分类、特征重要性分析、模型性能评估

## 🚀 快速开始
你可以直接使用已经部署到Streamlit的应用，也可以选择自己部署

###直接运行
如果想直接用软件，请在浏览器中访问 https://geneanalysis-app.streamlit.app/

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app.py
```

然后在浏览器中访问 http://localhost:8501

### 一键部署到云端

点击下方按钮，一键部署到 Streamlit Community Cloud（完全免费）：

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

## 📦 部署到 Streamlit Community Cloud

### 前置条件

1. 一个 GitHub 账号（免费注册：https://github.com/join）
2. 一个 Streamlit Community Cloud 账号（免费注册：https://share.streamlit.io/）

### 详细步骤

#### 第一步：创建 GitHub 仓库

1. 登录 GitHub，点击右上角 **"+"** → **"New repository"**
2. 填写仓库信息：
   - **Repository name**: `GeneAnalysis`（或你喜欢的名字）
   - **Description**: 基因表达调控分析与预测平台
   - **Public / Private**: 选择 Public（免费版只支持公开仓库）
   - 勾选 **"Add a README file"**（可选）
3. 点击 **"Create repository"**

#### 第二步：上传代码到 GitHub

**方法一：使用 Git 命令行（推荐）**

```bash
# 进入项目目录
cd GeneAnalysis

# 初始化Git仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit: 基因表达分析平台"

# 关联远程仓库（替换为你的GitHub仓库地址）
git remote add origin https://github.com/你的用户名/GeneAnalysis.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

**方法二：使用 GitHub Desktop（图形界面）**

1. 下载安装 GitHub Desktop：https://desktop.github.com/
2. 打开 GitHub Desktop，登录你的账号
3. 点击 **"File" → "Add Local Repository"**
4. 选择你的 GeneAnalysis 文件夹
5. 点击 **"Create a repository"**
6. 填写仓库信息，点击 **"Create repository"**
7. 点击 **"Publish repository"** 推送到 GitHub

**方法三：直接在网页上传（最简单，适合小项目）**

1. 打开你刚创建的 GitHub 仓库页面
2. 点击 **"Add file" → "Upload files"**
3. 把 GeneAnalysis 文件夹里的所有文件（除了 `env/`、`__pycache__/` 等）拖进去
4. 点击 **"Commit changes"**

#### 第三步：部署到 Streamlit Community Cloud

1. 访问 https://share.streamlit.io/
2. 点击 **"Sign up with GitHub"**，用 GitHub 账号登录
3. 授权 Streamlit 访问你的 GitHub 仓库
4. 登录后，点击 **"New app"** 按钮
5. 填写部署信息：
   - **Repository**: 选择你刚创建的仓库（如 `你的用户名/GeneAnalysis`）
   - **Branch**: `main`（或 `master`）
   - **Main file path**: `app.py`（注意路径！如果app.py在根目录就直接写app.py）
6. 点击 **"Deploy!"**
7. 等待 1-3 分钟，部署完成后会自动跳转到你的应用页面

### 部署后的URL

部署成功后，你的应用网址类似：
```
https://你的用户名-geneanalysis-app.streamlit.app
```

你可以把这个网址分享给任何人，他们都可以在浏览器中直接访问使用！

### 自定义域名（可选）

如果你有自己的域名，可以在 Streamlit Cloud 设置中配置自定义域名：

1. 在应用页面点击 **"Settings"**
2. 选择 **"General"** 标签
3. 在 **"Custom domain"** 中填入你的域名
4. 按照提示在域名服务商处配置DNS记录

## 📁 项目结构

```
GeneAnalysis/
├── app.py                  # Streamlit应用主入口
├── requirements.txt        # Python依赖
├── .gitignore              # Git忽略文件
├── .streamlit/
│   └── config.toml         # Streamlit配置
├── config.py               # 配置管理
├── data/                   # 示例数据
│   ├── simulated_genes.fasta
│   └── simulated_expression.csv
├── data_processing/        # 数据处理模块
│   ├── fasta_reader.py
│   └── data_cleaner.py
├── sequence_analysis/      # 序列分析模块
│   └── basic_stats.py
├── expression_analysis/    # 表达分析模块
│   └── differential.py
├── visualization/          # 可视化模块
│   └── plots.py
└── machine_learning/       # 机器学习模块
    └── classifier.py
```

## 🎯 使用说明

### 1. 数据配置
- 上传 FASTA 格式的序列文件
- 上传 CSV 格式的基因表达矩阵
- 设置分析参数（P值阈值、倍数变化阈值等）
- 配置对照组和处理组样本

### 2. 运行分析
- 点击"开始完整分析流程"按钮
- 实时查看分析进度和日志
- 等待所有步骤完成

### 3. 结果展示
- 查看火山图、热图、PCA图、GC分布图
- 浏览差异表达基因表格
- 查看机器学习模型性能指标

### 4. 下载结果
- 下载差异表达分析结果（CSV）
- 下载高清图表（PNG，300 DPI）

## 🔧 常见问题

### Q: 部署失败怎么办？
A: 检查以下几点：
1. `requirements.txt` 是否在仓库根目录
2. `app.py` 路径是否正确
3. 依赖包名称是否正确
4. 查看 Streamlit Cloud 的部署日志获取详细错误信息

### Q: 应用加载很慢？
A: 首次加载需要安装依赖，可能需要1-3分钟。后续访问会快很多。

### Q: 如何更新应用？
A: 直接把新代码推送到 GitHub，Streamlit Cloud 会自动检测更新并重新部署。

### Q: 可以使用私有仓库吗？
A: Streamlit Cloud 免费版只支持公开仓库。私有仓库需要付费版。

### Q: 有使用限制吗？
A: 免费版有资源限制（内存、CPU、时长），适合个人和小团队使用。大规模使用建议升级付费版或自己部署。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Made with ❤️ by GeneAnalysis Team**
