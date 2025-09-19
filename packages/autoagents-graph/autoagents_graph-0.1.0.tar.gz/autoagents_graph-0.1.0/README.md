<div align="center">

<img src="https://img.shields.io/badge/-Hermes-FFD700?style=for-the-badge&labelColor=FF6B35&color=FFD700&logoColor=white" alt="Hermes" width="280"/>


<h4>The AI Workflow Cross-Platform Engine</h4>

**English** | [简体中文](README-CN.md)

<a href="https://pypi.org/project/hermes">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/pypi/v/hermes.svg?style=for-the-badge" />
    <img alt="PyPI version" src="https://img.shields.io/pypi/v/hermes.svg?style=for-the-badge" />
  </picture>
</a>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/dark_license.svg" />
  <img alt="License MIT" src="media/light_license.svg" />
</picture>

</div>

## Table of Contents

- [Why Choose Hermes?](#why-choose-hermes)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

## Why Choose Hermes?

Hermes is a revolutionary AI workflow cross-platform engine that allows you to freely convert workflows between different AI platforms through a unified API. Like Hermes delivering messages between the divine and mortal realms, Hermes helps you seamlessly navigate through complex AI ecosystems.

- **Zero Learning Curve**: Unified API design - learn once, use everywhere
- **Type Safety**: Complete type validation based on Pydantic, ensuring secure workflow transmission
- **Platform Compatibility**: Supports mainstream platforms like Dify, Agentify, with continuous expansion
- **Intelligent Conversion**: Automatic node type recognition and conversion, as precise as divine prophecy

## Quick Start

### System Requirements
- Python 3.11+
- pip or poetry

### Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/Hehua-Fan/Hermes.git
cd Hermes

# 2. Install dependencies
pip install -r requirements.txt

# 3. Quick experience
cd playground/text2workflow
python test_text2workflow.py
```

### Basic Usage

Hermes provides three main usage patterns:

#### Text2Workflow - Cross-Platform Converter
```python
from src.Text2Workflow import Text2Workflow
from src.dify import DifyStartState, DifyLLMState, DifyEndState, START, END

# Create Dify platform workflow
workflow = Text2Workflow(
    platform="dify",
    app_name="Smart Assistant"
)

# Add nodes
workflow.add_node(id=START, state=DifyStartState(title="Start"))
workflow.add_node(id="ai", state=DifyLLMState(title="AI Response"))
workflow.add_node(id=END, state=DifyEndState(title="End"))

# Compile workflow
workflow.compile()
```

#### FlowGraph - Agentify Native Builder
```python
from src.agentify import FlowGraph, QuestionInputState, AiChatState

# Create Agentify workflow
flow = FlowGraph(
    personal_auth_key="your_key",
    personal_auth_secret="your_secret"
)

# Build intelligent conversation flow
flow.add_node("input", QuestionInputState(inputText=True))
flow.add_node("ai", AiChatState(model="doubao-deepseek-v3"))
flow.add_edge("input", "ai")

# Publish to platform
flow.publish_app("Smart Chat Assistant")
```

### Running Examples

```bash
# Test Agentify platform functionality
cd playground/agentify
python test.py

# Test Dify platform integration
cd playground/dify
python test_dify.py

# Test cross-platform conversion
cd playground/text2workflow
python test_text2workflow.py
```

## Architecture

### Core Components

```
Hermes/
├── src/                        # Core source code
│   ├── agentify/              # Agentify platform engine
│   │   ├── FlowGraph.py       # Workflow graph builder
│   │   ├── NodeRegistry.py    # Node registry
│   │   └── types/             # Node type definitions
│   ├── dify/                  # Dify platform adapter
│   │   ├── DifyGraph.py       # Dify workflow builder
│   │   └── DifyTypes.py       # Dify node types
│   └── Text2Workflow.py       # Cross-platform converter
└── playground/                 # Examples and tests
    ├── agentify/              # Agentify platform examples
    ├── dify/                  # Dify platform examples
    └── text2workflow/         # Cross-platform examples
```

### Design Philosophy

- **Unified Abstraction**: Workflows from different platforms unified as node-edge graph models
- **Intelligent Adaptation**: Automatic node type recognition and cross-platform conversion
- **Modular Design**: Each platform independently implemented for easy extension and maintenance
- **Type Safety**: Complete type system ensuring compile-time error detection

### Supported Node Types

#### Agentify Platform Nodes
- **QuestionInputState** - User input node
- **AiChatState** - AI conversation node
- **ConfirmReplyState** - Confirmation reply node
- **KnowledgeSearchState** - Knowledge base search node

#### Dify Platform Nodes
- **DifyStartState** - Start node
- **DifyLLMState** - LLM node
- **DifyKnowledgeRetrievalState** - Knowledge retrieval node
- **DifyEndState** - End node

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
- Platform adapters

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

If you have any questions or suggestions, please contact us through [Issues](https://github.com/Hehua-Fan/Hermes/issues).