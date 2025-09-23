#!/usr/bin/env python3
"""
Project generator for MCP server projects
"""

import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any
from importlib import resources

class ProjectGenerator:
    def __init__(self):

        try:
            self.template_dir = resources.files('create_mcp_app') / 'templates'
        except (AttributeError, TypeError):
            import os
            self.template_dir = Path(__file__).parent / "templates"

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def create_project(self, project_name: str, project_info: Dict[str, Any]):
        """Create a new MCP project from template"""
        project_path = Path(project_name)
        project_path.mkdir(exist_ok=True)
        
        template_name = 'fastmcp'
        self._copy_template(template_name, project_path, project_info)
        
        package_name = project_info['package_name']
        package_dir = project_path / package_name
        package_dir.mkdir(exist_ok=True)
        
        self._generate_package_files(package_dir, project_info)
        
    
    def _copy_template(self, template_name: str, dest_path: Path, context: Dict[str, Any]):
        """Copy template files to destination"""
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            raise ValueError(f"Template '{template_name}' not found")
        
        for root, dirs, files in os.walk(template_path):
            rel_root = Path(root).relative_to(template_path)
            dest_root = dest_path / rel_root
            dest_root.mkdir(exist_ok=True)
            
            for file in files:
                src_file = Path(root) / file
                dest_file = dest_root / file
                

                if file.endswith('.j2'):
                    dest_file = dest_root / file[:-3] 
                    self._render_template_file(src_file, dest_file, context)
                else:
                    shutil.copy2(src_file, dest_file)
    
    def _render_template_file(self, src_file: Path, dest_file: Path, context: Dict[str, Any]):
        """Render a Jinja2 template file"""
        rel_path = src_file.relative_to(self.template_dir)
        template = self.jinja_env.get_template(str(rel_path))
        content = template.render(**context)
        
        with open(dest_file, 'w') as f:
            f.write(content)
    
    def _generate_package_files(self, package_dir: Path, context: Dict[str, Any]):
        """Generate package-specific files"""
        init_content = f'"""\n{context["name"]} - {context.get("description", "MCP Server")}\n"""\n\n__version__ = "1.0.0"\n'
        with open(package_dir / "__init__.py", 'w') as f:
            f.write(init_content)
        
        self._generate_fastmcp_app(package_dir, context)
    
    def _generate_fastmcp_app(self, package_dir: Path, context: Dict[str, Any]):
        """Generate comprehensive FastMCP app.py with examples"""
        app_content = f'''#!/usr/bin/env python3
"""
{context["name"]} MCP Server

{context.get("description", "MCP Server using FastMCP framework")}
"""

import argparse
import asyncio
import logging
import os
from typing import Dict, Any, List, Optional

import httpx
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("{context["name"]} MCP Server")


@mcp.tool()
async def echo_message(message: str) -> Dict[str, Any]:
    """
    Echo a message back with a timestamp.
    
    Args:
        message: The message to echo
    
    Returns:
        Dictionary with the echoed message and timestamp
    """
    import datetime
    
    logger.info(f"Echoing message: {{message}}")
    
    return {{
        "success": True,
        "echo": message,
        "timestamp": datetime.datetime.now().isoformat(),
        "message": f"Hello from {context['name']}! You said: {{message}}"
    }}

@mcp.tool()
async def get_server_info() -> Dict[str, Any]:
    """
    Get information about this MCP server.
    
    Returns:
        Server information including name and available tools
    """
    return {{
        "name": "{context['name']}",
        "version": "1.0.0",
        "description": "{context.get('description', '')}",
        "author": "{context.get('author', '')}",
        "framework": "FastMCP",
        "tools": [
            "echo_message",
            "get_server_info"
        ],
        "features": [
            "HTTP support",
            "Async/await support", 
            "Type hints",
            "Error handling",
            "Logging"
        ]
    }}


def main():
    """Main entry point for the MCP server"""
    parser = argparse.ArgumentParser(description="{context['name']} MCP Server")
    parser.add_argument("--host", default="localhost", help="Host for HTTP transport")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP transport")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting {context['name']} MCP Server...")

    logger.info(f"🌐 Host: {{args.host}}")
    logger.info(f"🔌 Port: {{args.port}}")
    logger.info(f"🔗 Server URL: http://{{args.host}}:{{args.port}}/mcp")
    mcp.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
'''
        
        with open(package_dir / "app.py", 'w') as f:
            f.write(app_content)
    