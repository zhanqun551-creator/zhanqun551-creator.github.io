#!/usr/bin/env python3
"""
技术文档文章生成器
自动生成10篇技术文档文章HTML文件
使用DeepSeek API生成文章内容
"""

import os
import sys
import json
import time
import random
from datetime import datetime
from pathlib import Path

# 尝试导入requests，如果不存在则提示安装
try:
    import requests
except ImportError:
    print("错误：未找到requests库。请使用以下命令安装：")
    print("pip install requests")
    sys.exit(1)

# 配置文件
CONFIG = {
    "api_key": "sk-b87abdc445084a47a7ef45219025a6db",  # 直接写你的真实 Key
    "api_url": "https://api.deepseek.com/v1/chat/completions",
    "model": "deepseek-chat",
    "max_tokens": 6000,  # 生成足够的内容
    "temperature": 0.7,
    "post_dir": "post",
    "template_file": "article-template.html",
    "num_articles": 299,  # 每次生成的文章数量
    "num_links": 300,    # 每篇文章生成的纯文本外链数量
}

# 技术分类和主题
CATEGORIES = [
    {
        "name": "项目结构",
        "slug": "project-structure",
        "topics": [
            "微服务架构设计模式",
            "领域驱动设计实战指南",
            "代码模块化设计与实现",
            "API设计规范与版本管理",
            "配置管理系统设计",
            "单体应用架构优化",
            "分布式系统设计原理",
            "云原生架构最佳实践",
            "可扩展系统架构设计",
            "软件架构演进策略"
        ]
    },
]

def get_max_article_id():
    """获取post目录中最大的文章ID"""
    post_dir = Path(CONFIG["post_dir"])
    if not post_dir.exists():
        return 0

    max_id = 0
    for file in post_dir.glob("*.html"):
        try:
            # 从文件名中提取数字ID
            file_id = int(file.stem)
            if file_id > max_id:
                max_id = file_id
        except ValueError:
            continue

    return max_id

def generate_random_links(n=15):
    """
    生成 n 条纯文本随机外链
    格式：xxxx.com/xxxx/{随机数字}.html
    """
    links = []
    for _ in range(n):
        rand_num = random.randint(100, 186543)  # 6位随机数字
        links.append(f"hhhhhhh/voddetail/{rand_num}.html")  # 纯文本外链
    return links

