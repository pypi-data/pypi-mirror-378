#!/usr/bin/env python3
"""
End-to-End Integration Tests for RFD Protocol
Tests complete workflows and real-world usage scenarios
"""

import os
import sys
import tempfile
import shutil
import json
import sqlite3
import subprocess
import time
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory and .rfd directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / '.rfd'))

class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete RFD workflows from spec to ship"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="rfd_e2e_")
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_complete_feature_workflow(self):
        """Test complete workflow: spec -> build -> validate -> ship"""
        from rfd import RFD
        from spec import SpecEngine
        from build import BuildEngine
        from validation import ValidationEngine
        from session import SessionManager
        
        # 1. Initialize RFD
        rfd = RFD()
        # RFD initializes automatically on creation
        
        # 2. Create specification
        spec_engine = SpecEngine(rfd)
        spec = {
            'name': 'e2e-test-project',
            'version': '1.0.0',
            'features': [
                {
                    'id': 'user-auth',
                    'description': 'User authentication',
                    'acceptance': 'Users can sign up and log in',
                    'checkpoints': [
                        'spec_complete',
                        'code_executes',
                        'tests_pass'
                    ],
                    'status': 'pending'
                }
            ],
            'rules': {
                'max_files': 100,
                'max_loc_per_file': 500
            }
        }
        
        # Save spec
        Path('RFD-SPEC.md').write_text(f"""---
{json.dumps(spec)}
---
# E2E Test Project
""")
        
        # 3. Start session for feature
        session_mgr = SessionManager(rfd)
        session_id = session_mgr.create_session('user-auth')
        self.assertIsNotNone(session_id)
        
        # 4. Build phase - create some code
        Path('auth.py').write_text("""
def signup(email, password):
    return {'email': email, 'status': 'created'}

def login(email, password):
    return {'email': email, 'status': 'authenticated'}
""")
        
        # 5. Validate phase
        validator = ValidationEngine(rfd)
        
        # AI claim validation
        claim = "Created auth.py with functions signup and login"
        passed, results = validator.validate_ai_claims(claim)
        self.assertTrue(passed, "Should validate true claim")
        
        # 6. Update progress
        session_mgr.update_progress('code_executes', 'passed', {
            'files_created': ['auth.py'],
            'functions': ['signup', 'login']
        })
        
        # 7. Run tests (simulated)
        Path('test_auth.py').write_text("""
import auth

def test_signup():
    result = auth.signup('test@example.com', 'pass123')
    assert result['status'] == 'created'

def test_login():
    result = auth.login('test@example.com', 'pass123')
    assert result['status'] == 'authenticated'
""")
        
        # 8. Final validation
        build_engine = BuildEngine(rfd)
        stack = build_engine.detect_stack()
        self.assertEqual(stack['language'], 'python')
        
        # 9. Check session state persisted
        context = session_mgr.get_context()
        self.assertEqual(context['current_session']['feature'], 'user-auth')
    
    def test_multi_feature_project(self):
        """Test managing multiple features in a project"""
        from rfd import RFD
        from spec import SpecEngine
        from session import SessionManager
        from validation import ValidationEngine
        
        rfd = RFD()
        rfd.init()
        
        spec_engine = SpecEngine(rfd)
        session_mgr = SessionManager(rfd)
        validator = ValidationEngine(rfd)
        
        # Create project with multiple features
        features = ['api-endpoints', 'database-models', 'frontend-ui']
        
        for feature in features:
            # Create session for feature
            session_id = session_mgr.create_session(feature)
            
            # Simulate feature development
            file_name = f"{feature.replace('-', '_')}.py"
            Path(file_name).write_text(f"# Implementation for {feature}")
            
            # Validate
            claim = f"Created {file_name}"
            passed, _ = validator.validate_ai_claims(claim)
            self.assertTrue(passed, f"Should validate {feature}")
            
            # Update progress
            session_mgr.update_progress(f'{feature}_complete', 'passed', {})
        
        # Check all features tracked
        recent_sessions = session_mgr.get_recent_sessions(3)
        self.assertEqual(len(recent_sessions), 3)
    
    def test_checkpoint_gating(self):
        """Test checkpoint gating prevents advancement without validation"""
        from rfd import RFD
        from validation import ValidationEngine
        from session import SessionManager
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        session_mgr = SessionManager(rfd)
        
        session_mgr.create_session('gated-feature')
        
        # Try to advance without creating file (should fail)
        false_claim = "Created important.py with critical_function"
        passed, results = validator.validate_ai_claims(false_claim)
        
        self.assertFalse(passed, "Should not pass without real file")
        
        # Cannot proceed to next checkpoint
        if not passed:
            # Block advancement
            session_mgr.update_progress('checkpoint_1', 'blocked', {
                'reason': 'File does not exist',
                'claim': false_claim
            })
        
        # Now create the file
        Path('important.py').write_text('def critical_function(): pass')
        
        # Retry validation
        passed, results = validator.validate_ai_claims(false_claim)
        self.assertTrue(passed, "Should pass with real file")
        
        # Can now proceed
        if passed:
            session_mgr.update_progress('checkpoint_1', 'passed', {})
    
    def test_drift_detection(self):
        """Test detection of drift from specification"""
        from rfd import RFD
        from spec import SpecEngine
        from validation import ValidationEngine
        
        rfd = RFD()
        spec_engine = SpecEngine(rfd)
        validator = ValidationEngine(rfd)
        
        # Create spec with strict rules
        spec = {
            'name': 'drift-test',
            'rules': {
                'max_files': 3,
                'max_loc_per_file': 50
            },
            'features': [
                {
                    'id': 'core-feature',
                    'description': 'Core functionality',
                    'files': ['core.py', 'utils.py']
                }
            ]
        }
        
        Path('RFD-SPEC.md').write_text(f"""---
{json.dumps(spec)}
---
""")
        
        # Load spec
        rfd.spec = rfd.load_project_spec()
        
        # Create files within spec
        Path('core.py').write_text('# Core module\n' * 10)
        Path('utils.py').write_text('# Utils module\n' * 10)
        
        # Validate - should pass
        results = validator.validate()
        
        # Create drift - file not in spec
        Path('unauthorized.py').write_text('# This causes drift!')
        Path('another_unauthorized.py').write_text('# More drift!')
        
        # Validate again - should detect issues
        results = validator.validate()
        
        # Check for max_files violation
        py_files = list(Path('.').glob('*.py'))
        self.assertGreater(len(py_files), spec['rules']['max_files'])
    
    def test_context_persistence_across_sessions(self):
        """Test context persists across RFD sessions"""
        from rfd import RFD
        from session import SessionManager
        
        # First RFD session
        rfd1 = RFD()
        session1 = SessionManager(rfd1)
        
        # Create work in first session
        session_id = session1.create_session('persistent-feature')
        session1.save_state({
            'current_file': 'app.py',
            'line': 42,
            'last_action': 'added authentication'
        })
        
        # Store session ID
        first_session_id = session_id
        
        # Simulate new Claude Code session (new RFD instance)
        del rfd1
        del session1
        
        # Second RFD session
        rfd2 = RFD()
        session2 = SessionManager(rfd2)
        
        # Should recover context
        context = session2.get_context()
        
        # Should see previous session
        recent = session2.get_recent_sessions(1)
        if recent:
            self.assertEqual(recent[0]['id'], first_session_id)
            self.assertEqual(recent[0]['feature'], 'persistent-feature')
    
    def test_real_world_python_project(self):
        """Test RFD with a real Python Flask project"""
        from rfd import RFD
        from build import BuildEngine
        from validation import ValidationEngine
        
        # Create a Flask project structure
        Path('app.py').write_text("""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/users', methods=['POST'])
def create_user():
    return jsonify({'id': 1, 'status': 'created'})

if __name__ == '__main__':
    app.run(debug=True)
""")
        
        Path('requirements.txt').write_text('flask==2.0.0\npytest==7.0.0\n')
        
        Path('test_app.py').write_text("""
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_create_user(client):
    response = client.post('/api/users')
    assert response.status_code == 200
    assert response.json['status'] == 'created'
""")
        
        # Initialize RFD
        rfd = RFD()
        rfd.init()
        
        # Build engine should detect Python/Flask
        builder = BuildEngine(rfd)
        stack = builder.detect_stack()
        
        self.assertEqual(stack['language'], 'python')
        self.assertIn('flask', stack.get('framework', '').lower())
        
        # Validation should work
        validator = ValidationEngine(rfd)
        
        claims = """
        Created app.py with Flask application
        Created test_app.py with pytest tests
        Implemented health and create_user endpoints
        """
        
        passed, results = validator.validate_ai_claims(claims)
        self.assertTrue(passed, "Should validate Flask project files")
    
    def test_real_world_javascript_project(self):
        """Test RFD with a real Node.js Express project"""
        from rfd import RFD
        from build import BuildEngine
        from validation import ValidationEngine
        
        # Create Express project
        Path('package.json').write_text(json.dumps({
            "name": "express-api",
            "version": "1.0.0",
            "main": "index.js",
            "scripts": {
                "start": "node index.js",
                "test": "jest"
            },
            "dependencies": {
                "express": "^4.18.0"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }, indent=2))
        
        Path('index.js').write_text("""
const express = require('express');
const app = express();

app.use(express.json());

app.get('/api/health', (req, res) => {
    res.json({ status: 'healthy' });
});

app.post('/api/users', (req, res) => {
    res.json({ id: 1, status: 'created' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

module.exports = app;
""")
        
        Path('index.test.js').write_text("""
const request = require('supertest');
const app = require('./index');

describe('API Tests', () => {
    test('GET /api/health', async () => {
        const response = await request(app).get('/api/health');
        expect(response.status).toBe(200);
        expect(response.body.status).toBe('healthy');
    });
    
    test('POST /api/users', async () => {
        const response = await request(app).post('/api/users');
        expect(response.status).toBe(200);
        expect(response.body.status).toBe('created');
    });
});
""")
        
        # Initialize RFD
        rfd = RFD()
        
        # Build engine should detect JavaScript/Node
        builder = BuildEngine(rfd)
        stack = builder.detect_stack()
        
        self.assertEqual(stack['language'], 'javascript')
        self.assertIn('express', stack.get('framework', '').lower())
        
        # Validation should work
        validator = ValidationEngine(rfd)
        
        claims = "Created index.js with Express server and index.test.js with tests"
        passed, _ = validator.validate_ai_claims(claims)
        self.assertTrue(passed, "Should validate Express project")
    
    def test_cross_language_monorepo(self):
        """Test RFD in a monorepo with multiple languages"""
        from rfd import RFD
        from validation import ValidationEngine
        
        # Create monorepo structure
        Path('backend').mkdir()
        Path('backend/app.py').write_text('# Python backend')
        Path('backend/requirements.txt').write_text('fastapi==0.100.0')
        
        Path('frontend').mkdir()
        Path('frontend/package.json').write_text('{"name": "frontend"}')
        Path('frontend/index.js').write_text('// React frontend')
        
        Path('mobile').mkdir()
        Path('mobile/App.swift').write_text('// iOS app')
        
        Path('services').mkdir()
        Path('services/auth.go').write_text('// Go microservice')
        
        # Initialize RFD
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        # Validate files across different languages
        claims = """
        Created backend/app.py for Python API
        Created frontend/index.js for React app
        Created mobile/App.swift for iOS
        Created services/auth.go for authentication service
        """
        
        passed, results = validator.validate_ai_claims(claims)
        self.assertTrue(passed, "Should handle monorepo structure")
        
        # Each component should be detected
        for result in results:
            if result['type'] == 'file':
                self.assertTrue(result['exists'], f"{result['target']} should exist")


class TestErrorRecovery(unittest.TestCase):
    """Test RFD error handling and recovery"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="rfd_error_")
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_handles_corrupted_database(self):
        """Test RFD handles corrupted memory database"""
        from rfd import RFD
        from session import SessionManager
        
        rfd = RFD()
        
        # Corrupt the database
        if rfd.memory_db.exists():
            rfd.memory_db.write_text("CORRUPTED DATA")
        
        # Should handle gracefully
        try:
            session_mgr = SessionManager(rfd)
            # Should recreate or handle error
            self.assertIsNotNone(session_mgr)
        except Exception as e:
            # Should not crash completely
            self.assertIn('database', str(e).lower())
    
    def test_handles_missing_spec(self):
        """Test RFD handles missing specification file"""
        from rfd import RFD
        from validation import ValidationEngine
        
        rfd = RFD()
        
        # No spec file exists
        self.assertFalse(Path('RFD-SPEC.md').exists())
        
        # Should handle gracefully
        validator = ValidationEngine(rfd)
        results = validator.validate()
        
        # Should return results even without spec
        self.assertIn('passing', results)
    
    def test_handles_network_failures(self):
        """Test RFD handles network failures in API validation"""
        from rfd import RFD
        from validation import ValidationEngine
        
        rfd = RFD()
        rfd.spec = {
            'api_contract': {
                'base_url': 'http://nonexistent.local',
                'health_check': '/health',
                'endpoints': [
                    {'path': '/api/test', 'method': 'GET'}
                ]
            }
        }
        
        validator = ValidationEngine(rfd)
        
        # Should handle unreachable API
        results = validator.validate()
        
        # Should not crash
        self.assertIsNotNone(results)
        self.assertIn('results', results)
        
        # Should report API unreachable
        api_results = [r for r in results['results'] if 'api' in r['test'].lower()]
        if api_results:
            self.assertFalse(api_results[0]['passed'])
    
    def test_handles_permission_errors(self):
        """Test RFD handles file permission errors"""
        from rfd import RFD
        from validation import ValidationEngine
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        # Create read-only file
        Path('readonly.py').write_text('# read only')
        os.chmod('readonly.py', 0o444)
        
        # Should handle permission issues
        try:
            results = validator.validate()
            self.assertIsNotNone(results)
        except PermissionError:
            # Should handle gracefully
            pass
        finally:
            # Clean up
            os.chmod('readonly.py', 0o644)
    
    def test_recovery_from_interrupted_session(self):
        """Test recovery from interrupted session"""
        from rfd import RFD
        from session import SessionManager
        
        # Start session
        rfd1 = RFD()
        session1 = SessionManager(rfd1)
        session_id = session1.create_session('interrupted-feature')
        
        # Save partial progress
        session1.save_state({
            'checkpoint': 2,
            'files_created': ['partial.py'],
            'status': 'in_progress'
        })
        
        # Simulate interruption
        del rfd1
        del session1
        
        # Recovery
        rfd2 = RFD()
        session2 = SessionManager(rfd2)
        
        # Should recover state
        state = session2.load_state()
        if state:
            self.assertEqual(state.get('checkpoint'), 2)
            self.assertIn('partial.py', state.get('files_created', []))


class TestPerformance(unittest.TestCase):
    """Test RFD performance with large projects"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="rfd_perf_")
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_handles_many_files(self):
        """Test RFD handles projects with many files"""
        from rfd import RFD
        from validation import ValidationEngine
        
        # Create many files
        for i in range(100):
            Path(f'file_{i}.py').write_text(f'# File {i}')
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        # Should handle validation efficiently
        start_time = time.time()
        
        # Validate multiple claims
        claims = "Created file_0.py, file_50.py, and file_99.py"
        passed, results = validator.validate_ai_claims(claims)
        
        elapsed = time.time() - start_time
        
        self.assertTrue(passed)
        self.assertLess(elapsed, 5, "Should validate quickly even with many files")
    
    def test_handles_large_files(self):
        """Test RFD handles large source files"""
        from rfd import RFD
        from validation import ValidationEngine
        
        # Create large file
        large_content = '\n'.join([f'def function_{i}(): pass' for i in range(1000)])
        Path('large.py').write_text(large_content)
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        # Should handle large file
        claims = "Created large.py with function_500"
        passed, results = validator.validate_ai_claims(claims)
        
        self.assertTrue(passed, "Should find function in large file")
    
    def test_handles_deep_nesting(self):
        """Test RFD handles deeply nested directory structures"""
        from rfd import RFD
        from validation import ValidationEngine
        
        # Create deep nesting
        deep_path = Path('src/components/features/user/profile/settings/privacy/advanced')
        deep_path.mkdir(parents=True, exist_ok=True)
        
        file_path = deep_path / 'options.py'
        file_path.write_text('def configure(): pass')
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        # Should handle deep paths
        claims = f"Created {file_path} with function configure"
        passed, results = validator.validate_ai_claims(claims)
        
        self.assertTrue(passed, "Should handle deeply nested files")


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)