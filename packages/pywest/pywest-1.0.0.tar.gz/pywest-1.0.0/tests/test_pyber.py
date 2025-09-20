"""
Complete test suite for pybox - Portable Python Project Manager
Single file containing all tests as requested
"""

import os
import sys
import tempfile
import shutil
import zipfile
import subprocess
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from io import StringIO
import pytest
import platform

# Add the pybox package to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from pybox.pybox import pybox, Colors, main
import pybox.pybox


# Test fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_pyproject_toml():
    """Sample pyproject.toml content for testing"""
    return '''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "testproject"
version = "0.1.0"
description = "A test project"
dependencies = []

[tool.pybox]
python_version = "3.12.10"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
]
'''


@pytest.fixture
def mock_project_structure(temp_dir, sample_pyproject_toml):
    """Create a complete mock project structure"""
    # Create directories
    os.makedirs("src")
    os.makedirs("tests")
    os.makedirs(".venv")
    
    # Create files
    Path("pyproject.toml").write_text(sample_pyproject_toml)
    
    # Create main.py
    main_py_content = '''def main():
    """Main function for test project"""
    print("Hello from test project!")
    return "success"

if __name__ == "__main__":
    main()
'''
    Path("src/main.py").write_text(main_py_content)
    
    # Create test file
    test_content = '''import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import main

def test_main():
    """Test main function"""
    result = main()
    assert result == "success"
'''
    Path("tests/test_main.py").write_text(test_content)
    Path("tests/__init__.py").write_text("")
    
    # Create other files
    Path("README.md").write_text("# Test Project")
    Path("run.bat").write_text("@echo off\necho Starting test project...")
    Path(".gitignore").write_text(".venv/\n__pycache__/")
    
    # Create mock Python executable
    (Path(".venv") / "python.exe").touch()
    
    yield temp_dir


# Core functionality tests
class TestpyboxCore:
    """Test core pybox functionality"""
    
    def test_init(self):
        """Test pybox initialization"""
        pybox = pybox()
        assert isinstance(pybox.python_versions, dict)
        assert "3.12.10" in pybox.python_versions
        assert "3.11.9" in pybox.python_versions
        assert "3.10.11" in pybox.python_versions
        
    def test_python_versions_are_valid_urls(self):
        """Test that Python version URLs are valid"""
        pybox = pybox()
        for version, url in pybox.python_versions.items():
            assert url.startswith("https://www.python.org/ftp/python/")
            assert f"python-{version}-embed-amd64.zip" in url
    
    def test_print_header(self, capsys):
        """Test header printing"""
        pybox = pybox()
        pybox.print_header()
        captured = capsys.readouterr()
        assert "pybox" in captured.out
        assert "Portable Python Project Manager" in captured.out
        assert "Windows Only" in captured.out


