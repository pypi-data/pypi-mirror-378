# Multi-Agent Testing Framework

Agnostic testing framework designed for multi-agent development systems with GitHub integration.

## Philosophy

**Doesn't duplicate existing solutions** - extends them for multi-agent workflows:
- Uses your existing pytest, Playwright, Jest configurations
- Adds multi-agent coordination testing on top
- Integrates with GitHub workflows and PR processes
- Tests agent task assignment and completion

## Installation

```bash
pip install multiagent-testing
```

## Quick Start

```bash
# Detect existing testing infrastructure
mtest detect

# Run all tests with multi-agent awareness
mtest run

# Run specific test types
mtest run --backend          # API/backend only
mtest run --frontend         # UI/E2E only
mtest run --agents          # Agent coordination
mtest run --github          # Workflow automation

# Test specific agents
mtest agent --agent gemini --task "code review"
mtest agent --agent codex --task "implementation"

# Initialize testing for new projects
mtest init --template agent
mtest init --template pytest
mtest init --template playwright
```

## Features

### 🔍 Framework Detection
- Automatically detects pytest, Playwright, Jest, etc.
- Suggests integration strategies
- Works with existing test suites

### 🤖 Agent Testing
- Test agent coordination and communication
- Validate task assignment and completion
- Test agent-specific capabilities
- Parallel agent testing

### ⚙️ GitHub Integration
- Test workflow automation
- Validate PR processes
- Test issue creation and routing
- Integration with GitHub Actions

### 🌐 Agnostic Design
- Works with any existing testing framework
- Doesn't replace your current setup
- Adds multi-agent layer on top
- Extensible for custom workflows

## Architecture

```
mtest run --all
├── Backend Tests (pytest/existing)
├── Frontend Tests (Playwright/existing) 
├── Agent Coordination Tests (new)
└── GitHub Workflow Tests (new)
```

## Integration with Multi-Agent Ecosystem

```bash
# Full stack setup
pip install multiagent-core multiagent-agentswarm multiagent-devops multiagent-testing

# Initialize project
multiagent init --with agentswarm,devops,testing

# Run complete test suite
mtest run --parallel
```

## Examples

### Testing Agent Task Completion
```bash
# Test if agents complete assigned tasks
mtest agent --task "convert JS to Python"
```

### Testing Multi-Agent Coordination
```bash
# Test agent coordination during complex tasks
mtest run --agents --parallel
```

### CI/CD Integration
```bash
# In GitHub Actions
- name: Run Multi-Agent Tests
  run: mtest run --github
```

## Contributing

This framework is designed to be:
- **Agnostic**: Works with any existing testing setup
- **Extensible**: Easy to add new agent types and test patterns
- **Non-invasive**: Doesn't replace existing tools
- **GitHub-native**: Built for modern multi-agent development workflows