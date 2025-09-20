#!/usr/bin/env python3
"""
Dars Exporter - Command line tool for exporting Dars applications
"""
import shutil
import subprocess
import venv
from rich.prompt import Confirm
from rich.syntax import Syntax
import argparse
import os
import sys
import time
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown
from rich import print as rprint
from importlib import resources

# Importar exportadores
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dars.core.app import App
from dars.exporters.web.html_css_js import HTMLCSSJSExporter
from dars.cli.translations import translator

console = Console()

class RichHelpFormatter(argparse.HelpFormatter):
    """Custom formatter for argparse help using Rich"""
    
    def __init__(self, prog, indent_increment=2, max_help_position=24, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)
        
    def format_help(self):
        # Call the original method to get the help text
        help_text = super().format_help()
        return help_text
        
    def add_text(self, text):
        # Override this method to prevent the epilog from being shown in the options section
        if text and (text.startswith('\nEjemplos de uso:') or text.startswith('\nUsage examples:')):
            return
        return super().add_text(text)

    def _format_action(self, action):
        # Check if this is the help action and replace its help message with the translated one
        if action.option_strings and ('-h' in action.option_strings or '--help' in action.option_strings):
            action.help = translator.get('help_arg_message')
        return super()._format_action(action)
    
    @classmethod
    def rich_print_help(cls, parser, console=console):
        # Get the standard help text
        help_text = parser.format_help()
        
        # Extract the main sections
        sections = {}
        current_section = None
        lines = help_text.split('\n')
        section_content = []
        
        for line in lines:
            if line and not line.startswith(' ') and line.endswith(':'):
                # It's a section header
                if current_section:
                    sections[current_section] = '\n'.join(section_content)
                current_section = line[:-1]  # Remove the colon
                section_content = []
            elif current_section:
                section_content.append(line)
        
        # Add the last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)
        
        # Show the program title
        prog_name = parser.prog
        description = parser.description
        
        # Main panel
        console.print(Panel(
            Text(prog_name, style="bold cyan", justify="center"),
            subtitle=translator.get('cli_subtitle'),
            border_style="cyan"
        ))
        
        # Check if there are examples in the epilog
        epilog_content = ""
        if parser.epilog:
            epilog_content = parser.epilog.strip()
        
        # Show each section with style
        for section, content in sections.items():
            if section == 'usage':
                # Usage section
                usage = content.strip()
                console.print(f"\n[bold cyan]{translator.get('usage')}:[/bold cyan]")
                console.print(Syntax(usage, "bash", theme="monokai", word_wrap=True))
            elif 'positional arguments' in section.lower():
                # Positional arguments
                console.print(f"\n[bold cyan]{translator.get('positional_arguments')}:[/bold cyan]")
                _print_arguments_table(content)
            elif 'optional arguments' in section.lower() or 'options' in section.lower():
                # Optional arguments
                console.print(f"\n[bold cyan]{translator.get('options')}:[/bold cyan]")
                _print_arguments_table(content)
            elif section.lower() == 'commands' or 'subcommands' in section.lower():
                # Subcommands
                console.print(f"\n[bold cyan]{translator.get('commands')}:[/bold cyan]")
                _print_arguments_table(content)
            elif 'examples' in section.lower() or section.lower() == 'epilog':
                # We don't process examples here to avoid duplication
                pass
            elif section.lower() != 'usage examples':
                # Other sections (skip 'usage examples' to avoid duplication)
                console.print(f"\n[bold cyan]{section.upper()}:[/bold cyan]")
                console.print(content.strip())
        
        # Always show examples at the end
        console.print(f"\n[bold cyan]{translator.get('examples')}:[/bold cyan]")
        # Get the actual examples from translations
        examples_text = translator.get('examples_text')
        examples = [line.strip() for line in examples_text.strip().split('\n') if line.strip()]
        
        examples_table = Table(box=None, expand=True, show_header=False, padding=(0, 1, 0, 1))
        examples_table.add_column("Example", overflow="fold")
        
        for example in examples:
            if example.strip():
                examples_table.add_row(Syntax(example.strip(), "bash", theme="monokai"))
        
        console.print(Panel(examples_table, border_style="cyan", padding=(1, 2)))

