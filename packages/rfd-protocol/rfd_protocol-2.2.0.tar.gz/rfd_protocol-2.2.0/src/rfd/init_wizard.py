"""
Enhanced Initialization Wizard for RFD
Supports NEW and EXISTING projects with comprehensive spec generation
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import questionary
import frontmatter
from datetime import datetime

from .spec_generator import SpecGenerator

class InitWizard:
    """Interactive initialization wizard for RFD projects"""
    
    def __init__(self, rfd):
        self.rfd = rfd
        self.spec_generator = SpecGenerator(rfd)
        
    def run(self) -> bool:
        """Run the initialization wizard"""
        print("\n🚀 RFD Protocol Initialization Wizard\n")
        
        # Check if project already has RFD
        if Path('PROJECT.md').exists():
            if not questionary.confirm("PROJECT.md exists. Reinitialize?").ask():
                return self.enhance_existing()
        
        # Determine project type
        project_type = questionary.select(
            "Project type:",
            choices=[
                "New project (Greenfield)",
                "Existing project (Brownfield)",
                "Research/Exploration project",
                "Import from PRD document"
            ]
        ).ask()
        
        if project_type == "New project (Greenfield)":
            return self.init_new_project("0-to-1")
        elif project_type == "Existing project (Brownfield)":
            return self.init_existing_project()
        elif project_type == "Research/Exploration project":
            return self.init_new_project("exploration")
        elif project_type == "Import from PRD document":
            return self.init_from_prd()
        
        return False
    
    def init_new_project(self, development_mode: str = "0-to-1") -> bool:
        """Initialize a new greenfield project"""
        print("\n📋 New Project Setup\n")
        
        project_info = self.collect_project_info()
        
        # Ask about comprehensive spec generation
        generate_full = questionary.confirm(
            "Generate comprehensive specifications? (Constitution, Phases, API contracts, Guidelines)",
            default=True
        ).ask()
        
        if generate_full:
            print("\n🔨 Generating comprehensive specifications...\n")
            generated = self.spec_generator.generate_full_specification(
                project_info, 
                development_mode
            )
            
            print("✅ Generated specifications:")
            for name, path in generated.items():
                print(f"   - {path}")
        
        # Create base RFD files
        self.create_base_files(project_info)
        
        # Initialize git if needed
        if not Path('.git').exists():
            if questionary.confirm("Initialize git repository?").ask():
                subprocess.run(['git', 'init'])
                self.create_gitignore()
        
        print("\n✅ RFD Protocol initialized successfully!")
        print("\n→ Next steps:")
        print("   1. Review generated specifications in specs/")
        print("   2. Customize PROJECT.md as needed")
        print("   3. Run: rfd session start <first-feature>")
        
        return True
    
    def init_existing_project(self) -> bool:
        """Initialize RFD for an existing project"""
        print("\n🔍 Analyzing existing project...\n")
        
        # Detect project characteristics
        detected = self.detect_project_characteristics()
        
        print("Detected:")
        print(f"   Language: {detected['language']}")
        print(f"   Framework: {detected['framework']}")
        print(f"   Files: {detected['file_count']}")
        
        # Collect additional info
        project_info = self.collect_project_info(defaults=detected)
        
        # Analyze existing code
        if questionary.confirm("Analyze codebase to extract features?").ask():
            features = self.extract_features_from_code()
            project_info['features'] = features
        
        # Generate specs for brownfield
        if questionary.confirm("Generate modernization plan?").ask():
            print("\n🔄 Generating modernization specifications...\n")
            generated = self.spec_generator.generate_full_specification(
                project_info,
                development_mode="brownfield"
            )
            
            print("✅ Generated modernization plan:")
            for name, path in generated.items():
                print(f"   - {path}")
        
        # Create RFD files
        self.create_base_files(project_info)
        
        print("\n✅ RFD Protocol added to existing project!")
        print("\n→ Next steps:")
        print("   1. Review detected features in PROJECT.md")
        print("   2. Add missing features and acceptance criteria")
        print("   3. Run: rfd validate to check current state")
        
        return True
    
    def init_from_prd(self) -> bool:
        """Initialize from a PRD document"""
        print("\n📄 Import from PRD\n")
        
        prd_path = questionary.path(
            "Path to PRD document:",
            validate=lambda x: Path(x).exists()
        ).ask()
        
        print("\n📖 Parsing PRD document...\n")
        project_info = self.spec_generator.ingest_prd(Path(prd_path))
        
        # Show extracted info
        print("Extracted from PRD:")
        print(f"   Name: {project_info.get('name', 'Not found')}")
        print(f"   Goals: {len(project_info.get('goals', []))} found")
        print(f"   Requirements: {len(project_info.get('requirements', []))} found")
        
        # Allow editing
        if questionary.confirm("Edit extracted information?").ask():
            project_info = self.collect_project_info(defaults=project_info)
        
        # Generate full specs
        print("\n📝 Generating project specifications...\n")
        generated = self.spec_generator.generate_full_specification(project_info)
        
        print("✅ Generated specifications:")
        for name, path in generated.items():
            print(f"   - {path}")
        
        # Create base files
        self.create_base_files(project_info)
        
        print("\n✅ Project initialized from PRD!")
        print("\n→ Next steps:")
        print("   1. Review and refine generated specs")
        print("   2. Validate tech stack decisions")
        print("   3. Begin implementation with first phase")
        
        return True
    
    def enhance_existing(self) -> bool:
        """Enhance an existing RFD project with new features"""
        print("\n⚡ Enhance Existing RFD Project\n")
        
        enhancements = questionary.checkbox(
            "Select enhancements:",
            choices=[
                "Generate project constitution",
                "Create phase breakdown",
                "Generate API contracts",
                "Create development guidelines",
                "Add architecture decision records",
                "Update tech stack configuration",
                "Generate test specifications"
            ]
        ).ask()
        
        # Load existing PROJECT.md
        with open('PROJECT.md', 'r') as f:
            post = frontmatter.load(f)
        
        project_info = {
            'name': post.metadata.get('name', 'Project'),
            'description': post.metadata.get('description', ''),
            'requirements': [f['description'] for f in post.metadata.get('features', [])],
            'goals': post.metadata.get('goals', []),
            'constraints': post.metadata.get('constraints', [])
        }
        
        specs_created = []
        
        if "Generate project constitution" in enhancements:
            constitution = self.spec_generator.generate_project_constitution(project_info)
            path = Path('specs/CONSTITUTION.md')
            path.parent.mkdir(exist_ok=True)
            path.write_text(constitution)
            specs_created.append(path)
        
        if "Create phase breakdown" in enhancements:
            mode = questionary.select(
                "Development mode:",
                choices=["0-to-1", "exploration", "brownfield"]
            ).ask()
            phases = self.spec_generator.generate_phase_breakdown(project_info, mode)
            doc = self.spec_generator._format_phases_document(phases)
            path = Path('specs/PHASES.md')
            path.write_text(doc)
            specs_created.append(path)
        
        if "Generate API contracts" in enhancements:
            endpoints = self.spec_generator.generate_api_contracts(project_info)
            doc = self.spec_generator._format_api_document(endpoints)
            path = Path('specs/API_CONTRACT.md')
            path.write_text(doc)
            specs_created.append(path)
        
        if specs_created:
            print("\n✅ Enhanced with:")
            for path in specs_created:
                print(f"   - {path}")
        
        return True
    
    def collect_project_info(self, defaults: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Collect project information interactively"""
        if defaults is None:
            defaults = {}
        
        info = {}
        
        # Basic info
        info['name'] = questionary.text(
            "Project name:",
            default=defaults.get('name', Path.cwd().name)
        ).ask()
        
        info['description'] = questionary.text(
            "Project description (one line):",
            default=defaults.get('description', '')
        ).ask()
        
        # Goals
        goals = []
        print("\nProject goals (empty to finish):")
        while len(goals) < 5:
            goal = questionary.text(f"Goal {len(goals) + 1}:").ask()
            if not goal:
                break
            goals.append(goal)
        info['goals'] = goals
        
        # Requirements  
        requirements = []
        print("\nKey requirements (empty to finish):")
        while len(requirements) < 10:
            req = questionary.text(f"Requirement {len(requirements) + 1}:").ask()
            if not req:
                break
            requirements.append(req)
        info['requirements'] = requirements
        
        # Users
        users = []
        print("\nTarget users (empty to finish):")
        while len(users) < 3:
            user = questionary.text(f"User type {len(users) + 1}:").ask()
            if not user:
                break
            users.append(user)
        info['users'] = users if users else ['End users']
        
        # Constraints
        constraints = []
        if questionary.confirm("Add constraints?").ask():
            print("\nProject constraints (empty to finish):")
            while len(constraints) < 5:
                constraint = questionary.text(f"Constraint {len(constraints) + 1}:").ask()
                if not constraint:
                    break
                constraints.append(constraint)
        info['constraints'] = constraints
        
        # Success metrics
        metrics = []
        if questionary.confirm("Define success metrics?").ask():
            print("\nSuccess metrics (empty to finish):")
            while len(metrics) < 5:
                metric = questionary.text(f"Metric {len(metrics) + 1}:").ask()
                if not metric:
                    break
                metrics.append(metric)
        info['success_metrics'] = metrics
        
        # Features
        features = []
        print("\nInitial features (at least 1, max 3 for v1):")
        while len(features) < 3:
            if features and not questionary.confirm(f"Add feature {len(features) + 1}?").ask():
                break
            
            feature = {
                'id': questionary.text("Feature ID (e.g., user_auth):").ask(),
                'description': questionary.text("Description:").ask(),
                'acceptance': questionary.text("Acceptance criteria:").ask(),
                'status': 'pending'
            }
            features.append(feature)
        info['features'] = features
        
        return info
    
    def detect_project_characteristics(self) -> Dict[str, Any]:
        """Detect characteristics of existing project"""
        detected = {
            'language': None,
            'framework': None,
            'database': None,
            'file_count': 0
        }
        
        # Detect by file extensions
        py_files = list(Path('.').rglob('*.py'))
        js_files = list(Path('.').rglob('*.js')) + list(Path('.').rglob('*.ts'))
        go_files = list(Path('.').rglob('*.go'))
        rust_files = list(Path('.').rglob('*.rs'))
        
        if py_files:
            detected['language'] = 'python'
            detected['file_count'] = len(py_files)
            
            # Detect Python framework
            if Path('manage.py').exists():
                detected['framework'] = 'django'
            elif any('fastapi' in str(f) for f in py_files):
                detected['framework'] = 'fastapi'
            elif any('flask' in str(f) for f in py_files):
                detected['framework'] = 'flask'
                
        elif js_files:
            detected['language'] = 'javascript'
            detected['file_count'] = len(js_files)
            
            # Check package.json
            if Path('package.json').exists():
                import json
                with open('package.json') as f:
                    pkg = json.load(f)
                    deps = pkg.get('dependencies', {})
                    
                    if 'express' in deps:
                        detected['framework'] = 'express'
                    elif '@nestjs/core' in deps:
                        detected['framework'] = 'nestjs'
                    elif 'next' in deps:
                        detected['framework'] = 'nextjs'
                        
        elif go_files:
            detected['language'] = 'go'
            detected['file_count'] = len(go_files)
            
            # Check go.mod
            if Path('go.mod').exists():
                with open('go.mod') as f:
                    content = f.read()
                    if 'gin-gonic/gin' in content:
                        detected['framework'] = 'gin'
                    elif 'echo' in content:
                        detected['framework'] = 'echo'
                        
        elif rust_files:
            detected['language'] = 'rust'
            detected['file_count'] = len(rust_files)
            
            # Check Cargo.toml
            if Path('Cargo.toml').exists():
                with open('Cargo.toml') as f:
                    content = f.read()
                    if 'actix-web' in content:
                        detected['framework'] = 'actix'
                    elif 'rocket' in content:
                        detected['framework'] = 'rocket'
        
        # Detect database
        if Path('docker-compose.yml').exists():
            with open('docker-compose.yml') as f:
                content = f.read().lower()
                if 'postgres' in content:
                    detected['database'] = 'postgresql'
                elif 'mysql' in content:
                    detected['database'] = 'mysql'
                elif 'mongo' in content:
                    detected['database'] = 'mongodb'
        
        if not detected['database']:
            if Path('.').glob('*.db') or Path('.').glob('*.sqlite'):
                detected['database'] = 'sqlite'
        
        return detected
    
    def extract_features_from_code(self) -> list:
        """Extract potential features from existing code"""
        features = []
        
        # Look for route definitions, class names, etc
        # This is a simplified version - could be enhanced with AST parsing
        
        route_patterns = [
            r'@app\.route\(["\']([^"\']+)',  # Flask
            r'@router\.(get|post|put|delete)\(["\']([^"\']+)',  # FastAPI
            r'router\.(Get|Post|Put|Delete)\(["\']([^"\']+)',  # Go
            r'app\.(get|post|put|delete)\(["\']([^"\']+)'  # Express
        ]
        
        import re
        
        for pattern in route_patterns:
            for file in Path('.').rglob('*.py'):
                with open(file) as f:
                    content = f.read()
                    matches = re.findall(pattern, content)
                    for match in matches:
                        path = match[-1] if isinstance(match, tuple) else match
                        feature_id = path.strip('/').replace('/', '_')
                        if feature_id and feature_id not in [f['id'] for f in features]:
                            features.append({
                                'id': feature_id,
                                'description': f"Endpoint: {path}",
                                'acceptance': f"Endpoint {path} responds correctly",
                                'status': 'existing'
                            })
        
        return features[:10]  # Limit to 10
    
    def create_base_files(self, project_info: Dict[str, Any]):
        """Create base RFD files"""
        # Create PROJECT.md
        if 'features' not in project_info:
            project_info['features'] = [{
                'id': 'initial_setup',
                'description': 'Initial project setup',
                'acceptance': 'Project structure created and building',
                'status': 'pending'
            }]
        
        project_md = frontmatter.Post(
            project_info.get('description', 'Project description'),
            **{
                'name': project_info['name'],
                'description': project_info['description'],
                'version': '0.1.0',
                'stack': {
                    'language': 'python',
                    'framework': 'fastapi',
                    'database': 'sqlite'
                },
                'rules': {
                    'max_files': 100,
                    'max_loc_per_file': 500,
                    'must_pass_tests': True,
                    'no_mocks_in_prod': True
                },
                'features': project_info['features'],
                'constraints': project_info.get('constraints', [])
            }
        )
        
        with open('PROJECT.md', 'w') as f:
            f.write(frontmatter.dumps(project_md))
        
        # Create CLAUDE.md
        self.create_claude_md()
        
        # Create PROGRESS.md
        if not Path('PROGRESS.md').exists():
            with open('PROGRESS.md', 'w') as f:
                f.write(f"# Build Progress\n\n*Started: {datetime.now().isoformat()}*\n\n")
    
    def create_claude_md(self):
        """Create CLAUDE.md for AI assistance"""
        claude_md = """---
# Claude Code Configuration
model: claude-3-5-sonnet-20241022
temperature: 0.2
max_tokens: 4000
tools: enabled
memory: .rfd/context/memory.json
---

# RFD Project Assistant

You are working on a Reality-First Development (RFD) project.

## Your Responsibilities

1. **Read specifications first**
   - Check @PROJECT.md for requirements
   - Review @specs/ for detailed specifications
   - Follow @.rfd/context/current.md for current task

2. **Validate continuously**
   - Run `rfd validate` after changes
   - Ensure all tests pass
   - Check against acceptance criteria

3. **Reality over theory**
   - Write code that runs
   - Use real data, not mocks
   - Test with actual scenarios

## Project Structure

- @PROJECT.md - Main specification
- @specs/ - Detailed specifications
  - CONSTITUTION.md - Project principles
  - PHASES.md - Development phases
  - API_CONTRACT.md - API specifications
  - DEVELOPMENT_GUIDELINES.md - Coding standards
- @PROGRESS.md - Development progress
- @.rfd/context/ - Session context

## Workflow

1. `rfd check` - Check current status
2. `rfd session start <feature>` - Begin work
3. `rfd build` - Build the feature
4. `rfd validate` - Validate implementation
5. `rfd checkpoint "message"` - Save progress
6. `rfd session end` - Complete session

## Commands

```bash
rfd init              # Initialize RFD
rfd check            # Status check
rfd validate         # Run validation
rfd build           # Build current feature
rfd checkpoint      # Save checkpoint
rfd session start   # Start feature work
rfd session end     # End session
rfd spec generate   # Generate specifications
```

## Remember

- Follow specifications exactly
- Validate before claiming completion
- Use real implementations
- Track progress with checkpoints
- Update PROGRESS.md regularly
"""
        with open('CLAUDE.md', 'w') as f:
            f.write(claude_md)
    
    def create_gitignore(self):
        """Create .gitignore for RFD projects"""
        gitignore = """# RFD Protocol
.rfd/memory.db
.rfd/context/current.md
.rfd/context/memory.json
.rfd/context/snapshots/
*.pyc
__pycache__/
.env
.coverage
*.log
"""
        with open('.gitignore', 'w') as f:
            f.write(gitignore)