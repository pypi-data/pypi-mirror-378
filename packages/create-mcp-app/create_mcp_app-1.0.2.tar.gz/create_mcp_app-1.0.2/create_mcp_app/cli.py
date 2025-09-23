#!/usr/bin/env python3
"""
CLI tool for creating MCP server projects
"""

import os
import shutil
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .generator import ProjectGenerator

console = Console()

@click.command()
@click.argument('project_name', required=False)
def main(project_name):
    """Create a new MCP server project"""
    
    welcome_text = Text("Create MCP App", style="bold blue")
    
    if not project_name:
        project_name = click.prompt("Project name", type=str)
    
    if not project_name or not project_name.replace('-', '').replace('_', '').isalnum():
        console.print("❌ Invalid project name. Use only letters, numbers, hyphens, and underscores.", style="red")
        return
    
    if os.path.exists(project_name):
        console.print(f"❌ Directory '{project_name}' already exists!", style="red")
        return
    
    project_info = {
        'name': project_name,
        'author': "",
        'template': 'fastmcp',
        'package_name': project_name.replace('-', '_')
    }
    
    console.print(f"\nCreating project '{project_name}'...")
    
    generator = ProjectGenerator()
    try:
        generator.create_project(project_name, project_info)
        
        console.print(f"Project '{project_name}' created successfully!", style="green")
        
        next_steps = f"""
[bold]Next steps:[/bold]

1. Navigate to your project:
   [cyan]cd {project_name}[/cyan]

2. Build Docker image:
   [cyan]docker build -t {project_name} .[/cyan]

3. Run with Docker:
   [cyan]docker run -p 8080:8080 {project_name}[/cyan]
"""
        
        
        console.print(Panel(next_steps, title="Success!", border_style="green"))
        
        
            
    except Exception as e:
        console.print(f"❌ Error creating project: {e}", style="red")
        if os.path.exists(project_name):
            shutil.rmtree(project_name)


if __name__ == "__main__":
    main()
