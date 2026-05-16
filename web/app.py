"""
软件著作权申请材料生成系统 - Web服务器
提供文件存储、在线编辑和分享功能
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime
import zipfile
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'copyright-application-secret-key-2024'
app.config['GENERATED_FOLDER'] = 'generated'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# 确保目录存在
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

def get_project_dir(project_id):
    """获取项目目录"""
    return os.path.join(app.config['GENERATED_FOLDER'], project_id)

def create_project(project_id, data):
    """创建或更新项目"""
    project_dir = get_project_dir(project_id)
    os.makedirs(project_dir, exist_ok=True)
    
    # 保存项目数据
    project_file = os.path.join(project_dir, 'project.json')
    with open(project_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 生成文档
    generate_documents(project_dir, data)
    
    return project_dir

def generate_documents(project_dir, data):
    """生成申请材料文档"""
    owner_name = data.get('owner_name', '未填写')
    software_type = data.get('software_type', '小程序')
    dev_purpose = data.get('dev_purpose', '未填写')
    industry = data.get('industry', '未填写')
    main_functions = data.get('main_functions', '未填写')
    tech_features = data.get('tech_features', '未填写')
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    software_name = data.get('software_name', '示例软件')
    
    # 1. 生成软件著作权登记申请表
    application_content = """# 软件著作权登记申请表

**著作权人：%s**

## 基本信息

| 字段 | 内容 |
|------|------|
| 软件全称 | %s |
| 软件简称 | %s |
| 版本号 | %s |
| 开发完成日期 | %s |
| 首次发表日期 | %s |

## 著作权人信息

| 字段 | 内容 |
|------|------|
| 著作权人 | %s |
| 证件类型 | %s |
| 证件号码 | %s |
| 地址 | %s |
| 邮编 | %s |
| 联系人 | %s |
| 电话 | %s |
| 邮箱 | %s |

## 开发者信息

| 字段 | 内容 |
|------|------|
| 开发者 | %s |
| 证件类型 | %s |
| 证件号码 | %s |
| 地址 | %s |
| 邮编 | %s |
| 联系人 | %s |
| 电话 | %s |
| 邮箱 | %s |

## 软件信息

| 字段 | 内容 |
|------|------|
| 软件性质 | 原创 |
| 软件分类 | 移动应用软件-%s |
| 代码行数 | %s |
| 开发环境 | %s |
| 运行环境 | %s |
| 编程语言 | %s |
| 硬件要求 | %s |

## 软硬件环境信息

| 字段 | 内容 |
|------|------|
| 开发的硬件环境 | %s |
| 运行的硬件环境 | %s |
| 开发该软件的操作系统 | %s |
| 软件开发环境/开发工具 | %s |
| 该软件的运行平台/操作系统 | %s |
| 软件运行支撑环境/支持软件 | %s |

## 软件技术信息

| 字段 | 内容 |
|------|------|
| 编程语言 | %s |
| 源程序量 | %s行 |
| 开发目的 | %s |
| 面向领域/行业 | %s |
| 软件的主要功能 | %s |
| 软件的技术特点 | 【%s】%s |

## 软件功能简介

- 提供便捷的用户操作体验
- 支持多种功能模块
- 数据安全可靠
- 用户界面友好

## 备注