def _print_arguments_table(content):
    """Prints a table of arguments from the text content"""
    table = Table(show_header=False, box=None, padding=(0, 2, 0, 0), expand=True)
    table.add_column(translator.get('argument_column'), style="bold green", width=30, no_wrap=True)
    table.add_column(translator.get('description_column'), style="dim white", overflow="fold")
    
    lines = content.strip().split('\n')
    current_arg = None
    current_desc = []
    
    for line in lines:
        if line.strip():
            if not line.startswith('  '):
                # Es un nuevo argumento
                if current_arg:
                    # Estilizar el argumento
                    styled_arg = current_arg
                    if '-' in styled_arg:
                        # Resaltar las opciones cortas y largas
                        parts = styled_arg.split(', ')
                        styled_parts = []
                        for part in parts:
                            if part.startswith('--'):
                                styled_parts.append(f"[cyan]{part}[/cyan]")
                            elif part.startswith('-'):
                                styled_parts.append(f"[green]{part}[/green]")
                            else:
                                styled_parts.append(part)
                        styled_arg = ", ".join(styled_parts)
                    
                    table.add_row(styled_arg, '\n'.join(current_desc))
                
                parts = line.strip().split('  ', 1)
                current_arg = parts[0].strip()
                current_desc = [parts[1].strip()] if len(parts) > 1 else []
            else:
                # Es continuación de la descripción
                current_desc.append(line.strip())
    
    # Añadir el último argumento
    if current_arg:
        # Estilizar el último argumento
        styled_arg = current_arg
        if '-' in styled_arg:
            # Resaltar las opciones cortas y largas
            parts = styled_arg.split(', ')
            styled_parts = []
            for part in parts:
                if part.startswith('--'):
                    styled_parts.append(f"[cyan]{part}[/cyan]")
                elif part.startswith('-'):
                    styled_parts.append(f"[green]{part}[/green]")
                else:
                    styled_parts.append(part)
            styled_arg = ", ".join(styled_parts)
        
        table.add_row(styled_arg, '\n'.join(current_desc))
    
    console.print(table)

