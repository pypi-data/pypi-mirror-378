<div align="center">

<img src="https://img.shields.io/badge/-agentspro-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="Agentspro Python SDK" width="380"/>

<h4>Agentspro AI智能体装饰器SDK</h4>

[English](README.md) | **简体中文**

<a href="https://pypi.org/project/agentspro">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/pypi/v/agentspro.svg?style=for-the-badge" />
    <img alt="PyPI version" src="https://img.shields.io/pypi/v/agentspro.svg?style=for-the-badge" />
  </picture>
</a>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/dark_license.svg" />
  <img alt="License MIT" src="media/light_license.svg" />
</picture>

</div>

## 目录

- [为什么选择Agentspro？](#为什么选择agentspro)
- [快速开始](#快速开始)
- [核心特性](#核心特性)
- [示例](#示例)
- [平台集成](#平台集成)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 为什么选择Agentspro？

Agentspro 是一个强大的Python SDK，让你可以通过优雅的装饰器将本地Python函数无缝连接到Agentspro平台。只需简单的 `@agent(name=...)` 装饰器，就能将任何Python函数转换为云端可访问的AI智能体。

- **零配置**：只需为函数添加装饰器
- **无缝集成**：直接连接到Agentspro平台API
- **类型安全**：基于Pydantic的完整类型验证
- **实时同步**：自动函数注册和更新

## 快速开始

### 系统要求
- Python 3.11+
- Agentspro账号（在 [agentspro.com](https://agentspro.com) 注册）

### 安装
```bash
pip install agentspro
```

### 基础使用

```python
from agentspro import agent, init_agentspro

# 使用你的API凭证初始化
init_agentspro(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# 将任何函数转换为AI智能体
@agent(name="weather_checker")
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。"""
    # 你的函数逻辑
    return f"{city}的天气是晴天，25°C"

@agent(name="calculator")
def calculate(expression: str) -> float:
    """计算数学表达式。"""
    return eval(expression)  # 注意：生产环境请使用safe_eval
```

## 核心特性

### 基于装饰器的智能体注册
```python
from agentspro import agent

@agent(
    name="data_processor",
    description="处理和分析数据",
    tags=["数据", "分析"],
    version="1.0.0"
)
def process_data(data: list, operation: str) -> dict:
    """使用指定操作处理数据。"""
    # 你的处理逻辑
    return {"result": "已处理", "count": len(data)}
```

### 自动类型验证
```python
from typing import List, Dict
from agentspro import agent

@agent(name="user_manager")
def create_user(
    name: str, 
    age: int, 
    skills: List[str],
    metadata: Dict[str, str] = None
) -> Dict[str, any]:
    """创建新用户并进行验证。"""
    return {
        "id": "user_123",
        "name": name,
        "age": age,
        "skills": skills,
        "metadata": metadata or {}
    }
```

### 配置选项
```python
from agentspro import agent, AgentConfig

@agent(
    name="advanced_agent",
    config=AgentConfig(
        timeout=30,
        retry_attempts=3,
        cache_enabled=True,
        rate_limit=100
    )
)
def advanced_function(param: str) -> str:
    """具有自定义配置的高级智能体。"""
    return f"已处理: {param}"
```

## 示例

### 数据处理智能体
```python
from agentspro import agent
import pandas as pd

@agent(name="csv_analyzer")
def analyze_csv(file_path: str) -> dict:
    """分析CSV文件并返回统计信息。"""
    df = pd.read_csv(file_path)
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "summary": df.describe().to_dict()
    }
```

### 网页抓取智能体
```python
from agentspro import agent
import requests
from bs4 import BeautifulSoup

@agent(name="web_scraper")
def scrape_title(url: str) -> str:
    """从网页提取标题。"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.title.string if soup.title else "未找到标题"
```

### AI集成智能体
```python
from agentspro import agent
from openai import OpenAI

client = OpenAI()

@agent(name="text_summarizer")
def summarize_text(text: str, max_length: int = 100) -> str:
    """使用AI总结文本。"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "请简洁地总结以下文本。"},
            {"role": "user", "content": text}
        ],
        max_tokens=max_length
    )
    return response.choices[0].message.content
```

## 平台集成

当你用 `@agent` 装饰器装饰函数后，它们会自动在Agentspro平台上可用，你可以：

- **监控使用情况**：跟踪函数调用和性能
- **管理版本**：部署和回滚不同版本
- **配置访问权限**：设置权限和速率限制
- **查看分析数据**：分析使用模式和优化机会

## 贡献指南

我们欢迎社区贡献！请查看贡献指南了解详细流程。

### 开发流程
1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 贡献类型
- Bug修复
- 新功能开发
- 文档改进
- 测试用例
- 平台集成

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。