def generate_article_content(article_id, category, topic, num_links=None):
    """调用DeepSeek API生成文章内容

    返回包含标题、描述、关键词和正文的字典
    """
    if not CONFIG["api_key"]:
        print(f"错误：未设置DeepSeek API密钥。请设置环境变量DEEPSEEK_API_KEY。")
        sys.exit(1)

    # 如果未指定num_links，使用配置中的默认值
    if num_links is None:
        num_links = CONFIG["num_links"]

    # 构建提示词
    prompt = f"""请生成一篇关于「{topic}」的技术文档文章。

要求：
1. 文章标题：{topic}
2. 文章描述：约150字，概括文章主要内容和技术价值
3. 关键词：5-8个相关技术关键词，用中文逗号分隔
4. 正文内容：3888-4566字中文技术文档，包含以下结构：
   - 引言：介绍技术背景和问题
   - 核心概念：解释关键技术概念
   - 实践方法：提供具体的实施步骤或方法
   - 最佳实践：分享经验教训和优化建议
   - 总结：概括核心要点和未来展望
5. 使用适当的技术术语，内容专业、实用
6. 包含2-3个H2标题和4-6个H3标题
7. 段落清晰，逻辑连贯

请以JSON格式返回，包含以下字段：
- title: 文章标题
- description: 文章描述
- keywords: 关键词字符串
- content: 完整的HTML格式正文（只包含<article>标签内的内容，不要包含<html><body>等外层标签）
- category: 分类名称
- category_slug: 分类slug
- read_time: 预计阅读时间（如"约12分钟"）

注意：content字段应该是完整的HTML内容，包含<p>、<h2>、<h3>、<ul>、<ol>、<pre>等标签。"""

    headers = {
        "Authorization": f"Bearer {CONFIG['api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": CONFIG["model"],
        "messages": [
            {"role": "system", "content": "你是一位资深技术文档工程师，擅长撰写高质量、实用性的技术文档。"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": CONFIG["max_tokens"],
        "temperature": CONFIG["temperature"],
        "response_format": {"type": "json_object"}
    }

    print(f"正在生成文章 {article_id}: {topic}...")

    try:
        response = requests.post(CONFIG["api_url"], headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # 解析JSON响应
        article_data = json.loads(content)

        # 添加额外信息
        article_data["id"] = article_id
        article_data["date"] = datetime.now().strftime("%Y-%m-%d")
        article_data["date_display"] = datetime.now().strftime("%Y年%m月%d日")

        # 估算阅读时间（按每分钟500字计算）
        word_count = len(article_data.get("content", ""))
        read_time = max(5, word_count // 500)
        article_data["read_time"] = f"约{read_time}分钟"

        # 在正文后添加纯文本外链
        if num_links > 0 and "content" in article_data:
            random_links_text = "<br>\n".join(generate_random_links(num_links)) + "<br>"
            article_data["content"] += f"\n参考：<br>\n{random_links_text}\n"

        return article_data

    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应状态码: {e.response.status_code}")
            print(f"响应内容: {e.response.text}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"原始响应: {content[:500]}...")
        return None
    except Exception as e:
        print(f"生成文章时发生错误: {e}")
        return None

def load_template():
    """加载HTML模板"""
    template_path = Path(CONFIG["template_file"])
    if not template_path.exists():
        print(f"错误：模板文件 {CONFIG['template_file']} 不存在")
        sys.exit(1)

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def create_article_html(template, article_data):
    """使用模板和数据生成HTML文件"""
    # 替换模板中的占位符
    html = template

    # 基本替换
    replacements = {
        "文章标题": article_data.get("title", ""),
        "文章描述，简要概括文章内容，约150字左右。": article_data.get("description", ""),
        "关键词1, 关键词2, 关键词3, 关键词4": article_data.get("keywords", ""),
        "文章标题": article_data.get("title", ""),  # 再次替换H1标题
        "分类名称": article_data.get("category", ""),
        "{category}": article_data.get("category_slug", ""),
        "2025-01-01": article_data.get("date", ""),
        "2025年1月1日": article_data.get("date_display", ""),
        "约X分钟": article_data.get("read_time", "约10分钟"),
        "{id}": str(article_data.get("id", "")),
        "2025": datetime.now().strftime("%Y"),
        "文章引言段落，简要介绍文章主题、背景和主要内容。这部分应吸引读者继续阅读，明确文章的价值和适用范围。": article_data.get("content", "")
    }

    for old, new in replacements.items():
        html = html.replace(old, new)

    # 替换结构化数据中的标题和描述
    import re

    # 替换结构化数据中的标题
    headline_pattern = r'"headline": "文章标题"'
    html = re.sub(headline_pattern, f'"headline": "{article_data.get("title", "")}"', html)

    # 替换结构化数据中的描述
    desc_pattern = r'"description": "文章描述"'
    html = re.sub(desc_pattern, f'"description": "{article_data.get("description", "")}"', html)

    # 替换结构化数据中的ID
    id_pattern = r'"@id": "https://docs\.example\.com/post/\{id\}"'
    html = re.sub(id_pattern, f'"@id": "https://docs.example.com/post/{article_data.get("id", "")}"', html)

    # 替换相关文章ID（简单处理，使用相邻ID）
    article_id = article_data.get("id", 1)
    for i in range(1, 5):
        related_id = article_id - i if article_id - i > 0 else article_id + i
        html = html.replace(f"{{id{i}}}", str(related_id))
        html = html.replace(f"相关文章标题{i}", f"相关技术文章 {related_id}")
        html = html.replace(f"相关文章摘要，简要说明文章内容。", f"技术文档相关内容，提供实用的技术参考。")

    # 替换页脚年份
    html = html.replace("2025", datetime.now().strftime("%Y"))

    return html

def save_article(article_id, html_content):
    """保存HTML文件"""
    post_dir = Path(CONFIG["post_dir"])
    post_dir.mkdir(exist_ok=True)

    file_path = post_dir / f"{article_id}.html"

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return file_path

def main():
    """主函数：生成10篇新文章"""
    print("=" * 60)
    print("技术文档文章生成器")
    print("=" * 60)

    # 检查API密钥
    if not CONFIG["api_key"]:
        print("警告：未设置DeepSeek API密钥。")
        print("请设置环境变量：DEEPSEEK_API_KEY")
        print("或在脚本中直接设置CONFIG['api_key']")
        print("\n是否使用模拟数据生成文章？(y/n): ", end="")
        choice = input().strip().lower()
        if choice != 'y':
            print("退出程序。")
            sys.exit(1)
        # 使用模拟数据模式
        CONFIG["api_key"] = "mock"

    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    # 获取最大ID
    max_id = get_max_article_id()
    print(f"当前最大文章ID: {max_id}")

    # 加载模板
    print("加载HTML模板...")
    template = load_template()

    # 准备生成文章
    new_ids = list(range(max_id + 1, max_id + 1 + CONFIG["num_articles"]))
    print(f"将生成 {CONFIG['num_articles']} 篇新文章，ID: {new_ids[0]} - {new_ids[-1]}")

    # 选择分类和主题
    generated_articles = []

    for i, article_id in enumerate(new_ids):
        # 随机选择分类和主题
        category = random.choice(CATEGORIES)
        topic = random.choice(category["topics"])

        print(f"\n[{i+1}/{CONFIG['num_articles']}] 生成文章 {article_id}")
        print(f"分类: {category['name']}")
        print(f"主题: {topic}")

        # 生成文章内容
        if CONFIG["api_key"] == "mock":
            # 模拟模式：生成模拟数据
            article_data = generate_mock_article(article_id, category, topic, num_links=CONFIG["num_links"])
        else:
            # 调用API
            article_data = generate_article_content(article_id, category, topic, num_links=CONFIG["num_links"])

        if not article_data:
            print(f"文章 {article_id} 生成失败，跳过。")
            continue

        # 生成HTML
        html_content = create_article_html(template, article_data)

        # 保存文件
        file_path = save_article(article_id, html_content)
        print(f"已保存: {file_path}")

        generated_articles.append({
            "id": article_id,
            "title": article_data.get("title"),
            "file": file_path
        })

        # 延迟一下，避免API限速
        if CONFIG["api_key"] != "mock" and i < len(new_ids) - 1:
            time.sleep(2)

    # 生成完成
    print("\n" + "=" * 60)
    print("文章生成完成！")
    print("=" * 60)

    if generated_articles:
        print(f"成功生成 {len(generated_articles)} 篇文章：")
        for article in generated_articles:
            print(f"  [{article['id']}] {article['title']}")
    else:
        print("没有成功生成任何文章。")

    print(f"\n文章文件保存在: {Path(CONFIG['post_dir']).absolute()}")
    print("\n提示：")
    print("1. 可以使用 python -m http.server 8000 启动本地服务器测试")
    print("2. 访问 http://localhost:8000/post/[id].html 查看文章")
    print("3. 记得更新首页和分类页的文章列表")

def generate_mock_article(article_id, category, topic, num_links=None):
    """生成模拟文章数据（用于测试）"""
    print("（使用模拟数据）")

    # 如果未指定num_links，使用配置中的默认值
    if num_links is None:
        num_links = CONFIG["num_links"]

    # 模拟文章内容
    mock_content = f"""
<p>本文详细探讨了{topic}的相关技术和实践方法。在当今快速发展的技术环境中，掌握这一领域的核心知识对于开发者来说至关重要。</p>

<h2>技术背景与核心概念</h2>

<p>{topic}是现代软件开发中的关键环节，它涉及到系统设计、代码实现、性能优化等多个方面。理解其基本原理对于构建稳健、可扩展的应用系统具有重要意义。</p>

<p>在实际项目中，我们需要综合考虑技术选型、架构设计、团队协作等多重因素。良好的{topic.lower()}实践能够显著提升开发效率和系统质量。</p>

<h3>核心原则与最佳实践</h3>

<p>实施{topic}时，应遵循一些核心原则：首先是关注点分离，将不同功能模块解耦；其次是高内聚低耦合，提高代码的可维护性；第三是开闭原则，支持系统的平滑演进。</p>

<p>最佳实践包括：合理的模块划分、清晰的接口设计、完善的错误处理、详细的文档记录等。这些实践经过长期项目验证，能够有效提升项目成功率。</p>

<h2>实施步骤与方法</h2>

<p>实施{topic}通常包括以下步骤：需求分析、技术选型、架构设计、代码实现、测试验证、部署运维等。每个阶段都有其特定的关注点和产出物。</p>

<h3>常见问题与解决方案</h3>

<p>在实践中，常见的问题包括：技术债务积累、性能瓶颈、兼容性问题、安全漏洞等。针对这些问题，需要建立系统化的排查和解决机制。</p>

<ul>
<li>问题一：技术选型不当 - 解决方案：充分评估技术特性和团队能力</li>
<li>问题二：架构设计缺陷 - 解决方案：引入设计评审和架构验证</li>
<li>问题三：代码质量低下 - 解决方案：实施代码规范和自动化测试</li>
</ul>

<h2>总结与展望</h2>

<p>{topic}是一个持续演进的技术领域。随着新技术和新方法的出现，我们需要不断学习和实践，保持技术的先进性和适用性。</p>

<p>未来，随着人工智能、云计算、边缘计算等技术的发展，{topic.lower()}将面临新的机遇和挑战。持续学习和创新是保持竞争力的关键。</p>
"""

    # 生成指定数量的外链（纯文本形式）
    if num_links > 0:
        random_links_text = "<br>\n".join(generate_random_links(num_links))
        mock_content += f"\n参考：<br>\n{random_links_text}\n"

    return {
        "id": article_id,
        "title": topic,
        "description": f"本文深入探讨{topic}的核心概念、实践方法和最佳实践，为开发者提供全面的技术指导。涵盖技术背景、实施步骤、常见问题解决方案等内容。",
        "keywords": f"{category['name']}, {topic}, 技术实践, 开发指南, 最佳实践",
        "content": mock_content,
        "category": category["name"],
        "category_slug": category["slug"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "date_display": datetime.now().strftime("%Y年%m月%d日"),
        "read_time": "约12分钟"
    }

if __name__ == "__main__":
    main()