class DarsExporter:
    """Exportador principal de Dars"""
    
    def __init__(self):
        self.exporters = {
            'html': HTMLCSSJSExporter()
        }
        
    def load_app_from_file(self, file_path: str) -> Optional[App]:
        """Loads a Dars application from a Python file"""
        try:
            # Verify that the file exists
            if not os.path.exists(file_path):
                console.print(f"[red]{translator.get('error_file_not_exists')} {file_path}[/red]")
                return None
                
            # Add the application's root directory to sys.path
            file_dir = os.path.dirname(os.path.abspath(file_path))
            if file_dir not in sys.path:
                sys.path.insert(0, file_dir)
                
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location("user_app", file_path)
            if spec is None or spec.loader is None:
                console.print(f"[red]{translator.get('error_file_load')} {file_path}[/red]")
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for the 'app' variable in the module
            if hasattr(module, 'app') and isinstance(module.app, App):
                return module.app
            else:
                console.print(f"[red]{translator.get('error_no_app_var')} {file_path}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]{translator.get('error_loading_file')}: {e}[/red]")
            return None
            
    def validate_app(self, app: App) -> bool:
        """Validates a Dars application"""
        errors = app.validate()
        
        if errors:
            console.print(f"[red]{translator.get('validation_errors')}[/red]")
            for error in errors:
                console.print(f"  • {error}")
            return False
            
        return True
        
    def export_app(self, app: App, format_name: str, output_path: str, show_preview: bool = False) -> bool:
        """Exports an application to the specified format"""
        
        if format_name not in self.exporters:
            console.print(f"[red]{translator.get('error_format_not_supported')} '{format_name}'[/red]")
            self.show_supported_formats()
            return False
            
        exporter = self.exporters[format_name]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            # Validation task
            task1 = progress.add_task(translator.get('validating_app'), total=100)
            progress.update(task1, advance=30)
            
            if not self.validate_app(app):
                progress.update(task1, completed=100)
                return False
                
            progress.update(task1, advance=70)
            
            # Export task
            task2 = progress.add_task(f"{translator.get('exporting_to')} {format_name}...", total=100)
            progress.update(task2, advance=20)
            
            try:
                # En CLI 'dars export', generamos un bundle final (sin hot-reload dev)
                success = exporter.export(app, output_path, bundle=True)
                progress.update(task2, advance=80)
                
                if success:
                    progress.update(task1, completed=100)
                    progress.update(task2, completed=100)
                    
                    # Show success information
                    self.show_export_success(app, format_name, output_path)
                    
                    if show_preview and format_name == 'html':
                        self.show_preview_info(output_path)
                        
                    return True
                else:
                    console.print(f"[red]{translator.get('error_during_export')} {format_name}[/red]")
                    return False
                    
            except Exception as e:
                console.print(f"[red]{translator.get('error_during_export_exception')}: {e}[/red]")
                return False
                
    def show_supported_formats(self):
        """Shows supported formats"""
        table = Table(title=translator.get('supported_export_formats'))
        table.add_column(translator.get('format_name'), style="cyan")
        table.add_column(translator.get('format_description'), style="white")
        table.add_column(translator.get('html_description'), style="green")
        
        formats_info = {
            'html': ('HTML/CSS/JavaScript', 'Web'),
        }
        
        for format_name, (description, platform) in formats_info.items():
            table.add_row(format_name, description, platform)
            
        console.print(table)
        
    def show_export_success(self, app: App, format_name: str, output_path: str):
        """Shows export success information"""
        stats = app.get_stats()
        
        panel_content = f"""
[green]✓[/green] {translator.get('export_completed_successfully')}

[bold]{translator.get('application')}:[/bold] {app.title}
[bold]{translator.get('format')}:[/bold] {format_name}
[bold]{translator.get('output_directory')}:[/bold] {output_path}

[bold]{translator.get('statistics')}:[/bold]
• {translator.get('total_components')}: {stats['total_components']}
• {translator.get('total_pages')}: {stats.get('total_pages', 1)}
• {translator.get('max_depth')}: {stats['max_depth']}
• {translator.get('scripts')}: {stats['scripts_count']}
• {translator.get('global_styles')}: {stats['global_styles_count']}
"""
        
        console.print(Panel(panel_content, title=translator.get('export_successful'), border_style="green"))
        
    def show_preview_info(self, output_path: str):
        """Shows information about how to preview the application"""
        index_path = os.path.join(output_path, "index.html")
        
        if os.path.exists(index_path):
            console.print(f"\n[bold cyan]{translator.get('to_preview_app')}:[/bold cyan]")
            console.print(f"  {translator.get('open_in_browser')}: file://{os.path.abspath(index_path)}")
            console.print(f"  {translator.get('or_use')}: dars preview {output_path}")
            
    def show_app_info(self, app: App):
        """Shows detailed information about the application"""
        stats = app.get_stats()
        
        # Basic information
        info_table = Table(title=f"{translator.get('app_information')}: {app.title}")
        info_table.add_column(translator.get('property_column'), style="cyan")
        info_table.add_column(translator.get('value_column'), style="white")
        
        info_table.add_row(translator.get('title'), app.title)
        info_table.add_row(translator.get('total_components'), str(stats['total_components']))
        info_table.add_row(translator.get('max_depth'), str(stats['max_depth']))
        info_table.add_row(translator.get('scripts'), str(stats['scripts_count']))
        info_table.add_row(translator.get('global_styles'), str(stats['global_styles_count']))
        info_table.add_row(translator.get('theme'), app.config.get('theme', 'light'))
        
        console.print(info_table)
        
        # Component tree
        if app.root:
            console.print(f"\n[bold]{translator.get('component_structure')}:[/bold]")
            self.print_component_tree(app.root)
            
    def print_component_tree(self, component, level: int = 0):
        """Prints the component tree"""
        indent = "  " * level
        component_name = component.__class__.__name__
        component_id = f" (id: {component.id})" if component.id else ""
        
        console.print(f"{indent}├─ {component_name}{component_id}")
        
        for child in component.children:
            self.print_component_tree(child, level + 1)
    

    def init_project(self, name: str, template: Optional[str] = None):
        """Initializes a base Dars project, optionally using a template"""
        if os.path.exists(name):
            console.print(f"[red]❌ {translator.get('directory_exists').format(name=name)}[/red]")
            return

        # Create project directory
        os.makedirs(name)
        console.print(f"[green]✔ {translator.get('directory_created').format(name=name)}[/green]")

        if template:
            # Get template information
            templates = list_templates()
            if template not in templates:
                console.print(f"[red]❌ {translator.get('template_not_found').format(template=template)}[/red]")
                return
                
            template_info = templates[template]
            template_dir = template_info['template_dir']
            extra_files = template_info['extra_files']

            if not extra_files:
                console.print(f"[yellow]⚠ {translator.get('template_empty').format(template=template)}[/yellow]")
                return

            # Copy ALL files (no main_file anymore)
            for extra_file in extra_files:
                src_file = template_dir / extra_file
                dest_file = os.path.join(name, extra_file)
                
                # Create directories if needed
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                
                if src_file.exists():
                    shutil.copy2(src_file, dest_file)
                    console.print(f"[green]✔ {translator.get('extra_file_copied').format(file=extra_file)}[/green]")

            console.print(f"[green]✔ {translator.get('template_copied').format(template=template)}[/green]")
        else:
            # Default hello world code (sin template)
            HELLO_WORLD_CODE = """
from dars.all import *

app = App(title="Hello World", theme="dark")
# Crear componentes
container = Container(
    Text(
        text="Hello World",
        style={
            'font-size': '48px',
            'color': '#2c3e50',
            'margin-bottom': '20px',
            'font-weight': 'bold',
            'text-align': 'center'
        }
    ),
    Text(
        text="Hello World",
        style={
            'font-size': '20px',
            'color': '#7f8c8d',
            'margin-bottom': '40px',
            'text-align': 'center'
        }
    ),

    Button(
        text="Click Me!",
        on_click= dScript("alert('Hello World')"),
        on_mouse_enter=dScript("this.style.backgroundColor = '#2980b9';"),
        on_mouse_leave=dScript("this.style.backgroundColor = '#3498db';"),
        style={
            'background-color': '#3498db',
            'color': 'white',
            'padding': '15px 30px',
            'border': 'none',
            'border-radius': '8px',
            'font-size': '18px',
            'cursor': 'pointer',
            'transition': 'background-color 0.3s'
        }
    ),
    style={
        'display': 'flex',
        'flex-direction': 'column',
        'align-items': 'center',
        'justify-content': 'center',
        'min-height': '100vh',
        'background-color': '#f0f2f5',
        'font-family': 'Arial, sans-serif'
    }
) 

app.set_root(container)

if __name__ == "__main__":
    app.rTimeCompile()
"""
            main_py = Path(name) / "main.py"
            main_py.write_text(HELLO_WORLD_CODE.strip(), encoding="utf-8")
            console.print(f"[green]✔ {translator.get('main_py_created')}[/green]")

        # Final instructions
        console.print(f"\n[bold cyan]🎉 {translator.get('project_initialized')}[/bold cyan]")
        console.print(Syntax(f"cd {name}", "bash"))
        console.print(Syntax(f"\n{translator.get('export_command')}:", "bash"))
        console.print(Syntax(f"dars export (python file) --format html --output build", "bash"))
        console.print(Syntax(f"\n{translator.get('preview_command')}:", "bash"))
        console.print(Syntax(f"python (python file)", "bash"))

