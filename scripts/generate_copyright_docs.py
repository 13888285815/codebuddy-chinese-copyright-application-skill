#!/usr/bin/env python3
"""
中国软件著作权申请材料生成器
支持多种项目类型，自动生成申请表、源代码文档、用户手册和设计说明书，并可转换为PDF
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import subprocess
import sys

class CopyrightDocGenerator:
    """中国软件著作权申请材料生成器"""
    
    def __init__(self, project_path: str, output_dir: str = None):
        """
        初始化生成器
        
        Args:
            project_path: 项目路径
            output_dir: 输出目录，默认为项目路径下的 copyright-application-materials
        """
        self.project_path = Path(project_path).resolve()
        self.output_dir = Path(output_dir) if output_dir else self.project_path / 'copyright-application-materials'
        self.project_info = {
            'name': '',
            'version': '1.0.0',
            'description': '',
            'author': '',
            'type': '未知',
            'platform': '未知',
            'tech_stack': [],
            'features': [],
            'structure': {},
            'dependencies': [],
            'entry_file': None,
            'config_files': []
        }
        self.code_files = []
        self.total_lines = 0
        
    def log(self, message: str, level: str = 'INFO'):
        """打印日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def analyze_project(self) -> Dict:
        """
        分析项目结构，提取项目信息
        
        Returns:
            项目信息字典
        """
        self.log("开始分析项目...")
        
        # 检测项目类型
        self._detect_project_type()
        
        # 提取项目信息
        self._extract_project_info()
        
        # 收集代码文件
        self._collect_code_files()
        
        # 分析项目结构
        self._analyze_structure()
        
        # 统计代码行数
        self.total_lines = self.count_code_lines()
        
        self.log(f"项目分析完成：{self.project_info['name']} ({self.project_info['type']})")
        self.log(f"代码文件数：{len(self.code_files)}，总行数：{self.total_lines}")
        
        return self.project_info
    
    def _detect_project_type(self):
        """检测项目类型"""
        # 微信小程序
        if (self.project_path / 'app.json').exists() or (self.project_path / 'project.config.json').exists():
            self.project_info['type'] = '微信小程序'
            self.project_info['platform'] = '微信小程序平台'
            self.project_info['tech_stack'].append('微信小程序原生框架')
            return
        
        # Web前端项目
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                if 'vue' in deps or 'react' in deps or 'angular' in deps:
                    self.project_info['type'] = 'Web应用'
                    self.project_info['platform'] = '浏览器'
                    if 'vue' in deps:
                        self.project_info['tech_stack'].append('Vue.js')
                    if 'react' in deps:
                        self.project_info['tech_stack'].append('React')
                    if 'angular' in deps:
                        self.project_info['tech_stack'].append('Angular')
                    return
        
        # Node.js后端项目
        if (self.project_path / 'package.json').exists():
            self.project_info['type'] = 'Node.js应用'
            self.project_info['platform'] = '服务器'
            self.project_info['tech_stack'].append('Node.js')
            return
        
        # Python项目
        if (self.project_path / 'requirements.txt').exists() or (self.project_path / 'setup.py').exists():
            self.project_info['type'] = 'Python应用'
            self.project_info['platform'] = '跨平台'
            self.project_info['tech_stack'].append('Python')
            return
        
        # Java项目
        if (self.project_path / 'pom.xml').exists() or (self.project_path / 'build.gradle').exists():
            self.project_info['type'] = 'Java应用'
            self.project_info['platform'] = '跨平台'
            self.project_info['tech_stack'].append('Java')
            return
        
        # 其他类型
        self.project_info['type'] = '通用软件'
        self.project_info['platform'] = '跨平台'
    
    def _extract_project_info(self):
        """从配置文件中提取项目信息"""
        # 微信小程序
        app_json = self.project_path / 'app.json'
        if app_json.exists():
            with open(app_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not self.project_info['name']:
                    self.project_info['name'] = data.get('window', {}).get('navigationBarTitleText', '')
        
        project_config = self.project_path / 'project.config.json'
        if project_config.exists():
            with open(project_config, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.project_info['appid'] = data.get('appid', '')
                self.project_info['lib_version'] = data.get('libVersion', '')
        
        # package.json
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not self.project_info['name']:
                    self.project_info['name'] = data.get('name', '')
                self.project_info['version'] = data.get('version', '1.0.0')
                self.project_info['description'] = data.get('description', '')
                self.project_info['author'] = data.get('author', '')
                self.project_info['dependencies'] = list(data.get('dependencies', {}).keys())
        
        # README.md
        readme = self.project_path / 'README.md'
        if readme.exists():
            with open(readme, 'r', encoding='utf-8') as f:
                content = f.read()
                self._extract_features_from_readme(content)
                # 如果没有从配置文件中获取到名称，尝试从README中提取
                if not self.project_info['name']:
                    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    if title_match:
                        self.project_info['name'] = title_match.group(1).strip()
        
        # 如果名称仍然为空，使用项目目录名
        if not self.project_info['name']:
            self.project_info['name'] = self.project_path.name
        
        # 确保名称以"软件"结尾（符合软著申请要求）
        if '软件' not in self.project_info['name'] and not self.project_info['name'].endswith('软件'):
            self.project_info['name'] = self.project_info['name'] + '软件'
    
    def _extract_features_from_readme(self, content: str):
        """从README中提取功能特性"""
        features = []
        lines = content.split('\n')
        in_features = False
        feature_keywords = ['功能', '特性', 'features', 'functionality', '功能特性', '主要功能']
        
        for i, line in enumerate(lines):
            # 检测功能特性章节
            if any(kw in line.lower() for kw in feature_keywords) and ('##' in line or '#' in line):
                in_features = True
                continue
            
            # 遇到新的章节，结束功能特性提取
            if in_features and line.startswith('#'):
                break
            
            # 提取功能特性
            if in_features:
                # 匹配列表项
                if line.strip().startswith(('-', '*', '•', '✅')) or re.match(r'^\d+\.', line.strip()):
                    feature = re.sub(r'^[-*•✅\d\.]\s*', '', line.strip())
                    if feature and len(feature) > 5:  # 过滤太短的内容
                        features.append(feature)
        
        # 如果没有找到功能特性章节，尝试提取所有列表项
        if not features:
            for line in lines:
                if line.strip().startswith(('-', '*', '•', '✅')) or re.match(r'^\d+\.', line.strip()):
                    feature = re.sub(r'^[-*•✅\d\.]\s*', '', line.strip())
                    if feature and len(feature) > 5:
                        features.append(feature)
        
        self.project_info['features'] = features[:20]  # 限制最多20个功能特性
    
    def _collect_code_files(self):
        """收集项目中的代码文件"""
        code_extensions = {
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React JSX',
            '.tsx': 'React TSX',
            '.wxml': '微信小程序WXML',
            '.wxss': '微信小程序WXSS',
            '.json': 'JSON配置',
            '.py': 'Python',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.c': 'C',
            '.cpp': 'C++',
            '.h': 'C/C++ Header',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.dart': 'Dart'
        }
        
        exclude_dirs = [
            '.git', 'node_modules', '__pycache__', 'dist', 'build', '.trae',
            'venv', '.venv', 'env', 'target', 'bin', 'obj', 'packages',
            '.idea', '.vscode', '.settings', 'vendor'
        ]
        
        exclude_files = [
            'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            '.gitignore', '.eslintrc', '.prettierrc', 'tsconfig.json'
        ]
        
        for root, dirs, files in os.walk(self.project_path):
            # 过滤排除目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # 检查文件扩展名
                if file_path.suffix in code_extensions:
                    # 检查是否在排除文件中
                    if file not in exclude_files:
                        relative_path = file_path.relative_to(self.project_path)
                        self.code_files.append({
                            'path': str(relative_path),
                            'full_path': file_path,
                            'language': code_extensions[file_path.suffix],
                            'size': file_path.stat().st_size if file_path.exists() else 0
                        })
        
        # 按优先级排序
        self.code_files.sort(key=lambda x: self._file_priority(x['path']))
    
    def _file_priority(self, file_path: str) -> int:
        """计算文件优先级（数字越小优先级越高）"""
        path = Path(file_path)
        filename = path.name.lower()
        
        # 入口文件
        if filename in ['app.js', 'main.js', 'index.js', 'app.py', 'main.py', 'index.py']:
            return 0
        
        # 配置文件
        if filename in ['config.js', 'config.py', 'settings.py', 'configuration.py']:
            return 5
        
        # 工具函数
        if 'utils' in str(path) or 'helpers' in str(path) or 'tools' in str(path):
            return 10
        
        # 页面/组件
        if 'pages' in str(path) or 'components' in str(path) or 'views' in str(path):
            return 20
        
        # 路由/控制器
        if 'router' in str(path) or 'route' in str(path) or 'controller' in str(path):
            return 15
        
        # 模型/数据
        if 'model' in str(path) or 'schema' in str(path) or 'entity' in str(path):
            return 25
        
        # 配置文件
        if 'config' in str(path):
            return 30
        
        # 测试文件
        if 'test' in str(path) or 'spec' in str(path):
            return 100
        
        return 50
    
    def _analyze_structure(self):
        """分析项目结构"""
        structure = {}
        
        for file_info in self.code_files:
            parts = Path(file_info['path']).parts
            current = structure
            
            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # 文件
                    if part not in current:
                        current[part] = {
                            'type': 'file',
                            'language': file_info['language'],
                            'size': file_info['size']
                        }
                else:  # 目录
                    if part not in current:
                        current[part] = {'type': 'directory', 'children': {}}
                    if 'children' not in current[part]:
                        current[part]['children'] = {}
                    current = current[part]['children']
        
        self.project_info['structure'] = structure
    
    def count_code_lines(self) -> int:
        """统计代码总行数"""
        total_lines = 0
        
        for file_info in self.code_files:
            try:
                with open(file_info['full_path'], 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
            except Exception as e:
                self.log(f"无法读取文件 {file_info['path']}: {e}", 'WARNING')
        
        return total_lines
    
    def generate_all_docs(self, owner_info: Optional[Dict] = None):
        """
        生成所有申请材料
        
        Args:
            owner_info: 著作权人信息字典
        """
        self.log("开始生成申请材料...")
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成申请表
        self.log("生成软件著作权登记申请表...")
        self.generate_application_form(owner_info)
        
        # 生成源代码文档
        self.log("生成源代码文档...")
        self.generate_source_code_doc()
        
        # 生成用户手册
        self.log("生成用户手册...")
        self.generate_user_manual()
        
        # 生成设计说明书
        self.log("生成设计说明书...")
        self.generate_design_doc()
        
        # 转换为PDF
        self.log("转换为PDF格式...")
        self.convert_to_pdf()
        
        self.log(f"所有文档已生成到：{self.output_dir}")
    
    def generate_application_form(self, owner_info: Optional[Dict] = None):
        """生成软件著作权登记申请表"""
        output_file = self.output_dir / '软件著作权登记申请表.md'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {self.project_info['name']} - 软件著作权登记申请表\n\n")
            f.write(f"**生成日期**：{datetime.now().strftime('%Y年%m月%d日')}\n\n")
            f.write("---\n\n")
            
            # 基本信息
            f.write("## 一、软件基本信息\n\n")
            f.write("| 字段 | 内容 |\n")
            f.write("|------|------|\n")
            f.write(f"| 软件全称 | {self.project_info['name']} |\n")
            
            # 软件简称（取名称前10个字符）
            short_name = self.project_info['name'][:10] if len(self.project_info['name']) > 10 else self.project_info['name']
            f.write(f"| 软件简称 | {short_name} |\n")
            
            f.write(f"| 版本号 | V{self.project_info['version']} |\n")
            f.write(f"| 软件类型 | {self.project_info['type']} |\n")
            f.write(f"| 开发完成日期 | {datetime.now().strftime('%Y-%m-%d')} |\n")
            f.write(f"| 首次发表日期 | {datetime.now().strftime('%Y-%m-%d')} |\n")
            f.write(f"| 软件分类 | {self._get_software_category()} |\n")
            f.write(f"| 软件性质 | 原创 |\n\n")
            
            # 著作权人信息
            f.write("## 二、著作权人信息\n\n")
            f.write("| 字段 | 内容 |\n")
            f.write("|------|------|\n")
            
            if owner_info:
                f.write(f"| 著作权人 | {owner_info.get('name', '（请填写）')} |\n")
                f.write(f"| 证件类型 | {owner_info.get('id_type', '（请填写）')} |\n")
                f.write(f"| 证件号码 | {owner_info.get('id_number', '（请填写）')} |\n")
                f.write(f"| 地址 | {owner_info.get('address', '（请填写）')} |\n")
                f.write(f"| 邮编 | {owner_info.get('zip_code', '（请填写）')} |\n")
                f.write(f"| 联系人 | {owner_info.get('contact', '（请填写）')} |\n")
                f.write(f"| 电话 | {owner_info.get('phone', '（请填写）')} |\n")
                f.write(f"| 邮箱 | {owner_info.get('email', '（请填写）')} |\n")
            else:
                f.write("| 著作权人 | （请填写） |\n")
                f.write("| 证件类型 | （请填写） |\n")
                f.write("| 证件号码 | （请填写） |\n")
                f.write("| 地址 | （请填写） |\n")
                f.write("| 邮编 | （请填写） |\n")
                f.write("| 联系人 | （请填写） |\n")
                f.write("| 电话 | （请填写） |\n")
                f.write("| 邮箱 | （请填写） |\n")
            f.write("\n")
            
            # 开发者信息
            f.write("## 三、开发者信息\n\n")
            f.write("| 字段 | 内容 |\n")
            f.write("|------|------|\n")
            f.write(f"| 开发者 | {self.project_info.get('author', '（请填写）')} |\n")
            f.write("| 证件类型 | （请填写） |\n")
            f.write("| 证件号码 | （请填写） |\n")
            f.write("| 地址 | （请填写） |\n")
            f.write("| 邮编 | （请填写） |\n")
            f.write("| 联系人 | （请填写） |\n")
            f.write("| 电话 | （请填写） |\n")
            f.write("| 邮箱 | （请填写） |\n\n")
            
            # 技术信息
            f.write("## 四、技术信息\n\n")
            f.write("| 字段 | 内容 |\n")
            f.write("|------|------|\n")
            f.write(f"| 开发的硬件环境 | （请填写，如：Intel Core i5，8GB RAM） |\n")
            f.write(f"| 运行的硬件环境 | （请填写，如：智能手机/PC） |\n")
            f.write(f"| 开发该软件的操作系统 | {self._get_dev_os()} |\n")
            f.write(f"| 软件开发环境/开发工具 | {self._get_dev_tools()} |\n")
            f.write(f"| 该软件的运行平台/操作系统 | {self.project_info['platform']} |\n")
            f.write(f"| 软件运行支撑环境/支持软件 | {self._get_runtime_env()} |\n")
            f.write(f"| 编程语言 | {self._get_programming_languages()} |\n")
            f.write(f"| 源程序量 | {self.total_lines} 行 |\n")
            f.write(f"| 开发目的 | {self._get_development_purpose()} |\n")
            f.write(f"| 面向领域/行业 | {self._get_target_industry()} |\n\n")
            
            # 软件功能简介
            f.write("## 五、软件功能简介\n\n")
            if self.project_info['features']:
                for i, feature in enumerate(self.project_info['features'], 1):
                    f.write(f"{i}. {feature}\n")
            else:
                f.write(f"{self.project_info['description']}\n")
            f.write("\n")
            
            # 技术特点
            f.write("## 六、软件的技术特点\n\n")
            f.write(f"{self._get_technical_features()}\n\n")
            
            # 备注
            f.write("## 七、备注\n\n")
            f.write("本软件为原创开发，未使用第三方商业代码。\n")
    
    def _get_software_category(self) -> str:
        """获取软件分类"""
        type_mapping = {
            '微信小程序': '移动应用软件-小程序',
            'Web应用': '应用软件-Web应用',
            'Node.js应用': '应用软件-服务端应用',
            'Python应用': '应用软件',
            'Java应用': '应用软件',
            '通用软件': '应用软件'
        }
        return type_mapping.get(self.project_info['type'], '应用软件')
    
    def _get_dev_os(self) -> str:
        """获取开发操作系统"""
        return "Windows/macOS/Linux"
    
    def _get_dev_tools(self) -> str:
        """获取开发工具"""
        tools = []
        if '微信小程序' in self.project_info['type']:
            tools.append('微信开发者工具')
        if 'JavaScript' in self.project_info['tech_stack'] or 'TypeScript' in self.project_info['tech_stack']:
            tools.append('Visual Studio Code')
        if 'Python' in self.project_info['tech_stack']:
            tools.append('PyCharm')
        if 'Java' in self.project_info['tech_stack']:
            tools.append('IntelliJ IDEA')
        return '、'.join(tools) if tools else '（请填写）'
    
    def _get_runtime_env(self) -> str:
        """获取运行支撑环境"""
        envs = []
        if '微信小程序' in self.project_info['type']:
            envs.append('微信小程序基础库')
        if 'Node.js' in self.project_info['tech_stack']:
            envs.append('Node.js运行时')
        if 'Vue.js' in self.project_info['tech_stack']:
            envs.append('Vue.js框架')
        if 'React' in self.project_info['tech_stack']:
            envs.append('React框架')
        return '、'.join(envs) if envs else '（请填写）'
    
    def _get_programming_languages(self) -> str:
        """获取编程语言"""
        langs = set()
        for file_info in self.code_files:
            langs.add(file_info['language'])
        return '、'.join(langs) if langs else '（请填写）'
    
    def _get_development_purpose(self) -> str:
        """获取开发目的"""
        if self.project_info['description']:
            return f"为满足用户需求，开发{self.project_info['name']}，提供便捷的服务。"
        return "（请填写）"
    
    def _get_target_industry(self) -> str:
        """获取面向行业"""
        return "通用"
    
    def _get_technical_features(self) -> str:
        """获取技术特点"""
        features = []
        if '微信小程序' in self.project_info['type']:
            features.append('采用微信小程序原生框架开发')
        if 'Vue.js' in self.project_info['tech_stack']:
            features.append('前端采用Vue.js框架')
        if 'React' in self.project_info['tech_stack']:
            features.append('前端采用React框架')
        if 'Node.js' in self.project_info['tech_stack']:
            features.append('后端采用Node.js')
        features.append('采用模块化设计，代码结构清晰')
        features.append('支持跨平台运行')
        return '\n'.join(f"- {f}" for f in features)
    
    def generate_source_code_doc(self, lines_per_page: int = 50, total_pages: int = 60):
        """
        生成源代码文档（前30页 + 后30页）
        
        Args:
            lines_per_page: 每页行数
            total_pages: 总页数（前30 + 后30）
        """
        output_file = self.output_dir / '源代码文档.md'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {self.project_info['name']} - 源代码文档\n\n")
            f.write(f"**软件名称**：{self.project_info['name']}\n")
            f.write(f"**版本号**：{self.project_info['version']}\n")
            f.write(f"**生成日期**：{datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**代码总行数**：{self.total_lines} 行\n\n")
            f.write("---\n\n")
            
            # 计算需要展示的代码
            # 前30页：从第一个文件开始
            # 后30页：从最后倒推
            pages_generated = 0
            line_count = 0
            page_lines = []
            
            # 生成前30页
            f.write("## 源代码（前30页）\n\n")
            for file_info in self.code_files:
                if pages_generated >= 30:
                    break
                
                full_path = file_info['full_path']
                relative_path = file_info['path']
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as source_file:
                        lines = source_file.readlines()
                        
                        f.write(f"### 文件：{relative_path}\n\n")
                        f.write(f"**语言**：{file_info['language']}  \n")
                        f.write(f"**总行数**：{len(lines)}  \n\n")
                        f.write("```" + self._get_code_language(file_info['language']) + "\n")
                        
                        for line in lines:
                            f.write(line.rstrip() + '\n')
                            line_count += 1
                            
                            if line_count >= lines_per_page:
                                f.write("```\n\n")
                                f.write(f"**第 {pages_generated + 1} 页**  \n")
                                f.write(f"行数：{line_count}  \n\n")
                                f.write("---\n\n")
                                
                                pages_generated += 1
                                line_count = 0
                                
                                if pages_generated >= 30:
                                    break
                                
                                f.write(f"### 文件：{relative_path}（续）\n\n")
                                f.write("```" + self._get_code_language(file_info['language']) + "\n")
                        
                        if line_count > 0:
                            f.write("```\n\n")
                
                except Exception as e:
                    f.write(f"**无法读取文件**：{e}\n\n")
            
            # 如果前30页不足，补充空白页
            while pages_generated < 30:
                f.write(f"**第 {pages_generated + 1} 页**  \n\n")
                f.write("---\n\n")
                pages_generated += 1
            
            # 生成后30页
            f.write("## 源代码（后30页）\n\n")
            
            # 从后往前取文件
            remaining_pages = total_pages - 30
            reversed_files = list(reversed(self.code_files))
            
            pages_generated = 0
            line_count = 0
            
            for file_info in reversed_files:
                if pages_generated >= remaining_pages:
                    break
                
                full_path = file_info['full_path']
                relative_path = file_info['path']
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as source_file:
                        lines = source_file.readlines()
                        
                        f.write(f"### 文件：{relative_path}\n\n")
                        f.write(f"**语言**：{file_info['language']}  \n")
                        f.write(f"**总行数**：{len(lines)}  \n\n")
                        f.write("```" + self._get_code_language(file_info['language']) + "\n")
                        
                        for line in lines:
                            f.write(line.rstrip() + '\n')
                            line_count += 1
                            
                            if line_count >= lines_per_page:
                                f.write("```\n\n")
                                f.write(f"**第 {30 + pages_generated + 1} 页**  \n")
                                f.write(f"行数：{line_count}  \n\n")
                                f.write("---\n\n")
                                
                                pages_generated += 1
                                line_count = 0
                                
                                if pages_generated >= remaining_pages:
                                    break
                                
                                f.write(f"### 文件：{relative_path}（续）\n\n")
                                f.write("```" + self._get_code_language(file_info['language']) + "\n")
                        
                        if line_count > 0:
                            f.write("```\n\n")
                
                except Exception as e:
                    f.write(f"**无法读取文件**：{e}\n\n")
            
            # 如果后30页不足，补充空白页
            while pages_generated < remaining_pages:
                f.write(f"**第 {30 + pages_generated + 1} 页**  \n\n")
                f.write("---\n\n")
                pages_generated += 1
    
    def _get_code_language(self, language: str) -> str:
        """根据语言返回代码块标记"""
        mapping = {
            'JavaScript': 'javascript',
            'TypeScript': 'typescript',
            'Python': 'python',
            'Java': 'java',
            'Go': 'go',
            'Rust': 'rust',
            'C': 'c',
            'C++': 'cpp',
            'JSON': 'json',
            '微信小程序WXML': 'xml',
            '微信小程序WXSS': 'css'
        }
        return mapping.get(language, '')
    
    def generate_user_manual(self):
        """生成用户手册"""
        output_file = self.output_dir / '用户手册.md'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {self.project_info['name']} - 用户手册\n\n")
            f.write(f"**软件名称**：{self.project_info['name']}  \n")
            f.write(f"**版本号**：{self.project_info['version']}  \n")
            f.write(f"**生成日期**：{datetime.now().strftime('%Y-%m-%d')}  \n\n")
            f.write("---\n\n")
            
            # 第一章：软件简介
            f.write("## 第一章 软件简介\n\n")
            f.write("### 1.1 软件概述\n\n")
            f.write(f"{self.project_info['name']}是一款{self.project_info['type']}软件，")
            f.write(f"运行于{self.project_info['platform']}。\n\n")
            
            f.write("### 1.2 主要功能\n\n")
            if self.project_info['features']:
                for i, feature in enumerate(self.project_info['features'][:10], 1):
                    f.write(f"{i}. {feature}\n")
            else:
                f.write(f"{self.project_info['description']}\n")
            f.write("\n")
            
            f.write("### 1.3 系统要求\n\n")
            f.write(f"- **运行平台**：{self.project_info['platform']}  \n")
            f.write(f"- **技术支持**：{', '.join(self.project_info['tech_stack']) if self.project_info['tech_stack'] else '（请填写）'}  \n")
            f.write(f"- **网络要求**：需要网络连接  \n\n")
            
            # 第二章：安装与启动
            f.write("## 第二章 安装与启动\n\n")
            f.write("### 2.1 安装说明\n\n")
            
            if '微信小程序' in self.project_info['type']:
                f.write("1. 打开微信客户端  \n")
                f.write("2. 在微信搜索栏输入软件名称  \n")
                f.write("3. 点击搜索结果中的小程序  \n")
                f.write("4. 进入小程序即可使用  \n\n")
            else:
                f.write("1. 访问软件官方网站或应用商店  \n")
                f.write("2. 下载软件安装包  \n")
                f.write("3. 按照提示完成安装  \n")
                f.write("4. 启动软件  \n\n")
            
            f.write("### 2.2 启动说明\n\n")
            f.write("安装完成后，可以通过以下方式启动软件：  \n\n")
            
            if '微信小程序' in self.project_info['type']:
                f.write("1. 在微信中搜索小程序名称  \n")
                f.write("2. 点击小程序图标进入  \n")
                f.write("3. 首次使用可能需要授权  \n\n")
            else:
                f.write("1. 双击桌面快捷方式  \n")
                f.write("2. 从开始菜单启动  \n")
                f.write("3. 命令行启动（适用于开发者）  \n\n")
            
            # 第三章：功能说明
            f.write("## 第三章 功能详细说明\n\n")
            
            if self.project_info['features']:
                for i, feature in enumerate(self.project_info['features'][:8], 1):
                    f.write(f"### 3.{i} {feature}\n\n")
                    f.write(f"**功能描述**：{feature}  \n\n")
                    f.write("**使用步骤**：  \n")
                    f.write("1. 进入对应功能页面  \n")
                    f.write("2. 按照界面提示操作  \n")
                    f.write("3. 查看操作结果  \n\n")
                    f.write("**注意事项**：  \n")
                    f.write("- 请确保网络连接正常  \n")
                    f.write("- 按照提示正确操作  \n\n")
            else:
                f.write("### 3.1 基本功能\n\n")
                f.write("软件提供以下基本功能：  \n\n")
                f.write("1. 用户注册登录  \n")
                f.write("2. 数据查询和管理  \n")
                f.write("3. 报表生成  \n")
                f.write("4. 系统设置  \n\n")
            
            # 第四章：常见问题
            f.write("## 第四章 常见问题与解决方案\n\n")
            f.write("### 4.1 无法启动软件\n\n")
            f.write("**可能原因**：  \n")
            f.write("1. 系统不满足最低要求  \n")
            f.write("2. 安装文件损坏  \n")
            f.write("3. 权限不足  \n\n")
            f.write("**解决方案**：  \n")
            f.write("1. 检查系统要求  \n")
            f.write("2. 重新下载安装包  \n")
            f.write("3. 以管理员权限运行  \n\n")
            
            f.write("### 4.2 功能无法正常使用\n\n")
            f.write("**可能原因**：  \n")
            f.write("1. 网络连接不稳定  \n")
            f.write("2. 浏览器版本过低  \n")
            f.write("3. 缓存数据异常  \n\n")
            f.write("**解决方案**：  \n")
            f.write("1. 检查网络连接  \n")
            f.write("2. 更新浏览器版本  \n")
            f.write("3. 清除缓存后重试  \n\n")
            
            # 第五章：技术支持
            f.write("## 第五章 技术支持\n\n")
            f.write("### 5.1 联系方式\n\n")
            f.write(f"- **开发者**：{self.project_info.get('author', '（请填写）')}  \n")
            f.write("- **技术支持邮箱**：（请填写）  \n")
            f.write("- **官方网站**：（请填写）  \n\n")
            
            f.write("### 5.2 版本更新\n\n")
            f.write(f"- **当前版本**：{self.project_info['version']}  \n")
            f.write(f"- **发布日期**：{datetime.now().strftime('%Y-%m-%d')}  \n")
            f.write("- **更新内容**：（请填写）  \n\n")
    
    def generate_design_doc(self):
        """生成设计说明书"""
        output_file = self.output_dir / '设计说明书.md'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {self.project_info['name']} - 设计说明书\n\n")
            f.write(f"**软件名称**：{self.project_info['name']}  \n")
            f.write(f"**版本号**：{self.project_info['version']}  \n")
            f.write(f"**生成日期**：{datetime.now().strftime('%Y-%m-%d')}  \n\n")
            f.write("---\n\n")
            
            # 第一章：引言
            f.write("## 第一章 引言\n\n")
            f.write("### 1.1 编写目的\n\n")
            f.write(f"本文档旨在详细阐述{self.project_info['name']}的设计思路、架构设计、模块划分和实现细节，")
            f.write("为软件开发、测试和维护提供技术参考。\n\n")
            
            f.write("### 1.2 项目背景\n\n")
            f.write(f"随着信息技术的快速发展，用户对{self.project_info['type']}的需求日益增长。")
            f.write(f"为满足用户在{self.project_info['platform']}上的使用需求，")
            f.write(f"开发了{self.project_info['name']}。\n\n")
            
            f.write("### 1.3 设计目标\n\n")
            f.write("1. **易用性**：提供简洁直观的用户界面  \n")
            f.write("2. **稳定性**：确保软件稳定运行  \n")
            f.write("3. **可扩展性**：采用模块化设计，便于功能扩展  \n")
            f.write("4. **安全性**：保护用户数据安全  \n\n")
            
            # 第二章：总体设计
            f.write("## 第二章 总体设计\n\n")
            f.write("### 2.1 系统架构\n\n")
            f.write(f"{self.project_info['name']}采用{self.project_info['type']}架构，")
            f.write(f"基于{', '.join(self.project_info['tech_stack']) if self.project_info['tech_stack'] else '现代技术栈'}开发。\n\n")
            
            f.write("**系统架构特点**：  \n")
            f.write("1. 采用前后端分离架构（如适用）  \n")
            f.write("2. 模块化设计，职责清晰  \n")
            f.write("3. 支持跨平台运行  \n\n")
            
            f.write("### 2.2 模块划分\n\n")
            f.write(f"{self.project_info['name']}主要包含以下模块：  \n\n")
            f.write("1. **主界面模块**：负责用户界面的展示和交互  \n")
            f.write("2. **业务逻辑模块**：处理核心业务逻辑  \n")
            f.write("3. **数据存储模块**：负责数据的存储和管理  \n")
            f.write("4. **工具模块**：提供通用工具函数和辅助方法  \n")
            f.write("5. **网络模块**：处理网络通信和数据传输  \n\n")
            
            f.write("### 2.3 技术选型\n\n")
            if self.project_info['tech_stack']:
                for tech in self.project_info['tech_stack']:
                    f.write(f"- **{tech}**：用于{self._get_tech_usage(tech)}  \n")
            else:
                f.write("- （请根据实际情况填写技术选型）  \n")
            f.write("\n")
            
            f.write("### 2.4 运行环境\n\n")
            f.write(f"- **运行平台**：{self.project_info['platform']}  \n")
            f.write(f"- **开发工具**：{self._get_dev_tools()}  \n")
            f.write(f"- **依赖库**：{', '.join(self.project_info['dependencies'][:10]) if self.project_info['dependencies'] else '（请填写）'}  \n\n")
            
            # 第三章：详细设计
            f.write("## 第三章 详细设计\n\n")
            f.write("### 3.1 主界面模块设计\n\n")
            f.write("#### 3.1.1 模块功能\n\n")
            f.write("主界面模块负责软件的启动、界面展示和用户交互。  \n\n")
            
            f.write("#### 3.1.2 界面布局\n\n")
            f.write("采用响应式布局，适配不同屏幕尺寸。主要包含以下区域：  \n")
            f.write("1. 顶部导航栏  \n")
            f.write("2. 主内容区域  \n")
            f.write("3. 底部状态栏（如适用）  \n\n")
            
            f.write("#### 3.1.3 交互设计\n\n")
            f.write("- **点击交互**：按钮点击触发相应功能  \n")
            f.write("- **滑动交互**：支持手势操作（如适用）  \n")
            f.write("- **输入交互**：表单输入和验证  \n\n")
            
            f.write("### 3.2 业务逻辑模块设计\n\n")
            f.write("#### 3.2.1 模块功能\n\n")
            f.write("处理软件的核心业务逻辑，包括数据处理、计算和业务规则实现。  \n\n")
            
            f.write("#### 3.2.2 核心算法\n\n")
            f.write("（请根据实际业务描述核心算法）  \n\n")
            
            f.write("#### 3.2.3 数据流\n\n")
            f.write("用户界面 → 业务逻辑层 → 数据存储层 → 返回结果  \n\n")
            
            f.write("### 3.3 数据存储模块设计\n\n")
            f.write("#### 3.3.1 存储方式\n\n")
            if '微信小程序' in self.project_info['type']:
                f.write("采用微信小程序本地存储（wx.setStorage/wx.getStorage）。  \n\n")
            else:
                f.write("采用（请填写存储方式，如：LocalStorage、数据库等）。  \n\n")
            
            f.write("#### 3.3.2 数据格式\n\n")
            f.write("- **配置信息**：JSON格式  \n")
            f.write("- **用户数据**：JSON格式  \n")
            f.write("- **缓存数据**：键值对格式  \n\n")
            
            # 第四章：接口设计
            f.write("## 第四章 接口设计\n\n")
            f.write("### 4.1 内部接口\n\n")
            f.write("模块间的接口调用采用（请填写，如：函数调用、事件机制等）。  \n\n")
            
            f.write("### 4.2 外部接口\n\n")
            if '微信小程序' in self.project_info['type']:
                f.write("调用微信小程序API，包括：  \n")
                f.write("- wx.request() - 网络请求  \n")
                f.write("- wx.setStorage() - 本地存储  \n")
                f.write("- wx.getUserInfo() - 获取用户信息  \n\n")
            else:
                f.write("（请根据实际情况填写外部接口）  \n\n")
            
            # 第五章：安全设计
            f.write("## 第五章 安全设计\n\n")
            f.write("### 5.1 数据安全\n\n")
            f.write("- **敏感数据加密**：对密码、个人信息等敏感数据进行加密存储  \n")
            f.write("- **传输安全**：采用HTTPS协议进行数据传输  \n")
            f.write("- **访问控制**：合理的权限管理机制  \n\n")
            
            f.write("### 5.2 异常处理\n\n")
            f.write("- **输入验证**：对用户输入进行严格验证  \n")
            f.write("- **错误捕获**：完善的异常捕获和处理机制  \n")
            f.write("- **日志记录**：记录关键操作和异常信息  \n\n")
            
            # 第六章：测试设计
            f.write("## 第六章 测试设计\n\n")
            f.write("### 6.1 测试策略\n\n")
            f.write("- **单元测试**：对各个功能模块进行测试  \n")
            f.write("- **集成测试**：测试模块间的交互  \n")
            f.write("- **用户测试**：真实用户使用测试  \n\n")
            
            f.write("### 6.2 测试环境\n\n")
            f.write(f"- **测试平台**：{self.project_info['platform']}  \n")
            f.write(f"- **测试设备**：（请填写）  \n")
            f.write(f"- **测试工具**：（请填写）  \n\n")
            
            # 第七章：部署与维护
            f.write("## 第七章 部署与维护\n\n")
            f.write("### 7.1 部署方案\n\n")
            if '微信小程序' in self.project_info['type']:
                f.write("1. 在微信开发者工具中上传代码  \n")
                f.write("2. 登录微信公众平台提交审核  \n")
                f.write("3. 审核通过后发布上线  \n\n")
            else:
                f.write("（请根据实际情况填写部署方案）  \n\n")
            
            f.write("### 7.2 维护计划\n\n")
            f.write("1. **Bug修复**：及时修复发现的问题  \n")
            f.write("2. **功能更新**：根据用户反馈持续优化  \n")
            f.write("3. **性能优化**：定期优化软件性能  \n\n")
    
    def _get_tech_usage(self, tech: str) -> str:
        """获取技术用途描述"""
        usage_map = {
            '微信小程序原生框架': '小程序前端开发',
            'Vue.js': '前端界面开发',
            'React': '前端界面开发',
            'Node.js': '后端服务开发',
            'Python': '后端服务开发',
            'Java': '后端服务开发'
        }
        return usage_map.get(tech, '软件开发')
    
    def convert_to_pdf(self):
        """将Markdown文档转换为PDF"""
        self.log("开始转换为PDF...")
        
        # 检查是否安装了pandoc和latex
        has_pandoc = self._check_command('pandoc')
        has_wkhtmltopdf = self._check_command('wkhtmltopdf')
        
        md_files = [
            '软件著作权登记申请表.md',
            '源代码文档.md',
            '用户手册.md',
            '设计说明书.md'
        ]
        
        for md_file in md_files:
            md_path = self.output_dir / md_file
            pdf_path = self.output_dir / md_file.replace('.md', '.pdf')
            
            if not md_path.exists():
                self.log(f"文件不存在：{md_path}", 'WARNING')
                continue
            
            # 尝试使用pandoc转换
            if has_pandoc:
                try:
                    cmd = [
                        'pandoc',
                        str(md_path),
                        '-o', str(pdf_path),
                        '--pdf-engine=xelatex',
                        '-V', 'mainfont=SimSun',
                        '-V', 'geometry:margin=1in'
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    self.log(f"已生成PDF：{pdf_path}")
                except subprocess.CalledProcessError as e:
                    self.log(f"Pandoc转换失败：{e}", 'ERROR')
                    # 尝试使用wkhtmltopdf
                    if has_wkhtmltopdf:
                        self._convert_with_wkhtmltopdf(md_path, pdf_path)
            # 尝试使用wkhtmltopdf
            elif has_wkhtmltopdf:
                self._convert_with_wkhtmltopdf(md_path, pdf_path)
            else:
                self.log("未找到PDF转换工具（pandoc或wkhtmltopdf），请手动转换", 'WARNING')
    
    def _check_command(self, command: str) -> bool:
        """检查命令是否存在"""
        try:
            subprocess.run(['which', command], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _convert_with_wkhtmltopdf(self, md_path: Path, pdf_path: Path):
        """使用wkhtmltopdf转换PDF"""
        try:
            # 先将Markdown转换为HTML
            html_path = md_path.with_suffix('.html')
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # 简单的Markdown到HTML转换（实际应用中应该使用专业库）
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{md_path.stem}</title>
    <style>
        body {{ font-family: SimSun, serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #555; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
{self._md_to_html_simple(md_content)}
</body>
</html>"""
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 使用wkhtmltopdf转换HTML为PDF
            cmd = ['wkhtmltopdf', str(html_path), str(pdf_path)]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # 删除临时HTML文件
            html_path.unlink()
            
            self.log(f"已生成PDF：{pdf_path}")
        except Exception as e:
            self.log(f"wkhtmltopdf转换失败：{e}", 'ERROR')
    
    def _md_to_html_simple(self, md_content: str) -> str:
        """简单的Markdown到HTML转换（用于演示，生产环境应使用专业库）"""
        html = md_content
        # 标题
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        # 加粗
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        # 列表
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        # 段落
        html = re.sub(r'^([^<].+)$', r'<p>\1</p>', html, flags=re.MULTILINE)
        return html


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='中国软件著作权申请材料生成器')
    parser.add_argument('project_path', help='项目路径')
    parser.add_argument('-o', '--output', help='输出目录（默认为项目路径下的copyright-application-materials）')
    parser.add_argument('--owner-name', help='著作权人名称')
    parser.add_argument('--owner-id-type', default='身份证', help='证件类型')
    parser.add_argument('--owner-id-number', help='证件号码')
    parser.add_argument('--owner-address', help='地址')
    parser.add_argument('--owner-zip', help='邮编')
    parser.add_argument('--owner-contact', help='联系人')
    parser.add_argument('--owner-phone', help='电话')
    parser.add_argument('--owner-email', help='邮箱')
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = CopyrightDocGenerator(args.project_path, args.output)
    
    # 分析项目
    generator.analyze_project()
    
    # 准备著作权人信息
    owner_info = None
    if args.owner_name:
        owner_info = {
            'name': args.owner_name,
            'id_type': args.owner_id_type,
            'id_number': args.owner_id_number,
            'address': args.owner_address,
            'zip_code': args.owner_zip,
            'contact': args.owner_contact,
            'phone': args.owner_phone,
            'email': args.owner_email
        }
    
    # 生成所有文档
    generator.generate_all_docs(owner_info)
    
    print("\n" + "="*60)
    print("申请材料生成完成！")
    print("="*60)
    print(f"输出目录：{generator.output_dir}")
    print(f"生成的文件：")
    print(f"  - 软件著作权登记申请表.md/.pdf")
    print(f"  - 源代码文档.md/.pdf")
    print(f"  - 用户手册.md/.pdf")
    print(f"  - 设计说明书.md/.pdf")
    print("="*60)


if __name__ == '__main__':
    main()
