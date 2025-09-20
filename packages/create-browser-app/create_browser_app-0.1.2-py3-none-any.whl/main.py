#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
import shutil

console = Console()

TEMPLATE_BASIC = '''from stagehand import Stagehand
import asyncio

async def main():
    """Basic Stagehand browser automation example."""
    async with Stagehand() as stagehand:
        page = stagehand.page

        # Navigate to a website
        await page.goto("https://example.com")

        # Your automation code here
        print(f"Page title: {await page.title()}")

if __name__ == "__main__":
    asyncio.run(main())
'''

TEMPLATE_REQUIREMENTS = '''stagehand
python-dotenv
'''

TEMPLATE_ENV = '''# Add your environment variables here
# BROWSERBASE_API_KEY=your_api_key_here
# BROWSERBASE_PROJECT_ID=your_project_id_here
'''

TEMPLATE_README = '''# {project_name}

A Stagehand browser automation project.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your environment variables in `.env`:
```bash
BROWSERBASE_API_KEY=your_api_key_here
BROWSERBASE_PROJECT_ID=your_project_id_here
```

3. Run the project:
```bash
python main.py
```

## About Stagehand

Stagehand is a Python library for browser automation built on Playwright. Learn more at:
- [Stagehand Documentation](https://github.com/browserbase/stagehand)
- [Browserbase](https://browserbase.com)
'''

TEMPLATE_GITIGNORE = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/
.venv

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Logs
*.log
'''

@click.command()
@click.argument('name', default='my-stagehand-app', required=False)
@click.option('--template', '-t', default='basic', help='Template to get started with')
def main(name, template):
    """Start your Stagehand project with a single command"""

    console.print("""[yellow]
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡾⠻⣶⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢠⡶⠛⢳⡆⠀⠀⠀⠀⢸⡇⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⢸⣷⠶⣦⣴⠶⣾⡇⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⢸⡇⠀⢸⡇⠀⢸⡇⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠘⠷⣤⢾⡏⠉⠉⠉⠙⣾⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠈⣻⡿⠟⠂⠀⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⣷⠀⠀⠀⠀⢰⡏⠀⠀⠀⢀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣷⡀⠀⠀⠀⠀⠀⠀⢀⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠷⣦⣤⣤⣴⠾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    [/yellow]""")
    console.print("[yellow]Stagehand[/yellow]")
    console.print("[dim]The AI Browser Framework[/dim]\n")

    project_name = name

    # Sanitize project name for directory
    project_dir = project_name.lower().replace(" ", "-").replace("_", "-")
    project_path = Path.cwd() / project_dir

    # Check if directory exists
    if project_path.exists():
        console.print(f"[red]Error: Directory '{project_dir}' already exists[/red]")
        sys.exit(1)

    # Create project structure
    try:
        console.print(f"Creating [bold cyan]{project_dir}[/bold cyan]...\n")

        # Create directories
        project_path.mkdir(parents=True, exist_ok=True)

        # Create main.py
        main_file = project_path / "main.py"
        main_file.write_text(TEMPLATE_BASIC)

        # Create requirements.txt
        requirements_file = project_path / "requirements.txt"
        requirements_file.write_text(TEMPLATE_REQUIREMENTS)

        # Create .env.example
        env_file = project_path / ".env.example"
        env_file.write_text(TEMPLATE_ENV)

        # Create README.md
        readme_file = project_path / "README.md"
        readme_file.write_text(TEMPLATE_README.format(project_name=project_name))

        # Create .gitignore
        gitignore_file = project_path / ".gitignore"
        gitignore_file.write_text(TEMPLATE_GITIGNORE)

        # Success message
        console.print(f"[green]✓[/green] Find your project at [cyan]{project_path}[/cyan]\n")

        # Styled next steps
        console.print(Panel(
            f"[bold cyan]1.[/bold cyan] cd {project_dir}\n"
            f"[bold cyan]2.[/bold cyan] pip install -r requirements.txt\n"
            f"[bold cyan]3.[/bold cyan] cp .env.example .env\n"
            f"[bold cyan]4.[/bold cyan] [dim]Add your Browserbase API key to .env[/dim]\n"
            f"[bold cyan]5.[/bold cyan] python main.py",
            title="[bold yellow]🚀 Launch now 🚀[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        ))

    except Exception as e:
        console.print(f"[red]Error creating project: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()