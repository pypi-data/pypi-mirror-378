# 🚀 Django-CFG: Type-Safe Django Configuration

[![Python Version](https://img.shields.io/pypi/pyversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![Django Version](https://img.shields.io/pypi/djversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![License](https://img.shields.io/pypi/l/django-cfg.svg)](https://github.com/reformsai/django-cfg/blob/main/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/django-cfg.svg)](https://pypi.org/project/django-cfg/)

> **Create a production-ready Django project in 30 seconds, not 30 hours.**

Production-ready Django configuration with **Pydantic v2 models**, **AI agents**, and **enterprise integrations**. Build modern Django applications with full type safety, intelligent environment detection, and seamless deployment.

🌐 **Website**: [djangocfg.com](https://djangocfg.com/)  
📚 **Documentation**: [docs.djangocfg.com](https://docs.djangocfg.com/)  
🐙 **GitHub**: [github.com/reformsai/django-cfg](https://github.com/reformsai/django-cfg)

## 🎯 Quick Start

### Requirements
- **Python 3.12+** - [Download here](https://www.python.org/downloads/)

### Create Your First Project

```bash
# Install Django-CFG
pip install django-cfg

# Create a complete project instantly
django-cfg create-project "My Awesome Project"

# Enter the project and run
cd my-awesome-project
python manage.py runserver
```

**🎉 That's it!** Your app is now running with:
- **🚀 Main app:** http://127.0.0.1:8000/
- **🎯 Admin panel:** http://127.0.0.1:8000/admin/
- **📚 API docs:** http://127.0.0.1:8000/api/docs/

## ✨ What You Get Out of the Box

✅ **Beautiful admin interface** with Unfold + Tailwind CSS  
✅ **Complete API documentation** with Swagger/ReDoc  
✅ **Multi-channel user management** with email & SMS OTP authentication  
✅ **SMS & WhatsApp integration** with Twilio out of the box  
✅ **Support ticket system** with chat interface  
✅ **Newsletter campaigns** with email tracking  
✅ **Lead management** system with CRM integration  
✅ **Multi-database routing** and connection pooling  
✅ **Background task processing** with production-ready Dramatiq integration  
✅ **Webhook testing** with built-in ngrok integration  
✅ **Type-safe configuration** with full IDE support

## 🏆 Django-CFG vs Traditional Django

| Feature | Traditional Django | Django-CFG |
|---------|-------------------|-------------|
| **📝 Configuration** | 500+ lines of settings hell | **Type-safe & organized** |
| **🔒 Type Safety** | Pray and hope | **100% validated** |
| **🎨 Admin Interface** | Ugly 2010 design | **Modern Unfold + Tailwind** |
| **📊 Dashboard** | Basic admin index | **Real-time metrics & widgets** |
| **🗄️ Multi-Database** | Manual routing nightmare | **Smart auto-routing** |
| **📚 API Docs** | Hours of manual setup | **Auto-generated OpenAPI** |
| **🎫 Support System** | Build from scratch | **Built-in tickets & chat** |
| **👤 User Management** | Basic User model | **OTP auth & profiles** |
| **🚀 Deployment** | Cross fingers | **Production-ready defaults** |
| **💡 IDE Support** | Basic syntax highlighting | **Full IntelliSense paradise** |
| **🐛 Config Errors** | Runtime surprises | **Compile-time validation** |

## 🔥 Core Features

### 🔒 Type-Safe Configuration
Full Pydantic v2 validation with IDE autocomplete and compile-time error checking.

```python
from django_cfg import DjangoConfig
from django_cfg.models import DatabaseConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    secret_key: str = "${SECRET_KEY}"
    debug: bool = False
    
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="${DB_NAME}",
            user="${DB_USER}",
            password="${DB_PASSWORD}",
        )
    }

config = MyConfig()
```

### 🤖 Built-in AI Agents
Enterprise-grade AI agent system with type-safe agents and workflow orchestration.

```python
from django_cfg.agents import Agent, Workflow

@Agent.register("data_processor")
class DataProcessor(Agent):
    def process(self, data: dict) -> dict:
        # Your AI logic here
        return processed_data

# Use in workflows
workflow = Workflow([DataProcessor()])
result = workflow.run(input_data)
```

### 🌍 Smart Environment Detection
Automatic dev/staging/production detection with appropriate defaults.

```python
class MyConfig(DjangoConfig):
    # Automatically detects environment and applies settings
    # No manual configuration needed!
    pass
```

### 🗄️ Multi-Database Support
Smart database routing with connection pooling.

```python
databases: dict[str, DatabaseConfig] = {
    "default": DatabaseConfig.from_url("postgresql://..."),
    "analytics": DatabaseConfig.from_url(
        "postgresql://...",
        apps=["analytics"],  # Route analytics app here
    ),
}
```

### 🔄 Background Task Processing
Built-in Dramatiq integration for reliable background jobs.

```python
import dramatiq

@dramatiq.actor
def process_document(document_id: str):
    # Your background task
    pass

# Queue the task
process_document.send(document_id="123")
```

## 📦 Installation Methods

### Using pip (Recommended)
```bash
pip install django-cfg
```

### Using Poetry
```bash
poetry add django-cfg
```

### Using pipenv
```bash
pipenv install django-cfg
```

### Using conda
```bash
conda install -c conda-forge django-cfg
```

## 🚀 Advanced Usage

### Production Configuration

```python
from django_cfg import DjangoConfig
from django_cfg.models import *

class ProductionConfig(DjangoConfig):
    project_name: str = "My Production App"
    
    # Multi-database setup
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="${DB_NAME}",
            host="${DB_HOST}",
            sslmode="require",
        ),
        "analytics": DatabaseConfig(
            routing_apps=["analytics", "reports"],
        ),
    }
    
    # Background tasks
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            processes=4,
            threads=8,
            queues=["default", "high", "low"],
        ),
    )
    
    # Beautiful admin
    unfold: UnfoldConfig = UnfoldConfig(
        site_title="My Admin",
        theme="auto",
        dashboard_callback="myapp.dashboard.callback",
    )
```

### Built-in Features

```python
class MyConfig(DjangoConfig):
    # Enable built-in modules
    enable_support: bool = True      # Support ticket system
    enable_accounts: bool = True     # Advanced user management
    enable_newsletter: bool = True   # Email marketing
    enable_leads: bool = True        # Lead management
    enable_knowbase: bool = True     # AI knowledge base
    enable_agents: bool = True       # AI agents
```

## 🛠️ Management Commands

Django-CFG includes powerful CLI tools:

```bash
# Create new project
django-cfg create-project "My Project"

# Get system information
django-cfg info

# Enhanced Django commands
python manage.py migrator --auto          # Smart migrations
python manage.py validate_config         # Validate settings
python manage.py show_config             # Display config
python manage.py rundramatiq             # Background workers
python manage.py runserver_ngrok         # Dev server with ngrok
python manage.py test_email              # Test email config
python manage.py test_twilio             # Test SMS/WhatsApp
```

## 🌐 Real-World Example

See how **CarAPIS** (automotive data platform) uses Django-CFG in production:

- **Multi-database architecture** for vehicle data
- **Background task processing** for tax calculations
- **SMS/WhatsApp OTP** authentication
- **API zones** for different services
- **Custom admin dashboard** with real-time metrics

[View Full CarAPIS Example →](https://docs.djangocfg.com/examples/production-config)

## 📚 Documentation

### Getting Started
- [**Installation Guide**](https://docs.djangocfg.com/getting-started/installation) - Complete setup instructions
- [**First Project**](https://docs.djangocfg.com/getting-started/first-project) - Build your first app
- [**Configuration**](https://docs.djangocfg.com/getting-started/configuration) - Core concepts

### Core Features
- [**Architecture**](https://docs.djangocfg.com/core/architecture) - System overview
- [**Environment Detection**](https://docs.djangocfg.com/core/environment-detection) - Automatic environment setup
- [**Registry System**](https://docs.djangocfg.com/core/registry) - Component registration
- [**Utilities**](https://docs.djangocfg.com/core/utilities) - Helper functions

### AI & Agents
- [**AI Agents**](https://docs.djangocfg.com/agents/introduction) - Build intelligent workflows
- [**Knowledge Base**](https://docs.djangocfg.com/knowbase/setup) - AI-powered documentation

### Integrations
- [**Integration Patterns**](https://docs.djangocfg.com/integrations/patterns) - Common patterns
- [**Dramatiq**](https://docs.djangocfg.com/integrations/dramatiq) - Background tasks
- [**Twilio**](https://docs.djangocfg.com/integrations/twilio) - SMS/WhatsApp
- [**Authentication**](https://docs.djangocfg.com/integrations/auth) - OTP auth

### Built-in Apps
- [**Accounts**](https://docs.djangocfg.com/apps/accounts) - User management
- [**Support System**](https://docs.djangocfg.com/apps/support) - Ticket system
- [**Newsletter**](https://docs.djangocfg.com/apps/newsletter) - Email marketing

### CLI Tools
- [**CLI Introduction**](https://docs.djangocfg.com/cli/introduction) - Command overview
- [**Commands Reference**](https://docs.djangocfg.com/cli/commands) - All commands
- [**Custom Commands**](https://docs.djangocfg.com/cli/custom-commands) - Build your own

### Examples & Deployment
- [**Basic Setup**](https://docs.djangocfg.com/examples/basic-setup) - Simple examples
- [**Production Config**](https://docs.djangocfg.com/examples/production-config) - Real-world setup
- [**Migration Guide**](https://docs.djangocfg.com/examples/migration-guide) - Migrate existing projects
- [**Docker Deployment**](https://docs.djangocfg.com/deployment/docker) - Container deployment

## 🔄 Migration from Existing Django

### Option 1: Fresh Start (Recommended)
```bash
# Create new Django-CFG project
django-cfg create-project "My Migrated Project"

# Copy your apps and migrate data
# See migration guide for details
```

### Option 2: Gradual Migration
```bash
# Install in existing project
pip install django-cfg

# Create config.py
# Replace settings.py content
# Migrate features gradually
```

[**Complete Migration Guide →**](https://docs.djangocfg.com/examples/migration-guide)

## ⚠️ Troubleshooting

### Python Version Error
```bash
# Install Python 3.12+
brew install python@3.12  # macOS
# OR
pyenv install 3.12.0      # Using pyenv
```

### Virtual Environment Issues
```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate     # Windows
```

### Configuration Errors
```bash
# Validate your configuration
python manage.py validate_config --strict

# Show current configuration
python manage.py show_config
```

[**Full Troubleshooting Guide →**](https://docs.djangocfg.com/getting-started/installation#troubleshooting)

## 🧪 Testing

```python
def test_configuration():
    """Test your Django-CFG configuration"""
    from config import config
    
    # Validate configuration
    settings = config.get_all_settings()
    assert "SECRET_KEY" in settings
    assert settings["DEBUG"] is False
    
    # Test database connections
    assert "default" in settings["DATABASES"]
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

```bash
git clone https://github.com/reformsai/django-cfg.git
cd django-cfg
pip install -e ".[dev,test]"
pytest
```

### Development Commands
```bash
# Run tests
pytest

# Format code
black .

# Type checking
mypy .

# Build package
python -m build
```

## 📊 Performance

Django-CFG is designed for production:

- **Startup Time**: < 50ms additional startup time
- **Memory Usage**: < 1MB additional memory
- **Type Validation**: Cached after first load
- **Production Optimized**: Skip validation with `DJANGO_CFG_SKIP_VALIDATION=1`

## 🌟 Community

- **🌐 Website**: [djangocfg.com](https://djangocfg.com/)
- **📚 Documentation**: [docs.djangocfg.com](https://docs.djangocfg.com/)
- **🐙 GitHub**: [github.com/reformsai/django-cfg](https://github.com/reformsai/django-cfg)
- **📦 PyPI**: [pypi.org/project/django-cfg](https://pypi.org/project/django-cfg/)
- **💬 Discord**: [Join our Discord](https://discord.gg/django-cfg)
- **❓ Stack Overflow**: Tag questions with `django-cfg`

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django** - The web framework for perfectionists with deadlines
- **Pydantic** - Data validation using Python type hints
- **Django Unfold** - Beautiful modern admin interface
- **Dramatiq** - Fast and reliable background task processing

---

**Made with ❤️ by the Django-CFG Team**

*Transform your Django development experience with type-safe configuration, AI agents, and enterprise integrations.*

🚀 **[Get Started Now](https://docs.djangocfg.com/getting-started/installation)** | 📚 **[View Documentation](https://docs.djangocfg.com/)** | 🌐 **[Visit Website](https://djangocfg.com/)**