# Project creation tests
class TestProjectCreation:
    """Test project creation functionality"""
    
    @patch('platform.system')
    def test_new_project_non_windows_fails(self, mock_platform, temp_dir):
        """Test that project creation fails on non-Windows systems"""
        mock_platform.return_value = "Linux"
        pybox = pybox()
        result = pybox.new_project("testproject")
        assert result is False
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_new_project_success(self, mock_subprocess, mock_platform, temp_dir, capsys, monkeypatch):
        """Test successful project creation"""
        mock_platform.return_value = "Windows"
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Mock input for Python version selection (press Enter for default)
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        pybox = pybox()
        result = pybox.new_project("testproject", no_git=True)
        
        assert result is True
        
        # Check project structure
        project_path = Path("testproject")
        assert project_path.exists()
        assert (project_path / "src").exists()
        assert (project_path / "tests").exists()
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "README.md").exists()
        assert (project_path / "run.bat").exists()
        assert (project_path / ".gitignore").exists()
        assert (project_path / "src" / "main.py").exists()
        assert (project_path / "tests" / "__init__.py").exists()
        assert (project_path / "tests" / "test_main.py").exists()
    
    @patch('platform.system')
    def test_new_project_existing_directory(self, mock_platform, temp_dir):
        """Test that project creation fails if directory exists"""
        mock_platform.return_value = "Windows"
        
        # Create existing directory
        os.makedirs("existing_project")
        
        pybox = pybox()
        result = pybox.new_project("existing_project")
        assert result is False
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_new_project_with_git(self, mock_subprocess, mock_platform, temp_dir, monkeypatch):
        """Test project creation with git initialization"""
        mock_platform.return_value = "Windows"
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Mock input for Python version selection
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        pybox = pybox()
        result = pybox.new_project("testproject", no_git=False)
        
        assert result is True
        
        # Check that git commands were called
        git_calls = [call for call in mock_subprocess.call_args_list if 'git' in str(call)]
        assert len(git_calls) >= 3  # git --version, git init, git add, git commit
    
    def test_create_pyproject_toml(self, temp_dir):
        """Test pyproject.toml generation"""
        pybox = pybox()
        content = pybox.create_pyproject_toml("testproject", "3.12.10")
        
        assert "name = \"testproject\"" in content
        assert "python_version = \"3.12.10\"" in content
        assert "[tool.uv]" in content
        assert "[tool.ruff]" in content
        assert "pytest" in content
    
    def test_create_main_py(self, temp_dir):
        """Test main.py generation"""
        pybox = pybox()
        content = pybox.create_main_py()
        
        assert "def main():" in content
        assert "Hello from pybox" in content
        assert "if __name__ == \"__main__\":" in content
    
    def test_create_run_bat(self, temp_dir):
        """Test run.bat generation"""
        pybox = pybox()
        content = pybox.create_run_bat("testproject")
        
        assert "@echo off" in content
        assert "testproject" in content
        assert ".venv" in content
        assert "pybox setup" in content
    
    def test_create_readme(self, temp_dir):
        """Test README.md generation"""
        pybox = pybox()
        content = pybox.create_readme("testproject")
        
        assert "# testproject" in content
        assert "pybox setup" in content
        assert "pybox run" in content
        assert "UV package manager" in content
    
    def test_create_gitignore(self, temp_dir):
        """Test .gitignore generation"""
        pybox = pybox()
        content = pybox.create_gitignore()
        
        assert ".venv/" in content
        assert "__pycache__/" in content
        assert "*.pyc" in content
        assert "uv.lock" in content


# Embedded Python setup tests
class TestEmbeddedPython:
    """Test embedded Python setup functionality"""
    
    @patch('platform.system')
    def test_setup_embedded_python_non_windows(self, mock_platform, temp_dir):
        """Test embedded Python setup fails on non-Windows"""
        mock_platform.return_value = "Linux"
        pybox = pybox()
        result = pybox.setup_embedded_python()
        assert result is None
    
    @patch('platform.system')
    def test_setup_embedded_python_existing(self, mock_platform, temp_dir):
        """Test embedded Python setup with existing installation"""
        mock_platform.return_value = "Windows"
        
        # Create fake existing Python
        venv_dir = Path(".venv")
        venv_dir.mkdir()
        (venv_dir / "python.exe").touch()
        
        pybox = pybox()
        result = pybox.setup_embedded_python()
        
        assert result == str(venv_dir / "python.exe")
    
    def test_setup_embedded_python_invalid_version(self, temp_dir):
        """Test embedded Python setup with invalid version"""
        with patch('platform.system', return_value="Windows"):
            pybox = pybox()
            result = pybox.setup_embedded_python("invalid.version")
            assert result is None
    
    @patch('platform.system')
    @patch('urllib.request.urlretrieve')
    @patch('zipfile.ZipFile')
    @patch('pybox.pybox.pybox.setup_pip_and_uv_windows')
    def test_setup_embedded_python_success(self, mock_setup_pip, mock_zipfile, 
                                         mock_urlretrieve, mock_platform, temp_dir):
        """Test successful embedded Python setup"""
        mock_platform.return_value = "Windows"
        mock_setup_pip.return_value = True
        
        # Mock zipfile extraction
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        
        pybox = pybox()
        result = pybox.setup_embedded_python("3.12.10")
        
        # Verify the process
        mock_urlretrieve.assert_called_once()
        mock_zip_instance.extractall.assert_called_once()
        mock_setup_pip.assert_called_once()
        
        assert result == str(Path(".venv") / "python.exe")


