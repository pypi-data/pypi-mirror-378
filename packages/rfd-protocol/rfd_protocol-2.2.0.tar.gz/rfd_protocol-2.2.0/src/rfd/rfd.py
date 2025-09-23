#!/usr/bin/env python3
"""
RFD: Reality-First Development System
Single entry point for all development operations
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

from .build import BuildEngine
from .validation import ValidationEngine
from .spec import SpecEngine
from .session import SessionManager
from .project_updater import ProjectUpdater

class RFD:
    """Main RFD orchestrator - coordinates all subsystems"""
    
    def __init__(self):
        self.root = Path.cwd()
        self.rfd_dir = self.root / '.rfd'
        self.db_path = self.rfd_dir / 'memory.db'
        
        # Initialize subsystems
        self._init_structure()
        self._init_database()
        
        # Load modules with proper imports
        self.builder = BuildEngine(self)
        self.validator = ValidationEngine(self)
        self.spec = SpecEngine(self)
        self.session = SessionManager(self)
        self.project_updater = ProjectUpdater(self)
    
    def _init_structure(self):
        """Create RFD directory structure"""
        self.rfd_dir.mkdir(exist_ok=True)
        (self.rfd_dir / 'context').mkdir(exist_ok=True)
        (self.rfd_dir / 'context' / 'checkpoints').mkdir(exist_ok=True)
    
    def _init_database(self):
        """Initialize SQLite for state management"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Core tables
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS features (
                id TEXT PRIMARY KEY,
                description TEXT,
                acceptance_criteria TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                completed_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY,
                feature_id TEXT,
                timestamp TEXT,
                validation_passed BOOLEAN,
                build_passed BOOLEAN,
                git_hash TEXT,
                evidence JSON
            );
            
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                started_at TEXT,
                ended_at TEXT,
                feature_id TEXT,
                success BOOLEAN,
                changes JSON,
                errors JSON
            );
            
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value JSON,
                updated_at TEXT
            );
        """)
            conn.commit()
        finally:
            conn.close()
    
    def load_project_spec(self) -> Dict[str, Any]:
        """Load and parse PROJECT.md"""
        project_file = self.root / 'PROJECT.md'
        if not project_file.exists():
            return {}
        
        with open(project_file, 'r') as f:
            content = f.read()
            
        # Try frontmatter format first
        try:
            post = frontmatter.loads(content)
            if post.metadata:
                return post.metadata
        except:
            pass
            
        # Try to find JSON in the content
        try:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
            
        # Return empty dict if no valid format found
        return {}
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get complete current project state"""
        return {
            'spec': self.load_project_spec(),
            'validation': self.validator.get_status(),
            'build': self.builder.get_status(),
            'session': self.session.get_current(),
            'features': self.get_features_status()
        }
    
    def get_features_status(self) -> list:
        """Get status of all features"""
        conn = sqlite3.connect(self.db_path)
        try:
            return conn.execute("""
            SELECT id, status, 
                   (SELECT COUNT(*) FROM checkpoints 
                    WHERE feature_id = features.id 
                    AND validation_passed = 1) as passing_checkpoints
            FROM features
            ORDER BY created_at
        """).fetchall()
        finally:
            conn.close()

    def checkpoint(self, message: str):
        """Save checkpoint with current state"""
        # Get current state
        validation = self.validator.validate()
        build = self.builder.get_status()
        
        # Git commit
        try:
            git_hash = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True
            ).stdout.strip()
        except:
            git_hash = "no-git"
        
        # Save checkpoint
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
            INSERT INTO checkpoints (feature_id, timestamp, validation_passed, 
                                    build_passed, git_hash, evidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.session.get_current_feature(),
            datetime.now().isoformat(),
            validation['passing'],
            build['passing'],
            git_hash,
            json.dumps({'message': message, 'validation': validation, 'build': build})
        ))
            conn.commit()
        finally:
            conn.close()
        
        # Update PROGRESS.md
        progress_file = self.root / 'PROGRESS.md'
        with open(progress_file, 'a') as f:
            f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} - Checkpoint\n")
            f.write(f"MESSAGE: {message}\n")
            f.write(f"VALIDATION: {'✅' if validation['passing'] else '❌'}\n")
            f.write(f"BUILD: {'✅' if build['passing'] else '❌'}\n")
            f.write(f"COMMIT: {git_hash[:7]}\n")

    def revert_to_last_checkpoint(self):
        """Revert to last working checkpoint"""
        conn = sqlite3.connect(self.db_path)
        try:
            # CRITICAL FIX: Allow revert with validation-only checkpoints
            # Try to find a checkpoint with both validation AND build passing
            last_good = conn.execute("""
            SELECT git_hash, timestamp, validation_passed, build_passed FROM checkpoints
            WHERE validation_passed = 1 AND build_passed = 1
            ORDER BY id DESC LIMIT 1
            """).fetchone()
            
            # If no perfect checkpoint, try validation-only
            if not last_good:
                last_good = conn.execute("""
                    SELECT git_hash, timestamp, validation_passed, build_passed FROM checkpoints
                    WHERE validation_passed = 1
                    ORDER BY id DESC LIMIT 1
                """).fetchone()
            
            if not last_good:
                return False, "No checkpoint with passing validation found"
            
            git_hash, timestamp, val_passed, build_passed = last_good
            
            # Git revert
            try:
                subprocess.run(['git', 'reset', '--hard', git_hash], check=True)
                status = "validation+build" if build_passed else "validation-only"
                return True, f"Reverted to {status} checkpoint from {timestamp} (Git hash: {git_hash[:7]})"
            except subprocess.CalledProcessError:
                return False, "Git revert failed"
        finally:
            conn.close()