def print_version_info():
    import importlib.util
    import os
    from rich.panel import Panel
    from rich.console import Console
    console = Console()
    version_path = os.path.join(os.path.dirname(__file__), '../version.py')
    spec = importlib.util.spec_from_file_location("dars.version", version_path)
    version_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_mod)
    version = getattr(version_mod, "__version__", "unknown")
    release_url = getattr(version_mod, "__release_url__", "https://github.com/ZtaMDev/Dars-Framework/releases")
    panel_content = f"[bold cyan]Dars Framework[/bold cyan]\n\n[green]Version:[/green] {version}\n[green]Release notes:[/green] [link={release_url}]{release_url}[/link]"
    console.print(Panel(panel_content, title="Dars Version", border_style="cyan"))

def create_parser() -> argparse.ArgumentParser:
    """Creates the command line argument parser"""
    parser = argparse.ArgumentParser(
        description=translator.get('main_description'),
        formatter_class=RichHelpFormatter,
        epilog=""  # Remove epilog to avoid duplication
    )
    parser.add_argument('-v', '--version', action='store_true', help='Show Dars version and release link')
    
    # Add language parameter to the main parser
    parser.add_argument('--lang', '-l', choices=['en', 'es'], default='en',
                      help=translator.get('lang_help'))
    
    subparsers = parser.add_subparsers(dest='command', help=translator.get('available_commands'))
    
    # Export command
    export_parser = subparsers.add_parser('export', help=translator.get('export_help'))
    export_parser.add_argument('file', help=translator.get('file_help'))

    # --format opcional (default: html)
    export_parser.add_argument(
        '--format', '-f',
        choices=["html"],
        default="html",
        help=translator.get('format_help') + " (default: html)"
    )

    # --output opcional (default: ./dist)
    export_parser.add_argument(
        '--output', '-o',
        default="./dist",
        help=translator.get('output_help') + " (default: ./dist)"
    )

    export_parser.add_argument('--preview', '-p', action='store_true',
                            help=translator.get('preview_help'))

    
    # Info command
    info_parser = subparsers.add_parser('info', help=translator.get('info_help'))
    info_parser.add_argument('file', help=translator.get('file_help'))
    
    # Formats command
    formats_parser = subparsers.add_parser('formats', help=translator.get('formats_help'))
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help=translator.get('preview_cmd_help'))
    preview_parser.add_argument('path', help=translator.get('path_help'))
    
    init_parser = subparsers.add_parser('init', help=translator.get('init_help'))
    init_parser.add_argument('name', nargs='?', help=translator.get('name_help'))
    init_parser.add_argument(
        '--list-templates', '-L',  # Cambia -l por -L
        action='store_true',
        help=translator.get('list_templates_help')
    )
    init_parser.add_argument(
        '--template', '-t',
        help=translator.get('template_help')
    )
    # Add language option to all subparsers
    for subparser in [export_parser, info_parser, formats_parser, preview_parser, init_parser]:
        subparser.add_argument('--lang', '-l', choices=['en', 'es'], default='en',
                              help=translator.get('lang_help'))
    
    return parser

