"""AgentSwarm CLI

Agent orchestration and swarm management commands.
"""

import click
import requests
import pkg_resources
from rich.console import Console
from pathlib import Path

console = Console()

@click.group()
def main():
    """AgentSwarm - Agent orchestration for multi-agent development"""
    # Check for updates on every command
    _check_for_updates()
    pass

@main.command()
@click.option("--spec", help="Spec directory or file to deploy")
@click.option("--agents", multiple=True, help="Specific agents to deploy (gemini, codex, qwen)")
def deploy(spec, agents):
    """Deploy agents to work on specs"""
    if not spec:
        spec = Path.cwd() / "specs"
    
    # Create AgentSwarm templates if they don't exist
    _create_agentswarm_templates()
    
    console.print(f"🚀 Deploying agents to work on: {spec}")
    
    if agents:
        for agent in agents:
            console.print(f"  🤖 Deploying @{agent}")
    else:
        console.print("  🤖 Deploying all available agents")

@main.command()
def status():
    """Show current swarm status"""
    console.print("📊 AgentSwarm Status:")
    console.print("  🤖 Active agents: 0")
    console.print("  📋 Active tasks: 0")
    console.print("  ⏳ Queue: empty")

@main.command()
def stop():
    """Stop all running agents"""
    console.print("🛑 Stopping all agents...")

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
    """Check for AgentSwarm updates"""
    try:
        current_version = pkg_resources.get_distribution('multiagent-agentswarm').version
        latest_version = _get_latest_version('multiagent-agentswarm')
        
        if latest_version and current_version != latest_version:
            console.print(f"[dim yellow]💡 Update available: multiagent-agentswarm {current_version} → {latest_version}[/dim yellow]")
            console.print(f"[dim yellow]   Run 'multiagent upgrade' to update all packages[/dim yellow]")
    except Exception:
        # Silently fail - don't interrupt user workflow
        pass

def _create_agentswarm_templates():
    """Create AgentSwarm-specific templates if they don't exist"""
    try:
        claude_dir = Path.cwd() / ".claude"
        claude_dir.mkdir(exist_ok=True)
        
        # Create AgentSwarm agent coordination file
        coordination_file = claude_dir / "agentswarm-agents.md"
        
        if not coordination_file.exists():
            agentswarm_content = """# AgentSwarm Orchestration

## Multi-Agent Coordination
- **@gemini**: Large context analysis, document review, architectural planning
- **@qwen**: Local CLI development, rapid prototyping, everyday coding tasks  
- **@codex**: Interactive development, real-time code conversion and assistance

## Parallel Agent Deployment
```bash
agentswarm deploy --spec ./specs/
agentswarm deploy --agents gemini,qwen,codex
agentswarm status
agentswarm stop
```

## Agent Coordination Patterns
- **Spec-based routing**: Agents auto-assign based on spec complexity
- **Parallel execution**: Multiple agents work simultaneously on different specs
- **Result aggregation**: Coordinated output from all active agents

## Agent Capabilities
### @gemini (Large Context)
- Document analysis up to 2M tokens
- Architectural planning and review
- Cross-repository analysis
- Complex requirement analysis

### @qwen (Local CLI)
- Rapid prototyping and iteration
- Local development tasks
- File system operations
- Quick code generation

### @codex (Interactive)
- Real-time code assistance
- Interactive debugging
- Code conversion between languages
- Live development support
"""
            
            coordination_file.write_text(agentswarm_content)
            console.print("[dim green]✓ AgentSwarm templates created[/dim green]")
    except Exception:
        # Silently fail - don't interrupt user workflow
        pass

if __name__ == "__main__":
    main()