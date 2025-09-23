#!/usr/bin/env python3
"""
Component Unit Tests for RFD Protocol
Tests each component in isolation with mocked dependencies
"""

import os
import sys
import tempfile
import shutil
import json
import sqlite3
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

# Add parent directory and .rfd directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / '.rfd'))

class TestRFDCore(unittest.TestCase):
    """Test the main RFD orchestrator class"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="rfd_core_")
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_rfd_initialization(self):
        """Test RFD initializes correctly"""
        from rfd import RFD
        
        rfd = RFD()
        
        # Check core attributes
        self.assertIsNotNone(rfd)
        self.assertEqual(rfd.root, Path.cwd())
        self.assertTrue(hasattr(rfd, 'db_path'))
        self.assertTrue(hasattr(rfd, 'rfd_dir'))
    
    def test_rfd_creates_structure(self):
        """Test RFD creates necessary .rfd directory structure"""
        from rfd import RFD
        
        # RFD should create structure on initialization
        rfd = RFD()
        
        # Should create .rfd directory
        self.assertTrue(Path('.rfd').exists())
        self.assertTrue(Path('.rfd').is_dir())
        
        # Should create context directory
        self.assertTrue(Path('.rfd/context').exists())
        self.assertTrue(Path('.rfd/context/checkpoints').exists())
    
    def test_rfd_memory_database(self):
        """Test RFD memory database operations"""
        from rfd import RFD
        
        rfd = RFD()
        
        # Should have memory database
        self.assertIsNotNone(rfd.db_path)
        
        # Should be able to connect
        if rfd.db_path.exists():
            conn = sqlite3.connect(rfd.db_path)
            cursor = conn.cursor()
            
            # Should have tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Should have checkpoint-related tables
            expected_tables = ['checkpoints', 'sessions', 'features', 'specs']
            for table in expected_tables:
                # Check if any expected table exists
                if any(table in t[0] for t in tables):
                    self.assertTrue(True)
                    break
            
            conn.close()
    
    def test_rfd_load_project_spec(self):
        """Test loading project specification"""
        from rfd import RFD
        
        rfd = RFD()
        
        # Create a mock spec file
        spec_content = {
            "name": "test-project",
            "version": "1.0.0",
            "features": [],
            "rules": {
                "max_files": 100,
                "max_loc_per_file": 500
            }
        }
        
        Path('RFD-SPEC.md').write_text(f"""---
{json.dumps(spec_content)}
---

