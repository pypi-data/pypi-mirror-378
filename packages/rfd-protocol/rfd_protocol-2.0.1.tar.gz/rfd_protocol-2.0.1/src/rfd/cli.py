#!/usr/bin/env python3
"""
RFD CLI Entry Point
Command line interface for Reality-First Development Protocol
"""

import sys
import sqlite3
import json
import subprocess
from pathlib import Path
from datetime import datetime
import click
import frontmatter
from typing import Dict, Any, Optional

from .rfd import RFD
from . import __version__

@click.group()
@click.version_option(version=__version__, prog_name='rfd')
@click.pass_context
def cli(ctx):
    """RFD: Reality-First Development System"""
    ctx.obj = RFD()

@cli.command()
@click.pass_obj
def init(rfd):
    """Initialize RFD in current directory"""
    click.echo("🚀 Initializing RFD System...")
    
    # Create default files if not exist
    files_created = []
    
    # PROJECT.md template
    if not Path('PROJECT.md').exists():
        rfd.spec.create_interactive()
        files_created.append('PROJECT.md')
    
    # CLAUDE.md for Claude Code CLI
    if not Path('CLAUDE.md').exists():
        create_claude_md()
        files_created.append('CLAUDE.md')
    
    # PROGRESS.md
    if not Path('PROGRESS.md').exists():
        Path('PROGRESS.md').write_text("# Build Progress\n\n")
        files_created.append('PROGRESS.md')
    
    click.echo(f"✅ RFD initialized! Created: {', '.join(files_created)}")
    click.echo("\n→ Next: rfd spec review")

@cli.command()
@click.argument('action', type=click.Choice(['create', 'review', 'validate']))
@click.pass_obj
def spec(rfd, action):
    """Manage project specification"""
    if action == 'create':
        rfd.spec.create_interactive()
    elif action == 'review':
        rfd.spec.review()
    elif action == 'validate':
        rfd.spec.validate()

@cli.command()
@click.argument('feature_id', required=False)
@click.pass_obj
def build(rfd, feature_id):
    """Run build process for feature"""
    if not feature_id:
        feature_id = rfd.session.get_current_feature()
    
    if not feature_id:
        click.echo("❌ No feature specified. Use: rfd session start <feature>")
        return
    
    click.echo(f"🔨 Building feature: {feature_id}")
    success = rfd.builder.build_feature(feature_id)
    
    if success:
        click.echo("✅ Build successful!")
        rfd.checkpoint(f"Build passed for {feature_id}")
    else:
        click.echo("❌ Build failed - check errors above")

@cli.command()
@click.option('--feature', help='Validate specific feature')
@click.option('--full', is_flag=True, help='Full validation')
@click.pass_obj
def validate(rfd, feature, full):
    """Validate current implementation"""
    results = rfd.validator.validate(feature=feature, full=full)
    rfd.validator.print_report(results)
    
    if not results['passing']:
        sys.exit(1)

@cli.command()
@click.pass_obj
def check(rfd):
    """Quick health check"""
    state = rfd.get_current_state()
    
    # Quick status
    click.echo("\n=== RFD Status Check ===\n")
    
    # Validation
    val = state['validation']
    click.echo(f"📋 Validation: {'✅' if val['passing'] else '❌'}")
    
    # Build
    build = state['build']
    click.echo(f"🔨 Build: {'✅' if build['passing'] else '❌'}")
    
    # Current session
    session = state['session']
    if session:
        click.echo(f"📝 Session: {session['feature_id']} (started {session['started_at']})")
    
    # Features
    click.echo(f"\n📦 Features:")
    for fid, status, checkpoints in state['features']:
        icon = '✅' if status == 'complete' else '🔨' if status == 'building' else '⭕'
        click.echo(f"  {icon} {fid} ({checkpoints} checkpoints)")
    
    # Next action
    click.echo(f"\n→ Next: {rfd.session.suggest_next_action()}")

@cli.group()
@click.pass_obj
def session(rfd):
    """Manage development sessions"""
    pass

