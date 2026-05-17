#!/usr/bin/env python3
"""
软件著作权申请材料生成器 - 单元测试
"""

import os
import sys
import json
import tempfile
import shutil
import unittest
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from generate_copyright_docs import CopyrightDocGenerator


class TestProjectAnalysis(unittest.TestCase):
    """测试项目分析功能"""

    def setUp(self):
        """创建测试项目"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试项目"""
        shutil.rmtree(self.test_dir)

    def test_analyze_wechat_miniprogram(self):
        """测试微信小程序项目分析"""
        # 创建微信小程序项目结构
        project_dir = os.path.join(self.test_dir, "miniprogram")
        os.makedirs(project_dir)

        # 创建 app.json
        app_json = {
            "pages": ["pages/index/index", "pages/logs/logs"],
            "window": {"navigationBarTitleText": "测试小程序"},
        }
        with open(os.path.join(project_dir, "app.json"), "w", encoding="utf-8") as f:
            json.dump(app_json, f)

        # 创建 project.config.json
        project_config = {"appid": "wx1234567890", "libVersion": "2.19.4"}
        with open(
            os.path.join(project_dir, "project.config.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(project_config, f)

        # 创建 package.json
        package_json = {
            "name": "test-miniprogram",
            "version": "1.0.0",
            "description": "测试小程序描述",
        }
        with open(
            os.path.join(project_dir, "package.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(package_json, f)

        # 创建源代码文件
        os.makedirs(os.path.join(project_dir, "pages", "index"))
        with open(os.path.join(project_dir, "app.js"), "w", encoding="utf-8") as f:
            f.write("// app.js\nApp({})\n")
        with open(
            os.path.join(project_dir, "pages", "index", "index.js"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write("// index.js\nPage({})\n")

        # 分析项目
        generator = CopyrightDocGenerator(project_dir)
        generator.analyze_project()

        # 验证结果
        self.assertEqual(generator.project_info["type"], "微信小程序")
        # 项目名称会从 app.json 的 navigationBarTitleText 提取，并添加"软件"后缀
        self.assertIn("测试小程序", generator.project_info["name"])
        self.assertEqual(generator.project_info["version"], "1.0.0")
        self.assertIn("JavaScript", generator.project_info["tech_stack"])

    def test_analyze_web_project(self):
        """测试 Web 项目分析"""
        project_dir = os.path.join(self.test_dir, "webproject")
        os.makedirs(project_dir)

        # 创建 package.json
        package_json = {
            "name": "test-web-app",
            "version": "2.0.0",
            "description": "测试Web应用",
            "author": "测试作者",
        }
        with open(
            os.path.join(project_dir, "package.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(package_json, f)

        # 创建源代码文件
        with open(os.path.join(project_dir, "index.js"), "w", encoding="utf-8") as f:
            f.write("// index.js\nconsole.log('hello')\n")

        # 分析项目
        generator = CopyrightDocGenerator(project_dir)
        generator.analyze_project()

        # 验证结果
        self.assertEqual(generator.project_info["type"], "Web应用")
        self.assertEqual(generator.project_info["name"], "test-web-app")
        self.assertEqual(generator.project_info["version"], "2.0.0")

    def test_analyze_python_project(self):
        """测试 Python 项目分析"""
        project_dir = os.path.join(self.test_dir, "pythonproject")
        os.makedirs(project_dir)

        # 创建 setup.py
        setup_content = """
from setuptools import setup
setup(
    name='test-python',
    version='3.0.0',
    description='测试Python项目',
)
"""
        with open(os.path.join(project_dir, "setup.py"), "w", encoding="utf-8") as f:
            f.write(setup_content)

        # 创建源代码文件
        with open(os.path.join(project_dir, "main.py"), "w", encoding="utf-8") as f:
            f.write("# main.py\nprint('hello')\n")

        # 分析项目
        generator = CopyrightDocGenerator(project_dir)
        generator.analyze_project()

        # 验证结果
        self.assertEqual(generator.project_info["type"], "Python项目")
        self.assertIn("Python", generator.project_info["tech_stack"])


class TestDocumentGeneration(unittest.TestCase):
    """测试文档生成功能"""

    def setUp(self):
        """创建测试项目和生成器"""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()

        # 创建简单的测试项目
        project_dir = os.path.join(self.test_dir, "testproject")
        os.makedirs(project_dir)

        # 创建 package.json
        package_json = {
            "name": "test-software",
            "version": "1.0.0",
            "description": "测试软件",
        }
        with open(
            os.path.join(project_dir, "package.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(package_json, f)

        # 创建源代码文件
        with open(os.path.join(project_dir, "index.js"), "w", encoding="utf-8") as f:
            f.write("// index.js\n" + "console.log('test');\n" * 100)

        self.project_dir = project_dir
        self.generator = CopyrightDocGenerator(project_dir, self.output_dir)

    def tearDown(self):
        """清理测试文件"""
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.output_dir)

    def test_generate_application_form(self):
        """测试生成申请表"""
        self.generator.analyze_project()

        owner_info = {
            "name": "测试著作权人",
            "id_type": "身份证",
            "id_number": "123456789012345678",
            "address": "北京市海淀区",
            "zip_code": "100000",
            "contact": "张三",
            "phone": "13800138000",
            "email": "test@example.com",
        }

        software_info = {
            "dev_purpose": "测试开发目的",
            "industry": "软件行业",
            "main_functions": "测试主要功能",
            "tech_features": "测试技术特点",
            "software_type": "小程序",
        }

        # 生成申请表
        self.generator.generate_application_form(owner_info, software_info)

        # 验证文件是否生成
        output_file = os.path.join(self.output_dir, "软件著作权登记申请表.md")
        self.assertTrue(os.path.exists(output_file))

        # 验证内容
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("测试著作权人", content)
            self.assertIn("test-software", content)

    def test_generate_source_code_doc(self):
        """测试生成源代码文档"""
        self.generator.analyze_project()

        owner_info = {"name": "测试著作权人"}

        # 生成源代码文档
        self.generator.generate_source_code_doc(owner_info)

        # 验证文件是否生成
        output_file = os.path.join(self.output_dir, "源代码文档.md")
        self.assertTrue(os.path.exists(output_file))

        # 验证内容
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("测试著作权人", content)
            self.assertIn("index.js", content)

    def test_generate_user_manual(self):
        """测试生成用户手册"""
        self.generator.analyze_project()

        owner_info = {"name": "测试著作权人"}
        software_info = {
            "dev_purpose": "测试开发目的",
            "industry": "软件行业",
            "main_functions": "测试主要功能",
        }

        # 生成用户手册
        self.generator.generate_user_manual(owner_info, software_info)

        # 验证文件是否生成
        output_file = os.path.join(self.output_dir, "用户手册.md")
        self.assertTrue(os.path.exists(output_file))

        # 验证内容
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("测试著作权人", content)
            self.assertIn("test-software", content)

    def test_generate_design_doc(self):
        """测试生成设计说明书"""
        self.generator.analyze_project()

        owner_info = {"name": "测试著作权人"}
        software_info = {
            "dev_purpose": "测试开发目的",
            "industry": "软件行业",
            "main_functions": "测试主要功能",
            "tech_features": "测试技术特点",
        }

        # 生成设计说明书
        self.generator.generate_design_doc(owner_info, software_info)

        # 验证文件是否生成
        output_file = os.path.join(self.output_dir, "设计说明书.md")
        self.assertTrue(os.path.exists(output_file))

        # 验证内容
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("测试著作权人", content)
            self.assertIn("test-software", content)


class TestCodeExtraction(unittest.TestCase):
    """测试代码提取功能"""

    def setUp(self):
        """创建测试项目"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试文件"""
        shutil.rmtree(self.test_dir)

    def test_extract_code_lines(self):
        """测试代码行数提取"""
        project_dir = os.path.join(self.test_dir, "codeproject")
        os.makedirs(project_dir)

        # 创建多个代码文件
        with open(os.path.join(project_dir, "a.js"), "w", encoding="utf-8") as f:
            f.write("\n" * 100)  # 100行
        with open(os.path.join(project_dir, "b.js"), "w", encoding="utf-8") as f:
            f.write("\n" * 50)  # 50行

        generator = CopyrightDocGenerator(project_dir)
        generator.analyze_project()

        # 验证总行数
        self.assertEqual(generator.total_lines, 150)

    def test_code_file_priority(self):
        """测试代码文件优先级排序"""
        project_dir = os.path.join(self.test_dir, "priorityproject")
        os.makedirs(project_dir)
        os.makedirs(os.path.join(project_dir, "utils"))

        # 创建不同类型的文件
        with open(os.path.join(project_dir, "app.js"), "w", encoding="utf-8") as f:
            f.write("App({})\n")
        with open(os.path.join(project_dir, "index.js"), "w", encoding="utf-8") as f:
            f.write("Page({})\n")
        with open(
            os.path.join(project_dir, "utils", "util.js"), "w", encoding="utf-8"
        ) as f:
            f.write("function test() {}\n")

        generator = CopyrightDocGenerator(project_dir)
        generator.analyze_project()

        # 验证文件排序
        self.assertTrue(len(generator.code_files) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