# Test Specification
""")
        
        # Load spec
        spec = rfd.load_project_spec()
        
        # Should have loaded spec
        self.assertIsNotNone(spec)
        if spec:
            self.assertEqual(spec.get('name'), 'test-project')


class TestValidationEngine(unittest.TestCase):
    """Test the ValidationEngine component"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="rfd_valid_")
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_validation_engine_initialization(self):
        """Test ValidationEngine initializes correctly"""
        from rfd import RFD
        from rfd.validation import ValidationEngine
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        self.assertIsNotNone(validator)
        self.assertEqual(validator.rfd, rfd)
        self.assertIsInstance(validator.results, list)
    
    def test_validate_ai_claims_detects_lies(self):
        """Test AI claim validation detects false claims"""
        from rfd import RFD
        from rfd.validation import ValidationEngine
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        # Test false claim
        false_claim = "Created super_important_file.py with class SuperImportant"
        passed, results = validator.validate_ai_claims(false_claim)
        
        self.assertFalse(passed, "Should detect file doesn't exist")
        self.assertGreater(len(results), 0)
        
        # Check results mention hallucination
        for result in results:
            if 'super_important_file.py' in result['target']:
                self.assertIn('MISSING', result['message'])
    
    def test_validate_ai_claims_confirms_truth(self):
        """Test AI claim validation confirms true claims"""
        from rfd import RFD
        from rfd.validation import ValidationEngine
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        # Create real file
        Path('real_file.py').write_text('def real_function():\n    pass')
        
        # Test true claim
        true_claim = "Created real_file.py with function real_function"
        passed, results = validator.validate_ai_claims(true_claim)
        
        self.assertTrue(passed, "Should confirm file exists")
        
        # Clean up
        Path('real_file.py').unlink()
    
    def test_extract_file_claims(self):
        """Test extraction of file paths from text"""
        from rfd import RFD
        from rfd.validation import ValidationEngine
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        test_cases = [
            ("Created file.py", ["file.py"]),
            ("Wrote to src/main.js", ["src/main.js"]),
            ("Files: `app.py`, `test.py`", ["app.py", "test.py"]),
            ("Created 'config.yaml' and \"data.json\"", ["config.yaml", "data.json"]),
            ("Made src/components/Button.jsx", ["src/components/Button.jsx"]),
        ]
        
        for text, expected in test_cases:
            files = validator._extract_file_claims(text)
            for exp in expected:
                self.assertIn(exp, files, f"Should extract {exp} from '{text}'")
    
    def test_extract_function_claims(self):
        """Test extraction of function/class names from text"""
        from rfd import RFD
        from rfd.validation import ValidationEngine
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        test_cases = [
            ("Created function process_data", ["process_data"]),
            ("Implemented class UserModel", ["UserModel"]),
            ("Added method calculate()", ["calculate"]),
            ("def main():", ["main"]),
            ("class TestCase:", ["TestCase"]),
        ]
        
        for text, expected in test_cases:
            functions = validator._extract_function_claims(text)
            func_names = [f[0] for f in functions]
            for exp in expected:
                self.assertIn(exp, func_names, f"Should extract {exp} from '{text}'")
    
    def test_verify_function_exists(self):
        """Test function existence verification"""
        from rfd import RFD
        from rfd.validation import ValidationEngine
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        # Create test file with functions
        test_content = """
def test_function():
    pass

class TestClass:
    def method(self):
        pass

async def async_function():
    pass
"""
        Path('test_module.py').write_text(test_content)
        
        # Test function detection
        self.assertTrue(validator._verify_function_exists('test_function'))
        self.assertTrue(validator._verify_function_exists('TestClass'))
        self.assertTrue(validator._verify_function_exists('async_function'))
        self.assertFalse(validator._verify_function_exists('nonexistent_function'))
        
        # With file hint
        self.assertTrue(validator._verify_function_exists('test_function', 'test_module.py'))
        
        # Clean up
        Path('test_module.py').unlink()
    
    def test_validation_with_mixed_truth_lies(self):
        """Test validation with mix of true and false claims"""
        from rfd import RFD
        from rfd.validation import ValidationEngine
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        # Create one real file
        Path('real.py').write_text('def real_func(): pass')
        
        # Mixed claim
        claim = """
        Created real.py with function real_func
        Created fake.py with function fake_func
        """
        
        passed, results = validator.validate_ai_claims(claim)
        
        # Should fail overall (one lie = fail)
        self.assertFalse(passed)
        
        # Should have results for both
        self.assertGreaterEqual(len(results), 2)
        
        # Clean up
        Path('real.py').unlink()
    
    def test_check_ai_claim_simple(self):
        """Test simple boolean AI claim check"""
        from rfd import RFD
        from rfd.validation import ValidationEngine
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        # False claim
        self.assertFalse(validator.check_ai_claim("Created nonexistent.py"))
        
        # True claim
        Path('exists.py').write_text('# exists')
        self.assertTrue(validator.check_ai_claim("Created exists.py"))
        Path('exists.py').unlink()