本软件为原创开发，未使用第三方商业代码。
""" % (
        owner_name,
        software_name,
        data.get('software_short_name', '示例'),
        data.get('version', 'V1.0'),
        data.get('dev_complete_date', current_date),
        data.get('first_publish_date', current_date),
        owner_name,
        data.get('id_type', '身份证'),
        data.get('id_number', '（请填写）'),
        data.get('address', '（请填写）'),
        data.get('zip_code', '（请填写）'),
        data.get('contact', '（请填写）'),
        data.get('phone', '（请填写）'),
        data.get('email', '（请填写）'),
        owner_name,
        data.get('id_type', '身份证'),
        data.get('id_number', '（请填写）'),
        data.get('address', '（请填写）'),
        data.get('zip_code', '（请填写）'),
        data.get('contact', '（请填写）'),
        data.get('phone', '（请填写）'),
        data.get('email', '（请填写）'),
        software_type,
        data.get('code_lines', '15000'),
        data.get('dev_env', 'Visual Studio Code'),
        '微信客户端' if software_type == '小程序' else 'iOS/Android',
        data.get('programming_lang', 'JavaScript, TypeScript'),
        data.get('hardware_req', '智能手机'),
        data.get('dev_hardware', 'Intel i7-12700H, 16GB RAM'),
        data.get('run_hardware', 'Intel i5 或同等性能CPU, 4GB内存'),
        data.get('dev_os', 'Windows 11 / macOS Monterey'),
        data.get('dev_tools', 'Visual Studio Code 1.74'),
        '微信客户端' if software_type == '小程序' else 'iOS 15.0+/Android 10.0+',
        '微信小程序基础库' if software_type == '小程序' else 'Node.js 18.x',
        data.get('programming_lang', 'JavaScript, TypeScript'),
        data.get('code_lines', '15000'),
        dev_purpose,
        industry,
        main_functions,
        software_type,
        tech_features
    )
    
    with open(os.path.join(project_dir, 'software-copyright-form.md'), 'w', encoding='utf-8') as f:
        f.write(application_content)
    
    # 2. 生成用户手册
    manual_content = """# %s 用户手册

**著作权人：%s**

## 一、软件简介

本软件是一款%s，为用户提供便捷的服务体验。

### 1.1 软件概述

%s是一款功能强大的%s，运行于%s。

### 1.2 主要特点

- 简洁易用的用户界面
- 稳定可靠的性能
- 丰富的功能模块
- 良好的用户体验

## 二、功能概述

### 2.1 功能列表

1. 用户注册与登录
2. 数据管理
3. 信息查询
4. 数据导出
5. 系统设置

### 2.2 适用场景

本软件适用于%s领域，为用户提供专业的解决方案。

## 三、安装/使用说明

### 3.1 系统要求

- 平台：%s
- 技术栈：%s

### 3.2 使用说明

%s

## 四、主要功能说明

### 4.1 用户注册与登录

该功能提供了便捷的用户注册和登录体验。

**操作步骤：**
1. 点击注册/登录按钮
2. 输入用户名和密码
3. 完成验证
4. 进入系统

## 五、操作步骤

### 5.1 基本操作

1. 启动软件
2. 完成必要的初始化设置
3. 根据需求选择相应功能
4. 按照界面提示完成操作

### 5.2 高级操作

1. 进入高级设置界面
2. 自定义配置参数
3. 保存设置

## 六、注意事项

1. 请确保网络连接正常
2. 首次使用可能需要授权
3. 数据保存在本地，清除缓存会丢失数据
4. 请定期备份重要数据

## 七、常见问题

### 7.1 无法打开应用

- 检查网络连接是否正常
- 确认应用是否已正确安装
- 尝试重启应用或设备

### 7.2 数据加载失败

- 检查网络连接
- 清除应用缓存后重试
- 更新应用到最新版本

## 八、技术支持

### 8.1 版本信息

- 软件版本：%s
- 更新日期：%s
- 著作权人：%s
""" % (
        software_name,
        owner_name,
        software_type,
        software_name,
        software_type,
        '微信小程序平台' if software_type == '小程序' else '移动设备',
        industry,
        '微信客户端' if software_type == '小程序' else 'iOS/Android',
        data.get('programming_lang', 'JavaScript, TypeScript'),
        '1. 打开微信客户端\n2. 搜索或扫描小程序二维码\n3. 进入小程序开始使用' if software_type == '小程序' else '1. 下载并安装应用程序\n2. 启动应用程序\n3. 按照界面提示开始使用',
        data.get('version', 'V1.0'),
        current_date,
        owner_name
    )
    
    with open(os.path.join(project_dir, 'user-manual.md'), 'w', encoding='utf-8') as f:
        f.write(manual_content)
    
    # 3. 生成设计说明书
    design_content = """# %s 设计说明书

**著作权人：%s**

## 一、软件概述

### 1.1 软件简介

本软件是一款%s，为用户提供便捷的服务体验。

