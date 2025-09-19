<div align="center">

<img src="https://img.shields.io/badge/-agentspro-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="Agentspro Python SDK" width="380"/>

<h4>The AI Agent Decorator SDK for Agentspro</h4>

**English** | [简体中文](README-CN.md)

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

## Table of Contents

- [Why Agentspro?](#why-agentspro)
- [Quick Start](#quick-start)
- [Core Features](#core-features)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Why Agentspro?

Agentspro is a powerful Python SDK that enables you to seamlessly connect your local Python functions to the Agentspro platform through elegant decorators. With just a simple `@agent(name=...)` decorator, you can transform any Python function into a cloud-accessible AI agent.

- **Zero Configuration**: Simply add decorators to your functions
- **Seamless Integration**: Direct connection to Agentspro platform APIs
- **Type Safety**: Complete type validation based on Pydantic
- **Real-time Sync**: Automatic function registration and updates

## Quick Start

### Prerequisites
- Python 3.11+
- Agentspro account (sign up at [agentspro.com](https://agentspro.com))

### Installation
```bash
pip install agentspro
```

### Basic Usage

```python
from agentspro import agent, init_agentspro

# Initialize with your API credentials
init_agentspro(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Transform any function into an AI agent
@agent(name="weather_checker")
def get_weather(city: str) -> str:
    """Get weather information for a specific city."""
    # Your function logic here
    return f"The weather in {city} is sunny and 25°C"

@agent(name="calculator")
def calculate(expression: str) -> float:
    """Calculate mathematical expressions."""
    return eval(expression)  # Note: Use safe_eval in production
```

## Core Features

### Decorator-Based Agent Registration
```python
from agentspro import agent

@agent(
    name="data_processor",
    description="Process and analyze data",
    tags=["data", "analysis"],
    version="1.0.0"
)
def process_data(data: list, operation: str) -> dict:
    """Process data with specified operation."""
    # Your processing logic
    return {"result": "processed", "count": len(data)}
```

### Automatic Type Validation
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
    """Create a new user with validation."""
    return {
        "id": "user_123",
        "name": name,
        "age": age,
        "skills": skills,
        "metadata": metadata or {}
    }
```

### Configuration Options
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
    """An advanced agent with custom configuration."""
    return f"Processed: {param}"
```

## Examples

### Data Processing Agent
```python
from agentspro import agent
import pandas as pd

@agent(name="csv_analyzer")
def analyze_csv(file_path: str) -> dict:
    """Analyze CSV file and return statistics."""
    df = pd.read_csv(file_path)
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "summary": df.describe().to_dict()
    }
```

### Web Scraping Agent
```python
from agentspro import agent
import requests
from bs4 import BeautifulSoup

@agent(name="web_scraper")
def scrape_title(url: str) -> str:
    """Extract title from a webpage."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.title.string if soup.title else "No title found"
```

### AI Integration Agent
```python
from agentspro import agent
from openai import OpenAI

client = OpenAI()

@agent(name="text_summarizer")
def summarize_text(text: str, max_length: int = 100) -> str:
    """Summarize text using AI."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the following text concisely."},
            {"role": "user", "content": text}
        ],
        max_tokens=max_length
    )
    return response.choices[0].message.content
```

## Platform Integration

Once you've decorated your functions with `@agent`, they automatically become available on the Agentspro platform where you can:

- **Monitor Usage**: Track function calls and performance
- **Manage Versions**: Deploy and rollback different versions
- **Configure Access**: Set permissions and rate limits
- **View Analytics**: Analyze usage patterns and optimization opportunities

## Contributing

We welcome community contributions! Please check the contribution guidelines for detailed processes.

### Development Workflow
1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

### Contribution Types
- Bug fixes
- New feature development
- Documentation improvements
- Test cases
- Platform integrations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.