from pathlib import Path
from typing import Dict

from pathlib import Path
from typing import Dict

from pathlib import Path
from typing import Dict

from pathlib import Path
from typing import Dict

from pathlib import Path
from typing import Dict

from pathlib import Path
from typing import Dict

def list_templates(debug: bool = False) -> Dict[str, Dict]:
    """
    Descubre templates:
    - ignora dirs en IGNORED_DIRS (ej: __pycache__, .git, node_modules)
    - ignora extensiones compiladas ('.pyc', '.pyo', '.pyd')
    - ignora solo archivos ocultos que empiezan con '.' (ej: .env)
    - incluye TODOS los demás archivos ('.py', '.md', '.png', '.json', etc.)
    - salida determinista (ordenada)
    """
    current_file = Path(__file__).resolve()
    templates_base = current_file.parent.parent / "templates" / "examples"

    if not templates_base.exists():
        # usa console.print si tienes rich.console; aquí dejo print para compatibilidad
        print(f"[red]Error: Template directory not found: {templates_base}[/red]")
        return {}

    IGNORED_DIRS = {'__pycache__', '.git', '.venv', 'node_modules', '.pytest_cache'}
    IGNORE_EXTS = {'.pyc', '.pyo', '.pyd'}

    templates: Dict[str, Dict] = {}

    for category_dir in sorted(templates_base.iterdir()):
        if not (category_dir.is_dir() and not category_dir.name.startswith('__')):
            continue

        for template_dir in sorted(category_dir.iterdir()):
            if not (template_dir.is_dir() and not template_dir.name.startswith('__')):
                continue

            found_files = []
            for file_path in sorted(template_dir.rglob('*')):
                # 1) archivo
                if not file_path.is_file():
                    if debug: print(f"SKIP (not file): {file_path}")
                    continue

                # 2) si alguna parte del path es una carpeta ignorada
                intersect = set(file_path.parts) & IGNORED_DIRS
                if intersect:
                    if debug: print(f"SKIP (ignored dir {intersect}): {file_path}")
                    continue

                # 3) extensiones compiladas
                if file_path.suffix.lower() in IGNORE_EXTS:
                    if debug: print(f"SKIP (ignored ext): {file_path}")
                    continue

                # 4) solo ocultos que empiezan con '.' (por ejemplo .gitignore, .env)
                if file_path.name.startswith('.'):
                    if debug: print(f"SKIP (hidden file): {file_path}")
                    continue

                # si pasó todos los filtros, lo guardamos (ruta relativa al template)
                rel = str(file_path.relative_to(template_dir))
                if debug: print(f"INCLUDE: {rel}")
                found_files.append(rel)

            found_files = sorted(found_files)

            template_key = f"{category_dir.name}/{template_dir.name}"
            templates[template_key] = {
                'main_file': None,            # ya no usamos main_file
                'extra_files': found_files,
                'category': category_dir.name,
                'template_dir': template_dir,
                'all_files': found_files
            }

    return templates



                    
