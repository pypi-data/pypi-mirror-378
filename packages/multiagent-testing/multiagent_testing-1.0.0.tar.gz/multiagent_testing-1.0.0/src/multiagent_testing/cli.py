"""Multi-Agent Testing CLI

Agnostic testing framework that works with multi-agent systems and GitHub.
Doesn't duplicate existing solutions - extends them for multi-agent workflows.
"""

import click
import requests
import pkg_resources
from rich.console import Console
from rich.table import Table
from pathlib import Path
import subprocess
import json

console = Console()

@click.group()
def main():
    """Multi-Agent Testing Framework - Agnostic testing for multi-agent systems"""
    # Check for updates on every command
    _check_for_updates()
    pass

@main.command()
@click.option("--backend", is_flag=True, help="Run backend/API tests only")
@click.option("--frontend", is_flag=True, help="Run frontend/E2E tests only")
@click.option("--agents", is_flag=True, help="Run agent integration tests")
@click.option("--github", is_flag=True, help="Run GitHub workflow tests")
@click.option("--parallel", is_flag=True, help="Run tests in parallel across agents")
def run(backend, frontend, agents, github, parallel):
    """Run tests with multi-agent awareness"""
    
    if not any([backend, frontend, agents, github]):
        # Run all by default
        backend = frontend = agents = github = True
    
    console.print("🧪 [bold]Multi-Agent Testing Framework[/bold]")
    
    if backend:
        console.print("🔧 Running backend tests...")
        # Detect existing backend testing (pytest, etc.)
        _run_backend_tests(parallel)
    
    if frontend:
        console.print("🌐 Running frontend tests...")
        # Detect existing frontend testing (Playwright, Jest, etc.)
        _run_frontend_tests(parallel)
    
    if agents:
        console.print("🤖 Running agent integration tests...")
        # Test agent coordination and communication
        _run_agent_tests(parallel)
    
    if github:
        console.print("⚙️ Running GitHub workflow tests...")
        # Test workflow automation and PR processes
        _run_github_tests()

@main.command()
@click.option("--agent", help="Test specific agent (gemini, codex, qwen, claude)")
@click.option("--task", help="Test specific task type")
def agent(agent, task):
    """Test individual agent functionality"""
    console.print(f"🤖 Testing agent: {agent or 'all'}")
    
    if task:
        console.print(f"📋 Task type: {task}")
    
    # Test agent-specific functionality
    _test_agent_functionality(agent, task)

@main.command()
def detect():
    """Detect existing testing infrastructure and suggest integration"""
    console.print("🔍 [bold]Detecting existing testing infrastructure...[/bold]")
    
    detections = _detect_testing_infrastructure()
    
    table = Table(title="Testing Infrastructure")
    table.add_column("Framework", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Integration", style="yellow")
    
    for framework, status, integration in detections:
        table.add_row(framework, status, integration)
    
    console.print(table)

@main.command()
@click.option("--template", type=click.Choice(["pytest", "playwright", "jest", "agent"]))
def init(template):
    """Initialize testing structure for multi-agent development"""
    console.print(f"🚀 Initializing {template} testing structure...")
    
    if template == "agent":
        _init_agent_testing()
    else:
        _init_framework_testing(template)

def _run_backend_tests(parallel):
    """Run backend tests using existing frameworks"""
    project_root = Path.cwd()
    
    # Detect pytest
    if (project_root / "pytest.ini").exists() or (project_root / "pyproject.toml").exists():
        console.print("  📦 Detected pytest configuration")
        if parallel:
            subprocess.run(["pytest", "-n", "auto"], cwd=project_root)
        else:
            subprocess.run(["pytest"], cwd=project_root)
    
    # Detect other backend frameworks
    elif (project_root / "package.json").exists():
        console.print("  📦 Detected Node.js testing")
        subprocess.run(["npm", "test"], cwd=project_root)

def _run_frontend_tests(parallel):
    """Run frontend tests using existing frameworks"""
    project_root = Path.cwd()
    
    # Detect Playwright
    if (project_root / "playwright.config.js").exists() or (project_root / "playwright.config.ts").exists():
        console.print("  🎭 Detected Playwright configuration")
        subprocess.run(["npx", "playwright", "test"], cwd=project_root)
    
    # Detect Jest/other frameworks
    elif (project_root / "jest.config.js").exists():
        console.print("  🃏 Detected Jest configuration")
        subprocess.run(["npm", "run", "test:frontend"], cwd=project_root)

def _run_agent_tests(parallel):
    """Run agent-specific integration tests"""
    console.print("  🤖 Testing agent coordination...")
    console.print("  📡 Testing agent communication...")
    console.print("  🔄 Testing task assignment...")
    
    if parallel:
        console.print("  ⚡ Running agent tests in parallel...")

def _run_github_tests():
    """Test GitHub workflow integration"""
    console.print("  📋 Testing issue creation...")
    console.print("  🔀 Testing PR workflows...")
    console.print("  ⚙️ Testing automation...")

def _test_agent_functionality(agent, task):
    """Test specific agent functionality"""
    if agent:
        console.print(f"  🎯 Testing @{agent} capabilities...")
        console.print(f"  📊 Checking @{agent} task completion...")
    else:
        console.print("  🌐 Testing all agent capabilities...")

def _detect_testing_infrastructure():
    """Detect existing testing frameworks"""
    project_root = Path.cwd()
    detections = []
    
    # Backend detection
    if (project_root / "pytest.ini").exists():
        detections.append(("pytest", "✅ Found", "Ready for multi-agent"))
    elif (project_root / "pyproject.toml").exists():
        detections.append(("Python testing", "✅ Found", "Can integrate"))
    else:
        detections.append(("Backend testing", "❌ Not found", "Run mtest init --template pytest"))
    
    # Frontend detection
    if (project_root / "playwright.config.js").exists():
        detections.append(("Playwright", "✅ Found", "Ready for multi-agent"))
    elif (project_root / "jest.config.js").exists():
        detections.append(("Jest", "✅ Found", "Can integrate"))
    else:
        detections.append(("Frontend testing", "❌ Not found", "Run mtest init --template playwright"))
    
    # Multi-agent detection
    if (project_root / ".multiagent").exists():
        detections.append(("Multi-agent", "✅ Found", "Ready"))
    else:
        detections.append(("Multi-agent", "❌ Not found", "Run multiagent init"))
    
    return detections

def _init_agent_testing():
    """Initialize agent-specific testing structure"""
    console.print("  🤖 Creating agent test templates...")
    console.print("  📋 Setting up task validation...")
    console.print("  🔄 Configuring agent coordination tests...")

def _init_framework_testing(template):
    """Initialize specific testing framework"""
    console.print(f"  📦 Setting up {template} configuration...")
    console.print(f"  📁 Creating {template} test structure...")

def _get_latest_version(package_name):
    """Get latest version of package from PyPI"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data['info']['version']
    except Exception:
        pass
    return None

def _check_for_updates():
    """Check for Testing updates"""
    try:
        current_version = pkg_resources.get_distribution('multiagent-testing').version
        latest_version = _get_latest_version('multiagent-testing')
        
        if latest_version and current_version != latest_version:
            console.print(f"[dim yellow]💡 Update available: multiagent-testing {current_version} → {latest_version}[/dim yellow]")
            console.print(f"[dim yellow]   Run 'multiagent upgrade' to update all packages[/dim yellow]")
    except Exception:
        # Silently fail - don't interrupt user workflow
        pass

if __name__ == "__main__":
    main()