#!/usr/bin/env python3
import subprocess

def main():
    """Main entry point for the CLI"""
    subprocess.run(["node", "dist/index.js"])

if __name__ == "__main__":
    main()
    
    def list_templates(self) -> List[str]:
        """List all available templates"""
        if not self.templates_path.exists():
            return []
        
        return [d.name for d in self.templates_path.iterdir() if d.is_dir()]
    
    def list_features(self) -> List[str]:
        """List all available features"""
        return list(self.features_config.get("features", {}).keys())
    
    def create_project(self, template: str, project_name: str, output_dir: str = ".") -> bool:
        """Create a new project from template"""
        template_path = self.templates_path / template
        
        if not template_path.exists():
            console.print(f"[red]Error: Template '{template}' not found![/red]")
            return False
        
        output_path = Path(output_dir) / project_name
        
        if output_path.exists():
            if not Confirm.ask(f"Directory '{project_name}' already exists. Overwrite?"):
                return False
            shutil.rmtree(output_path)
        
        try:
            console.print(f"[green]Creating project '{project_name}' from template '{template}'...[/green]")
            shutil.copytree(template_path, output_path)
            
            # Replace placeholders in files
            self._replace_placeholders(output_path, project_name)
            
            console.print(f"[green]✓ Project '{project_name}' created successfully![/green]")
            console.print(f"[blue]📁 Location: {output_path.absolute()}[/blue]")
            
            return True
        except Exception as e:
            console.print(f"[red]Error creating project: {e}[/red]")
            return False
    
    def add_feature(self, feature: str, project_path: str = ".", framework: str = None, language: str = "javascript") -> bool:
        """Add a feature to an existing project"""
        if feature not in self.features_config.get("features", {}):
            console.print(f"[red]Error: Feature '{feature}' not found![/red]")
            return False
        
        feature_config = self.features_config["features"][feature]
        
        # Auto-detect framework if not specified
        if not framework:
            framework = self._detect_framework(project_path)
            if not framework:
                console.print("[red]Could not detect framework. Please specify with --framework[/red]")
                return False
        
        # Check if framework is supported
        if framework not in feature_config.get("supportedFrameworks", []):
            console.print(f"[red]Feature '{feature}' is not supported for framework '{framework}'[/red]")
            supported = ", ".join(feature_config.get("supportedFrameworks", []))
            console.print(f"[yellow]Supported frameworks: {supported}[/yellow]")
            return False
        
        try:
            console.print(f"[green]Adding feature '{feature}' to project...[/green]")
            self._install_feature_files(feature, framework, language, project_path)
            console.print(f"[green]✓ Feature '{feature}' added successfully![/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error adding feature: {e}[/red]")
            return False
    
    def _detect_framework(self, project_path: str) -> Optional[str]:
        """Auto-detect the framework used in the project"""
        path = Path(project_path)
        
        # Check for package.json and common framework patterns
        package_json = path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    dependencies = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    
                    if "next" in dependencies:
                        return "nextjs"
                    elif "react" in dependencies and "express" in dependencies:
                        return "reactjs+expressjs+shadcn"
                    elif "react" in dependencies:
                        return "reactjs"
                    elif "@nestjs/core" in dependencies:
                        return "nestjs"
                    elif "express" in dependencies:
                        return "expressjs"
                    elif "@angular/core" in dependencies:
                        return "angularjs"
                    elif "vue" in dependencies:
                        return "vuejs"
            except:
                pass
        
        # Check for Python frameworks
        if (path / "manage.py").exists() or (path / "django").exists():
            return "django"
        elif (path / "app.py").exists() or (path / "wsgi.py").exists():
            return "flask"
        
        # Check for other frameworks
        if (path / "go.mod").exists():
            return "go"
        elif (path / "Cargo.toml").exists():
            return "rust"
        elif (path / "Gemfile").exists():
            return "ruby"
        
        return None
    
    def _install_feature_files(self, feature: str, framework: str, language: str, project_path: str):
        """Install feature files to the project"""
        feature_path = self.features_path / feature / framework
        
        if not feature_path.exists():
            raise Exception(f"Feature files not found for {feature}/{framework}")
        
        # Copy feature files to project
        for item in feature_path.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(feature_path)
                target_path = Path(project_path) / relative_path
                
                # Create directory if it doesn't exist
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Handle different file actions (create, append, prepend)
                if target_path.exists():
                    # For existing files, we might need to merge content
                    with open(item, 'r') as src:
                        content = src.read()
                    
                    if "package.json" in str(target_path):
                        self._merge_package_json(target_path, content)
                    else:
                        # For other files, append by default
                        with open(target_path, 'a') as target:
                            target.write("\n" + content)
                else:
                    shutil.copy2(item, target_path)
    
    def _merge_package_json(self, target_path: Path, new_content: str):
        """Merge package.json dependencies"""
        try:
            with open(target_path, 'r') as f:
                existing = json.load(f)
            
            new_data = json.loads(new_content)
            
            # Merge dependencies
            for dep_type in ["dependencies", "devDependencies"]:
                if dep_type in new_data:
                    if dep_type not in existing:
                        existing[dep_type] = {}
                    existing[dep_type].update(new_data[dep_type])
            
            with open(target_path, 'w') as f:
                json.dump(existing, f, indent=2)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not merge package.json: {e}[/yellow]")
    
    def _replace_placeholders(self, project_path: Path, project_name: str):
        """Replace placeholders in template files"""
        placeholders = {
            "{{PROJECT_NAME}}": project_name,
            "{{PROJECT_NAME_LOWER}}": project_name.lower(),
            "{{PROJECT_NAME_UPPER}}": project_name.upper(),
        }
        
        for file_path in project_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.js', '.ts', '.json', '.md', '.py', '.go', '.rs']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for placeholder, value in placeholders.items():
                        content = content.replace(placeholder, value)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                except:
                    # Skip binary or problematic files
                    pass
    
    def show_templates_table(self):
        """Display available templates in a table"""
        table = Table(title="Available Templates")
        table.add_column("Template", style="cyan")
        table.add_column("Description", style="green")
        
        templates = self.list_templates()
        template_descriptions = {
            "nextjs": "Next.js React framework with TypeScript",
            "reactjs": "React.js with modern tooling",
            "expressjs": "Express.js Node.js backend",
            "nestjs": "NestJS TypeScript backend framework",
            "django": "Django Python web framework",
            "flask": "Flask lightweight Python framework",
            "angularjs": "Angular TypeScript frontend",
            "vuejs": "Vue.js progressive framework",
            "go": "Go/Golang backend application",
            "rust": "Rust systems programming",
            "ruby": "Ruby on Rails web application",
            "react-native": "React Native mobile app",
            "reactjs-expressjs-shadcn": "Full-stack React + Express + shadcn/ui",
            "reactjs-nestjs-shadcn": "Full-stack React + NestJS + shadcn/ui",
        }
        
        for template in sorted(templates):
            description = template_descriptions.get(template, "Template for " + template)
            table.add_row(template, description)
        
        console.print(table)
    
    def show_features_table(self):
        """Display available features in a table"""
        table = Table(title="Available Features")
        table.add_column("Feature", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Supported Frameworks", style="yellow")
        
        for feature, config in self.features_config.get("features", {}).items():
            frameworks = ", ".join(config.get("supportedFrameworks", []))
            table.add_row(
                feature,
                config.get("description", f"{feature.title()} integration"),
                frameworks
            )
        
        console.print(table)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="@0xshariq/package-installer - Bootstrap projects with templates and features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create nextjs my-app
  %(prog)s add ai --framework nextjs
  %(prog)s list templates
  %(prog)s list features
        """
    )
    
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new project from template")
    create_parser.add_argument("template", help="Template name")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument("--output", "-o", default=".", help="Output directory (default: current)")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a feature to existing project")
    add_parser.add_argument("feature", help="Feature name")
    add_parser.add_argument("--framework", "-f", help="Target framework")
    add_parser.add_argument("--language", "-l", default="javascript", help="Programming language (default: javascript)")
    add_parser.add_argument("--path", "-p", default=".", help="Project path (default: current)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available templates or features")
    list_parser.add_argument("type", choices=["templates", "features"], help="What to list")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show information about a template or feature")
    info_parser.add_argument("name", help="Template or feature name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    installer = PackageInstaller()
    
    try:
        if args.command == "create":
            success = installer.create_project(args.template, args.name, args.output)
            sys.exit(0 if success else 1)
        
        elif args.command == "add":
            success = installer.add_feature(args.feature, args.path, args.framework, args.language)
            sys.exit(0 if success else 1)
        
        elif args.command == "list":
            if args.type == "templates":
                installer.show_templates_table()
            elif args.type == "features":
                installer.show_features_table()
        
        elif args.command == "info":
            # Show info about template or feature
            templates = installer.list_templates()
            features = installer.list_features()
            
            if args.name in templates:
                console.print(f"[green]Template: {args.name}[/green]")
                template_path = installer.templates_path / args.name
                console.print(f"[blue]Path: {template_path}[/blue]")
            elif args.name in features:
                console.print(f"[green]Feature: {args.name}[/green]")
                feature_config = installer.features_config["features"][args.name]
                console.print(f"[blue]Description: {feature_config.get('description', 'No description')}[/blue]")
                console.print(f"[blue]Supported frameworks: {', '.join(feature_config.get('supportedFrameworks', []))}[/blue]")
            else:
                console.print(f"[red]'{args.name}' not found in templates or features[/red]")
                sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