### 1.2 开发背景

%s，开发了%s。

### 1.3 设计目标

- 提供简洁易用的用户界面
- 实现稳定可靠的功能
- 优化用户体验
- 确保数据安全

## 二、需求分析

### 2.1 功能需求

1. 用户注册与登录
2. 数据管理
3. 信息查询
4. 数据导出
5. 系统设置

### 2.2 行业领域

本软件主要面向%s领域。

### 2.3 性能需求

- 响应时间：操作响应时间小于500ms
- 并发支持：支持多用户同时使用
- 资源占用：内存占用合理
- 稳定性：运行稳定，无崩溃

### 2.4 安全需求

- 数据加密：敏感数据加密存储
- 权限控制：合理的权限管理
- 防护措施：防止常见安全漏洞

## 三、总体设计

### 3.1 系统架构

本软件采用%s架构，基于%s开发。

### 3.2 模块划分

软件主要包含以下模块：

- 主界面模块：负责用户界面的展示和交互
- 业务逻辑模块：处理核心业务逻辑
- 数据存储模块：负责数据的存储和管理
- 工具模块：提供通用工具函数
- 网络通信模块：处理与服务器的数据交互

### 3.3 技术选型

- %s

### 3.4 运行环境

- 平台：%s
- 基础库版本：最新
- 硬件要求：智能手机

## 四、详细设计

### 4.1 主界面模块

#### 4.1.1 模块功能

负责软件主界面的展示和用户交互。

#### 4.1.2 模块接口

- 页面路由接口
- 事件处理接口
- 生命周期管理接口

### 4.2 业务逻辑模块

#### 4.2.1 模块功能

处理软件的核心业务逻辑。

#### 4.2.2 模块接口

- 数据处理接口
- 计算接口
- 业务规则验证接口

### 4.3 数据存储模块

#### 4.3.1 模块功能

负责数据的持久化存储。

#### 4.3.2 数据存储方式

- 本地存储：使用本地缓存存储用户配置
- 数据格式：JSON格式

## 五、数据结构设计

### 5.1 数据存储

使用本地存储保存用户数据。

### 5.2 数据格式

- JSON格式存储配置信息
- 数组格式存储历史记录
- 键值对形式存储用户偏好设置

### 5.3 数据关系

- 用户信息与使用记录一一对应
- 配置信息独立存储
- 缓存数据定期清理

## 六、接口设计

### 6.1 内部接口

- 模块间通信接口
- 数据传递接口

### 6.2 外部接口

- API调用接口
- 数据上报接口

## 七、算法设计

### 7.1 核心算法

- 数据处理算法
- 排序算法
- 搜索算法

### 7.2 算法流程

1. 数据采集
2. 数据处理
3. 结果输出

## 八、界面设计

### 8.1 界面布局

采用响应式布局，适配不同屏幕尺寸。

### 8.2 交互设计

- 点击交互：按钮点击触发相应功能
- 手势交互：支持滑动等手势操作
- 表单交互：用户输入数据的交互

### 8.3 界面元素

- 按钮：触发功能操作
- 输入框：接收用户输入
- 列表：展示数据列表
- 弹窗：提示信息或确认操作

## 九、安全设计

### 9.1 安全机制

- 输入验证：对用户输入进行验证
- 错误处理：完善的错误处理机制
- 异常捕获：防止程序崩溃

### 9.2 数据保护

- 敏感数据加密存储
- 重要操作需要确认
- 数据备份机制

## 十、测试设计

### 10.1 测试策略

- 单元测试：测试各个功能模块
- 集成测试：测试模块间的交互
- 用户测试：真实用户使用测试
- 压力测试：验证系统稳定性

### 10.2 测试用例

- 功能测试用例
- 界面测试用例
- 性能测试用例
- 安全测试用例

### 10.3 测试环境

