"""
版本信息 - 基于Git标签的语义化版本2.0.0（SemVer 2.0）

自动从Git标签和提交历史生成版本号，机制：
1. git describe --tags → 读取最近的版本标签
2. 无标签时回退到默认版本号
3. 构建元数据 = git提交数.短哈希

版本号格式：主版本号.次版本号.修订号[-预发布标识]+构建元数据
- 主版本号：不兼容的API变更（手动打标签时指定）
- 次版本号：向后兼容的功能新增
- 修订号：向后兼容的问题修复
- 预发布标识：alpha/beta/rc等
- 构建元数据：提交数.短哈希

参考规范：https://semver.org/lang/zh-CN/
"""

import subprocess
import os
from pathlib import Path

# 默认版本号（无Git标签时使用）
_FALLBACK_VERSION = "2.0.0"

# 版本历史（CHANGELOG）
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


def _run_git(*args: str) -> str:
    """执行Git命令，失败返回空字符串"""
    try:
        # 自动向上查找Git仓库根目录
        repo_root = Path(__file__).resolve().parent
        result = subprocess.run(
            ["git", "-C", str(repo_root)] + list(args),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def _get_version_from_git() -> dict:
    """
    从Git标签自动提取版本号

    解析规则（与git describe --tags一致）：
    - 有标签且在标签上 → "2.0.0"
    - 有标签但不在标签上 → "2.0.0-dev.3+3.gabcdef1"（3次提交后）
    - 无标签 → 回退到默认版本号+提交数
    """
    info = {
        "base": _FALLBACK_VERSION,
        "major": 2,
        "minor": 0,
        "patch": 0,
        "prerelease": "",
        "commits_ahead": 0,
        "short_hash": "",
        "dirty": False,
    }

    # 获取最近标签
    describe = _run_git("describe", "--tags", "--match", "v[0-9]*", "--long", "--dirty")
    if not describe:
        # 无任何标签，用提交数构建
        count = _run_git("rev-list", "--count", "HEAD")
        short_hash = _run_git("rev-parse", "--short", "HEAD")
        info["commits_ahead"] = int(count) if count else 0
        info["short_hash"] = short_hash or "unknown"
        return info

    # 解析 git describe 输出：v2.0.0-3-gabcdef1-dirty
    # 或：v2.0.0-0-gabcdef1（在标签上）
    dirty = describe.endswith("-dirty")
    if dirty:
        describe = describe[: -len("-dirty")]

    parts = describe.rsplit("-", 2)
    if len(parts) == 3:
        tag_str, commits_str, hash_str = parts
        info["commits_ahead"] = int(commits_str)
        info["short_hash"] = hash_str[1:] if hash_str.startswith("g") else hash_str
        info["dirty"] = dirty
    else:
        tag_str = describe
        info["short_hash"] = _run_git("rev-parse", "--short", "HEAD") or "unknown"
        info["dirty"] = dirty

    # 解析标签（去掉v前缀）
    version_str = tag_str
    if version_str.startswith("v"):
        version_str = version_str[1:]

    # 解析主版本.次版本.修订号
    parts = version_str.split(".", 2)
    if len(parts) >= 1:
        try:
            info["major"] = int(parts[0])
        except ValueError:
            pass
    if len(parts) >= 2:
        try:
            info["minor"] = int(parts[1])
        except ValueError:
            pass
    if len(parts) >= 3:
        # 修订号可能含预发布标识，如 "1-alpha"
        patch_str = parts[2]
        if "-" in patch_str:
            patch_num, info["prerelease"] = patch_str.split("-", 1)
            try:
                info["patch"] = int(patch_num)
            except ValueError:
                pass
        else:
            try:
                info["patch"] = int(patch_str)
            except ValueError:
                pass

    info["base"] = f"{info['major']}.{info['minor']}.{info['patch']}"
    return info


def get_version() -> str:
    """
    获取完整版本号（SemVer 2.0格式）

    示例：
    - 在标签上："2.0.0+15.gabcdef1"
    - 标签后3次提交："2.0.0-dev.3+18.gabcdef1"
    - 有未提交修改："2.0.0-dev.3+18.gabcdef1.dirty"
    """
    info = _get_version_from_git()
    version = info["base"]

    # 预发布标识
    if info["prerelease"]:
        version += f"-{info['prerelease']}"
    elif info["commits_ahead"] > 0:
        version += f"-dev.{info['commits_ahead']}"

    # 构建元数据
    build_parts = []
    if info["short_hash"]:
        build_parts.append(f"g{info['short_hash']}")
    if build_parts:
        version += "+" + ".".join(build_parts)

    # 脏标记
    if info["dirty"]:
        version += ".dirty"

    return version


def get_version_info() -> dict:
    """获取版本详细信息"""
    info = _get_version_from_git()
    return {
        "version": get_version(),
        "base": info["base"],
        "major": info["major"],
        "minor": info["minor"],
        "patch": info["patch"],
        "prerelease": info["prerelease"],
        "commits_ahead": info["commits_ahead"],
        "short_hash": info["short_hash"],
        "dirty": info["dirty"],
    }


# 模块级缓存（避免每次import都执行git命令）
__version__ = get_version()
