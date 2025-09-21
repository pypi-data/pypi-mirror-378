# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['arcp',
 'arcp.api',
 'arcp.core',
 'arcp.models',
 'arcp.services',
 'arcp.utils',
 'web']

package_data = \
{'': ['*'],
 'web': ['static/css/*', 'static/icons/*', 'static/js/*', 'templates/*']}

install_requires = \
['PyJWT>=2.10.1,<3.0.0',
 'deprecated>=1.2.0,<2.0.0',
 'fastapi>=0.115.0,<1.0.0',
 'importlib-metadata>=1.7.0,<7.0.0',
 'openai>=1.3.0,<2.0.0',
 'opentelemetry-api>=1.21.0,<2.0.0',
 'opentelemetry-exporter-jaeger-thrift>=1.21.0,<2.0.0',
 'opentelemetry-exporter-otlp-proto-grpc>=1.21.0,<2.0.0',
 'opentelemetry-instrumentation-fastapi>=0.42b0,<1.0.0',
 'opentelemetry-instrumentation-httpx>=0.42b0,<1.0.0',
 'opentelemetry-instrumentation-redis>=0.42b0,<1.0.0',
 'opentelemetry-instrumentation>=0.42b0,<1.0.0',
 'opentelemetry-sdk>=1.21.0,<2.0.0',
 'opentelemetry-semantic-conventions>=0.42b0,<1.0.0',
 'prometheus-client>=0.19.0,<1.0.0',
 'psutil>=7.0.0,<8.0.0',
 'pydantic>=2.5.0,<3.0.0',
 'python-dotenv>=1.0.0,<2.0.0',
 'redis>=5.0.1,<7.0.0',
 'thrift>=0.13.0,<1.0.0',
 'uvicorn[standard]>=0.24.0,<1.0.0',
 'websockets>=11.0.3,<16.0.0',
 'wrapt>=1.10.0,<2.0.0']

extras_require = \
{':extra == "dev" or extra == "all"': ['httpx>=0.25.2,<1.0.0']}

setup_kwargs = {
    'name': 'arcp-py',
    'version': '2.0.2',
    'description': 'ARCP (Agent Registry & Control Protocol) is a sophisticated agent orchestration protocol that provides centralized service discovery, registration, communication, and control for distributed agent systems.',
    'long_description': '<div align="center">\n\n# ARCP - Agent Registry & Control Protocol\n\n[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)\n[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security](https://img.shields.io/badge/security+-brightgreen.svg)](#security)\n[![PyPI version](https://badge.fury.io/py/arcp-py.svg)](https://badge.fury.io/py/arcp-py)\n[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)\n\n**A sophisticated agent orchestration protocol that provides centralized service discovery, registration, communication, and control for distributed agent systems.**\n\n</div>\n\n## ✨ Features\n\n<div align="center">\n\n| 🔧 **Centralized Management** | 🔍 **Service Discovery** | 🤝 **Agent Communication** |\n|:---:|:---:|:---:|\n| *Register & control agents* | *Automatic endpoint resolution* | *Secure agent collaboration* |\n\n| 🛡️ **Security** | 📊 **Dashboard** | 🐳 **Production** |\n|:---:|:---:|:---:|\n| *Built-in authentication* | *Metrics & Alerts & Logs* | *Docker & monitoring stack* |\n\n| ⚙️ **Extensible** | 👨\u200d💻 **Developers** | 📚 **Docs** |\n|:---:|:---:|:---:|\n| *Custom use cases* | *Python client, API* | *Guides & references* |\n\n</div>\n\n\n## 🚀 Quick Start\n\n### Running the Server\n\n#### 🐍 pip Installation\n```bash\n# Install ARCP\npip install arcp-py\n\n# Set up configuration\ncurl -o .env https://raw.githubusercontent.com/0x00K1/ARCP/main/.env.example\n# Edit .env file with your configuration\n\n# Start the server\npython -m arcp\n```\n\n#### 🐳 Docker Deployment (Recommended)\nFor a complete production setup with monitoring, use Docker:\n\n```bash\n# Clone ARCP\ngit clone https://github.com/0x00K1/ARCP.git\ncd ARCP\n\n# Set up configuration\ncp .env.example .env\ncp .env.example deployment/docker/.env\n# Edit .env file with your configuration\n\n# Start full stack (ARCP + Redis + Monitoring)\ncd deployment/docker\ndocker-compose up -d --build\n```\n\n> 💡 **Need help?** Check out our detailed [Installation Guide](https://arcp.0x001.tech/docs/getting-started/installation).\n\n\n### 🛠️ Agent Development\n\nBuild agents that integrate seamlessly with ARCP:\n\n```python\nfrom arcp import ARCPClient, AgentRequirements\n\nasync def register_with_arcp():\n    """Register this agent with ARCP"""\n    # Create ARCP client\n    arcp_client = ARCPClient("http://localhost:8001")\n    \n    try:\n        # Register the agent\n        agent = await arcp_client.register_agent(\n            agent_id="my-agent-001",\n            name="My Demo Agent",\n            agent_type="automation",\n            endpoint="http://localhost:8080",\n            capabilities=["processing", "automation"],\n            context_brief="A demo agent showcasing ARCP integration",\n            version="1.0.0",\n            owner="Developer",\n            public_key="your-public-key-min-32-chars-long",\n            communication_mode="remote",\n            metadata={\n                "framework": "fastapi",\n                "language": "python",\n                "created_at": "2025-09-20T03:00:00.000000",\n            },\n            features=["http-api", "json-responses"],\n            max_tokens=1000,\n            language_support=["en"],\n            rate_limit=100,\n            requirements=AgentRequirements(\n                system_requirements=["Python 3.11+", "FastAPI"],\n                permissions=["http-server"],\n                dependencies=["fastapi", "arcp"],\n                minimum_memory_mb=256,\n                requires_internet=True,\n                network_ports=["8080"]\n            ),\n            policy_tags=["utility", "demo"],\n            agent_key="test-agent-001"\n        )\n        \n        print(f"✅ Agent registered: {agent.name}")\n        print(f"📊 Status: {agent.status}")\n        \n    finally:\n        await arcp_client.close()\n\n# Run the registration\nimport asyncio\nasyncio.run(register_with_arcp())\n```\n\n> 🎯 **Want to dive deeper?** Explore our comprehensive [Agent Development Guide](https://arcp.0x001.tech/docs/user-guide/agent-development).\n\n\n## 📚 Documentation\n\n<div align="center">\n\n### Everything you need to get started, develop agents, and operate ARCP\n\n**📖 [Complete Documentation](https://arcp.0x001.tech/docs)**\n\n</div>\n\n\n## 📄 License\n\n<div>\n\nThis project is licensed under the **Apache License 2.0** - see the [LICENSE](https://arcp.0x001.tech/docs/LICENSE) file for details.\n\n</div>',
    'author': 'Muhannad',
    'author_email': '01muhannad.a@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/0x00K1/ARCP',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