- 开发工具：%s
- 操作系统：%s
- 硬件环境：%s
""" % (
        software_name,
        owner_name,
        software_type,
        dev_purpose,
        software_name,
        industry,
        software_type,
        data.get('programming_lang', 'JavaScript, TypeScript'),
        data.get('programming_lang', 'JavaScript, TypeScript').replace(', ', '\n- '),
        '微信小程序平台' if software_type == '小程序' else 'iOS/Android',
        data.get('dev_tools', 'Visual Studio Code'),
        data.get('dev_os', 'Windows 11'),
        data.get('dev_hardware', 'Intel i7-12700H, 16GB RAM')
    )
    
    with open(os.path.join(project_dir, 'design-specification.md'), 'w', encoding='utf-8') as f:
        f.write(design_content)
    
    # 4. 生成源代码文档
    source_content = """# %s 源代码文档

**著作权人：%s**

软件名称：%s
版本号：%s
生成日期：%s

---

## 前30页（核心业务逻辑）

本源代码文档包含软件的核心业务逻辑代码片段。完整的源代码文档应包含所有代码文件，每个文件标注文件名、路径和行数。

## 代码文件说明

### 主要文件列表

1. **app.js** - 应用入口文件，包含服务器配置和路由定义
2. **utils/helpers.js** - 工具函数库，提供通用工具函数
3. **controllers/userController.js** - 用户控制器，处理用户相关业务逻辑
4. **models/User.js** - 用户数据模型，定义用户数据结构
5. **routes/index.js** - 路由配置文件，管理所有API路由

## 代码片段示例

### 示例1：应用入口文件（app.js）

```javascript
const express = require('express');
const app = express();

// 中间件配置
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 路由配置
app.use('/api', require('./routes'));

// 错误处理
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Internal Server Error' });
});

// 启动服务器
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
```

### 示例2：工具函数库（utils/helpers.js）

```javascript
// 工具函数库

/**
 * 格式化日期
 * @param {Date} date - 日期对象
 * @returns {string} 格式化后的日期字符串
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * 生成唯一ID
 * @returns {string} 唯一ID
 */
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

module.exports = {
    formatDate,
    generateId
};
```

### 示例3：用户控制器（controllers/userController.js）

```javascript
// 用户控制器
const User = require('../models/User');

/**
 * 获取用户列表
 */
async function getUsers(req, res) {
    try {
        const users = await User.find();
        res.json(users);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
}

/**
 * 创建用户
 */
async function createUser(req, res) {
    try {
        const user = new User(req.body);
        await user.save();
        res.status(201).json(user);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
}

module.exports = {
    getUsers,
    createUser
};
```

## 注意事项

