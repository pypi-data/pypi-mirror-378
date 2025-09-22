"""
File utility functions for the MCP Code Scanner.

This module provides utilities for finding Python files, detecting Python projects,
and other file-related operations needed by the scanner.
"""

import os
from pathlib import Path
from typing import List, Set


def find_python_files(
    project_path: Path, 
    include_tests: bool = True,
    exclude_patterns: Set[str] = None
) -> List[Path]:
    """
    Find all Python files in a project directory.
    
    Args:
        project_path: Root directory to search
        include_tests: Whether to include test files
        exclude_patterns: Set of patterns to exclude (e.g., {'__pycache__', '.venv'})
    
    Returns:
        List of Python file paths
    """
    if exclude_patterns is None:
        exclude_patterns = {
            '__pycache__',
            '.pytest_cache',
            '.mypy_cache',
            '.ruff_cache',
            '.venv',
            'venv',
            'env',
            '.env',
            '.git',
            '.tox',
            'node_modules',
            'build',
            'dist',
            '*.egg-info'
        }
    
    python_files = []
    
    for root, dirs, files in os.walk(project_path):
        root_path = Path(root)
        
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not _should_exclude_dir(d, exclude_patterns)]
        
        # Skip test directories if not including tests
        if not include_tests:
            dirs[:] = [d for d in dirs if not _is_test_directory(d)]
        
        for file in files:
            if file.endswith('.py'):
                file_path = root_path / file
                
                # Skip test files if not including tests
                if not include_tests and _is_test_file(file_path):
                    continue
                
                python_files.append(file_path)
    
    return sorted(python_files)


def is_python_project(project_path: Path) -> bool:
    """
    Check if a directory contains a Python project.
    
    Args:
        project_path: Directory to check
    
    Returns:
        True if it appears to be a Python project
    """
    # Check for common Python project files
    python_indicators = [
        'pyproject.toml',
        'setup.py',
        'setup.cfg',
        'requirements.txt',
        'Pipfile',
        'poetry.lock',
        'environment.yml',
        'conda.yml'
    ]
    
    for indicator in python_indicators:
        if (project_path / indicator).exists():
            return True
    
    # Check for Python files in the root or immediate subdirectories
    python_files = list(project_path.glob('*.py'))
    if python_files:
        return True
    
    # Check one level deep for Python files
    for subdir in project_path.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('.'):
            python_files = list(subdir.glob('*.py'))
            if python_files:
                return True
    
    return False


def get_project_structure(project_path: Path) -> dict:
    """
    Analyze the structure of a Python project.
    
    Args:
        project_path: Root directory of the project
    
    Returns:
        Dictionary containing project structure information
    """
    structure = {
        'root_path': str(project_path),
        'python_files': [],
        'test_files': [],
        'config_files': [],
        'documentation_files': [],
        'package_directories': [],
        'total_lines': 0,
        'has_tests': False,
        'has_docs': False,
        'packaging_info': {}
    }
    
    # Find all Python files
    all_python_files = find_python_files(project_path, include_tests=True)
    
    for py_file in all_python_files:
        relative_path = py_file.relative_to(project_path)
        
        if _is_test_file(py_file):
            structure['test_files'].append(str(relative_path))
        else:
            structure['python_files'].append(str(relative_path))
        
        # Count lines (excluding empty lines and comments)
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                code_lines = [
                    line.strip() for line in lines 
                    if line.strip() and not line.strip().startswith('#')
                ]
                structure['total_lines'] += len(code_lines)
        except Exception:
            pass  # Skip files that can't be read
    
    # Check for test presence
    structure['has_tests'] = len(structure['test_files']) > 0 or any(
        test_dir.exists() for test_dir in [
            project_path / 'tests',
            project_path / 'test',
            project_path / 'testing'
        ]
    )
    
    # Check for documentation
    doc_patterns = ['*.md', '*.rst', '*.txt']
    doc_files = []
    for pattern in doc_patterns:
        doc_files.extend(project_path.glob(pattern))
    
    structure['documentation_files'] = [
        str(f.relative_to(project_path)) for f in doc_files
    ]
    structure['has_docs'] = len(doc_files) > 0 or (project_path / 'docs').exists()
    
    # Check for configuration files
    config_files = [
        'pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt',
        'Pipfile', 'poetry.lock', 'tox.ini', '.pre-commit-config.yaml',
        '.flake8', '.pylintrc', 'mypy.ini', 'pytest.ini'
    ]
    
    structure['config_files'] = [
        config for config in config_files 
        if (project_path / config).exists()
    ]
    
    # Packaging information
    structure['packaging_info'] = _analyze_packaging(project_path)
    
    # Find package directories
    for item in project_path.iterdir():
        if (item.is_dir() and 
            not item.name.startswith('.') and 
            (item / '__init__.py').exists()):
            structure['package_directories'].append(item.name)
    
    return structure