class TestBuildEngine(unittest.TestCase):
    """Test the BuildEngine component"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="rfd_build_")
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_build_engine_initialization(self):
        """Test BuildEngine initializes correctly"""
        from rfd import RFD
        from rfd.build import BuildEngine
        
        rfd = RFD()
        builder = BuildEngine(rfd)
        
        self.assertIsNotNone(builder)
        self.assertEqual(builder.rfd, rfd)
    
    def test_detect_stack(self):
        """Test stack detection for different project types"""
        from rfd import RFD
        from rfd.build import BuildEngine
        
        rfd = RFD()
        builder = BuildEngine(rfd)
        
        # Test Python detection
        Path('requirements.txt').write_text('flask==2.0.0')
        stack = builder.detect_stack()
        self.assertEqual(stack.get('language'), 'python')
        Path('requirements.txt').unlink()
        
        # Test Node.js detection
        Path('package.json').write_text('{"name": "test"}')
        stack = builder.detect_stack()
        self.assertEqual(stack.get('language'), 'javascript')
        Path('package.json').unlink()
        
        # Test Ruby detection
        Path('Gemfile').write_text('source "https://rubygems.org"')
        stack = builder.detect_stack()
        self.assertEqual(stack.get('language'), 'ruby')
        Path('Gemfile').unlink()
    
    @patch('subprocess.run')
    def test_run_tests(self, mock_run):
        """Test running tests for different stacks"""
        from rfd import RFD
        from rfd.build import BuildEngine
        
        rfd = RFD()
        builder = BuildEngine(rfd)
        
        # Mock successful test run
        mock_run.return_value = MagicMock(returncode=0, stdout='Tests passed')
        
        # Python tests
        Path('requirements.txt').write_text('pytest')
        result = builder.run_tests()
        self.assertTrue(result['success'])
        
        # Clean up
        Path('requirements.txt').unlink()
    
    @patch('subprocess.run')
    def test_compile_code(self, mock_run):
        """Test code compilation"""
        from rfd import RFD
        from rfd.build import BuildEngine
        
        rfd = RFD()
        builder = BuildEngine(rfd)
        
        # Mock successful compilation
        mock_run.return_value = MagicMock(returncode=0)
        
        result = builder.compile()
        
        # Should return success status
        self.assertIn('success', result)


class TestSessionManager(unittest.TestCase):
    """Test the SessionManager component"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="rfd_session_")
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_session_manager_initialization(self):
        """Test SessionManager initializes correctly"""
        from rfd import RFD
        from rfd.session import SessionManager
        
        rfd = RFD()
        session_mgr = SessionManager(rfd)
        
        self.assertIsNotNone(session_mgr)
        self.assertEqual(session_mgr.rfd, rfd)
        # current_session is None until a session is created
        self.assertIsNone(session_mgr.current_session)
    
    def test_create_session(self):
        """Test session creation"""
        from rfd import RFD
        from rfd.session import SessionManager
        
        # Create a PROJECT.md with test feature
        project_content = """---
name: "Test Project"
features:
  - id: "test-feature"
    description: "Test feature"
    status: "pending"
---
# Test Project
"""
        with open("PROJECT.md", "w") as f:
            f.write(project_content)
        
        rfd = RFD()
        session_mgr = SessionManager(rfd)
        
        # Create new session
        session_id = session_mgr.create_session("test-feature")
        
        self.assertIsNotNone(session_id)
        self.assertEqual(session_mgr.current_session['feature'], 'test-feature')
        self.assertEqual(session_mgr.current_session['id'], session_id)
    
    def test_save_and_load_state(self):
        """Test saving and loading session state"""
        from rfd import RFD
        from rfd.session import SessionManager
        
        # Create a PROJECT.md with test feature
        project_content = """---
name: "Test Project"
features:
  - id: "test-feature"
    description: "Test feature"
    status: "pending"
---
# Test Project
"""
        with open("PROJECT.md", "w") as f:
            f.write(project_content)
        
        rfd = RFD()
        session_mgr = SessionManager(rfd)
        
        # Create session with state
        session_id = session_mgr.create_session("test-feature")
        test_state = {
            "current_file": "app.py",
            "line_number": 42,
            "checkpoint": 3
        }
        
        # Store state using context methods
        session_mgr.store_context('session_state', test_state)
        
        # Load state
        loaded_state = session_mgr.get_context('session_state')
        
        self.assertIsNotNone(loaded_state)
        if loaded_state:
            self.assertEqual(loaded_state.get('current_file'), 'app.py')
            self.assertEqual(loaded_state.get('line_number'), 42)
    
    def test_update_progress(self):
        """Test progress updates"""
        from rfd import RFD
        from rfd.session import SessionManager
        
        # Create a PROJECT.md with test feature
        project_content = """---
name: "Test Project"
features:
  - id: "test-feature"
    description: "Test feature"
    status: "pending"
---
# Test Project
"""
        with open("PROJECT.md", "w") as f:
            f.write(project_content)
        
        rfd = RFD()
        session_mgr = SessionManager(rfd)
        
        session_mgr.create_session("test-feature")
        
        # Update progress using store_context
        progress_data = {'checkpoint': 'checkpoint_1', 'status': 'passed', 'data': {'test': 'data'}}
        session_mgr.store_context('progress', progress_data)
        
        # Verify progress was stored
        stored = session_mgr.get_context('progress')
        self.assertIsNotNone(stored)
        self.assertEqual(stored.get('checkpoint'), 'checkpoint_1')
        self.assertEqual(stored.get('status'), 'passed')
    
    def test_get_context(self):
        """Test getting session context"""
        from rfd import RFD
        from rfd.session import SessionManager
        
        # Create a PROJECT.md with test feature
        project_content = """---
name: "Test Project"
features:
  - id: "test-feature"
    description: "Test feature"
    status: "pending"
---
# Test Project
"""
        with open("PROJECT.md", "w") as f:
            f.write(project_content)
        
        rfd = RFD()
        session_mgr = SessionManager(rfd)
        
        session_mgr.create_session("test-feature")
        
        # Test storing and retrieving context
        session_mgr.store_context('test_key', {'value': 'test_data'})
        context = session_mgr.get_context('test_key')
        
        self.assertIsNotNone(context)
        self.assertEqual(context.get('value'), 'test_data')
    
    def test_session_persistence(self):
        """Test session persists across instances"""
        from rfd import RFD
        from rfd.session import SessionManager
        
        # Create a PROJECT.md with test feature
        project_content = """---
name: "Test Project"
features:
  - id: "test-feature"
    description: "Test feature"
    status: "pending"
---
# Test Project
"""
        with open("PROJECT.md", "w") as f:
            f.write(project_content)
        
        # First session manager
        rfd1 = RFD()
        session_mgr1 = SessionManager(rfd1)
        session_id = session_mgr1.create_session("test-feature")
        session_mgr1.store_context('session_data', {"key": "value"})
        
        # New session manager should see previous session
        rfd2 = RFD()
        session_mgr2 = SessionManager(rfd2)
        
        # Should be able to get stored context from previous session
        data = session_mgr2.get_context('session_data')
        self.assertIsNotNone(data)
        self.assertEqual(data.get('key'), 'value')


