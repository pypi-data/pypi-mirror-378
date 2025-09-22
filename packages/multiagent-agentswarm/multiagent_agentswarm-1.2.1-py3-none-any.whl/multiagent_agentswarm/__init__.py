"""Multi-Agent AgentSwarm

Agent orchestration and swarm management for multi-agent development.
"""

import json
from pathlib import Path

def _get_version():
    """Get version from VERSION file (semantic-release managed)"""
    try:
        version_file = Path(__file__).parent.parent.parent / "VERSION"
        if version_file.exists():
            with open(version_file, 'r') as f:
                version_data = json.load(f)
                return version_data.get("version", "1.12.0").lstrip('v')
    except:
        pass
    return "1.12.0"

__version__ = _get_version()
__author__ = "Multi-Agent Template Framework"

from .cli import main

__all__ = ["main"]