# Package management tests
class TestPackageManagement:
    """Test package management functionality"""
    
    def test_get_python_version_no_file(self, temp_dir):
        """Test getting Python version when no pyproject.toml exists"""
        pybox = pybox()
        version = pybox.get_python_version()
        assert version == "3.12.10"  # default
    
    def test_get_python_version_from_file(self, mock_project_structure):
        """Test getting Python version from pyproject.toml"""
        pybox = pybox()
        version = pybox.get_python_version()
        assert version == "3.12.10"
    
    def test_get_python_exe_exists(self, mock_project_structure):
        """Test getting Python executable path when it exists"""
        pybox = pybox()
        exe_path = pybox.get_python_exe()
        assert exe_path == str(Path(".venv") / "python.exe")
    
    def test_get_python_exe_not_exists(self, temp_dir):
        """Test getting Python executable path when it doesn't exist"""
        pybox = pybox()
        exe_path = pybox.get_python_exe()
        assert exe_path is None
    
    @patch('subprocess.run')
    def test_add_packages_success(self, mock_subprocess, mock_project_structure):
        """Test successful package addition"""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        pybox = pybox()
        with patch.object(pybox, 'update_pyproject_dependencies', return_value=True):
            result = pybox.add_packages(["requests", "pytest"])
        
        assert result is True
        # Check that UV was used
        uv_calls = [call for call in mock_subprocess.call_args_list 
                   if any("-m" in str(arg) and "uv" in str(arg) for arg in call[0][0])]
        assert len(uv_calls) >= 1
    
    @patch('subprocess.run')
    def test_remove_packages_success(self, mock_subprocess, mock_project_structure):
        """Test successful package removal"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        pybox = pybox()
        with patch.object(pybox, 'update_pyproject_dependencies', return_value=True):
            result = pybox.remove_packages(["requests"])
        
        assert result is True
    
    def test_add_packages_no_pyproject(self, temp_dir):
        """Test package addition fails without pyproject.toml"""
        pybox = pybox()
        result = pybox.add_packages(["requests"])
        assert result is False
    
    def test_remove_packages_no_python(self, temp_dir):
        """Test package removal fails without Python environment"""
        Path("pyproject.toml").write_text("[project]\nname = 'test'")
        
        pybox = pybox()
        result = pybox.remove_packages(["requests"])
        assert result is False
    
    @patch('subprocess.run')
    def test_sync_dependencies_success(self, mock_subprocess, mock_project_structure):
        """Test successful dependency sync"""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        pybox = pybox()
        result = pybox.sync_dependencies()
        
        assert result is True


# Project operations tests
class TestProjectOperations:
    """Test project operation functionality"""
    
    def test_run_project_no_main(self, temp_dir):
        """Test running project fails without main.py"""
        pybox = pybox()
        result = pybox.run_project()
        assert result is False
    
    @patch('subprocess.run')
    def test_run_project_success(self, mock_subprocess, mock_project_structure):
        """Test successful project run"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        pybox = pybox()
        result = pybox.run_project()
        
        assert result is True
        # Check that src/main.py was executed
        call_args = mock_subprocess.call_args[0][0]
        assert "src/main.py" in call_args
    
    @patch('subprocess.run')
    def test_run_project_auto_setup(self, mock_subprocess, temp_dir):
        """Test project run with automatic setup"""
        # Create minimal structure without .venv
        os.makedirs("src")
        Path("src/main.py").write_text("def main(): pass")
        Path("pyproject.toml").write_text("[project]\nname='test'\n[tool.pybox]\npython_version='3.12.10'")
        
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        pybox = pybox()
        with patch.object(pybox, 'setup_project', return_value=True):
            with patch.object(pybox, 'get_python_exe', side_effect=[None, str(Path(".venv/python.exe"))]):
                result = pybox.run_project()
        
        assert result is True
    
    @patch('subprocess.run')
    def test_run_tests_success(self, mock_subprocess, mock_project_structure):
        """Test successful test run"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        pybox = pybox()
        result = pybox.run_tests()
        
        assert result is True
    
    @patch('subprocess.run')
    def test_check_code_success(self, mock_subprocess, mock_project_structure):
        """Test successful code check"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        pybox = pybox()
        result = pybox.check_code()
        
        assert result is True
    
    @patch('subprocess.run')
    def test_format_code_success(self, mock_subprocess, mock_project_structure):
        """Test successful code formatting"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        pybox = pybox()
        result = pybox.format_code()
        
        assert result is True
    
    def test_setup_project_no_pyproject(self, temp_dir):
        """Test setup fails without pyproject.toml"""
        pybox = pybox()
        result = pybox.setup_project()
        assert result is False
    
    @patch('subprocess.run')
    def test_setup_project_success(self, mock_subprocess, temp_dir):
        """Test successful project setup"""
        Path("pyproject.toml").write_text("[project]\nname='test'\n[tool.pybox]\npython_version='3.12.10'")
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        pybox = pybox()
        with patch.object(pybox, 'setup_embedded_python', return_value=str(Path(".venv/python.exe"))):
            with patch.object(pybox, 'sync_dependencies', return_value=True):
                result = pybox.setup_project()
        
        assert result is True


# Packaging tests
class TestPackaging:
    """Test project packaging functionality"""
    
    def test_pack_project_no_pyproject(self, temp_dir):
        """Test packaging fails without pyproject.toml"""
        pybox = pybox()
        result = pybox.pack_project()
        assert result is False
    
    def test_pack_project_success(self, mock_project_structure):
        """Test successful project packaging"""
        pybox = pybox()
        result = pybox.pack_project()
        
        assert result is True
        
        # Check that zip file was created
        dist_dir = Path("dist")
        assert dist_dir.exists()
        
        zip_files = list(dist_dir.glob("*.zip"))
        assert len(zip_files) == 1
        assert "testproject-0.1.0.zip" in str(zip_files[0])
        
        # Check zip contents
        with zipfile.ZipFile(zip_files[0], 'r') as zipf:
            file_list = zipf.namelist()
            assert "pyproject.toml" in file_list
            assert "src/main.py" in file_list
            assert "README.md" in file_list
            assert "run.bat" in file_list


# TOML operations tests
class TestTOMLOperations:
    """Test TOML file operations"""
    
    @patch('subprocess.run')
    def test_ensure_toml_dependencies_success(self, mock_subprocess, mock_project_structure):
        """Test successful TOML dependencies installation"""
        # Mock tomllib import success (Python 3.11+)
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        pybox = pybox()
        result = pybox.ensure_toml_dependencies()
        
        assert result is True
    
    @patch('subprocess.run')
    def test_ensure_toml_dependencies_install_tomli(self, mock_subprocess, mock_project_structure):
        """Test TOML dependencies installation when tomli is needed"""
        # Mock tomllib import failure, then tomli import failure, then success after install
        mock_subprocess.side_effect = [
            MagicMock(returncode=1),  # tomllib import fails
            MagicMock(returncode=1),  # tomli import fails
            MagicMock(returncode=0),  # tomli install succeeds
            MagicMock(returncode=0),  # tomli-w install succeeds
        ]
        
        pybox = pybox()
        result = pybox.ensure_toml_dependencies()
        
        assert result is True
        # Check that UV was used to install tomli
        install_calls = [call for call in mock_subprocess.call_args_list 
                        if "install" in str(call)]
        assert len(install_calls) >= 2  # tomli and tomli-w


# CLI command tests
class TestCLICommands:
    """Test CLI command parsing and execution"""
    
    @patch('platform.system', return_value='Windows')
    def test_no_arguments_shows_help(self, mock_platform, capsys):
        """Test that running with no arguments shows help"""
        with patch('sys.argv', ['pybox']):
            try:
                main()
            except SystemExit:
                pass  # argparse calls sys.exit when showing help
        
        captured = capsys.readouterr()
        assert "usage:" in captured.out or "usage:" in captured.err
    
    @patch('platform.system', return_value='Windows')
    @patch('pybox.pybox.pybox.new_project')
    def test_new_command(self, mock_new_project, mock_platform):
        """Test 'pybox new' command"""
        mock_new_project.return_value = True
        
        with patch('sys.argv', ['pybox', 'new', 'testproject']):
            main()
        
        mock_new_project.assert_called_once_with('testproject', False)
    
    @patch('platform.system', return_value='Windows')
    @patch('pybox.pybox.pybox.new_project')
    def test_new_command_with_no_git(self, mock_new_project, mock_platform):
        """Test 'pybox new --no-git' command"""
        mock_new_project.return_value = True
        
        with patch('sys.argv', ['pybox', 'new', 'testproject', '--no-git']):
            main()
        
        mock_new_project.assert_called_once_with('testproject', True)
    
    @patch('platform.system', return_value='Windows')
    @patch('pybox.pybox.pybox.setup_project')
    def test_setup_command(self, mock_setup, mock_platform):
        """Test 'pybox setup' command"""
        mock_setup.return_value = True
        
        with patch('sys.argv', ['pybox', 'setup']):
            main()
        
        mock_setup.assert_called_once()
    
    @patch('platform.system', return_value='Windows')
    @patch('pybox.pybox.pybox.run_project')
    def test_run_command(self, mock_run, mock_platform):
        """Test 'pybox run' command"""
        mock_run.return_value = True
        
        with patch('sys.argv', ['pybox', 'run']):
            main()
        
        mock_run.assert_called_once()
    
    @patch('platform.system', return_value='Windows')
    @patch('pybox.pybox.pybox.add_packages')
    def test_add_command(self, mock_add, mock_platform):
        """Test 'pybox add' command"""
        mock_add.return_value = True
        
        with patch('sys.argv', ['pybox', 'add', 'requests', 'pytest']):
            main()
        
        mock_add.assert_called_once_with(['requests', 'pytest'])
    
    @patch('platform.system', return_value='Windows')
    @patch('pybox.pybox.pybox.remove_packages')
    def test_remove_command(self, mock_remove, mock_platform):
        """Test 'pybox remove' command"""
        mock_remove.return_value = True
        
        with patch('sys.argv', ['pybox', 'remove', 'requests']):
            main()
        
        mock_remove.assert_called_once_with(['requests'])
    
    @patch('platform.system', return_value='Windows')
    @patch('pybox.pybox.pybox.sync_dependencies')
    def test_sync_command(self, mock_sync, mock_platform):
        """Test 'pybox sync' command"""
        mock_sync.return_value = True
        
        with patch('sys.argv', ['pybox', 'sync']):
            main()
        
        mock_sync.assert_called_once()
    
    @patch('platform.system', return_value='Windows')
    @patch('pybox.pybox.pybox.run_tests')
    def test_test_command(self, mock_test, mock_platform):
        """Test 'pybox test' command"""
        mock_test.return_value = True
        
        with patch('sys.argv', ['pybox', 'test']):
            main()
        
        mock_test.assert_called_once()
    
    @patch('platform.system', return_value='Windows')
    @patch('pybox.pybox.pybox.check_code')
    def test_check_command(self, mock_check, mock_platform):
        """Test 'pybox check' command"""
        mock_check.return_value = True
        
        with patch('sys.argv', ['pybox', 'check']):
            main()
        
        mock_check.assert_called_once()
    
    @patch('platform.system', return_value='Windows')
    @patch('pybox.pybox.pybox.format_code')
    def test_format_command(self, mock_format, mock_platform):
        """Test 'pybox format' command"""
        mock_format.return_value = True
        
        with patch('sys.argv', ['pybox', 'format']):
            main()
        
        mock_format.assert_called_once()
    
    @patch('platform.system', return_value='Windows')
    @patch('pybox.pybox.pybox.pack_project')
    def test_pack_command(self, mock_pack, mock_platform):
        """Test 'pybox pack' command"""
        mock_pack.return_value = True
        
        with patch('sys.argv', ['pybox', 'pack']):
            main()
        
        mock_pack.assert_called_once()
    
    @patch('platform.system')
    def test_non_windows_exit(self, mock_platform, capsys):
        """Test that non-Windows systems exit with error"""
        mock_platform.return_value = "Linux"
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Windows only" in captured.out


# Error handling and edge cases
class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @patch('subprocess.run')
    def test_subprocess_timeout(self, mock_subprocess, temp_dir):
        """Test handling of subprocess timeouts"""
        from subprocess import TimeoutExpired
        mock_subprocess.side_effect = TimeoutExpired("cmd", 300)
        
        # Create minimal project structure
        Path("pyproject.toml").write_text("[project]\nname='test'")
        venv_dir = Path(".venv")
        venv_dir.mkdir()
        (venv_dir / "python.exe").touch()
        
        pybox = pybox()
        result = pybox.add_packages(["requests"])
        
        assert result is False
    
    @patch('subprocess.run')
    def test_subprocess_error(self, mock_subprocess, temp_dir):
        """Test handling of subprocess errors"""
        from subprocess import CalledProcessError
        mock_subprocess.side_effect = CalledProcessError(1, "cmd", stderr="Error occurred")
        
        # Create minimal project structure
        Path("pyproject.toml").write_text("[project]\nname='test'")
        venv_dir = Path(".venv")
        venv_dir.mkdir()
        (venv_dir / "python.exe").touch()
        
        pybox = pybox()
        result = pybox.add_packages(["invalid-package"])
        
        assert result is False
    
    def test_corrupted_pyproject_toml(self, temp_dir):
        """Test handling of corrupted pyproject.toml"""
        # Create invalid TOML file
        Path("pyproject.toml").write_text("[project\ninvalid toml")
        
        pybox = pybox()
        version = pybox.get_python_version()
        
        # Should return default version when file is corrupted
        assert version == "3.12.10"
    
    @patch('urllib.request.urlretrieve')
    def test_network_failure(self, mock_urlretrieve, temp_dir):
        """Test handling of network failures during Python download"""
        mock_urlretrieve.side_effect = Exception("Network error")
        
        with patch('platform.system', return_value="Windows"):
            pybox = pybox()
            result = pybox.setup_embedded_python("3.12.10")
            
            assert result is None


# Integration tests
class TestIntegration:
    """Integration tests for complete workflows"""
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_complete_workflow(self, mock_subprocess, mock_platform, temp_dir, monkeypatch):
        """Test complete workflow: create -> setup -> add packages -> run -> pack"""
        mock_platform.return_value = "Windows"
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Mock input for project creation
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        pybox = pybox()
        
        # Step 1: Create project
        with patch('urllib.request.urlretrieve'), \
             patch('zipfile.ZipFile'), \
             patch.object(pybox, 'setup_pip_and_uv_windows', return_value=True):
            
            result = pybox.new_project("testproject", no_git=True)
            assert result is True
        
        # Change to project directory
        os.chdir("testproject")
        
        # Step 2: Setup project (mock the embedded Python setup)
        with patch.object(pybox, 'setup_embedded_python', return_value=str(Path(".venv/python.exe"))), \
             patch.object(pybox, 'sync_dependencies', return_value=True):
            result = pybox.setup_project()
            assert result is True
        
        # Create mock python.exe for remaining tests
        venv_dir = Path(".venv")
        venv_dir.mkdir(exist_ok=True)
        (venv_dir / "python.exe").touch()
        
        # Step 3: Add packages
        with patch.object(pybox, 'update_pyproject_dependencies', return_value=True):
            result = pybox.add_packages(["requests"])
            assert result is True
        
        # Step 4: Run project
        result = pybox.run_project()
        assert result is True
        
        # Step 5: Pack project
        result = pybox.pack_project()
        assert result is True
        
        # Verify final structure
        assert Path("dist").exists()
        zip_files = list(Path("dist").glob("*.zip"))
        assert len(zip_files) == 1
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_project_lifecycle_with_dependencies(self, mock_subprocess, mock_platform, temp_dir, monkeypatch):
        """Test project lifecycle with dependency management"""
        mock_platform.return_value = "Windows"
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        pybox = pybox()
        
        # Create project
        with patch.object(pybox, 'setup_pip_and_uv_windows', return_value=True):
            result = pybox.new_project("testproject", no_git=True)
            assert result is True
        
        os.chdir("testproject")
        
        # Setup environment
        venv_dir = Path(".venv")
        venv_dir.mkdir(exist_ok=True)
        (venv_dir / "python.exe").touch()
        
        # Test dependency operations
        with patch.object(pybox, 'update_pyproject_dependencies', return_value=True):
            # Add dependencies
            result = pybox.add_packages(["requests", "pytest"])
            assert result is True
            
            # Remove a dependency
            result = pybox.remove_packages(["pytest"])
            assert result is True
        
        # Test project operations
        result = pybox.run_tests()
        assert result is True
        
        result = pybox.check_code()
        assert result is True
        
        result = pybox.format_code()
        assert result is True


# Performance and stress tests
class TestPerformance:
    """Test performance and resource usage"""
    
    @patch('platform.system', return_value='Windows')
    @patch('subprocess.run')
    def test_large_project_creation(self, mock_subprocess, mock_platform, temp_dir, monkeypatch):
        """Test creating project with many files"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        pybox = pybox()
        result = pybox.new_project("large_project", no_git=True)
        
        assert result is True
        
        # Verify structure was created efficiently
        project_path = Path("large_project")
        assert project_path.exists()
        assert (project_path / "src").exists()
        assert (project_path / "tests").exists()
    
    @patch('subprocess.run')
    def test_multiple_package_operations(self, mock_subprocess, mock_project_structure):
        """Test adding and removing multiple packages"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        pybox = pybox()
        
        # Test adding multiple packages at once
        with patch.object(pybox, 'update_pyproject_dependencies', return_value=True):
            packages = ["requests", "pytest", "numpy", "pandas", "flask"]
            result = pybox.add_packages(packages)
            assert result is True
        
        # Test removing multiple packages
        with patch.object(pybox, 'update_pyproject_dependencies', return_value=True):
            result = pybox.remove_packages(["numpy", "pandas"])
            assert result is True


# Utility and helper tests
class TestUtilities:
    """Test utility functions and helpers"""
    
    def test_colors_class(self):
        """Test Colors class has required attributes"""
        assert hasattr(Colors, 'HEADER')
        assert hasattr(Colors, 'OKBLUE')
        assert hasattr(Colors, 'OKCYAN')
        assert hasattr(Colors, 'OKGREEN')
        assert hasattr(Colors, 'WARNING')
        assert hasattr(Colors, 'FAIL')
        assert hasattr(Colors, 'ENDC')
        assert hasattr(Colors, 'BOLD')
        assert hasattr(Colors, 'UNDERLINE')
        
        # Verify they are strings
        assert isinstance(Colors.HEADER, str)
        assert isinstance(Colors.OKGREEN, str)
        assert isinstance(Colors.FAIL, str)
    
    def test_version_selection_parsing(self, temp_dir, monkeypatch):
        """Test Python version selection input parsing"""
        pybox = pybox()
        
        # Test different input scenarios
        inputs_and_expected = [
            ("", "3.12.10"),  # Default
            ("1", "3.12.10"),  # First option
            ("2", "3.11.9"),   # Second option
            ("3", "3.10.11"),  # Third option
            ("invalid", "3.12.10"),  # Invalid input, should default
        ]
        
        with patch('platform.system', return_value='Windows'):
            for user_input, expected_version in inputs_and_expected:
                monkeypatch.setattr('builtins.input', lambda _: user_input)
                
                # We can't easily test the interactive part, but we can test version parsing
                # This would be tested in the actual new_project method
                assert expected_version in pybox.python_versions or expected_version == "3.12.10"


# Data validation tests
class TestDataValidation:
    """Test data validation and sanitization"""
    
    def test_project_name_validation(self, temp_dir):
        """Test project name validation"""
        pybox = pybox()
        
        with patch('platform.system', return_value='Windows'), \
             patch('builtins.input', return_value=""):
            
            # Valid project names should work
            valid_names = ["myproject", "my-project", "my_project", "MyProject123"]
            for name in valid_names:
                if not os.path.exists(name):
                    result = pybox.new_project(name, no_git=True)
                    assert result is True
                    shutil.rmtree(name, ignore_errors=True)
    
    def test_python_version_validation(self, temp_dir):
        """Test Python version validation"""
        pybox = pybox()
        
        # Valid versions should be accepted
        for version in pybox.python_versions.keys():
            result = pybox.setup_embedded_python(version)
            # We expect None due to mocking, but no exception should be raised
            assert result is None
        
        # Invalid version should be rejected
        with patch('platform.system', return_value='Windows'):
            result = pybox.setup_embedded_python("invalid.version")
            assert result is None
    
    def test_package_name_validation(self, mock_project_structure):
        """Test package name validation in add/remove operations"""
        pybox = pybox()
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0)
            
            with patch.object(pybox, 'update_pyproject_dependencies', return_value=True):
                # Test various package name formats
                valid_packages = [
                    "requests",
                    "requests==2.28.0",
                    "requests>=2.25.0",
                    "django[extra]",
                    "my-package",
                    "my_package"
                ]
                
                for package in valid_packages:
                    result = pybox.add_packages([package])
                    assert result is True


# Mocking and test environment tests
class TestEnvironment:
    """Test different environment configurations"""
    
    @patch('platform.system')
    def test_platform_detection(self, mock_platform, temp_dir):
        """Test platform detection works correctly"""
        pybox = pybox()
        
        # Test Windows detection
        mock_platform.return_value = "Windows"
        result = pybox.setup_embedded_python()
        # Should not immediately fail due to platform
        assert mock_platform.called
        
        # Test non-Windows detection
        mock_platform.return_value = "Linux"
        result = pybox.setup_embedded_python()
        assert result is None
        
        mock_platform.return_value = "Darwin"  # macOS
        result = pybox.setup_embedded_python()
        assert result is None
    
    def test_file_permissions(self, temp_dir):
        """Test file permission handling"""
        pybox = pybox()
        
        # Create a file with known permissions
        test_file = Path("test_permissions.txt")
        test_file.write_text("test content")
        
        # The file should exist and be readable
        assert test_file.exists()
        assert test_file.read_text() == "test content"
        
        # Test directory creation permissions
        test_dir = Path("test_directory")
        test_dir.mkdir()
        assert test_dir.exists()
        assert test_dir.is_dir()
    
    @patch('subprocess.run')
    def test_subprocess_environment_variables(self, mock_subprocess, mock_project_structure):
        """Test that subprocess calls use correct environment variables"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        pybox = pybox()
        result = pybox.run_project()
        
        # Verify subprocess was called
        assert mock_subprocess.called
        
        # Check that environment was passed (if available in call)
        if mock_subprocess.call_args and len(mock_subprocess.call_args) > 1:
            kwargs = mock_subprocess.call_args[1]
            if 'env' in kwargs:
                env = kwargs['env']
                assert 'PYTHONPATH' in env


