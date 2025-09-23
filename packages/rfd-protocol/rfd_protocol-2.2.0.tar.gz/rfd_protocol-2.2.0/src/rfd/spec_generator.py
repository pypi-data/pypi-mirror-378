"""
Comprehensive Spec Generation System for RFD
Combines RFD's reality-first approach with spec-kit's planning methodologies
"""

import yaml
import json
import frontmatter
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import questionary
from dataclasses import dataclass, asdict

@dataclass
class ProjectPhase:
    """Represents a development phase"""
    id: str
    name: str
    type: str  # planning, development, testing, deployment
    duration_weeks: int
    dependencies: List[str]
    deliverables: List[str]
    tasks: List[Dict[str, Any]]
    acceptance_criteria: List[str]

@dataclass
class TechStackDecision:
    """Represents a technology stack decision"""
    category: str  # language, framework, database, etc.
    choice: str
    rationale: str
    alternatives_considered: List[str]
    constraints: List[str]
    risks: List[str]

@dataclass
class APIEndpoint:
    """Represents an API endpoint specification"""
    method: str
    path: str
    description: str
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    auth_required: bool
    rate_limit: Optional[str]
    errors: List[Dict[str, Any]]

class SpecGenerator:
    """Generates comprehensive project specifications"""
    
    def __init__(self, rfd):
        self.rfd = rfd
        self.specs_dir = Path('specs')
        self.specs_dir.mkdir(exist_ok=True)
        
    def ingest_prd(self, prd_path: Path) -> Dict[str, Any]:
        """Ingest a PRD document and extract project information"""
        with open(prd_path, 'r') as f:
            content = f.read()
        
        # Try to parse as YAML/frontmatter first
        try:
            if content.startswith('---'):
                post = frontmatter.loads(content)
                return self._parse_frontmatter_prd(post)
            else:
                return self._parse_text_prd(content)
        except Exception:
            return self._parse_text_prd(content)
    
    def _parse_text_prd(self, content: str) -> Dict[str, Any]:
        """Parse a text-based PRD using AI-like extraction"""
        extracted = {
            'name': '',
            'description': '',
            'goals': [],
            'requirements': [],
            'users': [],
            'constraints': [],
            'success_metrics': []
        }
        
        # Simple keyword-based extraction (could be enhanced with NLP)
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Detect sections
            if 'project' in line_lower and 'name' in line_lower:
                current_section = 'name'
            elif 'description' in line_lower or 'overview' in line_lower:
                current_section = 'description'
            elif 'goal' in line_lower or 'objective' in line_lower:
                current_section = 'goals'
            elif 'requirement' in line_lower:
                current_section = 'requirements'
            elif 'user' in line_lower or 'persona' in line_lower:
                current_section = 'users'
            elif 'constraint' in line_lower or 'limitation' in line_lower:
                current_section = 'constraints'
            elif 'success' in line_lower or 'metric' in line_lower:
                current_section = 'success_metrics'
            elif line.strip() and current_section:
                # Add content to current section
                if current_section in ['name', 'description']:
                    if not extracted[current_section]:
                        extracted[current_section] = line.strip()
                else:
                    if line.strip().startswith(('-', '*', '•', '1', '2', '3')):
                        extracted[current_section].append(line.strip().lstrip('-*•0123456789. '))
        
        return extracted
    
    def _parse_frontmatter_prd(self, post: frontmatter.Post) -> Dict[str, Any]:
        """Parse a frontmatter-based PRD"""
        return {
            'name': post.metadata.get('name', 'Unnamed Project'),
            'description': post.metadata.get('description', post.content[:200]),
            'goals': post.metadata.get('goals', []),
            'requirements': post.metadata.get('requirements', []),
            'users': post.metadata.get('users', []),
            'constraints': post.metadata.get('constraints', []),
            'success_metrics': post.metadata.get('success_metrics', [])
        }
    
    def generate_project_constitution(self, project_info: Dict[str, Any]) -> str:
        """Generate a project constitution document"""
        constitution = f"""# {project_info['name']} - Project Constitution

## Purpose
{project_info['description']}

## Core Principles

### 1. Reality-First Development
- Code that runs > Perfect architecture
- Working features > Planned features
- Real data > Mocked responses
- Passing tests > Theoretical correctness

### 2. User-Centric Design
"""
        for user in project_info.get('users', ['End users']):
            constitution += f"- Optimize for: {user}\n"
        
        constitution += """
### 3. Quality Standards
- All code must pass validation checks
- Features require acceptance tests
- Documentation must be maintained
- Security considerations in all decisions

## Project Goals
"""
        for goal in project_info.get('goals', []):
            constitution += f"- {goal}\n"
        
        constitution += """
## Constraints & Boundaries
"""
        for constraint in project_info.get('constraints', []):
            constitution += f"- {constraint}\n"
        
        constitution += """
## Success Metrics
"""
        for metric in project_info.get('success_metrics', []):
            constitution += f"- {metric}\n"
        
        constitution += """
## Development Guidelines

### Code Style
- Follow language-specific conventions
- Meaningful variable and function names
- Comments for complex logic
- Consistent formatting

### Testing Strategy
- Unit tests for all business logic
- Integration tests for API endpoints
- End-to-end tests for critical paths
- Performance tests for bottlenecks

### Documentation Requirements
- README with setup instructions
- API documentation
- Architecture decision records
- User guides for features

### Review Process
- All code requires review
- Tests must pass before merge
- Documentation updates required
- Security review for sensitive changes

## Decision Making

### Architecture Decisions
1. Document rationale in ADRs
2. Consider alternatives
3. Evaluate trade-offs
4. Review with team

### Technology Selection
1. Align with project goals
2. Consider team expertise
3. Evaluate maintenance burden
4. Assess community support

## Communication

### Channels
- Development discussions in issues
- Architecture decisions in ADRs
- Progress updates in PROGRESS.md
- Feature planning in specs/

### Cadence
- Daily checkpoint validations
- Weekly progress reviews
- Sprint planning sessions
- Retrospectives after milestones

---
*Generated on {datetime.now().isoformat()}*
"""
        return constitution
    
    def generate_phase_breakdown(self, project_info: Dict[str, Any], 
                                development_mode: str = "0-to-1") -> List[ProjectPhase]:
        """Generate project phases based on development mode"""
        phases = []
        
        if development_mode == "0-to-1":  # Greenfield
            phases = [
                ProjectPhase(
                    id="planning",
                    name="Planning & Architecture",
                    type="planning",
                    duration_weeks=2,
                    dependencies=[],
                    deliverables=[
                        "Technical specification",
                        "Architecture design",
                        "API contracts",
                        "Database schema"
                    ],
                    tasks=[
                        {"id": "tech_stack", "name": "Select technology stack", "hours": 8},
                        {"id": "architecture", "name": "Design system architecture", "hours": 16},
                        {"id": "api_design", "name": "Design API contracts", "hours": 12},
                        {"id": "db_design", "name": "Design database schema", "hours": 12}
                    ],
                    acceptance_criteria=[
                        "All specifications reviewed and approved",
                        "Technology decisions documented",
                        "API contracts defined",
                        "Database schema finalized"
                    ]
                ),
                ProjectPhase(
                    id="foundation",
                    name="Foundation & Infrastructure",
                    type="development",
                    duration_weeks=2,
                    dependencies=["planning"],
                    deliverables=[
                        "Project setup",
                        "CI/CD pipeline",
                        "Basic authentication",
                        "Database connections"
                    ],
                    tasks=[
                        {"id": "project_init", "name": "Initialize project structure", "hours": 4},
                        {"id": "ci_cd", "name": "Setup CI/CD pipeline", "hours": 8},
                        {"id": "auth_basic", "name": "Implement basic authentication", "hours": 16},
                        {"id": "db_setup", "name": "Setup database connections", "hours": 8}
                    ],
                    acceptance_criteria=[
                        "Project builds successfully",
                        "CI/CD pipeline running",
                        "Authentication working",
                        "Database connected"
                    ]
                ),
                ProjectPhase(
                    id="core_features",
                    name="Core Features",
                    type="development",
                    duration_weeks=4,
                    dependencies=["foundation"],
                    deliverables=["Core functionality", "API endpoints", "Basic UI"],
                    tasks=[],  # Generated from requirements
                    acceptance_criteria=[]  # Generated from requirements
                ),
                ProjectPhase(
                    id="testing",
                    name="Testing & Validation",
                    type="testing",
                    duration_weeks=1,
                    dependencies=["core_features"],
                    deliverables=["Test suite", "Performance benchmarks", "Security audit"],
                    tasks=[
                        {"id": "unit_tests", "name": "Write unit tests", "hours": 16},
                        {"id": "integration_tests", "name": "Write integration tests", "hours": 12},
                        {"id": "perf_test", "name": "Performance testing", "hours": 8},
                        {"id": "security_audit", "name": "Security audit", "hours": 8}
                    ],
                    acceptance_criteria=[
                        "90% test coverage",
                        "All tests passing",
                        "Performance targets met",
                        "Security vulnerabilities addressed"
                    ]
                ),
                ProjectPhase(
                    id="deployment",
                    name="Deployment & Launch",
                    type="deployment",
                    duration_weeks=1,
                    dependencies=["testing"],
                    deliverables=["Production deployment", "Documentation", "Monitoring"],
                    tasks=[
                        {"id": "prod_setup", "name": "Setup production environment", "hours": 8},
                        {"id": "deploy", "name": "Deploy to production", "hours": 4},
                        {"id": "monitoring", "name": "Setup monitoring", "hours": 8},
                        {"id": "documentation", "name": "Finalize documentation", "hours": 12}
                    ],
                    acceptance_criteria=[
                        "Application deployed successfully",
                        "Monitoring active",
                        "Documentation complete",
                        "Handoff completed"
                    ]
                )
            ]
            
        elif development_mode == "exploration":  # Creative Exploration
            phases = [
                ProjectPhase(
                    id="research",
                    name="Research & Exploration",
                    type="planning",
                    duration_weeks=1,
                    dependencies=[],
                    deliverables=["Research findings", "Technology options", "Prototypes"],
                    tasks=[
                        {"id": "research", "name": "Research solutions", "hours": 16},
                        {"id": "prototype", "name": "Build prototypes", "hours": 24}
                    ],
                    acceptance_criteria=["Multiple approaches evaluated", "Prototypes functional"]
                ),
                ProjectPhase(
                    id="parallel_impl",
                    name="Parallel Implementations",
                    type="development",
                    duration_weeks=3,
                    dependencies=["research"],
                    deliverables=["Multiple implementations", "Comparison matrix"],
                    tasks=[],
                    acceptance_criteria=["Each approach implemented", "Performance compared"]
                ),
                ProjectPhase(
                    id="selection",
                    name="Selection & Refinement",
                    type="development",
                    duration_weeks=1,
                    dependencies=["parallel_impl"],
                    deliverables=["Final implementation", "Decision documentation"],
                    tasks=[],
                    acceptance_criteria=["Best approach selected", "Implementation refined"]
                )
            ]
            
        elif development_mode == "brownfield":  # Iterative Enhancement
            phases = [
                ProjectPhase(
                    id="analysis",
                    name="Current State Analysis",
                    type="planning",
                    duration_weeks=1,
                    dependencies=[],
                    deliverables=["System analysis", "Improvement plan", "Risk assessment"],
                    tasks=[
                        {"id": "audit", "name": "Audit existing system", "hours": 16},
                        {"id": "plan", "name": "Create improvement plan", "hours": 8}
                    ],
                    acceptance_criteria=["Current state documented", "Improvements identified"]
                ),
                ProjectPhase(
                    id="refactoring",
                    name="Refactoring & Modernization",
                    type="development",
                    duration_weeks=2,
                    dependencies=["analysis"],
                    deliverables=["Refactored code", "Updated dependencies"],
                    tasks=[],
                    acceptance_criteria=["Code modernized", "Tests passing"]
                ),
                ProjectPhase(
                    id="enhancement",
                    name="Feature Enhancement",
                    type="development",
                    duration_weeks=3,
                    dependencies=["refactoring"],
                    deliverables=["New features", "Improved performance"],
                    tasks=[],
                    acceptance_criteria=["Features implemented", "Performance improved"]
                )
            ]
        
        # Add tasks from requirements
        if "requirements" in project_info:
            for i, req in enumerate(project_info["requirements"][:10]):  # Limit to 10
                phases[2].tasks.append({
                    "id": f"req_{i}",
                    "name": req[:50],  # Truncate long requirements
                    "hours": 8  # Default estimate
                })
                phases[2].acceptance_criteria.append(f"{req[:50]} implemented")
        
        return phases
    
    def generate_tech_stack_recommendations(self, project_info: Dict[str, Any]) -> List[TechStackDecision]:
        """Generate technology stack recommendations based on project requirements"""
        recommendations = []
        
        # Analyze requirements to suggest stack
        requirements_text = ' '.join(project_info.get('requirements', []))
        
        # Language recommendation
        if 'real-time' in requirements_text.lower() or 'performance' in requirements_text.lower():
            language_choice = TechStackDecision(
                category="language",
                choice="go",
                rationale="High performance and excellent concurrency support for real-time features",
                alternatives_considered=["rust", "java", "node.js"],
                constraints=["Team must learn Go", "Smaller ecosystem than Node.js"],
                risks=["Learning curve for team"]
            )
        elif 'machine learning' in requirements_text.lower() or 'ai' in requirements_text.lower():
            language_choice = TechStackDecision(
                category="language",
                choice="python",
                rationale="Rich ecosystem for ML/AI with libraries like TensorFlow, PyTorch",
                alternatives_considered=["r", "julia", "java"],
                constraints=["Performance limitations for CPU-intensive tasks"],
                risks=["GIL limitations for true parallelism"]
            )
        else:
            language_choice = TechStackDecision(
                category="language",
                choice="typescript",
                rationale="Type safety with JavaScript ecosystem, full-stack development",
                alternatives_considered=["python", "go", "java"],
                constraints=["Requires build step", "Type system complexity"],
                risks=["Build tool complexity"]
            )
        recommendations.append(language_choice)
        
        # Framework recommendation based on language
        if language_choice.choice == "python":
            framework = TechStackDecision(
                category="framework",
                choice="fastapi",
                rationale="Modern, fast, type-hints support, automatic API documentation",
                alternatives_considered=["django", "flask", "pyramid"],
                constraints=["Newer framework", "Less mature ecosystem than Django"],
                risks=["Fewer third-party packages"]
            )
        elif language_choice.choice == "typescript":
            framework = TechStackDecision(
                category="framework",
                choice="nestjs",
                rationale="Enterprise-grade, modular architecture, TypeScript-first",
                alternatives_considered=["express", "fastify", "koa"],
                constraints=["Opinionated structure", "Learning curve"],
                risks=["Over-engineering for simple projects"]
            )
        else:
            framework = TechStackDecision(
                category="framework",
                choice="gin",
                rationale="Minimal, fast, good middleware support",
                alternatives_considered=["echo", "fiber", "chi"],
                constraints=["Less batteries-included"],
                risks=["Need to add many third-party libraries"]
            )
        recommendations.append(framework)
        
        # Database recommendation
        if 'scale' in requirements_text.lower() or 'distributed' in requirements_text.lower():
            database = TechStackDecision(
                category="database",
                choice="postgresql",
                rationale="Proven scalability, rich features, strong consistency",
                alternatives_considered=["mysql", "mongodb", "cassandra"],
                constraints=["Operational complexity", "Requires DBA knowledge for optimization"],
                risks=["Scaling beyond single node requires additional tools"]
            )
        else:
            database = TechStackDecision(
                category="database",
                choice="sqlite",
                rationale="Zero configuration, embedded, perfect for MVPs",
                alternatives_considered=["postgresql", "mysql"],
                constraints=["Single writer", "Not suitable for high concurrency"],
                risks=["Migration needed when scaling"]
            )
        recommendations.append(database)
        
        return recommendations
    
    def generate_api_contracts(self, project_info: Dict[str, Any]) -> List[APIEndpoint]:
        """Generate API contract specifications"""
        endpoints = []
        
        # Generate standard CRUD endpoints for main entities
        entities = self._extract_entities(project_info.get('requirements', []))
        
        for entity in entities[:5]:  # Limit to 5 main entities
            entity_lower = entity.lower()
            entity_plural = entity_lower + 's'
            
            # CREATE
            endpoints.append(APIEndpoint(
                method="POST",
                path=f"/{entity_plural}",
                description=f"Create a new {entity_lower}",
                request_schema={
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"}
                    }
                },
                response_schema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                },
                auth_required=True,
                rate_limit="100/hour",
                errors=[
                    {"code": 400, "message": "Invalid request data"},
                    {"code": 401, "message": "Unauthorized"},
                    {"code": 409, "message": f"{entity} already exists"}
                ]
            ))
            
            # READ (List)
            endpoints.append(APIEndpoint(
                method="GET",
                path=f"/{entity_plural}",
                description=f"List all {entity_plural}",
                request_schema={},
                response_schema={
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {"$ref": f"#/definitions/{entity}"}
                        },
                        "total": {"type": "integer"},
                        "page": {"type": "integer"},
                        "per_page": {"type": "integer"}
                    }
                },
                auth_required=False,
                rate_limit="1000/hour",
                errors=[
                    {"code": 401, "message": "Unauthorized for private resources"}
                ]
            ))
            
            # READ (Single)
            endpoints.append(APIEndpoint(
                method="GET",
                path=f"/{entity_plural}/{{id}}",
                description=f"Get a specific {entity_lower}",
                request_schema={},
                response_schema={"$ref": f"#/definitions/{entity}"},
                auth_required=False,
                rate_limit="1000/hour",
                errors=[
                    {"code": 404, "message": f"{entity} not found"}
                ]
            ))
            
            # UPDATE
            endpoints.append(APIEndpoint(
                method="PUT",
                path=f"/{entity_plural}/{{id}}",
                description=f"Update a {entity_lower}",
                request_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"}
                    }
                },
                response_schema={"$ref": f"#/definitions/{entity}"},
                auth_required=True,
                rate_limit="100/hour",
                errors=[
                    {"code": 400, "message": "Invalid request data"},
                    {"code": 401, "message": "Unauthorized"},
                    {"code": 404, "message": f"{entity} not found"}
                ]
            ))
            
            # DELETE
            endpoints.append(APIEndpoint(
                method="DELETE",
                path=f"/{entity_plural}/{{id}}",
                description=f"Delete a {entity_lower}",
                request_schema={},
                response_schema={"type": "object", "properties": {"success": {"type": "boolean"}}},
                auth_required=True,
                rate_limit="100/hour",
                errors=[
                    {"code": 401, "message": "Unauthorized"},
                    {"code": 404, "message": f"{entity} not found"}
                ]
            ))
        
        # Add standard utility endpoints
        endpoints.extend([
            APIEndpoint(
                method="GET",
                path="/health",
                description="Health check endpoint",
                request_schema={},
                response_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"}
                    }
                },
                auth_required=False,
                rate_limit=None,
                errors=[]
            ),
            APIEndpoint(
                method="POST",
                path="/auth/login",
                description="User authentication",
                request_schema={
                    "type": "object",
                    "required": ["email", "password"],
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                        "password": {"type": "string"}
                    }
                },
                response_schema={
                    "type": "object",
                    "properties": {
                        "token": {"type": "string"},
                        "expires_at": {"type": "string", "format": "date-time"}
                    }
                },
                auth_required=False,
                rate_limit="10/hour",
                errors=[
                    {"code": 401, "message": "Invalid credentials"},
                    {"code": 429, "message": "Too many attempts"}
                ]
            )
        ])
        
        return endpoints
    
    def _extract_entities(self, requirements: List[str]) -> List[str]:
        """Extract entity names from requirements"""
        entities = []
        entity_keywords = ['user', 'product', 'order', 'payment', 'customer', 
                          'account', 'profile', 'item', 'transaction', 'report',
                          'document', 'file', 'message', 'notification', 'setting']
        
        requirements_text = ' '.join(requirements).lower()
        
        for keyword in entity_keywords:
            if keyword in requirements_text:
                entities.append(keyword.capitalize())
        
        # If no entities found, use defaults
        if not entities:
            entities = ['Resource', 'Item', 'User']
        
        return entities
    
    def generate_development_guidelines(self, project_info: Dict[str, Any], 
                                       tech_stack: List[TechStackDecision]) -> str:
        """Generate comprehensive development guidelines"""
        language = next((t.choice for t in tech_stack if t.category == "language"), "python")
        framework = next((t.choice for t in tech_stack if t.category == "framework"), "fastapi")
        
        guidelines = f"""# Development Guidelines

## Code Standards

### {language.capitalize()} Standards
"""
        
        if language == "python":
            guidelines += """- Follow PEP 8 style guide
- Use type hints for all functions
- Docstrings for all public functions
- Maximum line length: 100 characters
- Use black for formatting
- Use ruff for linting
"""
        elif language == "typescript":
            guidelines += """- Follow ESLint configuration
- Use strict TypeScript settings
- Interfaces for all data structures
- Avoid 'any' type
- Use Prettier for formatting
- Maximum line length: 100 characters
"""
        elif language == "go":
            guidelines += """- Follow effective Go guidelines
- Use gofmt for formatting
- Package names should be lowercase
- Exported names start with capital letter
- Handle all errors explicitly
- Use go vet and golint
"""
        
        guidelines += f"""
### {framework.capitalize()} Patterns
"""
        
        if framework == "fastapi":
            guidelines += """- Use dependency injection
- Pydantic models for validation
- Async functions where appropriate
- Proper exception handling
- OpenAPI documentation
"""
        elif framework == "nestjs":
            guidelines += """- Follow modular architecture
- Use decorators appropriately
- Dependency injection via providers
- DTOs for data transfer
- Guards for authentication
"""
        elif framework == "gin":
            guidelines += """- Use middleware for cross-cutting concerns
- Group routes logically
- Proper error handling
- Context usage patterns
- Validation via binding
"""
        
        guidelines += """
## Testing Standards

### Test Coverage Requirements
- Minimum 80% code coverage
- 100% coverage for business logic
- Integration tests for all APIs
- Unit tests for all utilities

### Test Structure
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # API and database tests
├── e2e/           # End-to-end scenarios
└── fixtures/      # Test data and mocks
```

### Testing Practices
- Arrange-Act-Assert pattern
- One assertion per test preferred
- Descriptive test names
- Test error conditions
- No test interdependencies

## Git Workflow

### Branch Strategy
- `main` - Production ready code
- `develop` - Integration branch
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches
- `release/*` - Release preparation

### Commit Messages
Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

### Pull Request Process
1. Create feature branch
2. Write code with tests
3. Ensure all tests pass
4. Update documentation
5. Create pull request
6. Code review required
7. Squash and merge

## Documentation Standards

### Code Documentation
- README with setup instructions
- API documentation (OpenAPI/Swagger)
- Architecture diagrams
- Database schema documentation
- Deployment instructions

### Inline Documentation
- Comment complex algorithms
- Document business logic
- Explain non-obvious decisions
- TODO comments with issue links

## Security Practices

### General Security
- Never commit secrets
- Use environment variables
- Validate all inputs
- Sanitize outputs
- Use prepared statements
- Implement rate limiting

### Authentication & Authorization
- Use proven libraries
- Hash passwords properly
- Implement JWT correctly
- Role-based access control
- Audit logging for sensitive operations

## Performance Guidelines

### Optimization Principles
- Measure before optimizing
- Focus on bottlenecks
- Cache appropriately
- Optimize database queries
- Use pagination
- Implement lazy loading

### Monitoring
- Application metrics
- Error tracking
- Performance monitoring
- User analytics
- Uptime monitoring

## Development Environment

### Required Tools
- Version control: Git
- Package manager: {self._get_package_manager(language)}
- IDE: VSCode with extensions
- Database client
- API testing tool (Postman/Insomnia)

### Environment Setup
```bash
# Clone repository
git clone <repository>

# Install dependencies
{self._get_install_command(language)}

# Setup environment
cp .env.example .env
# Edit .env with your values

# Run development server
{self._get_run_command(language, framework)}
```

## Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance acceptable
- [ ] Error handling complete
- [ ] Logging appropriate
- [ ] No code duplication
- [ ] Clear naming conventions
- [ ] RFD validation passing

---
*Generated on {datetime.now().isoformat()}*
"""
        return guidelines
    
    def _get_package_manager(self, language: str) -> str:
        """Get package manager for language"""
        managers = {
            "python": "pip/poetry/uv",
            "typescript": "npm/yarn/pnpm",
            "javascript": "npm/yarn/pnpm",
            "go": "go mod",
            "rust": "cargo",
            "ruby": "bundler"
        }
        return managers.get(language, "package manager")
    
    def _get_install_command(self, language: str) -> str:
        """Get install command for language"""
        commands = {
            "python": "pip install -r requirements.txt",
            "typescript": "npm install",
            "javascript": "npm install",
            "go": "go mod download",
            "rust": "cargo build",
            "ruby": "bundle install"
        }
        return commands.get(language, "install dependencies")
    
    def _get_run_command(self, language: str, framework: str) -> str:
        """Get run command for framework"""
        commands = {
            "fastapi": "uvicorn main:app --reload",
            "flask": "flask run --debug",
            "django": "python manage.py runserver",
            "express": "npm run dev",
            "nestjs": "npm run start:dev",
            "gin": "go run main.go",
            "rails": "rails server"
        }
        return commands.get(framework, "start development server")
    
    def generate_full_specification(self, project_info: Dict[str, Any], 
                                   development_mode: str = "0-to-1") -> Dict[str, Path]:
        """Generate complete project specification suite"""
        generated_files = {}
        
        # 1. Generate Constitution
        constitution = self.generate_project_constitution(project_info)
        constitution_path = self.specs_dir / "CONSTITUTION.md"
        constitution_path.write_text(constitution)
        generated_files["constitution"] = constitution_path
        
        # 2. Generate Phase Breakdown
        phases = self.generate_phase_breakdown(project_info, development_mode)
        phases_doc = self._format_phases_document(phases)
        phases_path = self.specs_dir / "PHASES.md"
        phases_path.write_text(phases_doc)
        generated_files["phases"] = phases_path
        
        # 3. Generate Tech Stack ADR
        tech_stack = self.generate_tech_stack_recommendations(project_info)
        adr = self._format_adr(tech_stack)
        adr_path = self.specs_dir / "ADR-001-tech-stack.md"
        adr_path.write_text(adr)
        generated_files["tech_adr"] = adr_path
        
        # 4. Generate API Contracts
        api_endpoints = self.generate_api_contracts(project_info)
        api_doc = self._format_api_document(api_endpoints)
        api_path = self.specs_dir / "API_CONTRACT.md"
        api_path.write_text(api_doc)
        generated_files["api_contract"] = api_path
        
        # 5. Generate Development Guidelines
        guidelines = self.generate_development_guidelines(project_info, tech_stack)
        guidelines_path = self.specs_dir / "DEVELOPMENT_GUIDELINES.md"
        guidelines_path.write_text(guidelines)
        generated_files["guidelines"] = guidelines_path
        
        # 6. Update PROJECT.md with comprehensive spec
        self._update_project_md(project_info, phases, tech_stack, api_endpoints)
        
        return generated_files
    
    def _format_phases_document(self, phases: List[ProjectPhase]) -> str:
        """Format phases into markdown document"""
        doc = "# Project Phases\n\n"
        
        total_weeks = sum(p.duration_weeks for p in phases)
        doc += f"**Total Duration**: {total_weeks} weeks\n\n"
        
        doc += "## Phase Overview\n\n"
        doc += "| Phase | Type | Duration | Dependencies |\n"
        doc += "|-------|------|----------|-------------|\n"
        
        for phase in phases:
            deps = ', '.join(phase.dependencies) if phase.dependencies else 'None'
            doc += f"| {phase.name} | {phase.type} | {phase.duration_weeks} weeks | {deps} |\n"
        
        doc += "\n## Detailed Phases\n\n"
        
        for phase in phases:
            doc += f"### {phase.name}\n"
            doc += f"**ID**: {phase.id}\n"
            doc += f"**Type**: {phase.type}\n"
            doc += f"**Duration**: {phase.duration_weeks} weeks\n\n"
            
            if phase.dependencies:
                doc += f"**Dependencies**: {', '.join(phase.dependencies)}\n\n"
            
            doc += "#### Deliverables\n"
            for deliverable in phase.deliverables:
                doc += f"- {deliverable}\n"
            
            doc += "\n#### Tasks\n"
            for task in phase.tasks:
                doc += f"- [ ] {task['name']} ({task['hours']}h)\n"
            
            doc += "\n#### Acceptance Criteria\n"
            for criteria in phase.acceptance_criteria:
                doc += f"- {criteria}\n"
            
            doc += "\n---\n\n"
        
        return doc
    
    def _format_adr(self, tech_stack: List[TechStackDecision]) -> str:
        """Format Architecture Decision Record"""
        doc = f"""# ADR-001: Technology Stack Selection

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Proposed

## Context
We need to select the technology stack for the project implementation.

## Decisions

"""
        for decision in tech_stack:
            doc += f"### {decision.category.capitalize()}: {decision.choice}\n\n"
            doc += f"**Rationale**: {decision.rationale}\n\n"
            
            if decision.alternatives_considered:
                doc += "**Alternatives Considered**:\n"
                for alt in decision.alternatives_considered:
                    doc += f"- {alt}\n"
                doc += "\n"
            
            if decision.constraints:
                doc += "**Constraints**:\n"
                for constraint in decision.constraints:
                    doc += f"- {constraint}\n"
                doc += "\n"
            
            if decision.risks:
                doc += "**Risks**:\n"
                for risk in decision.risks:
                    doc += f"- {risk}\n"
                doc += "\n"
        
        doc += """## Consequences

### Positive
- Technology choices aligned with project requirements
- Clear rationale for decisions
- Team can prepare for identified constraints

### Negative  
- Some learning curve expected
- Potential risks need mitigation strategies

## References
- Project requirements document
- Team skill assessment
- Technology evaluation criteria
"""
        return doc
    
    def _format_api_document(self, endpoints: List[APIEndpoint]) -> str:
        """Format API contract document"""
        doc = "# API Contract Specification\n\n"
        doc += f"**Version**: 1.0.0\n"
        doc += f"**Generated**: {datetime.now().isoformat()}\n\n"
        
        doc += "## Endpoints\n\n"
        
        for endpoint in endpoints:
            doc += f"### {endpoint.method} {endpoint.path}\n"
            doc += f"{endpoint.description}\n\n"
            
            doc += "**Authentication**: "
            doc += "Required\n" if endpoint.auth_required else "Not required\n"
            
            if endpoint.rate_limit:
                doc += f"**Rate Limit**: {endpoint.rate_limit}\n"
            
            doc += "\n**Request**:\n```json\n"
            doc += json.dumps(endpoint.request_schema, indent=2)
            doc += "\n```\n\n"
            
            doc += "**Response**:\n```json\n"
            doc += json.dumps(endpoint.response_schema, indent=2)
            doc += "\n```\n\n"
            
            if endpoint.errors:
                doc += "**Error Responses**:\n"
                for error in endpoint.errors:
                    doc += f"- `{error['code']}`: {error['message']}\n"
            
            doc += "\n---\n\n"
        
        return doc
    
    def _update_project_md(self, project_info: Dict[str, Any],
                           phases: List[ProjectPhase],
                           tech_stack: List[TechStackDecision],
                           api_endpoints: List[APIEndpoint]):
        """Update PROJECT.md with comprehensive specification"""
        project_file = Path('PROJECT.md')
        
        if project_file.exists():
            with open(project_file, 'r') as f:
                post = frontmatter.load(f)
        else:
            post = frontmatter.Post("")
        
        # Update metadata
        post.metadata.update({
            'name': project_info['name'],
            'description': project_info['description'],
            'version': '0.1.0',
            'development_mode': '0-to-1',
            'generated_at': datetime.now().isoformat()
        })
        
        # Update stack
        stack_dict = {}
        for decision in tech_stack:
            stack_dict[decision.category] = decision.choice
        post.metadata['stack'] = stack_dict
        
        # Add phases summary
        post.metadata['phases'] = [
            {
                'id': p.id,
                'name': p.name,
                'duration_weeks': p.duration_weeks,
                'task_count': len(p.tasks)
            }
            for p in phases
        ]
        
        # Add API summary
        post.metadata['api_endpoints_count'] = len(api_endpoints)
        
        # Add specs references
        post.metadata['specifications'] = {
            'constitution': 'specs/CONSTITUTION.md',
            'phases': 'specs/PHASES.md',
            'tech_adr': 'specs/ADR-001-tech-stack.md',
            'api_contract': 'specs/API_CONTRACT.md',
            'guidelines': 'specs/DEVELOPMENT_GUIDELINES.md'
        }
        
        # Write back
        with open(project_file, 'w') as f:
            f.write(frontmatter.dumps(post))