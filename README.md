# Chinese Copyright Application Skill

用于生成中国软件著作权申请材料的完整工具包。支持从项目代码、文档等自动提取信息，生成软件著作权登记申请表、源代码文档（前后各30页）、用户手册和设计说明书。适用于微信小程序、Web应用、移动App、桌面应用等各类软件项目。

## 功能特性

- **自动分析项目结构**：智能识别项目类型（微信小程序、Web/Node.js等）
- **交互式信息收集**：引导用户输入著作权人和软件信息
- **完整申请材料**：生成符合中国版权保护中心要求的所有文档
- **源代码文档**：自动提取前后各30页，每页50行
- **多格式输出**：支持Markdown和PDF格式
- **详细的文档模板**：包含用户手册和设计说明书模板

## 快速开始

### 前提条件

- Python 3.6+
- 可选：wkhtmltopdf（用于生成PDF）

### 安装依赖

```bash
pip install markdown pdfkit
```

### 安装wkhtmltopdf（用于PDF转换）

**Ubuntu/Debian:**
```bash
sudo apt-get install wkhtmltopdf
```

**macOS:**
```bash
brew install wkhtmltopdf
```

**Windows:**
从 https://wkhtmltopdf.org/downloads.html 下载并安装

## 使用方法

### 方法1：使用Python脚本（交互式）

```bash
cd qoder-chinese-copyright-application-skill
python3 scripts/generate_copyright_docs.py <项目路径> [输出目录]
```

**示例：**

```bash
# 在当前目录生成文档
python3 scripts/generate_copyright_docs.py /path/to/your/project

# 指定输出目录
python3 scripts/generate_copyright_docs.py /path/to/your/project /path/to/output
```

脚本会交互式地询问以下信息：

1. **著作权人信息**：
   - 名称（个人姓名或公司全称）
   - 证件类型（身份证/营业执照）
   - 证件号码
   - 联系地址
   - 邮政编码
   - 联系人
   - 联系电话
   - 电子邮箱

2. **软件信息**：
   - 开发目的（限50字）
   - 面向领域/行业（限50字）
   - 软件的主要功能（限200字）
   - 软件的技术特点（限100字）
   - 软件类型（APP/小程序/游戏软件等）

### 方法2：在Trae IDE中使用

当用户需要申请中国软件著作权时，这个skill会自动触发，提供完整的生成流程指导。

## 生成的文档

所有文档将生成在 `copyright-application-materials/` 目录下：

1. **软件著作权登记申请表.md** - 包含所有必填字段的申请表
   - 基本信息（软件全称、版本号、日期等）
   - 著作权人信息
   - 开发者信息
   - 软件信息
   - 软硬件环境信息
   - 软件技术信息

2. **源代码文档.md** - 前后各30页，每页50行的源代码
   - 按文件重要性排序
   - 包含文件路径和行数
   - 标准页格式，便于打印

3. **用户手册.md** - 完整的用户使用手册
   - 软件简介
   - 功能概述
   - 安装/使用说明
   - 主要功能说明
   - 操作步骤
   - 常见问题
   - 技术支持

4. **设计说明书.md** - 详细的技术设计文档
   - 软件概述
   - 需求分析
   - 总体设计
   - 详细设计
   - 数据结构设计
   - 接口设计
   - 算法设计
   - 界面设计
   - 安全设计
   - 测试设计

## PDF转换

### 方法1：使用转换脚本（推荐）

生成Markdown文档后，使用以下命令转换为PDF：

```bash
# 转换单个文件
python3 scripts/convert_to_pdf.py 源代码文档.md

# 转换整个目录
python3 scripts/convert_to_pdf.py copyright-application-materials/
```

### 方法2：使用在线工具

- **Typora** - Markdown编辑器，支持直接导出PDF
- **GitHub + 导出** - 将README等文件导出为PDF
- **Marp** - Markdown演示工具，支持PDF导出

### 方法3：使用命令行工具

```bash
# 使用pandoc
pandoc input.md -o output.pdf

# 使用markdown-pdf
npx markdown-pdf input.md
```

## 支持的项目类型

- **微信小程序**（app.json, project.config.json）
- **Web/Node.js项目**（package.json）
- **Python项目**（setup.py, pyproject.toml）
- **Java项目**（pom.xml, build.gradle）
- **其他项目**（自动查找配置文件）

## 项目信息来源

- **微信小程序**：app.json, project.config.json, package.json, README.md
- **Web/Node.js**：package.json, README.md
- **Python**：setup.py, pyproject.toml, README.md
- **其他项目**：自动查找配置文件和README

## 申请表字段说明

根据中国版权保护中心要求，生成的申请表包含以下字段：

### 必填字段

- **软件全称**：应当有辨识度，应该叫"xxx软件"
- **版本号**：保留两位，例如"1.0"、"1.1"等
- **开发的硬件环境**：开发使用的计算机配置
- **运行的硬件环境**：运行所需的最低配置
- **开发该软件的操作系统**：Windows/macOS/Linux等
- **软件开发环境/开发工具**：IDE版本等
- **该软件的运行平台/操作系统**：目标平台
- **软件运行支撑环境/支持软件**：依赖的运行时
- **编程语言**：主要使用的语言
- **源程序量**：代码总行数
- **开发目的**：限50字
- **面向领域/行业**：限50字
- **软件的主要功能**：限200字
- **软件的技术特点**：限100字

## 注意事项

- **著作权人信息**：确保在所有文档开头都包含著作权人名称
- **申请表完整性**：所有必填字段必须完整
- **源代码要求**：前后各30页，每页50行，不足则全部提供
- **信息一致性**：所有文档中的软件名称、版本号必须一致
- **原创性声明**：确保软件为原创，不侵犯他人著作权

## 文档模板

项目提供了完整的文档模板，位于 `references/` 目录：

- `application-form-template.md` - 申请表模板
- `user-manual-template.md` - 用户手册模板
- `design-doc-template.md` - 设计说明书模板
- `requirements.md` - 申请要求说明

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 支持

如有问题，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件至项目维护者
