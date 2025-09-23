"""
Spec Engine for RFD
Manages spec-driven design following GitHub Spec Kit patterns
"""

import yaml
import frontmatter
from pathlib import Path
from typing import Dict, Any
import questionary
from datetime import datetime

class SpecEngine:
    def __init__(self, rfd):
        self.rfd = rfd
    
    def create_interactive(self):
        """Interactive spec creation wizard"""
        print("\n🎯 RFD Spec Creator\n")
        
        # Basic info
        name = questionary.text("Project name:").ask()
        description = questionary.text("What does this do? (30 words max):").ask()
        
        # Stack selection
        language = questionary.select(
            "Language:",
            choices=['python', 'javascript', 'typescript', 'ruby', 'go']
        ).ask()
        
        framework = self._select_framework(language)
        database = questionary.select(
            "Database:",
            choices=['sqlite', 'postgresql', 'mysql', 'mongodb', 'none']
        ).ask()
        
        # Features (max 3 for v1)
        features = []
        for i in range(3):
            if i > 0 and not questionary.confirm(f"Add feature {i+1}?").ask():
                break
            
            feature_id = questionary.text(f"Feature {i+1} ID (e.g., user_signup):").ask()
            feature_desc = questionary.text(f"Feature {i+1} description:").ask()
            feature_acceptance = questionary.text(f"Acceptance criteria:").ask()
            
            features.append({
                'id': feature_id,
                'description': feature_desc,
                'acceptance': feature_acceptance,
                'status': 'pending'
            })
        
        # Rules
        max_files = questionary.text("Max files allowed:", default="20").ask()
        max_loc = questionary.text("Max lines per file:", default="200").ask()
        
        # Generate PROJECT.md
        spec = {
            'version': '1.0',
            'name': name,
            'stack': {
                'language': language,
                'framework': framework,
                'database': database
            },
            'rules': {
                'max_files': int(max_files),
                'max_loc_per_file': int(max_loc),
                'must_pass_tests': True,
                'no_mocks_in_prod': True
            },
            'features': features,
            'constraints': self._default_constraints()
        }
        
        # Add API contract if web framework
        if framework in ['fastapi', 'express', 'rails']:
            spec['api_contract'] = self._generate_api_contract(features)
        
        # Write PROJECT.md
        post = frontmatter.Post(description, **spec)
        
        with open('PROJECT.md', 'w') as f:
            f.write(frontmatter.dumps(post))
        
        print("✅ PROJECT.md created!")
        
        # Initialize features in database
        self._init_features(features)
    
    def _select_framework(self, language: str) -> str:
        """Select framework based on language"""
        frameworks = {
            'python': ['fastapi', 'flask', 'django', 'none'],
            'javascript': ['express', 'nestjs', 'koa', 'none'],
            'typescript': ['express', 'nestjs', 'none'],
            'ruby': ['rails', 'sinatra', 'none'],
            'go': ['gin', 'echo', 'none']
        }
        
        return questionary.select(
            "Framework:",
            choices=frameworks.get(language, ['none'])
        ).ask()
    
    def _default_constraints(self) -> list:
        """Default constraints for any project"""
        return [
            "NO authentication libraries until core works",
            "NO database migrations until schema stable", 
            "NO frontend until API complete",
            "NO optimization until features work",
            "NO abstractions until patterns emerge"
        ]
    
    def _generate_api_contract(self, features: list) -> Dict:
        """Generate API contract from features"""
        contract = {
            'base_url': 'http://localhost:8000',
            'health_check': '/health',
            'endpoints': []
        }
        
        # Generate endpoints from features
        for feature in features:
            if 'signup' in feature['id']:
                contract['endpoints'].append({
                    'method': 'POST',
                    'path': '/signup',
                    'validates': 'returns 201 with {user_id: string}'
                })
            elif 'login' in feature['id']:
                contract['endpoints'].append({
                    'method': 'POST',
                    'path': '/login',
                    'validates': 'returns 200 with {token: string}'
                })
            # Add more patterns
        
        return contract
    
    def _init_features(self, features: list):
        """Initialize features in database"""
        import sqlite3
        conn = sqlite3.connect(self.rfd.db_path)
        
        for feature in features:
            conn.execute("""
                INSERT OR REPLACE INTO features (id, description, acceptance_criteria, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                feature['id'],
                feature['description'],
                feature.get('acceptance', ''),
                'pending',
                datetime.now().isoformat()
            ))
        
        conn.commit()
    
    def validate(self, spec=None) -> bool:
        """Validate spec against Spec Kit standards"""
        if spec is None:
            spec = self.rfd.load_project_spec()
        
        # Return list of errors for testing
        errors = []
        
        required_fields = ['version', 'name', 'stack', 'features']
        for field in required_fields:
            if field not in spec:
                error_msg = f"Missing required field: {field}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        # Validate features
        if 'features' not in spec or len(spec['features']) == 0:
            error_msg = "No features defined"
            errors.append(error_msg)
            print(f"❌ {error_msg}")
        
        if 'features' in spec and len(spec['features']) > 3:
            print("⚠️  Warning: More than 3 features for v1")
        
        if not errors:
            print("✅ Spec is valid")
            return []  # Return empty list for no errors
        
        return errors  # Return list of errors
    
    def review(self):
        """Display spec in readable format"""
        spec = self.rfd.load_project_spec()
        
        print("\n=== PROJECT SPECIFICATION ===\n")
        print(f"📦 {spec.get('name', 'Unnamed Project')}")
        print(f"Version: {spec.get('version', '1.0')}\n")
        
        # Stack
        stack = spec.get('stack', {})
        print("🔧 Technology Stack:")
        print(f"  Language: {stack.get('language', 'not specified')}")
        print(f"  Framework: {stack.get('framework', 'not specified')}")
        print(f"  Database: {stack.get('database', 'not specified')}\n")
        
        # Features
        print("📋 Features:")
        for f in spec.get('features', []):
            status_icon = '✅' if f['status'] == 'complete' else '🔨' if f['status'] == 'building' else '⭕'
            print(f"  {status_icon} {f['id']}")
            print(f"      {f['description']}")
            print(f"      Acceptance: {f.get('acceptance', 'Not specified')}\n")
        
        # Rules
        print("📏 Rules:")
        for rule, value in spec.get('rules', {}).items():
            print(f"  • {rule}: {value}")
        
        # Constraints
        print("\n🚫 Constraints:")
        for constraint in spec.get('constraints', []):
            print(f"  • {constraint}")
    
    def add_feature(self, spec: Dict, feature: Dict) -> Dict:
        """Add a new feature to the spec"""
        if 'features' not in spec:
            spec['features'] = []
        spec['features'].append(feature)
        return spec
    
    def update_feature_status(self, spec: Dict, feature_id: str, status: str) -> Dict:
        """Update the status of a feature"""
        if 'features' in spec:
            for feature in spec['features']:
                if feature.get('id') == feature_id:
                    feature['status'] = status
        return spec
    
    def validate_spec(self, spec: Dict) -> bool:
        """Validate a spec structure"""
        required_fields = ['name', 'features']
        for field in required_fields:
            if field not in spec:
                return False
        return True
    
    def create_spec_interactive(self) -> Dict:
        """Alias for create_interactive for backward compatibility"""
        return self.create_interactive()
    
    def create(self) -> Dict:
        """Alias for create_interactive for backward compatibility"""
        return self.create_interactive()