1. 源代码应为原创代码，未使用第三方商业代码
2. 代码应清晰、规范，便于审查
3. 注释应完整，便于理解代码逻辑
4. 所有代码文件应按照重要性排序，主要业务逻辑在前
5. 每个文件应包含文件头注释，说明文件名、路径和行数
""" % (
        software_name,
        owner_name,
        software_name,
        data.get('version', 'V1.0'),
        current_date
    )
    
    with open(os.path.join(project_dir, 'source-code.md'), 'w', encoding='utf-8') as f:
        f.write(source_content)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/editor/<project_id>')
def editor(project_id):
    """编辑器页面"""
    return render_template('editor.html', project_id=project_id)

@app.route('/api/projects', methods=['POST'])
def create_new_project():
    """创建新项目"""
    data = request.json
    project_id = str(uuid.uuid4())
    
    create_project(project_id, data)
    
    return jsonify({
        'success': True,
        'project_id': project_id,
        'message': '项目创建成功'
    })

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """获取项目数据"""
    project_file = os.path.join(get_project_dir(project_id), 'project.json')
    
    if not os.path.exists(project_file):
        return jsonify({
            'success': False,
            'message': '项目不存在'
        }), 404
    
    with open(project_file, 'r', encoding='utf-8') as f:
        project_data = json.load(f)
    
    return jsonify({
        'success': True,
        'data': project_data
    })

@app.route('/api/projects/<project_id>/documents', methods=['GET'])
def get_documents(project_id):
    """获取项目文档列表"""
    project_dir = get_project_dir(project_id)
    
    if not os.path.exists(project_dir):
        return jsonify({
            'success': False,
            'message': '项目不存在'
        }), 404
    
    # 文件名映射
    file_map = {
        'software-copyright-form.md': '软件著作权登记申请表.md',
        'user-manual.md': '用户手册.md',
        'design-specification.md': '设计说明书.md',
        'source-code.md': '源代码文档.md'
    }
    
    documents = []
    for filename in os.listdir(project_dir):
        if filename.endswith('.md') and filename != 'project.json':
            filepath = os.path.join(project_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            display_name = file_map.get(filename, filename)
            
            documents.append({
                'name': display_name,
                'filename': filename,
                'content': content,
                'size': len(content),
                'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return jsonify({
        'success': True,
        'documents': documents
    })

@app.route('/api/projects/<project_id>/documents/<filename>', methods=['GET'])
def get_document(project_id, filename):
    """获取单个文档内容"""
    # 文件名反向映射
    file_map = {
        '软件著作权登记申请表.md': 'software-copyright-form.md',
        '用户手册.md': 'user-manual.md',
        '设计说明书.md': 'design-specification.md',
        '源代码文档.md': 'source-code.md'
    }
    
    actual_filename = file_map.get(filename, filename)
    filepath = os.path.join(get_project_dir(project_id), actual_filename)
    
    if not os.path.exists(filepath):
        return jsonify({
            'success': False,
            'message': '文档不存在'
        }), 404
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return jsonify({
        'success': True,
        'content': content,
        'filename': filename
    })

@app.route('/api/projects/<project_id>/documents/<filename>', methods=['PUT'])
def update_document(project_id, filename):
    """更新文档内容"""
    # 文件名反向映射
    file_map = {
        '软件著作权登记申请表.md': 'software-copyright-form.md',
        '用户手册.md': 'user-manual.md',
        '设计说明书.md': 'design-specification.md',
        '源代码文档.md': 'source-code.md'
    }
    
    actual_filename = file_map.get(filename, filename)
    data = request.json
    filepath = os.path.join(get_project_dir(project_id), actual_filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data.get('content', ''))
    
    return jsonify({
        'success': True,
        'message': '文档保存成功'
    })

@app.route('/api/projects/<project_id>/export', methods=['POST'])
def export_project(project_id):
    """导出项目文档"""
    project_dir = get_project_dir(project_id)
    
    if not os.path.exists(project_dir):
        return jsonify({
            'success': False,
            'message': '项目不存在'
        }), 404
    
    # 创建ZIP文件 - 使用英文文件名
    zip_filename = 'copyright-materials-%s.zip' % project_id[:8]
    zip_filepath = os.path.join(app.config['GENERATED_FOLDER'], zip_filename)
    
    # 文件名映射
    file_map = {
        'software-copyright-form.md': '软件著作权登记申请表.md',
        'user-manual.md': '用户手册.md',
        'design-specification.md': '设计说明书.md',
        'source-code.md': '源代码文档.md'
    }
    
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith('.md') and file != 'project.json':
                    file_path = os.path.join(root, file)
                    arcname = file_map.get(file, file)
                    zipf.write(file_path, arcname)
    
    return jsonify({
        'success': True,
        'download_url': '/api/download/%s' % zip_filename
    })

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """下载文件"""
    filepath = os.path.join(app.config['GENERATED_FOLDER'], secure_filename(filename))
    
    if not os.path.exists(filepath):
        return jsonify({
            'success': False,
            'message': '文件不存在'
        }), 404
    
    # 为下载设置中文文件名
    download_name = filename.replace('copyright-materials-', '软件著作权申请材料-')
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=download_name
    )

@app.route('/api/projects/<project_id>/share', methods=['POST'])
def share_project(project_id):
    """生成分享链接"""
    project_dir = get_project_dir(project_id)
    
    if not os.path.exists(project_dir):
        return jsonify({
            'success': False,
            'message': '项目不存在'
        }), 404
    
    share_link = '%seditor/%s' % (request.host_url, project_id)
    
    return jsonify({
        'success': True,
        'share_link': share_link
    })

if __name__ == '__main__':
    print("="*60)
    print("软件著作权申请材料生成系统")
    print("="*60)
    print("访问地址：http://localhost:5002")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5002, threaded=True)
