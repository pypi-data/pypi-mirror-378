"""
PROJECT.md Auto-Updater for RFD
Maintains PROJECT.md as single source of truth
"""

import frontmatter
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class ProjectUpdater:
    """Updates PROJECT.md automatically while preserving user content"""
    
    def __init__(self, rfd):
        self.rfd = rfd
        self.project_file = Path('PROJECT.md')
        
    def update_feature_status(self, feature_id: str, new_status: str) -> bool:
        """Update a feature's status in PROJECT.md"""
        if not self.project_file.exists():
            return False
            
        # Load PROJECT.md
        with open(self.project_file, 'r') as f:
            post = frontmatter.load(f)
        
        # Update feature status
        features = post.metadata.get('features', [])
        updated = False
        
        for feature in features:
            if feature.get('id') == feature_id:
                feature['status'] = new_status
                if new_status == 'complete':
                    feature['completed_at'] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            # Save PROJECT.md
            with open(self.project_file, 'w') as f:
                f.write(frontmatter.dumps(post))
            return True
            
        return False
    
    def update_metrics(self) -> bool:
        """Update metrics section in PROJECT.md from database"""
        if not self.project_file.exists():
            return False
            
        # Load PROJECT.md
        with open(self.project_file, 'r') as f:
            post = frontmatter.load(f)
        
        # Calculate metrics from database
        conn = sqlite3.connect(self.rfd.db_path)
        
        # Total checkpoints
        total_checkpoints = conn.execute(
            "SELECT COUNT(*) FROM checkpoints"
        ).fetchone()[0]
        
        # Passing vs failing checkpoints
        passing_checkpoints = conn.execute(
            "SELECT COUNT(*) FROM checkpoints WHERE validation_passed = 1 AND build_passed = 1"
        ).fetchone()[0]
        
        failed_checkpoints = total_checkpoints - passing_checkpoints
        
        # Feature completion rate
        total_features = conn.execute(
            "SELECT COUNT(*) FROM features"
        ).fetchone()[0]
        
        completed_features = conn.execute(
            "SELECT COUNT(*) FROM features WHERE status = 'complete'"
        ).fetchone()[0]
        
        # Average feature time (in hours)
        avg_time_result = conn.execute("""
            SELECT AVG(
                CAST((julianday(completed_at) - julianday(created_at)) * 24 AS REAL)
            )
            FROM features 
            WHERE completed_at IS NOT NULL
        """).fetchone()[0]
        
        avg_feature_time = round(avg_time_result, 2) if avg_time_result else 0
        
        # Count drift incidents (validation failures)
        drift_incidents = conn.execute(
            "SELECT COUNT(*) FROM checkpoints WHERE validation_passed = 0"
        ).fetchone()[0]
        
        conn.close()
        
        # Update or create metrics section
        if 'metrics' not in post.metadata:
            post.metadata['metrics'] = {}
        
        post.metadata['metrics'].update({
            'total_checkpoints': total_checkpoints,
            'passing_checkpoints': passing_checkpoints,
            'failed_checkpoints': failed_checkpoints,
            'completed_features': completed_features,
            'total_features': total_features,
            'drift_incidents': drift_incidents,
            'avg_feature_time': avg_feature_time,
            'last_updated': datetime.now().isoformat()
        })
        
        # Save PROJECT.md
        with open(self.project_file, 'w') as f:
            f.write(frontmatter.dumps(post))
            
        return True
    
    def add_feature(self, feature: Dict[str, Any]) -> bool:
        """Add a new feature to PROJECT.md"""
        if not self.project_file.exists():
            return False
            
        # Load PROJECT.md
        with open(self.project_file, 'r') as f:
            post = frontmatter.load(f)
        
        # Add feature
        if 'features' not in post.metadata:
            post.metadata['features'] = []
        
        # Ensure required fields
        feature.setdefault('status', 'pending')
        feature.setdefault('created_at', datetime.now().isoformat())
        
        post.metadata['features'].append(feature)
        
        # Save PROJECT.md
        with open(self.project_file, 'w') as f:
            f.write(frontmatter.dumps(post))
            
        return True
    
    def update_stack(self, stack_updates: Dict[str, str]) -> bool:
        """Update technology stack configuration"""
        if not self.project_file.exists():
            return False
            
        # Load PROJECT.md
        with open(self.project_file, 'r') as f:
            post = frontmatter.load(f)
        
        # Update stack
        if 'stack' not in post.metadata:
            post.metadata['stack'] = {}
        
        post.metadata['stack'].update(stack_updates)
        
        # Save PROJECT.md
        with open(self.project_file, 'w') as f:
            f.write(frontmatter.dumps(post))
            
        return True
    
    def add_milestone(self, milestone: Dict[str, Any]) -> bool:
        """Add a milestone to PROJECT.md"""
        if not self.project_file.exists():
            return False
            
        # Load PROJECT.md
        with open(self.project_file, 'r') as f:
            post = frontmatter.load(f)
        
        # Add milestone
        if 'milestones' not in post.metadata:
            post.metadata['milestones'] = []
        
        post.metadata['milestones'].append(milestone)
        
        # Save PROJECT.md
        with open(self.project_file, 'w') as f:
            f.write(frontmatter.dumps(post))
            
        return True
    
    def validate_and_fix(self) -> Dict[str, Any]:
        """Validate PROJECT.md and fix common issues"""
        if not self.project_file.exists():
            return {'valid': False, 'error': 'PROJECT.md not found'}
        
        # Load PROJECT.md
        with open(self.project_file, 'r') as f:
            post = frontmatter.load(f)
        
        issues_fixed = []
        
        # Ensure required fields exist
        required_fields = ['name', 'description', 'version', 'stack', 'rules', 'features']
        for field in required_fields:
            if field not in post.metadata:
                if field == 'name':
                    post.metadata['name'] = Path.cwd().name
                    issues_fixed.append(f"Added missing name: {post.metadata['name']}")
                elif field == 'description':
                    post.metadata['description'] = "Project description"
                    issues_fixed.append("Added placeholder description")
                elif field == 'version':
                    post.metadata['version'] = "0.1.0"
                    issues_fixed.append("Added default version 0.1.0")
                elif field == 'stack':
                    post.metadata['stack'] = {
                        'language': 'python',
                        'framework': 'none',
                        'database': 'sqlite'
                    }
                    issues_fixed.append("Added default stack configuration")
                elif field == 'rules':
                    post.metadata['rules'] = {
                        'max_files': 100,
                        'max_loc_per_file': 1000,
                        'must_pass_tests': True,
                        'no_mocks_in_prod': True
                    }
                    issues_fixed.append("Added default validation rules")
                elif field == 'features':
                    post.metadata['features'] = []
                    issues_fixed.append("Added empty features list")
        
        # Ensure stack has required fields
        stack_required = ['language', 'framework', 'database']
        if 'stack' in post.metadata:
            for field in stack_required:
                if field not in post.metadata['stack']:
                    if field == 'language':
                        post.metadata['stack']['language'] = 'python'
                    elif field == 'framework':
                        post.metadata['stack']['framework'] = 'none'
                    elif field == 'database':
                        post.metadata['stack']['database'] = 'sqlite'
                    issues_fixed.append(f"Added missing stack.{field}")
        
        # Save if we fixed anything
        if issues_fixed:
            with open(self.project_file, 'w') as f:
                f.write(frontmatter.dumps(post))
        
        return {
            'valid': True,
            'issues_fixed': issues_fixed,
            'metadata': post.metadata
        }
    
    def sync_with_database(self) -> Dict[str, Any]:
        """Sync PROJECT.md with database state"""
        if not self.project_file.exists():
            return {'success': False, 'error': 'PROJECT.md not found'}
        
        # Load PROJECT.md
        with open(self.project_file, 'r') as f:
            post = frontmatter.load(f)
        
        conn = sqlite3.connect(self.rfd.db_path)
        changes = []
        
        # Sync features
        db_features = conn.execute("""
            SELECT id, description, acceptance_criteria, status, created_at, completed_at
            FROM features
        """).fetchall()
        
        project_features = {f['id']: f for f in post.metadata.get('features', [])}
        
        for db_id, desc, accept, status, created, completed in db_features:
            if db_id in project_features:
                # Update existing feature
                feature = project_features[db_id]
                if feature.get('status') != status:
                    feature['status'] = status
                    changes.append(f"Updated {db_id} status to {status}")
                if completed and not feature.get('completed_at'):
                    feature['completed_at'] = completed
                    changes.append(f"Added completion time for {db_id}")
            else:
                # Add missing feature
                new_feature = {
                    'id': db_id,
                    'description': desc or "No description",
                    'acceptance': accept or "No criteria",
                    'status': status,
                    'created_at': created
                }
                if completed:
                    new_feature['completed_at'] = completed
                post.metadata.setdefault('features', []).append(new_feature)
                changes.append(f"Added missing feature {db_id} from database")
        
        conn.close()
        
        # Update metrics
        self.update_metrics()
        changes.append("Updated metrics")
        
        # Save changes
        if changes:
            with open(self.project_file, 'w') as f:
                f.write(frontmatter.dumps(post))
        
        return {
            'success': True,
            'changes': changes,
            'features_synced': len(db_features)
        }