def get_file_complexity_metrics(file_path: Path) -> dict:
    """
    Get basic complexity metrics for a Python file.
    
    Args:
        file_path: Path to the Python file
    
    Returns:
        Dictionary containing complexity metrics
    """
    metrics = {
        'total_lines': 0,
        'code_lines': 0,
        'comment_lines': 0,
        'blank_lines': 0,
        'function_count': 0,
        'class_count': 0,
        'import_count': 0
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        in_multiline_comment = False
        
        for line in lines:
            metrics['total_lines'] += 1
            stripped = line.strip()
            
            if not stripped:
                metrics['blank_lines'] += 1
                continue
            
            # Handle multiline strings/comments
            if '"""' in line or "'''" in line:
                in_multiline_comment = not in_multiline_comment
                if in_multiline_comment or '"""' in line or "'''" in line:
                    metrics['comment_lines'] += 1
                    continue
            
            if in_multiline_comment:
                metrics['comment_lines'] += 1
                continue
            
            # Single line comments
            if stripped.startswith('#'):
                metrics['comment_lines'] += 1
                continue
            
            # Code lines
            metrics['code_lines'] += 1
            
            # Count constructs
            if stripped.startswith('def '):
                metrics['function_count'] += 1
            elif stripped.startswith('class '):
                metrics['class_count'] += 1
            elif stripped.startswith(('import ', 'from ')):
                metrics['import_count'] += 1
    
    except Exception:
        pass  # Return empty metrics if file can't be read
    
    return metrics


def _should_exclude_dir(dirname: str, exclude_patterns: Set[str]) -> bool:
    """Check if a directory should be excluded from scanning."""
    for pattern in exclude_patterns:
        if pattern.endswith('*'):
            if dirname.startswith(pattern[:-1]):
                return True
        elif dirname == pattern:
            return True
    return False


def _is_test_directory(dirname: str) -> bool:
    """Check if a directory name indicates it contains tests."""
    test_indicators = {'test', 'tests', 'testing', 'spec', 'specs'}
    return dirname.lower() in test_indicators


def _is_test_file(file_path: Path) -> bool:
    """Check if a file appears to be a test file."""
    filename = file_path.name.lower()
    
    # Common test file patterns
    test_patterns = [
        'test_',      # test_something.py
        '_test',      # something_test.py
        'tests',      # tests.py
        'conftest'    # conftest.py
    ]
    
    for pattern in test_patterns:
        if pattern in filename:
            return True
    
    # Check if in a test directory
    for parent in file_path.parents:
        if _is_test_directory(parent.name):
            return True
    
    return False


def _analyze_packaging(project_path: Path) -> dict:
    """Analyze packaging configuration of a project."""
    packaging_info = {
        'has_pyproject_toml': False,
        'has_setup_py': False,
        'has_setup_cfg': False,
        'has_requirements_txt': False,
        'has_pipfile': False,
        'build_system': 'unknown',
        'dependencies_source': 'unknown'
    }
    
    # Check for packaging files
    if (project_path / 'pyproject.toml').exists():
        packaging_info['has_pyproject_toml'] = True
        packaging_info['build_system'] = 'pyproject.toml'
        packaging_info['dependencies_source'] = 'pyproject.toml'
    
    if (project_path / 'setup.py').exists():
        packaging_info['has_setup_py'] = True
        if packaging_info['build_system'] == 'unknown':
            packaging_info['build_system'] = 'setuptools'
    
    if (project_path / 'setup.cfg').exists():
        packaging_info['has_setup_cfg'] = True
    
    if (project_path / 'requirements.txt').exists():
        packaging_info['has_requirements_txt'] = True
        if packaging_info['dependencies_source'] == 'unknown':
            packaging_info['dependencies_source'] = 'requirements.txt'
    
    if (project_path / 'Pipfile').exists():
        packaging_info['has_pipfile'] = True
        packaging_info['dependencies_source'] = 'Pipfile'
    
    return packaging_info


def create_gitignore(project_path: Path, template: str = 'python') -> bool:
    """
    Create a .gitignore file for the project.
    
    Args:
        project_path: Root directory of the project
        template: Template to use ('python', 'django', etc.)
    
    Returns:
        True if .gitignore was created successfully
    """
    gitignore_content = _get_gitignore_template(template)
    gitignore_path = project_path / '.gitignore'
    
    try:
        if not gitignore_path.exists():
            gitignore_path.write_text(gitignore_content, encoding='utf-8')
            return True
        else:
            # Append to existing .gitignore
            existing_content = gitignore_path.read_text(encoding='utf-8')
            if '# Python Code Scanner additions' not in existing_content:
                gitignore_path.write_text(
                    existing_content + '\n\n# Python Code Scanner additions\n' + gitignore_content,
                    encoding='utf-8'
                )
            return True
    except Exception:
        return False


def _get_gitignore_template(template: str) -> str:
    """Get gitignore template content."""
    python_template = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Code quality tool caches
.ruff_cache/
.pylint.d/
"""
    
    templates = {
        'python': python_template,
        'django': python_template + '\n# Django specific\ndb.sqlite3\nmedia/\nstatic/\n',
        'flask': python_template + '\n# Flask specific\ninstance/\n.webassets-cache\n'
    }
    
    return templates.get(template, python_template)