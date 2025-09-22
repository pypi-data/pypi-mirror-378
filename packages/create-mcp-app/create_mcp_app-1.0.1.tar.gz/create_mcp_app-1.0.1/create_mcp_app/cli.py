#!/usr/bin/env python3
"""
CLI tool for creating MCP server projects
"""

import os
import shutil
import click
import inquirer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .generator import ProjectGenerator

console = Console()

@click.command()
@click.argument('project_name', required=False)
@click.option('--no-install', is_flag=True, help='Skip installing dependencies')
@click.option('--no-git', is_flag=True, help='Skip git initialization')
def main(project_name, no_install, no_git):
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
    
    questions = [
        inquirer.Text('author', message="Author name", default=""),
    ]
    
    project_info = inquirer.prompt(questions)
    project_info.update({
        'name': project_name,
        'template': 'fastmcp',
        'package_name': project_name.replace('-', '_'),
        'include_docker': True,   
    })
    
    console.print(f"\nCreating project '{project_name}'...")
    
    generator = ProjectGenerator()
    try:
        generator.create_project(project_name, project_info)
        
        console.print(f"Project '{project_name}' created successfully!", style="green")
        
        next_steps = f"""
[bold]Next steps:[/bold]

1. Navigate to your project:
   [cyan]cd {project_name}[/cyan]

2. Set up virtual environment:
   [cyan]python -m venv venv[/cyan]
   [cyan]source venv/bin/activate[/cyan]  # On Windows: venv\\Scripts\\activate

3. Install dependencies:
   [cyan]pip install -r requirements.txt[/cyan]

4. Install your MCP server:
   [cyan]pip install -e .[/cyan]

5. Run your MCP server:
   [cyan]{project_info['package_name']}-mcp --transport stdio[/cyan]

6. For HTTP transport:
   [cyan]{project_info['package_name']}-mcp --transport streamable-http --port 8080[/cyan]
"""
        

        next_steps += """
7. Build Docker image:
   [cyan]docker build -t {project_name} .[/cyan]

8. Run with Docker:
   [cyan]docker run -p 8080:8080 {project_name}[/cyan]
""".format(project_name=project_name)
        
        console.print(Panel(next_steps, title="Success!", border_style="green"))
        
        if not no_install:
            install_deps = inquirer.confirm("Install dependencies now?", default=True)
            if install_deps:
                console.print("\nInstalling dependencies...")
                os.chdir(project_name)
                os.system("python -m venv venv")
                os.system("venv/bin/pip install -r requirements.txt")
                os.system("venv/bin/pip install -e .")
                console.print("✅ Dependencies installed!", style="green")
        
            
    except Exception as e:
        console.print(f"❌ Error creating project: {e}", style="red")
        if os.path.exists(project_name):
            shutil.rmtree(project_name)


if __name__ == "__main__":
    main()
