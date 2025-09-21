# AgentRouter SDK

**Simplify the Complex, Amplify the Intelligent for Enterprise**

Orchestrate multiple agents with ease: register agents, integrate tools, define custom instructions, and leverage multiple models. Enterprise-grade and production-ready, with full control, deep customization, strong defaults, clear boundaries, and developer-focused APIs.

📚 **Full Documentation**: [https://agents-docs.us.inc](https://agents-docs.us.inc)

## Overview

AgentRouter is an enterprise-grade, production-ready framework that provides:

- 🏗️ **Hierarchical Agent Management** - Create manager and worker agents with unlimited nesting
- 🔧 **Tool Integration** - Easy tool creation with OpenAI-compatible schemas  
- 🚀 **Enterprise-Ready** - Built-in error handling, logging, and monitoring
- 🔒 **Complete Isolation** - Full isolation between agent instances
- 🤝 **OpenAI Compatible** - Works seamlessly with OpenAI message formats
- 📊 **Visual Tracing** - Zero-overhead tracing with beautiful execution visualizations

## Why AgentRouter?

### 🎯 Purpose-Built for Enterprise Scale
Unlike generic agent frameworks, AgentRouter is designed from the ground up for production environments handling millions of requests daily. Every architectural decision prioritizes reliability, performance, and maintainability.

### 🔄 True Hierarchical Management
While other frameworks offer basic agent coordination, AgentRouter provides **unlimited nesting depth** with intelligent message routing, automatic context propagation, and seamless worker sharing across multiple managers.

### 💡 Key Differentiators

**1. Complete Agent Isolation**
- Each agent instance is fully isolated with no state leakage
- Concurrent execution without interference
- Secure multi-tenant deployments

**2. Shared Worker Pattern**
- Reuse specialized workers across multiple managers
- Reduce resource consumption and API costs
- Maintain consistency across workflows

**3. Intelligent Configuration Inheritance**
- Workers automatically inherit parent configurations
- Override specific settings when needed
- Centralized credential management

**4. Production-Grade Features**
- Built-in retry mechanisms and circuit breakers
- Comprehensive error handling and recovery
- Structured logging and monitoring hooks
- Configurable timeouts at every level

**5. Zero-Overhead Tracing**
- Performance profiling adds < 1ns when disabled
- Beautiful visualization of execution flows
- Export to multiple formats (Mermaid, HTML, JSON)

**6. OpenAI Drop-in Compatibility**
- Use existing OpenAI code with minimal changes
- Enhanced with multi-agent capabilities
- Support for any OpenAI-compatible model provider

### 📊 When to Choose AgentRouter

✅ **Perfect for:**
- Complex multi-department workflows
- Applications requiring agent specialization
- Systems needing audit trails and compliance
- High-volume production deployments
- Teams wanting gradual migration from OpenAI

📖 **[Learn more about our architecture →](https://agents-docs.us.inc/docs/architecture/overview)**

## Key Features

### 🏗️ Hierarchical Multi-Agent System
- Unlimited nesting depth for complex workflows
- Shared worker agents across multiple parents
- Dynamic agent creation and attachment

### 🔧 Tool Integration
- OpenAI-compatible function schemas
- Automatic validation and error handling
- Support for async operations

### 🚀 Production Ready
- Configurable timeouts and retries
- Built-in monitoring and logging
- Scale to millions of users per day

### 📊 Visualization & Tracing
- Zero-overhead tracing (< 1ns when disabled)
- Multiple output formats: Mermaid, HTML, JSON
- Pipeline validation before execution

## Installation

```bash
pip install agentrouter
```

## Quick Start

```python
from agentrouter import ManagerAgent, WorkerAgent, tool

# Create a manager agent
manager = ManagerAgent(
    name="Customer_Service_Manager",
    model="usf-mini",
    api_key="your-api-key"
)

# Create and attach workers
tech_support = manager.create_worker(
    name="Technical_Support",
    role="Technical Support Specialist"
)

# Execute tasks
messages = [{"role": "user", "content": "Help needed"}]
response = await manager.execute(messages)
```

📖 **[View Complete Quick Start Guide →](https://agents-docs.us.inc/docs/quickstart)**

## Documentation

### Getting Started
- 📖 **[Quick Start Guide](https://agents-docs.us.inc/docs/quickstart)** - Get up and running in minutes
- 📦 **[Installation](https://agents-docs.us.inc/docs/installation/install)** - Installation and setup instructions
- ⚙️ **[Configuration](https://agents-docs.us.inc/docs/installation/config)** - Configuration options and best practices

### Architecture & Concepts
- 🏛️ **[Architecture Overview](https://agents-docs.us.inc/docs/architecture/overview)** - System design and concepts
- 🔄 **[Execution Flow](https://agents-docs.us.inc/docs/architecture/execution)** - Understanding agent execution
- 🌲 **[Nested Workers](https://agents-docs.us.inc/docs/architecture/nested-workers)** - Building hierarchical systems
- 🔧 **[Tools Integration](https://agents-docs.us.inc/docs/architecture/tools)** - Working with tools
- 🏢 **[Enterprise Features](https://agents-docs.us.inc/docs/architecture/enterprise)** - Production-ready features

### Examples & Cookbook
- 📚 **[Cookbook Overview](https://agents-docs.us.inc/docs/cookbook/overview)** - Collection of recipes and patterns
- 🛍️ **[Customer Service](https://agents-docs.us.inc/docs/cookbook/colab/customer-service)** - Multi-department coordination
- 💼 **[Finance Portfolio](https://agents-docs.us.inc/docs/cookbook/colab/finance-portfolio)** - Financial analysis system
- 🏥 **[Healthcare Diagnosis](https://agents-docs.us.inc/docs/cookbook/colab/healthcare-diagnosis)** - Medical diagnostic workflow
- 🏭 **[Manufacturing](https://agents-docs.us.inc/docs/cookbook/colab/manufacturing-supply-chain)** - Supply chain management
- 📚 **[Education Platform](https://agents-docs.us.inc/docs/cookbook/colab/education-learning)** - Adaptive learning system

### Advanced Topics
- 🔌 **[Plugin System](https://agents-docs.us.inc/docs/architecture/orchestration)** - Extending with plugins
- 📊 **[Visualization Guide](https://agents-docs.us.inc/docs/architecture/execution#visualization)** - Tracing and visualization
- 🚀 **[Performance Optimization](https://agents-docs.us.inc/docs/architecture/enterprise#performance)** - Scaling best practices

📂 **[Browse All Examples →](https://agents-docs.us.inc/docs/cookbook/overview)**

📖 **[Development Guide →](https://agents-docs.us.inc/docs/installation/install#development)**

## License

AgentRouter SDK is licensed under the **Permissive Commercial Use License**. See the [LICENSE](https://agents-docs.us.inc/docs/license) file for full details.

### ✅ You are free to:
- Use AgentRouter for **ANY commercial purpose**
- Build commercial applications and services with AgentRouter
- Deploy AgentRouter in production environments
- Integrate AgentRouter into your products
- Use AgentRouter for research and development

### ❌ You cannot:
- Create competing orchestration frameworks based on AgentRouter's code
- Fork and modify AgentRouter to create competitive products
- Use AgentRouter's source code as inspiration for competitive products

For additional support or custom licensing arrangements, please contact the UltraSafe AI Team at support@us.inc.

---

**[Visit Full Documentation →](https://agents-docs.us.inc)**