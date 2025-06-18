#!/usr/bin/env python3
"""
Real AI Developer Tool v2.0 FINAL
Creator: Daniel Guzman
Purpose: Command-line interface for AI development system
SAVE AS: ai_developer.py
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime

# Import our agents
try:
    from mito_agent import MitoAgent
    from root_agent import RootAgent
    from integration_operator import IntegrationOperator
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

class RealAIDeveloper:
    """Command-line interface for Daniel Guzman's AI Empire"""
    
    def __init__(self):
        self.name = "Real AI Developer"
        self.version = "2.0 FINAL"
        self.agents_ready = AGENTS_AVAILABLE
        
        if self.agents_ready:
            self.mito = MitoAgent()
            self.root = RootAgent()
            self.integration = IntegrationOperator()
        
        print(f"{self.name} v{self.version}")
        print("Command-line interface for real AI development")
        
        if not self.agents_ready:
            print("Warning: Agent modules not found. Some features disabled.")
    
    async def create_project(self, name, project_type, description, output_dir=None):
        """Create a new project using AI agents"""
        
        if not self.agents_ready:
            print("Error: AI agents not available")
            return False
        
        print(f"Creating project: {name}")
        print(f"Type: {project_type}")
        print(f"Description: {description}")
        
        requirements = {
            "name": name,
            "type": project_type,
            "description": description
        }
        
        if output_dir:
            requirements["output_dir"] = output_dir
        
        try:
            result = await self.integration.execute_full_project(requirements)
            
            if result["status"] == "SUCCESS":
                print("Project created successfully!")
                print(f"Location: {result.get('project_path', 'Unknown')}")
                return True
            else:
                print(f"Project creation failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Error creating project: {e}")
            return False
    
    async def generate_code(self, description, language=None, output_file=None):
        """Generate code using MITO agent"""
        
        if not self.agents_ready:
            print("Error: MITO agent not available")
            return False
        
        print(f"Generating code: {description}")
        
        requirements = {
            "description": description,
            "type": "script"
        }
        
        if language:
            requirements["language"] = language
        
        try:
            result = await self.mito.generate_code(requirements)
            
            if result["status"] == "SUCCESS":
                print("Code generated successfully!")
                
                if output_file:
                    # Save to specific file
                    with open(output_file, 'w') as f:
                        f.write(str(result))
                    print(f"Saved to: {output_file}")
                else:
                    print("Generated files:")
                    for file in result.get("files_created", []):
                        print(f"  - {file}")
                
                return True
            else:
                print(f"Code generation failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Error generating code: {e}")
            return False
    
    async def design_architecture(self, name, description, project_type="web"):
        """Design system architecture using ROOT agent"""
        
        if not self.agents_ready:
            print("Error: ROOT agent not available")
            return False
        
        print(f"Designing architecture for: {name}")
        
        requirements = {
            "name": name,
            "description": description,
            "type": project_type
        }
        
        try:
            result = await self.root.design_architecture(requirements)
            
            if result["status"] == "SUCCESS":
                print("Architecture designed successfully!")
                print(f"Architecture files created in: {result['infrastructure']['project_path']}")
                return True
            else:
                print(f"Architecture design failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Error designing architecture: {e}")
            return False
    
    def list_projects(self, projects_dir="./projects"):
        """List all created projects"""
        
        print("Created Projects:")
        print("-" * 40)
        
        if not os.path.exists(projects_dir):
            print("No projects directory found")
            return
        
        projects = []
        for item in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, item)
            if os.path.isdir(project_path):
                projects.append(item)
        
        if not projects:
            print("No projects found")
        else:
            for i, project in enumerate(projects, 1):
                project_path = os.path.join(projects_dir, project)
                
                # Try to get project info
                manifest_path = os.path.join(project_path, "PROJECT_MANIFEST.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                        
                        created = manifest.get('created_at', 'Unknown')
                        description = manifest.get('description', 'No description')
                        
                        print(f"{i}. {project}")
                        print(f"   Created: {created}")
                        print(f"   Description: {description}")
                        print()
                        
                    except json.JSONDecodeError:
                        print(f"{i}. {project} (No manifest)")
                        print()
                else:
                    print(f"{i}. {project} (No manifest)")
                    print()
    
    async def status(self):
        """Check system status"""
        
        print("System Status:")
        print("-" * 40)
        
        if self.agents_ready:
            try:
                status = await self.integration.status_check()
                
                print(f"Integration Operator: {status['integration_operator']['status']}")
                print(f"MITO Agent: {status['mito_agent']['status']}")
                print(f"ROOT Agent: {status['root_agent']['status']}")
                print(f"GPT-4 Connected: {status['mito_agent'].get('gpt4_connected', False)}")
                print("All systems operational")
                
            except Exception as e:
                print(f"Error checking status: {e}")
        else:
            print("Agents not available - check installation")
    
    def interactive_mode(self):
        """Start interactive command mode"""
        
        print("Entering interactive mode...")
        print("Type 'help' for commands, 'exit' to quit")
        print()
        
        while True:
            try:
                command = input("AI Developer> ").strip()
                
                if command.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                elif command.lower() == 'help':
                    self._show_help()
                elif command.lower() == 'status':
                    asyncio.run(self.status())
                elif command.lower() == 'list':
                    self.list_projects()
                elif command.startswith('create '):
                    self._interactive_create(command)
                elif command.startswith('generate '):
                    self._interactive_generate(command)
                elif command.startswith('design '):
                    self._interactive_design(command)
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _show_help(self):
        """Show help information"""
        
        print("Available Commands:")
        print("-" * 40)
        print("help                    - Show this help")
        print("status                  - Check system status")
        print("list                    - List all projects")
        print("create <name>           - Create new project interactively")
        print("generate <description>  - Generate code")
        print("design <name>           - Design architecture")
        print("exit                    - Exit interactive mode")
        print()
    
    def _interactive_create(self, command):
        """Handle interactive project creation"""
        
        parts = command.split(' ', 1)
        if len(parts) < 2:
            print("Usage: create <project_name>")
            return
        
        name = parts[1]
        
        print(f"Creating project: {name}")
        
        # Get project type
        print("Project types: website, api, mobile, script, custom")
        project_type = input("Project type: ").strip() or "website"
        
        # Get description
        description = input("Project description: ").strip() or f"AI generated {project_type}"
        
        # Create project
        try:
            result = asyncio.run(self.create_project(name, project_type, description))
            if result:
                print("Project created successfully!")
            else:
                print("Project creation failed")
        except Exception as e:
            print(f"Error: {e}")
    
    def _interactive_generate(self, command):
        """Handle interactive code generation"""
        
        parts = command.split(' ', 1)
        if len(parts) < 2:
            print("Usage: generate <description>")
            return
        
        description = parts[1]
        
        # Optional language
        language = input("Programming language (optional): ").strip() or None
        
        # Optional output file
        output_file = input("Output file (optional): ").strip() or None
        
        try:
            result = asyncio.run(self.generate_code(description, language, output_file))
            if result:
                print("Code generated successfully!")
            else:
                print("Code generation failed")
        except Exception as e:
            print(f"Error: {e}")
    
    def _interactive_design(self, command):
        """Handle interactive architecture design"""
        
        parts = command.split(' ', 1)
        if len(parts) < 2:
            print("Usage: design <project_name>")
            return
        
        name = parts[1]
        
        # Get description
        description = input("System description: ").strip() or f"Architecture for {name}"
        
        # Get project type
        print("Architecture types: web, api, mobile, script")
        project_type = input("Architecture type: ").strip() or "web"
        
        try:
            result = asyncio.run(self.design_architecture(name, description, project_type))
            if result:
                print("Architecture designed successfully!")
            else:
                print("Architecture design failed")
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Real AI Developer - Daniel Guzman's AI Development System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ai_developer.py create "My Website" website "A modern responsive website"
  python ai_developer.py generate "Python script to process CSV files"
  python ai_developer.py design "E-commerce System" "Online shopping platform"
  python ai_developer.py status
  python ai_developer.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create project command
    create_parser = subparsers.add_parser('create', help='Create new project')
    create_parser.add_argument('name', help='Project name')
    create_parser.add_argument('type', help='Project type (website, api, mobile, script)')
    create_parser.add_argument('description', help='Project description')
    create_parser.add_argument('--output', help='Output directory')
    
    # Generate code command
    generate_parser = subparsers.add_parser('generate', help='Generate code')
    generate_parser.add_argument('description', help='Code description')
    generate_parser.add_argument('--language', help='Programming language')
    generate_parser.add_argument('--output', help='Output file')
    
    # Design architecture command
    design_parser = subparsers.add_parser('design', help='Design system architecture')
    design_parser.add_argument('name', help='System name')
    design_parser.add_argument('description', help='System description')
    design_parser.add_argument('--type', default='web', help='Architecture type')
    
    # Status command
    subparsers.add_parser('status', help='Check system status')
    
    # List projects command
    subparsers.add_parser('list', help='List all projects')
    
    # Interactive mode command
    subparsers.add_parser('interactive', help='Start interactive mode')
    
    args = parser.parse_args()
    
    # Create AI Developer instance
    ai_dev = RealAIDeveloper()
    
    if args.command == 'create':
        result = asyncio.run(ai_dev.create_project(
            args.name, args.type, args.description, args.output
        ))
        sys.exit(0 if result else 1)
        
    elif args.command == 'generate':
        result = asyncio.run(ai_dev.generate_code(
            args.description, args.language, args.output
        ))
        sys.exit(0 if result else 1)
        
    elif args.command == 'design':
        result = asyncio.run(ai_dev.design_architecture(
            args.name, args.description, args.type
        ))
        sys.exit(0 if result else 1)
        
    elif args.command == 'status':
        asyncio.run(ai_dev.status())
        
    elif args.command == 'list':
        ai_dev.list_projects()
        
    elif args.command == 'interactive':
        ai_dev.interactive_mode()
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()