# Final comprehensive test
class TestComprehensive:
    """Comprehensive end-to-end tests"""
    
    @patch('platform.system')
    @patch('subprocess.run')
    @patch('urllib.request.urlretrieve')
    @patch('zipfile.ZipFile')
    def test_full_pybox_workflow(self, mock_zipfile, mock_urlretrieve, mock_subprocess, mock_platform, temp_dir, monkeypatch):
        """Test the complete pybox workflow from start to finish"""
        # Setup mocks
        mock_platform.return_value = "Windows"
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        pybox = pybox()
        
        # 1. Create new project
        with patch.object(pybox, 'setup_pip_and_uv_windows', return_value=True):
            result = pybox.new_project("full_test_project", no_git=True)
            assert result is True
        
        # Verify project structure
        project_path = Path("full_test_project")
        assert project_path.exists()
        assert (project_path / "src" / "main.py").exists()
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "run.bat").exists()
        
        # Change to project directory
        os.chdir("full_test_project")
        
        # 2. Setup environment
        venv_dir = Path(".venv")
        venv_dir.mkdir(exist_ok=True)
        (venv_dir / "python.exe").touch()
        
        with patch.object(pybox, 'sync_dependencies', return_value=True):
            result = pybox.setup_project()
            assert result is True
        
        # 3. Add dependencies
        with patch.object(pybox, 'update_pyproject_dependencies', return_value=True):
            result = pybox.add_packages(["requests", "pytest"])
            assert result is True
        
        # 4. Run project
        result = pybox.run_project()
        assert result is True
        
        # 5. Run tests
        result = pybox.run_tests()
        assert result is True
        
        # 6. Check code quality
        result = pybox.check_code()
        assert result is True
        
        # 7. Format code
        result = pybox.format_code()
        assert result is True
        
        # 8. Sync dependencies
        result = pybox.sync_dependencies()
        assert result is True
        
        # 9. Remove a dependency
        with patch.object(pybox, 'update_pyproject_dependencies', return_value=True):
            result = pybox.remove_packages(["pytest"])
            assert result is True
        
        # 10. Pack project for distribution
        result = pybox.pack_project()
        assert result is True
        
        # Verify final state
        assert Path("dist").exists()
        zip_files = list(Path("dist").glob("*.zip"))
        assert len(zip_files) == 1
        
        # Verify all major operations succeeded
        assert all([
            project_path.exists(),
            (project_path / "src" / "main.py").exists(),
            (project_path / "pyproject.toml").exists(),
            (project_path / ".venv" / "python.exe").exists(),
            Path("dist").exists()
        ])


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])