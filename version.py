"""
版本信息 - 语义化版本2.0.0（SemVer 2.0）

格式：主版本号.次版本号.修订号+构建元数据
- 主版本号：不兼容的API变更
- 次版本号：向后兼容的功能新增
- 修订号：向后兼容的问题修复
- 构建元数据：发布时间戳，格式 YYYYMMDDHHMM

参考规范：https://semver.org/lang/zh-CN/
"""

__version__ = "2.0.0+202605171048"
__version_major__ = 2
__version_minor__ = 0
__version_patch__ = 0
__version_build__ = "202605171048"
__version_prerelease__ = ""

# 版本历史
VERSION_HISTORY = {
    "2.0.0": {
        "date": "2026-05-17",
        "changes": [
            "新增完整Web应用系统（上传源码分析、PDF导出、项目列表）",
            "新增交互式信息收集（著作权人信息+软件信息）",
            "新增PDF转换功能（pandoc/wkhtmltopdf双引擎）",
            "新增文件优先级排序算法（_file_priority）",
            "新增单元测试（test_generator.py）",
            "修复Flask路由中文参数兼容性问题",
        ],
    },
    "1.0.0": {
        "date": "2026-05-16",
        "changes": [
            "基础文档生成功能（申请表、源代码文档、用户手册、设计说明书）",
            "项目类型自动识别（微信小程序、Web、Python、Java等）",
            "命令行参数支持",
            "CI/CD自动发布工作流",
        ],
    },
}


def get_version() -> str:
    """获取完整版本号"""
    version = f"{__version_major__}.{__version_minor__}.{__version_patch__}"
    if __version_prerelease__:
        version += f"-{__version_prerelease__}"
    version += f"+{__version_build__}"
    return version


def get_version_info() -> dict:
    """获取版本详细信息"""
    return {
        "version": get_version(),
        "major": __version_major__,
        "minor": __version_minor__,
        "patch": __version_patch__,
        "build": __version_build__,
        "prerelease": __version_prerelease__,
    }