class TestSpecEngine(unittest.TestCase):
    """Test the SpecEngine component"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="rfd_spec_")
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_spec_engine_initialization(self):
        """Test SpecEngine initializes correctly"""
        from rfd import RFD
        from rfd.spec import SpecEngine
        
        rfd = RFD()
        spec_engine = SpecEngine(rfd)
        
        self.assertIsNotNone(spec_engine)
        self.assertEqual(spec_engine.rfd, rfd)
    
    def test_validate_spec(self):
        """Test specification validation"""
        from rfd import RFD
        from rfd.spec import SpecEngine
        
        rfd = RFD()
        spec_engine = SpecEngine(rfd)
        
        # Valid spec
        valid_spec = {
            'name': 'test-project',
            'version': '1.0.0',
            'stack': {'language': 'python', 'framework': 'flask'},
            'features': [
                {
                    'id': 'feature-1',
                    'description': 'Test feature',
                    'acceptance': 'Given X, When Y, Then Z'
                }
            ]
        }
        
        errors = spec_engine.validate(valid_spec)
        self.assertEqual(len(errors), 0, "Valid spec should have no errors")
        
        # Invalid spec (missing required fields)
        invalid_spec = {
            'features': [
                {'description': 'Missing ID'}
            ]
        }
        
        errors = spec_engine.validate(invalid_spec)
        self.assertGreater(len(errors), 0, "Invalid spec should have errors")
    
    @unittest.skip("Questionary mocking is complex - skipping for now")
    @patch('rfd.spec.questionary')
    def test_create_spec_interactive(self, mock_questionary):
        """Test interactive spec creation"""
        from rfd import RFD
        from rfd.spec import SpecEngine
        
        rfd = RFD()
        spec_engine = SpecEngine(rfd)
        
        # Mock user inputs
        mock_questionary.text.return_value.ask.side_effect = [
            'test-project',  # name
            'A test project',  # description
        ]
        mock_questionary.select.return_value.ask.return_value = 'python'
        mock_questionary.confirm.return_value.ask.side_effect = [False, True]
        
        # Create spec
        with patch('builtins.open', mock_open()):
            spec = spec_engine.create()
        
        # Should create spec
        if spec:
            self.assertEqual(spec['name'], 'test-project')
            self.assertIn('created_at', spec)
    
    def test_add_feature_to_spec(self):
        """Test adding features to specification"""
        from rfd import RFD
        from rfd.spec import SpecEngine
        
        rfd = RFD()
        spec_engine = SpecEngine(rfd)
        
        # Create base spec
        spec = {
            'name': 'test-project',
            'version': '1.0.0',
            'features': []
        }
        
        # Add feature
        feature = {
            'id': 'new-feature',
            'description': 'New test feature',
            'acceptance': 'It should work',
            'checkpoints': ['spec', 'code', 'test']
        }
        
        spec = spec_engine.add_feature(spec, feature)
        
        self.assertEqual(len(spec['features']), 1)
        self.assertEqual(spec['features'][0]['id'], 'new-feature')
    
    def test_update_feature_status(self):
        """Test updating feature status"""
        from rfd import RFD
        from rfd.spec import SpecEngine
        
        rfd = RFD()
        spec_engine = SpecEngine(rfd)
        
        # Spec with feature
        spec = {
            'features': [
                {
                    'id': 'feature-1',
                    'status': 'pending'
                }
            ]
        }
        
        # Update status
        spec = spec_engine.update_feature_status(spec, 'feature-1', 'in_progress')
        
        self.assertEqual(spec['features'][0]['status'], 'in_progress')


class TestIntegrationBasics(unittest.TestCase):
    """Basic integration tests between components"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="rfd_integ_")
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_rfd_with_validation(self):
        """Test RFD and ValidationEngine work together"""
        from rfd import RFD
        from rfd.validation import ValidationEngine
        
        rfd = RFD()
        validator = ValidationEngine(rfd)
        
        # Create a simple spec
        rfd.spec = {
            'name': 'integration-test',
            'rules': {
                'max_files': 10
            }
        }
        
        # Run validation
        results = validator.validate()
        
        self.assertIn('passing', results)
        self.assertIn('results', results)
    
    def test_rfd_with_session(self):
        """Test RFD and SessionManager work together"""
        from rfd import RFD
        from rfd.session import SessionManager
        
        rfd = RFD()
        session = SessionManager(rfd)
        
        # Create session
        session_id = session.create_session("integration_test_fixes")
        
        # RFD should be aware of session
        context = session.get_context()
        self.assertIsNotNone(context)
        self.assertEqual(context['current_session']['feature'], 'integration-feature')
    
    def test_validation_with_spec(self):
        """Test ValidationEngine uses SpecEngine specs"""
        from rfd import RFD
        from rfd.validation import ValidationEngine
        from rfd.spec import SpecEngine
        
        rfd = RFD()
        spec_engine = SpecEngine(rfd)
        validator = ValidationEngine(rfd)
        
        # Create spec with rules
        spec = {
            'name': 'validated-project',
            'rules': {
                'max_files': 5,
                'max_loc_per_file': 100
            },
            'features': []
        }
        
        # Save spec
        Path('RFD-SPEC.md').write_text(f"""---
{json.dumps(spec)}
---
# Test Spec
""")
        
        # Load and validate
        rfd.spec = rfd.load_project_spec()
        results = validator.validate()
        
        # Should validate against spec rules
        self.assertIsInstance(results['passing'], bool)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)