def list_templates_detailed():
    """Muestra información detallada de los templates disponibles"""
    templates = list_templates()
    
    if not templates:
        console.print("[yellow]No templates found[/yellow]")
        return
    
    table = Table(title="Available Templates")
    table.add_column("Template", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Extra Files", style="white")
    table.add_column("Description", style="dim")
    
    for template_name, template_info in templates.items():
        extra_files = ", ".join(template_info['extra_files']) if template_info['extra_files'] else "None"
        table.add_row(
            template_name,
            template_info['category'],
            extra_files,
            f"Template with {len(template_info['extra_files'])} extra files"
        )
    
    console.print(table)
def main():
    """Main CLI function"""
    # Check for language parameter before parsing arguments
    # If --lang is not specified, it will use the saved preference or default to English
    for i, arg in enumerate(sys.argv):
        if arg in ['--lang', '-l'] and i + 1 < len(sys.argv):
            lang = sys.argv[i + 1]
            if lang in ['en', 'es']:
                # Save the language preference when explicitly specified
                translator.set_language(lang, save=True)
    
    # Intercept help before parsing arguments
    if len(sys.argv) == 1 or '-h' in sys.argv or '--help' in sys.argv:
        parser = create_parser()
        
        # Show banner
        console.print(Panel(
            Text("Dars Exporter", style="bold cyan", justify="center"),
            subtitle=translator.get('main_description'),
            border_style="cyan"
        ))
        
        # If it's general help
        if len(sys.argv) == 1 or (len(sys.argv) == 2 and (sys.argv[1] == '-h' or sys.argv[1] == '--help')):
            RichHelpFormatter.rich_print_help(parser)
            return
        
        # If it's help for a subcommand
        if len(sys.argv) > 2 and (sys.argv[2] == '-h' or sys.argv[2] == '--help'):
            subcommand = sys.argv[1]
            # Get the corresponding subparser
            subparsers_actions = [action for action in parser._actions 
                                if isinstance(action, argparse._SubParsersAction)]
            for subparsers_action in subparsers_actions:
                for choice, subparser in subparsers_action.choices.items():
                    if choice == subcommand:
                        RichHelpFormatter.rich_print_help(subparser)
                        return
    
    # Continue with normal flow if not help
    parser = create_parser()
    args = parser.parse_args()
    
    # Set language from args only if explicitly provided
    # This is already handled in the pre-parsing step above, so we don't need to do it again
    # The translator will already have the correct language set
    
    # Show version and exit if -v/--version is passed
    if getattr(args, 'version', False):
        print_version_info()
        sys.exit(0)

    # Show banner for normal commands
    console.print(Panel(
        Text("Dars Exporter", style="bold cyan", justify="center"),
        subtitle=translator.get('cli_subtitle'),
        border_style="cyan"
    ))
    
    exporter = DarsExporter()
    
    if args.command == 'export':
        # Load application
        app = exporter.load_app_from_file(args.file)
        if app is None:
            sys.exit(1)
            
        # Export
        success = exporter.export_app(app, args.format, args.output, args.preview)
        sys.exit(0 if success else 1)
        
    elif args.command == 'info':
        # Show information
        app = exporter.load_app_from_file(args.file)
        if app is None:
            sys.exit(1)
            
        exporter.show_app_info(app)
        
    elif args.command == 'formats':
        # Show formats
        exporter.show_supported_formats()
    
    elif args.command == 'init':
        if args.list_templates:
            list_templates_detailed()
        elif not args.name:
            console.print("[red]Error: Project name is required[/red]")
            parser.parse_args(['init', '--help'])
        else:
            exporter.init_project(args.name, template=args.template)

        
    elif args.command == 'preview':
        index_path = os.path.join(args.path, "index.html")
        if os.path.exists(index_path):
            console.print(f"[green]{translator.get('app_found')}: {args.path} [/green]")
            console.print(f"{translator.get('open_in_browser')}: file://{os.path.abspath(index_path)}")
            console.print(f"{translator.get('view_preview')} [green]y[/green] / [red]n[/red] [y/n] ")
            if input().lower() == 'y':
                # Pass the current language to preview.py
                
                import subprocess
                process = None
                try:
                    process = subprocess.Popen([sys.executable, '-m', 'dars.cli.preview', args.path])
                    process.wait()
                except KeyboardInterrupt:
                    if process:
                        process.terminate()
                        process.wait()
                finally:
                    if process and process.poll() is None:
                        process.terminate()
                        process.wait()
        else:
            console.print(f"[red]{translator.get('index_not_found')} {args.path}[/red]")

            
    else:
        # Usar nuestro formateador personalizado en lugar del estándar
        RichHelpFormatter.rich_print_help(parser)

if __name__ == "__main__":
    main()

