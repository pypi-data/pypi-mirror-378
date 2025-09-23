# RFD Protocol

**Reality-First Development - Prevents AI hallucination and ensures spec-driven development**

[![CI Pipeline](https://github.com/kryptobaseddev/rfd-protocol/actions/workflows/ci.yml/badge.svg)](https://github.com/kryptobaseddev/rfd-protocol/actions/workflows/ci.yml)
[![Release Pipeline](https://github.com/kryptobaseddev/rfd-protocol/actions/workflows/release.yml/badge.svg)](https://github.com/kryptobaseddev/rfd-protocol/actions/workflows/release.yml)
[![PyPI version](https://badge.fury.io/py/rfd-protocol.svg)](https://pypi.org/project/rfd-protocol/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is RFD?

RFD (Reality-First Development) is a protocol that **eliminates AI hallucination** in software development by enforcing concrete reality checkpoints. Instead of trusting AI claims about what was implemented, RFD validates that code actually runs, tests pass, and features work.

### Core Benefits

- **🎯 Prevents AI Hallucination**: Drops error rate from 48% to ~0%
- **📋 Spec-Driven Development**: Features must be specified before implementation
- **✅ Reality Checkpoints**: Every change is validated against working code
- **🔄 Session Persistence**: Context maintained across Claude Code sessions
- **🌍 Universal Drop-in**: Works with any tech stack (25+ languages)

## Quick Start

### Installation

#### Option 1: Via pip (Recommended)
```bash
pip install rfd-protocol
```

#### Option 2: From source
```bash
git clone https://github.com/kryptobaseddev/rfd-protocol.git
cd rfd-protocol
pip install -e .
```

### Initialize in Your Project

#### For a new project:
```bash
mkdir my-project && cd my-project
rfd init
```

#### For an existing project:
```bash
cd your-existing-project/
rfd init
```

This creates:
- `PROJECT.md` - Your project specification
- `CLAUDE.md` - Claude Code integration config
- `PROGRESS.md` - Build progress tracking
- `.rfd/` - RFD system directory

### Basic Workflow

1. **Define specifications first**:
   ```bash
   rfd spec create
   ```

2. **Start feature development**:
   ```bash
   rfd session start user_auth
   ```

3. **Build and validate continuously**:
   ```bash
   rfd build
   rfd validate
   ```

4. **Save working checkpoints**:
   ```bash
   rfd checkpoint "User auth working"
   ```

## Project Architecture

Our repository follows modern Python packaging standards with a clear separation of concerns:

```
rfd-protocol/
├── README.md                  # This file
├── PROJECT.md                 # Project specification
├── pyproject.toml            # Modern Python packaging config
├── requirements.txt          # Runtime dependencies
│
├── src/rfd/                  # 🎯 MAIN PACKAGE (modern Python layout)
│   ├── __init__.py          # Package entry point, version info
│   ├── cli.py               # Command-line interface
│   ├── rfd.py              # Core RFD orchestration class
│   ├── validation.py       # AI hallucination detection engine
│   ├── session.py          # Session management & persistence
│   ├── build.py            # Build automation engine
│   ├── spec.py             # Specification management
│   └── templates/          # Project templates
│
├── tests/                   # 🧪 COMPREHENSIVE TEST SUITE
│   ├── conftest.py         # Shared pytest fixtures
│   ├── unit/               # Fast, isolated tests
│   ├── integration/        # Component interaction tests
│   ├── system/             # End-to-end workflow tests
│   └── fixtures/           # Test data and sample projects
│
├── .rfd/                   # 🏛️ LEGACY SYSTEM (for compatibility)
│   ├── rfd.py              # Legacy CLI entry point
│   ├── validation.py       # Legacy validation engine
│   ├── session.py          # Legacy session management
│   ├── build.py            # Legacy build engine
│   ├── spec.py             # Legacy spec management
│   ├── memory.db           # SQLite persistent state
│   └── context/            # Session context files
│
├── docs/                   # 📚 DOCUMENTATION
│   ├── AGENTS.md           # Agent orchestration definitions
│   ├── CLAUDE.md           # Claude Code CLI configuration
│   ├── INSTALL.md          # Installation instructions
│   ├── RFD-PROTOCOL.md     # Core protocol specification
│   ├── @RFD-PROTOCOL.md    # Protocol summary
│   ├── RFD-PLAN.md         # Development roadmap
│   └── archive/            # Historical documents
│
├── tools/                  # 🔧 DEVELOPMENT TOOLS
│   ├── comprehensive_audit.py    # Codebase audit tool
│   └── detailed_bug_analysis.py  # Bug analysis tool
│
├── research/               # 📖 RESEARCH & BACKGROUND
│   ├── brain-dump.md       # Original problem statement
│   ├── CONSENSUS-FINAL.md  # Design decisions
│   └── round-*/            # Development phases
│
├── scripts/                # 📜 LEGACY SCRIPTS
│   └── [legacy tools]      # Historical development scripts
│
├── nexus_rfd_protocol/     # 🔄 TRANSITION PACKAGE
│   └── [legacy modules]    # Old package structure (being phased out)
│
├── .github/workflows/      # 🚀 CI/CD PIPELINE
│   ├── ci.yml             # Continuous integration
│   └── release.yml        # Automated releases
│
└── rfd -> .rfd/rfd.py     # 🔗 SYMLINK (legacy compatibility)
```

### Directory Purposes

#### Core Directories

- **`src/rfd/`**: Modern Python package following PEP standards. This is the main codebase.
- **`tests/`**: Comprehensive test suite with 90+ test functions across unit/integration/system categories.
- **`.rfd/`**: Legacy system directory for backward compatibility. Contains working database and CLI.

#### Documentation Directories

- **`docs/`**: Essential documentation and specifications.
- **`docs/archive/`**: Historical documents from development phases.
- **`research/`**: Background research and design decisions.

#### Development Directories

- **`tools/`**: Development and analysis tools.
- **`scripts/`**: Legacy development scripts.
- **`.github/workflows/`**: CI/CD automation.

#### Transition Directories

- **`nexus_rfd_protocol/`**: Old package structure being phased out.
- **`rfd` (symlink)**: Legacy CLI compatibility.

## Core Concepts

### Reality-First Principles

1. **Code that runs > Perfect architecture**
2. **Working features > Planned features**  
3. **Real data > Mocked responses**
4. **Passing tests > Theoretical correctness**

### Validation Engine

RFD continuously validates:
- ✅ Files actually exist (detects AI file creation lies)
- ✅ Functions are implemented (not just claimed)
- ✅ APIs respond correctly
- ✅ Tests pass with real data
- ✅ Build processes work

### Session Management

- **Persistent Context**: RFD maintains what you're working on across restarts
- **Memory**: AI remembers what worked/failed in previous sessions
- **Progress Tracking**: Visual progress through complex features
- **Auto-Recovery**: Continue from last checkpoint if interrupted

## Integration with Claude Code

RFD is designed to work seamlessly with [Claude Code](https://claude.ai/code):

1. **Install RFD** in your project: `rfd init`
2. **Claude Code reads** `CLAUDE.md` automatically
3. **AI follows RFD workflow** - validates every change
4. **Context persists** in `.rfd/context/memory.json`

### Example Claude Code Session

```bash
# AI automatically follows this workflow:
rfd check                    # Check current status
rfd build                    # Implement features  
rfd validate                 # Verify everything works
rfd checkpoint "Feature X"   # Save progress
```

## Command Reference

### Core Commands

```bash
rfd init                    # Initialize RFD in current directory
rfd check                   # Quick status check
rfd spec create            # Interactive spec creation
rfd spec review            # Review current specification
```

### Development Workflow

```bash
rfd session start <feature>  # Start working on a feature  
rfd build [feature]          # Build/compile feature
rfd validate [--feature X]  # Run validation tests
rfd checkpoint "message"     # Save working state
rfd session end             # Mark feature complete
```

### State Management

```bash
rfd revert                  # Revert to last checkpoint
rfd memory show            # Show AI memory
rfd memory reset           # Clear AI memory
```

## Specification Format

RFD uses YAML frontmatter in PROJECT.md as the single source of truth. See [PROJECT_SCHEMA.md](docs/PROJECT_SCHEMA.md) for complete schema documentation.

### Quick Schema Reference

```yaml
---
# Required Fields
name: "Project Name"
description: "Brief project description"
version: "1.0.0"

# Stack (extensible beyond these core fields)
stack:
  language: python          # Required
  framework: fastapi        # Required  
  database: postgresql      # Required
  runtime: python-3.11      # Optional
  package_manager: pip      # Optional
  test_framework: pytest    # Optional
  deployment: docker        # Optional

# Validation Rules
rules:
  max_files: 50
  max_loc_per_file: 500
  must_pass_tests: true
  no_mocks_in_prod: true
  min_test_coverage: 80     # Optional
  require_types: true       # Optional

# Features (at least 1 required)
features:
  - id: feature_id
    description: "What this feature does"
    acceptance: "How to verify it works"
    status: pending          # pending|building|testing|complete
    priority: high           # Optional: critical|high|medium|low
    depends_on: []           # Optional: feature dependencies

# Constraints (recommended)
constraints:
  - "Must support 1000 concurrent users"
  - "API response time < 200ms"
  - "GDPR compliant"
---

# Project Name

Detailed project documentation in markdown...
```

### Customizing Schema After Init

After running `rfd init`, you can modify PROJECT.md to:

1. **Extend the stack** - Add runtime, package_manager, deployment fields
2. **Add validation rules** - Set coverage requirements, complexity limits
3. **Define API contracts** - Document endpoints and schemas
4. **Set team info** - Track developers and responsibilities
5. **Create milestones** - Plan release schedules

Example: Adding custom stack fields:
```bash
# Edit PROJECT.md and add under stack:
stack:
  language: python
  framework: fastapi
  database: postgresql
  runtime: python-3.11        # Added
  package_manager: poetry      # Added
  deployment: kubernetes       # Added
  monitoring: prometheus       # Added
```

RFD automatically validates schema changes and preserves custom fields.

## Getting Started Guide

### For Brand New Projects

1. **Create project directory**:
   ```bash
   mkdir my-awesome-project
   cd my-awesome-project
   ```

2. **Initialize RFD**:
   ```bash
   rfd init
   ```
   This will walk you through:
   - Project name and description
   - Technology stack selection
   - Initial feature definitions
   - Acceptance criteria

3. **Review generated files**:
   - `PROJECT.md` - Your specification
   - `CLAUDE.md` - AI instructions
   - `PROGRESS.md` - Progress tracking

4. **Start developing**:
   ```bash
   rfd session start <first-feature>
   # Write code...
   rfd build
   rfd validate
   rfd checkpoint "First feature working"
   ```

### For Existing Projects

1. **Add RFD to existing project**:
   ```bash
   cd existing-project/
   rfd init
   ```

2. **RFD will analyze your project**:
   - Detect programming language
   - Identify build system
   - Suggest initial feature breakdown

3. **Define what you want to build**:
   - Edit generated `PROJECT.md`
   - Add acceptance criteria for features
   - Set validation rules

4. **Start RFD workflow**:
   ```bash
   rfd check                # See current state
   rfd session start <feature>
   # Continue development with RFD validation
   ```

### What You Need to Provide

#### Minimum Required:
- **Project goal**: What are you building?
- **Technology stack**: Language, framework, database
- **First feature**: What's the first thing you want working?

#### Recommended:
- **Acceptance criteria**: How do you know a feature is done?
- **Validation rules**: Max files, complexity limits
- **Test requirements**: What tests must pass?

## Technology Stack Support

RFD works with any stack by detecting your configuration:

- **Python**: FastAPI, Flask, Django, any framework
- **JavaScript/TypeScript**: Express, NestJS, Next.js, React, Vue
- **Go**: Gin, Echo, standard library
- **Rust**: Actix, Rocket, Axum
- **Java/Kotlin**: Spring Boot, Quarkus
- **C/C++**: Any build system
- **And 20+ more languages...**

## Development

### Running Tests

```bash
# All tests
pytest

# By category
pytest -m unit           # Fast unit tests
pytest -m integration    # Integration tests  
pytest -m system         # End-to-end tests

# With coverage
pytest --cov=src/rfd --cov-report=html
```

### Code Quality

```bash
# Linting
ruff check src tests

# Formatting
ruff format src tests

# Type checking (optional)
mypy src --ignore-missing-imports
```

## Troubleshooting

### Common Issues

**"No feature specified"**
```bash
rfd session start <feature_id>  # Start a session first
```

**"Validation failed"**
```bash
rfd validate                    # See what's failing
rfd build                       # Fix build issues first
```

**"Lost context"**
```bash
rfd check                       # See current state
cat .rfd/context/current.md     # Check session file
```

### Debug Mode

```bash
export RFD_DEBUG=1
rfd validate                    # Verbose output
```

### Legacy vs Modern CLI

We provide two CLI options:

- **Modern**: `rfd` (via pip install) - Uses src/rfd/ package
- **Legacy**: `./rfd` or `python .rfd/rfd.py` - Uses .rfd/ directory

Both provide the same functionality for backward compatibility.

## Architecture Decisions

### Why Both `docs/RFD-PROTOCOL.md` and `docs/@RFD-PROTOCOL.md`?

- **`docs/RFD-PROTOCOL.md`**: Complete protocol specification with all details
- **`docs/@RFD-PROTOCOL.md`**: Summary version for quick reference with @ prefix for Claude Code CLI

### Why Keep Legacy `.rfd/` Directory?

- **Backward Compatibility**: Existing projects using RFD continue working
- **Migration Path**: Gradual transition to modern package structure
- **Working Database**: Contains SQLite state and session data
- **Symlink Compatibility**: Legacy `./rfd` command still works

### Why Both `nexus_rfd_protocol/` and `src/rfd/`?

- **Transition Period**: Moving from old package name to new clean structure
- **Testing**: Ensuring both old and new imports work during transition
- **Release Safety**: No breaking changes for existing users

## Contributing

RFD Protocol is open source. Contributions welcome!

1. **Fork** the repository
2. **Create** a feature branch
3. **Use RFD** to develop your feature 😉
4. **Ensure tests pass**: `pytest`
5. **Submit** a pull request

### Development Setup

```bash
git clone https://github.com/kryptobaseddev/rfd-protocol.git
cd rfd-protocol
pip install -e ".[dev]"
pytest  # Run tests
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

- **GitHub Issues**: [Report bugs](https://github.com/kryptobaseddev/rfd-protocol/issues)
- **Documentation**: [Full docs](docs/)
- **Discord**: Coming soon

---

**Built with RFD Protocol** - This project was developed using its own reality-first methodology.

## Version History

- **v1.0.0**: Production release with modern Python packaging, comprehensive test suite, CI/CD pipeline, and full documentation.