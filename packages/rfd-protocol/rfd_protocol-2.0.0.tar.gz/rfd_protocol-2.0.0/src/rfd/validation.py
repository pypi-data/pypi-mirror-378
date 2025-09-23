"""
Validation Engine for RFD
Tests that code actually works as specified
"""

import requests
import sqlite3
import json
import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class ValidationEngine:
    def __init__(self, rfd):
        self.rfd = rfd
        self.spec = rfd.load_project_spec()
        self.results = []
    
    def validate(self, feature: Optional[str] = None, full: bool = False) -> Dict[str, Any]:
        """Run validation tests"""
        self.results = []
        
        # Structural validation
        self._validate_structure()
        
        # API validation
        if 'api_contract' in self.spec:
            self._validate_api()
        
        # Feature validation
        if feature:
            self._validate_feature(feature)
        elif full:
            for f in self.spec.get('features', []):
                self._validate_feature(f['id'])
        
        # Database validation
        self._validate_database()
        
        return {
            'passing': all(r['passed'] for r in self.results),
            'results': self.results
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Quick validation status"""
        results = self.validate()
        return {
            'passing': results['passing'],
            'failed_count': sum(1 for r in results['results'] if not r['passed']),
            'message': 'All validations passing' if results['passing'] else 'Validation failures detected'
        }
    
    def check_ai_claim(self, claim: str) -> bool:
        """Simple boolean check if an AI claim is true or false"""
        passed, _ = self.validate_ai_claims(claim)
        return passed
    
    def _validate_structure(self):
        """Validate project structure - REAL validation that checks if files exist"""
        rules = self.spec.get('rules', {})
        
        # Check claimed files actually exist
        claimed_files = self.spec.get('claimed_files', [])
        for file_path in claimed_files:
            exists = Path(file_path).exists()
            self.results.append({
                'test': f'file_exists_{file_path}',
                'passed': exists,
                'message': f"File {file_path}: {'EXISTS' if exists else 'MISSING - AI LIED!'}"
            })
        
        # Original rule-based validation
        if 'max_files' in rules:
            files = list(Path('.').glob('**/*.py'))
            passed = len(files) <= rules['max_files']
            self.results.append({
                'test': 'max_files',
                'passed': passed,
                'message': f"{len(files)} files (max: {rules['max_files']})"
            })
        
        # Lines per file
        if 'max_loc_per_file' in rules:
            for f in Path('.').glob('**/*.py'):
                if '.rfd' in str(f):
                    continue
                try:
                    lines = len(open(f).readlines())
                    passed = lines <= rules['max_loc_per_file']
                    if not passed:
                        self.results.append({
                            'test': f'loc_{f.name}',
                            'passed': False,
                            'message': f"{f.name} has {lines} lines (max: {rules['max_loc_per_file']})"
                        })
                except:
                    pass
    
    def _validate_api(self):
        """Validate API endpoints against contract"""
        contract = self.spec['api_contract']
        base_url = contract['base_url']
        
        # Check health endpoint first
        try:
            r = requests.get(f"{base_url}{contract['health_check']}", timeout=2)
            self.results.append({
                'test': 'api_health',
                'passed': r.status_code == 200,
                'message': f"Health check: {r.status_code}"
            })
        except Exception as e:
            self.results.append({
                'test': 'api_health',
                'passed': False,
                'message': f"API not reachable: {e}"
            })
            return  # Skip other tests if API is down
        
        # Test each endpoint
        for endpoint in contract.get('endpoints', []):
            self._test_endpoint(base_url, endpoint)
    
    def _test_endpoint(self, base_url: str, endpoint: Dict):
        """Test single endpoint"""
        url = f"{base_url}{endpoint['path']}"
        method = endpoint['method']
        
        # Generate test data
        test_data = self._generate_test_data(endpoint['path'])
        
        try:
            if method == 'GET':
                r = requests.get(url)
            elif method == 'POST':
                r = requests.post(url, json=test_data)
            else:
                r = requests.request(method, url, json=test_data)
            
            # Check response
            expected = endpoint.get('validates', '')
            passed = self._check_response(r, expected)
            
            self.results.append({
                'test': f"{method}_{endpoint['path']}",
                'passed': passed,
                'message': f"{r.status_code} - {expected}"
            })
        except Exception as e:
            self.results.append({
                'test': f"{method}_{endpoint['path']}",
                'passed': False,
                'message': str(e)
            })
    
    def _check_response(self, response, expected: str) -> bool:
        """Check if response matches expected format"""
        if not expected:
            return True
        
        # Parse expected format
        if "returns" in expected:
            parts = expected.split("returns")[1].strip()
            expected_code = int(parts.split()[0])
            
            if response.status_code != expected_code:
                return False
            
            # Check response shape
            if "{" in expected:
                import re
                shape = re.search(r'\{([^}]+)\}', expected).group(1)
                fields = [f.split(':')[0].strip() for f in shape.split(',')]
                
                try:
                    data = response.json()
                    for field in fields:
                        if field not in data:
                            return False
                except:
                    return False
        
        return True
    
    def _validate_feature(self, feature_id: str):
        """Validate specific feature"""
        # Find feature in spec
        feature = None
        for f in self.spec.get('features', []):
            if f['id'] == feature_id:
                feature = f
                break
        
        if not feature:
            self.results.append({
                'test': f'feature_{feature_id}',
                'passed': False,
                'message': 'Feature not found in spec'
            })
            return
        
        # Run acceptance test
        acceptance = feature.get('acceptance', '')
        # Parse and run acceptance criteria
        # This would be expanded based on your testing needs
        
        self.results.append({
            'test': f'feature_{feature_id}',
            'passed': feature.get('status') == 'complete',
            'message': f"{feature['description']} - {feature.get('status', 'pending')}"
        })
    
    def _validate_database(self):
        """Validate database state"""
        db_type = self.spec.get('stack', {}).get('database')
        
        if db_type == 'sqlite':
            # Check if DB exists and has tables
            db_files = list(Path('.').glob('*.db'))
            if not db_files:
                self.results.append({
                    'test': 'database',
                    'passed': False,
                    'message': 'No SQLite database found'
                })
                return
            
            # Check schema
            conn = sqlite3.connect(db_files[0])
            try:
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                
                self.results.append({
                    'test': 'database',
                    'passed': len(tables) > 0,
                    'message': f"Database has {len(tables)} tables"
                })
            finally:
                conn.close()
    
    def _generate_test_data(self, path: str) -> Dict:
        """Generate test data based on path"""
        # Smart defaults
        if 'signup' in path or 'register' in path:
            return {"email": "test@example.com", "password": "Test123!"}
        elif 'login' in path:
            return {"email": "test@example.com", "password": "Test123!"}
        return {}
    
    def validate_ai_claims(self, claims: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate AI claims about file and function creation AND modifications.
        Returns (passed, details) where passed is False if AI lied.
        """
        validation_results = []
        
        # Parse claims for file paths and function/class names
        file_claims = self._extract_file_claims(claims)
        function_claims = self._extract_function_claims(claims)
        modification_claims = self._extract_modification_claims(claims)
        
        # Check for vague/comprehensive claims that are often hallucinations
        vague_claims = self._detect_vague_claims(claims)
        
        # Check each claimed file exists
        for file_path in file_claims:
            try:
                # Handle edge cases like extremely long filenames or invalid characters
                if len(file_path) > 255:  # Most filesystems limit filenames to 255 chars
                    exists = False
                    message = f"File {file_path[:50]}...: FILENAME TOO LONG - AI HALLUCINATION!"
                else:
                    exists = Path(file_path).exists()
                    message = f"File {file_path}: {'EXISTS' if exists else 'MISSING - AI HALLUCINATION!'}"
            except (OSError, ValueError) as e:
                # Handle filesystem errors, invalid characters, etc.
                exists = False
                message = f"File {file_path[:50]}...: INVALID PATH ({str(e)[:50]}) - AI HALLUCINATION!"
            
            validation_results.append({
                'type': 'file',
                'target': file_path,
                'exists': exists,
                'message': message
            })
        
        # Check each claimed function/class exists in the files
        for func_name, file_hint in function_claims:
            # If a specific file was mentioned, we need strict verification
            if file_hint:
                # Strict check: function must be in the specific file mentioned AND file must exist
                try:
                    if len(file_hint) > 255:
                        found = False  # Filename too long
                    elif Path(file_hint).exists():
                        found = self._check_function_in_file(func_name, file_hint)
                    else:
                        found = False  # File doesn't exist, so function can't be in it
                except (OSError, ValueError):
                    found = False  # Invalid path
            else:
                # No specific file mentioned, search all files
                found = self._verify_function_exists(func_name, file_hint)
            
            validation_results.append({
                'type': 'function',
                'target': func_name,
                'exists': found,
                'message': f"Function/Class {func_name}: {'FOUND' if found else 'NOT FOUND - AI HALLUCINATION!'}"
            })
        
        # Check modification claims - this is where we catch subtle lies
        for modification_type, target, details, file_hint in modification_claims:
            verified = self._verify_modification_claim(modification_type, target, details, file_hint)
            validation_results.append({
                'type': 'modification',
                'target': f"{target} ({modification_type})",
                'exists': verified,
                'message': f"Modification '{details}' to {target}: {'VERIFIED' if verified else 'NOT FOUND - AI HALLUCINATION!'}"
            })
        
        # Check vague claims that are likely hallucinations
        for claim_type, claim_text, is_likely_hallucination in vague_claims:
            validation_results.append({
                'type': 'vague_claim',
                'target': f"{claim_type}",
                'exists': not is_likely_hallucination,
                'message': f"Vague claim '{claim_text}': {'SUSPICIOUS - LIKELY HALLUCINATION' if is_likely_hallucination else 'ACCEPTABLE'}"
            })
        
        # Overall pass/fail
        # If no claims were detected, this might be suspicious unless it's a very simple statement
        if not validation_results:
            # Check if this looks like a claim but wasn't parsed
            suspicious_keywords = ['created', 'added', 'implemented', 'wrote', 'built', 'made', 'fixed', 'updated', 'modified', 'enhanced']
            contains_claim = any(keyword in claims.lower() for keyword in suspicious_keywords)
            if contains_claim:
                # Looks like a claim but we couldn't parse it - might be hallucination
                return False, [{'type': 'unparseable_claim', 'target': claims[:50], 'exists': False, 'message': 'Unparseable claim - possible AI hallucination'}]
            else:
                # Doesn't look like a claim, pass it through
                return True, []
        
        all_passed = all(r['exists'] for r in validation_results)
        return all_passed, validation_results
    
    def _extract_file_claims(self, text: str) -> List[str]:
        """Extract file paths mentioned in AI claims"""
        patterns = [
            # Match any file with an extension
            r'[cC]reated?\s+(?:file\s+)?([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)',
            r'[wW]rote?\s+(?:to\s+)?([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)',
            r'[mM]ade\s+([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)',
            r'[fF]ile[s]?:\s*([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)',
            r'`([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)`',
            r'"([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)"',
            r"'([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)'",
            # Also match common files without extensions
            r'[cC]reated?\s+(Makefile|Dockerfile|Gemfile|Rakefile|Procfile)',
            r'[mM]ade\s+(Makefile|Dockerfile|Gemfile|Rakefile|Procfile)',
        ]
        
        files = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            files.update(matches)
        
        # Filter out obvious non-paths and common words
        filtered = []
        for f in files:
            # Skip common false positives
            if f in ['and', 'with', 'called', 'class', 'function', 'method']:
                continue
            if not f.startswith('http') and '://' not in f:
                filtered.append(f)
        
        return list(set(filtered))  # Remove duplicates
    
    def _extract_function_claims(self, text: str) -> List[Tuple[str, Optional[str]]]:
        """Extract function/class names mentioned in AI claims"""
        # Enhanced patterns that handle async, JS, Go, and other languages
        patterns = [
            # Explicit function creation patterns with async support
            r'[cC]reated\s+(?:async\s+)?(?:function|method)\s+(?:called\s+)?(\w+)',  # "Created async function foo"
            r'[cC]reated\s+(\w+)\s+(?:function|method)',                            # "Created foo function"
            r'[aA]dded\s+(?:async\s+)?(?:function|method)\s+(?:called\s+)?(\w+)',    # "Added async function foo"
            r'[aA]dded\s+(\w+)\s+(?:function|method)',                              # "Added foo function"
            r'[iI]mplemented\s+(?:async\s+)?(?:function|method)\s+(?:called\s+)?(\w+)',  # "Implemented async function foo"
            r'[iI]mplemented\s+(\w+)\s+(?:function|method)',                        # "Implemented foo function"
            r'[wW]rote\s+(?:async\s+)?(?:function|method)\s+(?:called\s+)?(\w+)',    # "Wrote async function foo"
            r'[wW]rote\s+(\w+)\s+(?:function|method)',                              # "Wrote foo function"
            
            # Function definition patterns with async and multi-language support
            r'[aA]sync\s+function\s+(\w+)',   # "async function foo"
            r'[fF]unction\s+called\s+(\w+)',  # "function called foo"
            r'[fF]unction\s+(\w+)',           # "function foo" - but NOT "async version of function"
            r'[mM]ethod\s+(\w+)',             # "method foo"
            r'[dD]ef\s+(\w+)',                # "def foo" (Python)
            r'[aA]sync\s+def\s+(\w+)',        # "async def foo" (Python)
            
            # JavaScript/TypeScript patterns
            r'function\s+(\w+)\s*\(',         # JavaScript function declarations
            r'const\s+(\w+)\s*=.*?=>\s*{',    # Arrow functions
            r'(\w+)\s*:\s*function',          # Object method definitions
            
            # Go patterns
            r'func\s+(\w+)\s*\(',             # Go functions
            
            # Class creation patterns
            r'[cC]reated\s+(?:class)\s+(?:called\s+)?(\w+)',  # "Created class Foo"
            r'[cC]reated\s+(\w+)\s+class',                    # "Created Foo class" 
            r'[aA]dded\s+(?:class)\s+(?:called\s+)?(\w+)',    # "Added class Foo"
            r'[aA]dded\s+(\w+)\s+class',                      # "Added Foo class"
            r'[iI]mplemented\s+(?:class)\s+(?:called\s+)?(\w+)',  # "Implemented class Foo"
            r'[iI]mplemented\s+(\w+)\s+class',                # "Implemented Foo class"
            r'[iI]mplemented\s+(\w+)\s+model',                # "Implemented Foo model"
            r'[cC]lass\s+(?:called\s+)?(\w+)(?:\s|$)',        # "class DataProcessor" (with word boundary)
            
            # Backtick patterns (code references)
            r'`(\w+)\(\)`',         # Function calls in backticks like `foo()`
            r'`def\s+(\w+)`',       # Function definitions in backticks like `def foo`
            r'`async\s+def\s+(\w+)`', # Async function definitions in backticks
            r'`class\s+(\w+)`',     # Class definitions in backticks like `class Foo`
            r'`function\s+(\w+)`',  # JavaScript functions in backticks
            r'`func\s+(\w+)`',      # Go functions in backticks
        ]
        
        functions = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            functions.update(matches)
        
        # Filter out common false positives and action words
        filtered_functions = set()
        false_positives = {
            'and', 'with', 'called', 'function', 'class', 'method', 'a', 'the', 'in', 'to', 'for',
            'created', 'added', 'implemented', 'wrote', 'def', 'async', 'return', 'returns',
            'error', 'handling', 'version', 'database', 'connection', 'init', 'self'
        }
        
        # Special filtering for async version patterns which should be treated as modifications
        for func in list(functions):
            # Check if this is part of an "async version" pattern
            if re.search(rf'async\s+version\s+of\s+{func}', text, re.IGNORECASE):
                functions.discard(func)  # Remove from function list (will be caught by modification detection)
        
        for func in functions:
            # Skip common words that aren't function names
            if func.lower() in false_positives:
                continue
            # Skip single letters
            if len(func) < 2:
                continue
            # Skip if starts with lowercase action words
            if func.lower().startswith(('add', 'created', 'implement', 'wrote')):
                continue
            filtered_functions.add(func)
        
        # Try to associate with file hints if mentioned nearby
        result = []
        for func in filtered_functions:
            file_hint = self._find_file_hint_for_function(func, text)
            result.append((func, file_hint))
        
        return result
    
    def _find_file_hint_for_function(self, func_name: str, text: str) -> Optional[str]:
        """Try to find which file a function was claimed to be in"""
        # Look for explicit patterns that indicate file association with the function
        patterns = [
            # "function foo in file.py" - more specific patterns
            rf'{func_name}.*?\bin\s+([^\s,]+\.[a-zA-Z0-9]+)',
            rf'in\s+([^\s,]+\.[a-zA-Z0-9]+).*?{func_name}',
            rf'{func_name}.*?\bto\s+([^\s,]+\.[a-zA-Z0-9]+)',
            # "Created function foo in file.py" patterns
            rf'[cC]reated.*?{func_name}.*?\bin\s+([^\s,]+\.[a-zA-Z0-9]+)',
            rf'[aA]dded.*?{func_name}.*?\bin\s+([^\s,]+\.[a-zA-Z0-9]+)',
            rf'[iI]mplemented.*?{func_name}.*?\bin\s+([^\s,]+\.[a-zA-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                file_path = match.group(1)
                # Only return if the file actually exists
                try:
                    if len(file_path) <= 255 and Path(file_path).exists():
                        return file_path
                except (OSError, ValueError):
                    # Invalid path, skip
                    pass
        
        return None
    
    def _verify_function_exists(self, func_name: str, file_hint: Optional[str] = None) -> bool:
        """Verify if a function/class actually exists in the codebase"""
        # If we have a file hint, check there first
        if file_hint:
            try:
                if len(file_hint) <= 255 and Path(file_hint).exists():
                    if self._check_function_in_file(func_name, file_hint):
                        return True
            except (OSError, ValueError):
                # Invalid path, skip
                pass
        
        # Search all relevant source code files
        source_extensions = ['*.py', '*.js', '*.ts', '*.go', '*.java', '*.cpp', '*.c', '*.rs', '*.rb', '*.php', '*.swift', '*.kt']
        for pattern in source_extensions:
            for source_file in Path('.').rglob(pattern):
                try:
                    if self._check_function_in_file(func_name, str(source_file)):
                        return True
                except:
                    continue
        
        return False
    
    def _check_function_in_file(self, func_name: str, file_path: str) -> bool:
        """Check if a function exists in a specific file, handling multiple languages"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_ext = Path(file_path).suffix.lower()
            
            # Python patterns
            if file_ext == '.py':
                patterns = [
                    rf'^\s*def\s+{func_name}\s*\(',
                    rf'^\s*async\s+def\s+{func_name}\s*\(',
                    rf'^\s*class\s+{func_name}\s*[:\(]'
                ]
            
            # JavaScript/TypeScript patterns
            elif file_ext in ['.js', '.ts']:
                patterns = [
                    rf'^\s*function\s+{func_name}\s*\(',
                    rf'^\s*async\s+function\s+{func_name}\s*\(',
                    rf'^\s*const\s+{func_name}\s*=',
                    rf'^\s*let\s+{func_name}\s*=',
                    rf'^\s*var\s+{func_name}\s*=',
                    rf'^\s*{func_name}\s*:\s*function',
                    rf'^\s*{func_name}\s*\(',  # Method definitions
                    rf'^\s*class\s+{func_name}\s*{{',
                ]
            
            # Go patterns
            elif file_ext == '.go':
                patterns = [
                    rf'^\s*func\s+{func_name}\s*\(',
                    rf'^\s*func\s+\(\w+\s+\*?\w+\)\s+{func_name}\s*\(',  # Method definitions
                    rf'^\s*type\s+{func_name}\s+struct',  # Struct definitions
                    rf'^\s*type\s+{func_name}\s+interface',  # Interface definitions
                ]
            
            # Java patterns
            elif file_ext == '.java':
                patterns = [
                    rf'^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:\w+\s+)*{func_name}\s*\(',
                    rf'^\s*(?:public\s+|private\s+|protected\s+)?class\s+{func_name}\s*{{',
                    rf'^\s*(?:public\s+|private\s+|protected\s+)?interface\s+{func_name}\s*{{',
                ]
            
            # C/C++ patterns
            elif file_ext in ['.c', '.cpp', '.h', '.hpp']:
                patterns = [
                    rf'^\s*(?:\w+\s+)*{func_name}\s*\(',
                    rf'^\s*class\s+{func_name}\s*{{',
                    rf'^\s*struct\s+{func_name}\s*{{',
                ]
            
            # Rust patterns
            elif file_ext == '.rs':
                patterns = [
                    rf'^\s*fn\s+{func_name}\s*\(',
                    rf'^\s*pub\s+fn\s+{func_name}\s*\(',
                    rf'^\s*struct\s+{func_name}\s*{{',
                    rf'^\s*pub\s+struct\s+{func_name}\s*{{',
                    rf'^\s*trait\s+{func_name}\s*{{',
                    rf'^\s*impl.*{func_name}',
                ]
            
            # Ruby patterns
            elif file_ext == '.rb':
                patterns = [
                    rf'^\s*def\s+{func_name}\s*[\(\n]',
                    rf'^\s*class\s+{func_name}\s*[<\n]',
                    rf'^\s*module\s+{func_name}\s*\n',
                ]
            
            # PHP patterns
            elif file_ext == '.php':
                patterns = [
                    rf'^\s*function\s+{func_name}\s*\(',
                    rf'^\s*(?:public\s+|private\s+|protected\s+)?function\s+{func_name}\s*\(',
                    rf'^\s*class\s+{func_name}\s*{{',
                ]
            
            # Swift patterns
            elif file_ext == '.swift':
                patterns = [
                    rf'^\s*func\s+{func_name}\s*\(',
                    rf'^\s*class\s+{func_name}\s*{{',
                    rf'^\s*struct\s+{func_name}\s*{{',
                    rf'^\s*protocol\s+{func_name}\s*{{',
                ]
            
            # Kotlin patterns
            elif file_ext == '.kt':
                patterns = [
                    rf'^\s*fun\s+{func_name}\s*\(',
                    rf'^\s*class\s+{func_name}\s*[{{:]',
                    rf'^\s*interface\s+{func_name}\s*{{',
                    rf'^\s*object\s+{func_name}\s*{{',
                ]
            
            else:
                # Default pattern for unknown file types
                patterns = [rf'\b{func_name}\b']
            
            # Check if any pattern matches
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE):
                    return True
            
            return False
        except:
            return False
    
    def _extract_modification_claims(self, text: str) -> List[Tuple[str, str, str, Optional[str]]]:
        """
        Extract modification claims from AI text.
        Returns list of (modification_type, target, details, file_hint) tuples.
        """
        modification_claims = []
        
        # Enhanced patterns for different types of modifications
        patterns = [
            # Error handling additions - more comprehensive patterns
            (r'[aA]dded\s+(?:comprehensive\s+)?error\s+handling\s+(?:to\s+|throughout\s+)?(\w+)', 'error_handling', 'added error handling'),
            (r'[aA]dded\s+try[/-]catch\s+(?:to\s+)?(\w+)', 'error_handling', 'added try-catch'),
            (r'[iI]mplemented\s+(?:comprehensive\s+)?error\s+handling\s+(?:in\s+|throughout\s+)?(\w+)', 'error_handling', 'implemented error handling'),
            (r'[aA]dded\s+exception\s+handling\s+(?:to\s+)?(\w+)', 'error_handling', 'added exception handling'),
            
            # Async/await modifications with better patterns - but avoid when "async function" is literally being created
            (r'[aA]dded\s+async\s+version\s+of\s+(\w+)', 'async_conversion', 'made async version'),
            (r'[iI]mplemented\s+async\s+version\s+of\s+(\w+)', 'async_conversion', 'implemented async version'),
            (r'[cC]reated\s+async\s+version\s+of\s+(\w+)', 'async_conversion', 'created async version'),
            (r'[cC]onverted\s+(\w+)\s+to\s+async', 'async_conversion', 'converted to async'),
            (r'[aA]dded\s+async/await\s+(?:pattern\s+)?(?:to\s+)?(\w+)', 'async_conversion', 'added async/await'),
            (r'[iI]mplemented\s+async/await\s+(?:pattern\s+)?(?:for\s+)?(\w+)', 'async_conversion', 'implemented async/await'),
            
            # Database connections with variations
            (r'[aA]dded\s+database\s+connection\s+(?:to\s+)?(\w+)', 'database_integration', 'added database connection'),
            (r'[iI]mplemented\s+database\s+(?:integration\s+|connection\s+|persistence\s+)?(?:in\s+)?(\w+)', 'database_integration', 'implemented database integration'),
            (r'[iI]mplemented\s+(\w+)\s+model\s+with\s+database\s+connection', 'database_integration', 'implemented model with database connection'),
            (r'[aA]dded\s+(?:database\s+)?persistence\s+(?:to\s+)?(\w+)', 'database_integration', 'added database persistence'),
            
            # Input validation and sanitization
            (r'[aA]dded\s+(?:input\s+)?validation\s+(?:and\s+sanitization\s+)?(?:to\s+)?(\w+)', 'input_validation', 'added input validation'),
            (r'[iI]mplemented\s+(?:input\s+)?validation\s+(?:and\s+sanitization\s+)?(?:in\s+)?(\w+)', 'input_validation', 'implemented input validation'),
            (r'[aA]dded\s+(?:data\s+)?sanitization\s+(?:to\s+)?(\w+)', 'input_validation', 'added sanitization'),
            
            # Logging additions with variations
            (r'[aA]dded\s+(?:comprehensive\s+)?logging\s+(?:to\s+|throughout\s+)?(\w+)', 'logging', 'added logging'),
            (r'[iI]mplemented\s+(?:comprehensive\s+)?logging\s+(?:in\s+|throughout\s+)?(\w+)', 'logging', 'implemented logging'),
            (r'[aA]dded\s+logging\s+framework\s+(?:to\s+)?(\w+)', 'logging', 'added logging framework'),
            
            # Authentication and security
            (r'[aA]dded\s+authentication\s+(?:check\s+|middleware\s+)?(?:to\s+)?(\w+)', 'authentication', 'added authentication'),
            (r'[iI]mplemented\s+authentication\s+(?:middleware\s+)?(?:for\s+)?(\w+)', 'authentication', 'implemented authentication'),
            (r'[aA]dded\s+(?:security\s+)?(?:JWT\s+)?token\s+validation\s+(?:to\s+)?(\w+)', 'authentication', 'added token validation'),
            
            # Caching and performance
            (r'[aA]dded\s+caching\s+(?:layer\s+)?(?:to\s+)?(\w+)', 'caching', 'added caching'),
            (r'[iI]mplemented\s+caching\s+(?:layer\s+)?(?:in\s+)?(\w+)', 'caching', 'implemented caching'),
            (r'[iI]ntegrated\s+(?:caching\s+layer\s+)?(?:with\s+)?Redis\s+(?:for\s+)?(\w+)', 'caching', 'integrated caching'),
            
            # Performance optimizations
            (r'[oO]ptimized\s+(?:the\s+)?(\w+)', 'optimization', 'optimized performance'),
            (r'[iI]mproved\s+performance\s+of\s+(\w+)', 'optimization', 'improved performance'),
            (r'[eE]nhanced\s+(?:the\s+)?(\w+)\s+(?:for\s+better\s+)?performance', 'optimization', 'enhanced performance'),
            
            # Configuration and environment
            (r'[aA]dded\s+configuration\s+management\s+(?:to\s+)?(\w+)', 'configuration', 'added configuration'),
            (r'[iI]mplemented\s+(?:configuration\s+management\s+)?(?:with\s+)?environment\s+variables\s+(?:for\s+)?(\w+)', 'configuration', 'implemented configuration'),
            
            # Rate limiting and security
            (r'[iI]mplemented\s+rate\s+limiting\s+(?:to\s+prevent\s+abuse\s+)?(?:for\s+)?(\w+)', 'rate_limiting', 'implemented rate limiting'),
            (r'[aA]dded\s+rate\s+limiting\s+(?:to\s+)?(\w+)', 'rate_limiting', 'added rate limiting'),
            
            # Testing and documentation
            (r'[aA]dded\s+(?:comprehensive\s+)?(?:unit\s+)?tests\s+(?:with\s+\d+%\s+code\s+coverage\s+)?(?:for\s+)?(\w+)', 'testing', 'added tests'),
            (r'[cC]reated\s+(?:comprehensive\s+)?API\s+documentation\s+(?:with\s+OpenAPI/Swagger\s+)?(?:for\s+)?(\w+)', 'documentation', 'created documentation'),
            
            # Graceful shutdown and error handling
            (r'[iI]mplemented\s+graceful\s+shutdown\s+handling\s+(?:for\s+)?(\w+)', 'shutdown_handling', 'implemented graceful shutdown'),
            
            # General modifications - broader patterns
            (r'[mM]odified\s+(\w+)', 'general_modification', 'modified'),
            (r'[uU]pdated\s+(\w+)', 'general_modification', 'updated'),
            (r'[eE]nhanced\s+(\w+)', 'general_modification', 'enhanced'),
            (r'[iI]mproved\s+(\w+)', 'general_modification', 'improved'),
            
            # Bug fixes
            (r'[fF]ixed\s+(?:bug\s+in\s+|memory\s+leak\s+in\s+)?(\w+)', 'bug_fix', 'fixed bug'),
            (r'[rR]esolved\s+(?:issue\s+in\s+)?(\w+)', 'bug_fix', 'resolved issue'),
        ]
        
        for pattern, mod_type, description in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Try to find file hint
                file_hint = self._find_file_hint_for_function(match, text)
                modification_claims.append((mod_type, match, description, file_hint))
        
        return modification_claims
    
    def _detect_vague_claims(self, text: str) -> List[Tuple[str, str, bool]]:
        """
        Detect vague/comprehensive claims that are often AI hallucinations.
        Returns list of (claim_type, claim_text, is_likely_hallucination) tuples.
        """
        vague_patterns = [
            # Comprehensive claims that are too broad to verify
            (r'[aA]dded\s+comprehensive\s+(\w+)\s+throughout\s+(?:the\s+)?application', 'comprehensive_throughout', True),
            (r'[iI]mplemented\s+comprehensive\s+(\w+)\s+throughout\s+(?:the\s+)?application', 'comprehensive_throughout', True),
            (r'[aA]dded\s+(\w+)\s+throughout\s+(?:the\s+)?(?:application|codebase|system)', 'added_throughout', True),
            
            # Input validation claims that are too broad
            (r'[aA]dded\s+input\s+validation\s+and\s+sanitization\s+to\s+all\s+user-facing\s+functions?', 'all_user_facing', True),
            (r'[iI]mplemented\s+input\s+validation\s+(?:and\s+sanitization\s+)?for\s+all\s+(?:user\s+)?inputs?', 'all_inputs', True),
            
            # Authentication claims that are too broad
            (r'[aA]dded\s+authentication\s+middleware\s+with\s+JWT\s+token\s+validation', 'auth_middleware_jwt', True),
            (r'[iI]mplemented\s+authentication\s+system\s+with\s+(?:JWT\s+)?tokens?', 'auth_system', True),
            
            # Performance claims that are too vague
            (r'[iI]mplemented\s+async/await\s+pattern\s+for\s+better\s+performance', 'async_for_performance', True),
            (r'[oO]ptimized\s+(?:the\s+)?algorithm\s+for\s+better\s+time\s+complexity', 'optimized_algorithm', True),
            
            # Testing claims that are too broad
            (r'[aA]dded\s+comprehensive\s+unit\s+tests\s+with\s+\d+%\s+code\s+coverage', 'comprehensive_tests', True),
            (r'[iI]mplemented\s+(?:comprehensive\s+)?testing\s+suite\s+(?:with\s+\d+%\s+coverage)?', 'testing_suite', True),
            
            # Documentation claims
            (r'[cC]reated\s+comprehensive\s+API\s+documentation\s+with\s+OpenAPI/Swagger', 'api_documentation', True),
            (r'[aA]dded\s+(?:comprehensive\s+)?documentation\s+throughout\s+(?:the\s+)?(?:codebase|application)', 'comprehensive_docs', True),
            
            # Configuration claims
            (r'[aA]dded\s+configuration\s+management\s+with\s+environment\s+variables', 'config_management', True),
            (r'[iI]mplemented\s+graceful\s+shutdown\s+handling', 'graceful_shutdown', True),
            
            # Security claims
            (r'[iI]mplemented\s+rate\s+limiting\s+to\s+prevent\s+abuse', 'rate_limiting', True),
            (r'[aA]dded\s+(?:comprehensive\s+)?security\s+measures', 'security_measures', True),
            
            # Database claims that are too broad
            (r'[cC]reated\s+database\s+connection\s+pool\s+with\s+automatic\s+retry\s+logic', 'db_connection_pool', True),
            (r'[iI]mplemented\s+database\s+(?:layer\s+)?with\s+(?:automatic\s+)?(?:connection\s+)?pooling', 'db_layer_pooling', True),
            
            # Caching claims
            (r'[iI]ntegrated\s+caching\s+layer\s+with\s+Redis\s+for\s+improved\s+performance', 'redis_caching', True),
            (r'[iI]mplemented\s+caching\s+(?:layer\s+)?(?:with\s+\w+\s+)?for\s+(?:improved\s+)?performance', 'caching_performance', True),
            
            # Error handling that's too broad
            (r'[eE]nhanced\s+error\s+messages\s+to\s+be\s+more\s+user-friendly', 'user_friendly_errors', True),
            
            # General "improvement" claims
            (r'[eE]nhanced\s+(?:the\s+)?overall\s+(?:performance|user\s+experience|security)', 'enhanced_overall', True),
            (r'[iI]mproved\s+(?:overall\s+)?(?:performance|efficiency|user\s+experience)', 'improved_overall', True),
        ]
        
        vague_claims = []
        for pattern, claim_type, is_hallucination in vague_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get the full match text for display
                full_match = re.search(pattern, text, re.IGNORECASE)
                if full_match:
                    claim_text = full_match.group(0)
                    vague_claims.append((claim_type, claim_text, is_hallucination))
        
        return vague_claims
    
    def _verify_modification_claim(self, modification_type: str, target: str, details: str, file_hint: Optional[str] = None) -> bool:
        """
        Verify if a claimed modification was actually made.
        This is conservative - for most modification types, we return False 
        unless we can definitively prove the modification exists.
        """
        
        # First, verify the target function/class exists
        if not self._verify_function_exists(target, file_hint):
            return False  # Can't modify what doesn't exist
        
        # Find the file containing the target
        target_file = None
        if file_hint and Path(file_hint).exists():
            target_file = file_hint
        else:
            # Search for the target in all Python files
            for py_file in Path('.').rglob('*.py'):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        if re.search(rf'^\s*def\s+{target}\s*\(', content, re.MULTILINE) or \
                           re.search(rf'^\s*class\s+{target}\s*[:\(]', content, re.MULTILINE) or \
                           re.search(rf'^\s*async\s+def\s+{target}\s*\(', content, re.MULTILINE):
                            target_file = str(py_file)
                            break
                except:
                    continue
        
        if not target_file:
            return False
        
        # Read the target file and analyze the function/class
        try:
            with open(target_file, 'r') as f:
                content = f.read()
            
            # Extract the function/class definition
            function_content = self._extract_function_content(content, target)
            if not function_content:
                return False
            
            # Check for specific modification types
            return self._verify_modification_type(modification_type, function_content, details)
            
        except Exception:
            return False
    
    def _extract_function_content(self, file_content: str, function_name: str) -> Optional[str]:
        """Extract the content of a specific function or class from file content"""
        lines = file_content.split('\n')
        
        # Find the function/class definition
        start_line = None
        for i, line in enumerate(lines):
            # Check for function definition
            if re.match(rf'^\s*def\s+{function_name}\s*\(', line) or \
               re.match(rf'^\s*async\s+def\s+{function_name}\s*\(', line) or \
               re.match(rf'^\s*class\s+{function_name}\s*[:\(]', line):
                start_line = i
                break
        
        if start_line is None:
            return None
        
        # Find the end of the function/class (next definition at same indentation level)
        start_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
        end_line = len(lines)
        
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':  # Skip empty lines
                continue
            current_indent = len(line) - len(line.lstrip())
            # If we find a line at same or lower indentation that starts a definition, that's the end
            if current_indent <= start_indent and (line.strip().startswith('def ') or 
                                                  line.strip().startswith('class ') or
                                                  line.strip().startswith('async def ')):
                end_line = i
                break
        
        return '\n'.join(lines[start_line:end_line])
    
    def _verify_modification_type(self, modification_type: str, function_content: str, details: str) -> bool:
        """Verify if a specific type of modification exists in the function content"""
        
        if modification_type == 'error_handling':
            # Much stricter error handling detection
            has_try_except = 'try:' in function_content and ('except ' in function_content or 'except:' in function_content)
            has_raise = re.search(r'\braise\s+\w+', function_content)  # Actual raise statement
            has_exception_import = 'Exception' in function_content or 'Error' in function_content
            # Must have actual structured error handling, not just print statements
            return has_try_except and (has_raise or has_exception_import)
        
        elif modification_type == 'async_conversion':
            # Function must actually be async
            is_async_function = 'async def' in function_content
            has_await = 'await ' in function_content
            return is_async_function and has_await
        
        elif modification_type == 'database_integration':
            # Look for actual database connection code, not just keywords
            db_connection_patterns = [
                r'\.connect\(',
                r'\.cursor\(',
                r'\.execute\(',
                r'sqlite3\.',
                r'psycopg2\.',
                r'mysql\.',
                r'Session\(',
                r'engine\.',
                r'connection\s*='
            ]
            return any(re.search(pattern, function_content) for pattern in db_connection_patterns)
        
        elif modification_type == 'input_validation':
            # Look for actual validation code, not just type hints
            validation_patterns = [
                r'isinstance\(',
                r'type\(.*\)\s*==',
                r'if\s+not\s+\w+:',
                r'assert\s+\w+',
                r'raise\s+ValueError',
                r'raise\s+TypeError',
                r'\.isdigit\(',
                r'len\(.*\)\s*[<>=]'
            ]
            return any(re.search(pattern, function_content) for pattern in validation_patterns)
        
        elif modification_type == 'logging':
            # Must have actual logging imports and calls, not just print
            logging_patterns = [
                r'import\s+logging',
                r'from\s+logging',
                r'logger\.',
                r'logging\.',
                r'log\.',
                r'getLogger\('
            ]
            has_logging_import = any(re.search(pattern, function_content) for pattern in logging_patterns)
            has_logging_call = re.search(r'(logger|logging)\.(debug|info|warning|error|critical)', function_content)
            return has_logging_import or has_logging_call
        
        elif modification_type == 'authentication':
            # Look for actual authentication code
            auth_patterns = [
                r'token',
                r'auth',
                r'jwt',
                r'session',
                r'login',
                r'verify',
                r'@login_required',
                r'@auth',
                r'Authentication',
                r'Authorization'
            ]
            return any(re.search(pattern, function_content, re.IGNORECASE) for pattern in auth_patterns)
        
        elif modification_type == 'caching':
            # Look for actual caching implementation
            cache_patterns = [
                r'cache',
                r'redis',
                r'memcache',
                r'@lru_cache',
                r'@cache',
                r'Cache',
                r'get.*cache',
                r'set.*cache'
            ]
            return any(re.search(pattern, function_content, re.IGNORECASE) for pattern in cache_patterns)
        
        elif modification_type == 'optimization':
            # Very conservative - require explicit optimization indicators
            opt_patterns = [
                r'@lru_cache',
                r'@cache',
                r'cache',
                r'optimize',
                r'performance',
                r'efficient',
                r'O\([nN]\)',  # Big O notation
                r'complexity'
            ]
            return any(re.search(pattern, function_content, re.IGNORECASE) for pattern in opt_patterns)
        
        elif modification_type == 'configuration':
            # Look for environment variables or config patterns
            config_patterns = [
                r'os\.environ',
                r'getenv',
                r'config',
                r'settings',
                r'\.env',
                r'environ',
                r'Config'
            ]
            return any(re.search(pattern, function_content, re.IGNORECASE) for pattern in config_patterns)
        
        elif modification_type in ['rate_limiting', 'testing', 'documentation', 'shutdown_handling']:
            # These require very specific implementations
            return False  # Very conservative - likely AI hallucination
        
        elif modification_type in ['general_modification', 'bug_fix']:
            # For general modifications, we can't verify without original code
            # Be very conservative - assume lying unless we have git history
            return False
        
        # Default to false for unknown modification types
        return False
    
    def print_report(self, results: Dict[str, Any]):
        """Print validation report"""
        print("\n=== Validation Report ===\n")
        
        for result in results['results']:
            icon = '✅' if result['passed'] else '❌'
            print(f"{icon} {result['test']}: {result['message']}")
        
        print(f"\nOverall: {'✅ PASSING' if results['passing'] else '❌ FAILING'}")