@session.command('start')
@click.argument('feature_id')
@click.pass_obj
def session_start(rfd, feature_id):
    """Start new feature session"""
    try:
        rfd.session.start(feature_id)
        click.echo(f"🚀 Session started for: {feature_id}")
        click.echo(f"📋 Context updated at: .rfd/context/current.md")
        click.echo(f"\n→ Next: rfd build")
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@session.command('end')
@click.option('--success/--failed', default=True)
@click.pass_obj
def session_end(rfd, success):
    """End current session"""
    session_id = rfd.session.end(success=success)
    if session_id:
        click.echo(f"📝 Session {session_id} ended")

@cli.command()
@click.argument('message')
@click.pass_obj
def checkpoint(rfd, message):
    """Save checkpoint with current state"""
    # Get current state
    validation = rfd.validator.validate()
    build = rfd.builder.get_status()
    
    # Git commit
    try:
        git_hash = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True, text=True
        ).stdout.strip()
    except:
        git_hash = "no-git"
    
    # Save checkpoint
    conn = sqlite3.connect(rfd.db_path)
    conn.execute("""
        INSERT INTO checkpoints (feature_id, timestamp, validation_passed, 
                                build_passed, git_hash, evidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        rfd.session.get_current_feature(),
        datetime.now().isoformat(),
        validation['passing'],
        build['passing'],
        git_hash,
        json.dumps({'message': message, 'validation': validation, 'build': build})
    ))
    conn.commit()
    
    # Update PROGRESS.md
    with open('PROGRESS.md', 'a') as f:
        f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} - Checkpoint\n")
        f.write(f"MESSAGE: {message}\n")
        f.write(f"VALIDATION: {'✅' if validation['passing'] else '❌'}\n")
        f.write(f"BUILD: {'✅' if build['passing'] else '❌'}\n")
        f.write(f"COMMIT: {git_hash[:7]}\n")
    
    click.echo(f"✅ Checkpoint saved: {message}")

@cli.command()
@click.pass_obj
def revert(rfd):
    """Revert to last working checkpoint"""
    success, message = rfd.revert_to_last_checkpoint()
    
    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}")

@cli.group()
@click.pass_obj
def memory(rfd):
    """Manage AI memory"""
    pass

@memory.command('show')
@click.pass_obj
def memory_show(rfd):
    """Show current AI memory"""
    memory_file = rfd.rfd_dir / 'context' / 'memory.json'
    if memory_file.exists():
        data = json.loads(memory_file.read_text())
        click.echo(json.dumps(data, indent=2))

@memory.command('reset')
@click.pass_obj
def memory_reset(rfd):
    """Reset AI memory"""
    memory_file = rfd.rfd_dir / 'context' / 'memory.json'
    memory_file.write_text('{}')
    click.echo("✅ Memory reset")

def create_claude_md():
    """Create CLAUDE.md for Claude Code CLI"""
    content = """---
# Claude Code Configuration
model: claude-3-5-sonnet-20241022
temperature: 0.2
max_tokens: 4000
tools: enabled
memory: .rfd/context/memory.json
---

# RFD Project Assistant

You are operating in a Reality-First Development (RFD) project. Your ONLY job is to make tests pass.

## Critical Rules
1. Read @PROJECT.md for the specification
2. Check @.rfd/context/current.md for your current task
3. Read @PROGRESS.md for what's already done
4. Run `rfd check` before ANY changes
5. Every code change MUST improve `rfd validate` output
6. NEVER mock data - use real implementations
7. NEVER add features not in @PROJECT.md

## Workflow for Every Response

### 1. Check Current State
```bash
rfd check
```

### 2. Read Context
- @PROJECT.md - What we're building
- @.rfd/context/current.md - Current feature/task
- @PROGRESS.md - What already works

### 3. Write Code
- Minimal code to fix the FIRST failing test
- Complete, runnable code only
- No explanations, just code that works

### 4. Validate
```bash
rfd build && rfd validate
```

### 5. Checkpoint Success
```bash
rfd checkpoint "Fixed: [describe what you fixed]"
```

### 6. Move to Next
Check @.rfd/context/current.md for next failing test. Repeat.

## Your Memory
- Located at @.rfd/context/memory.json
- Automatically loaded/saved
- Remembers what you've tried
- Tracks what works/doesn't

## Never Forget
- You're fixing tests, not designing architecture
- If tests pass, you're done
- If tests fail, fix them
- Reality (passing tests) > Theory (perfect code)
"""
    Path('CLAUDE.md').write_text(content)

def main():
    """Main entry point for the CLI"""
    cli()

if __name__ == '__main__':
    main()