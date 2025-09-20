"""
pybox - No Code Obfuscation, No Compiled PYCs, Open Python Projects
A tool for developing quickly shareable portable python apps based on embeddable python for Windows
"""

import os
import sys
import json
import shutil
import zipfile
import argparse
import subprocess
from pathlib import Path
from urllib.request import urlretrieve
from urllib.parse import urlparse
import tempfile
import platform

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class pybox:
    def __init__(self):
        self.python_versions = {
            "3.12.10": "https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip",
            "3.11.9": "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip",
            "3.10.11": "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip",
        }
        
    def print_header(self):
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("╔═════════════════════════════════════════════╗")
        print("║              🚀 pybox 🚀                  ║")
        print("║   Portable Python Project Manager        ║")
        print("║   No Code Obfuscation, Open Projects     ║")
        print("║              Windows Only                 ║")
        print("╚═════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")

    def create_pyproject_toml(self, project_name, python_version="3.12.10"):
        """Create minimal pyproject.toml with uv support"""
        return f'''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = "A portable Python project created with pybox"
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
readme = "README.md"
requires-python = ">={python_version[:3]}"
license = {{text = "MIT"}}
dependencies = []

# CLI Entry point for your project
[project.scripts]
{project_name} = "main:main"

[tool.pybox]
python_version = "{python_version}"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.ruff]
line-length = 88
target-version = "py{python_version.replace('.', '')[:3]}"

[tool.ruff.lint]
select = ["E", "F", "W", "C90"]
ignore = []
'''

    def create_main_py(self):
        """Create minimal main.py"""
        return '''"""
Main module for your pybox project
"""

def main():
    """Main function - entry point of your application"""
    print("🚀 Hello from pybox! 🚀")
    print("Your portable Python project is ready!")
    print("Edit this file to add your application logic.")

if __name__ == "__main__":
    main()
'''

    def create_run_bat(self, project_name):
        """Create run.bat for Windows that auto-setups environment"""
        return f'''@echo off
setlocal EnableDelayedExpansion
REM pybox Project Runner - {project_name}
REM This batch file sets up the environment and runs your pybox project

echo Starting {project_name}...

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Set up Python path and encoding (use local scope to avoid PATH pollution)
set "PYTHONPATH=%SCRIPT_DIR%\\src"
set "PYTHONIOENCODING=utf-8"
set "PYTHONLEGACYWINDOWSFSENCODING=1"

REM Check if .venv directory exists (Python virtual environment)
if exist "%SCRIPT_DIR%\\.venv\\python.exe" (
    echo Using existing Python environment...
    goto :run_project
)

echo No Python environment found. Setting up automatically...

REM Setup embedded Python environment
call :setup_python
if !ERRORLEVEL! neq 0 (
    echo Failed to setup Python environment.
    goto :error
)

REM Install dependencies
call :install_dependencies
if !ERRORLEVEL! neq 0 (
    echo Failed to install dependencies.
    goto :error
)

:run_project
echo Running {project_name}...
"%SCRIPT_DIR%\\.venv\\python.exe" "%SCRIPT_DIR%\\src\\main.py" %*
if !ERRORLEVEL! neq 0 (
    echo Application exited with error code !ERRORLEVEL!
    goto :error
)
goto :success

:setup_python
echo Setting up embedded Python environment...
set "PYTHON_VERSION=3.12.10"
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip"
set "VENV_DIR=%SCRIPT_DIR%\\.venv"

REM Create .venv directory
if not exist "%VENV_DIR%" mkdir "%VENV_DIR%"

REM Download Python if not exists
if not exist "%VENV_DIR%\\python-embed.zip" (
    echo Downloading Python %PYTHON_VERSION%...
    powershell -Command "& {{[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%VENV_DIR%\\python-embed.zip'}}"
    if !ERRORLEVEL! neq 0 (
        echo Failed to download Python. Please check your internet connection.
        exit /b 1
    )
)

REM Extract Python
if not exist "%VENV_DIR%\\python.exe" (
    echo Extracting embedded Python...
    powershell -Command "& {{Expand-Archive -Path '%VENV_DIR%\\python-embed.zip' -DestinationPath '%VENV_DIR%' -Force}}"
    if !ERRORLEVEL! neq 0 (
        echo Failed to extract Python.
        exit /b 1
    )
    del "%VENV_DIR%\\python-embed.zip"
)

REM Configure Python paths
echo Configuring Python environment...
for %%f in ("%VENV_DIR%\\*._pth") do (
    set "PTH_FILE=%%f"
    goto :found_pth
)
:found_pth

if exist "!PTH_FILE!" (
    REM Read existing content
    set "CONTENT="
    for /f "usebackq delims=" %%i in ("!PTH_FILE!") do (
        set "line=%%i"
        if "!line!"=="#import site" (
            set "CONTENT=!CONTENT!import site" & echo.
        ) else if "!line!"=="import site" (
            set "CONTENT=!CONTENT!!line!" & echo.
        ) else (
            set "CONTENT=!CONTENT!!line!" & echo.
        )
    )
    
    REM Write updated content
    echo import site> "!PTH_FILE!"
    echo Lib>> "!PTH_FILE!"
    echo Lib/site-packages>> "!PTH_FILE!"
    echo .>> "!PTH_FILE!"
    
    echo Python paths configured successfully.
) else (
    echo Warning: Could not find ._pth file to configure.
)

REM Install pip
if not exist "%VENV_DIR%\\Scripts\\pip.exe" (
    echo Installing pip...
    powershell -Command "& {{[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%VENV_DIR%\\get-pip.py'}}"
    "%VENV_DIR%\\python.exe" "%VENV_DIR%\\get-pip.py"
    if !ERRORLEVEL! neq 0 (
        echo Failed to install pip.
        exit /b 1
    )
    del "%VENV_DIR%\\get-pip.py"
)

REM Install UV package manager
echo Installing UV package manager...
"%VENV_DIR%\\python.exe" -m pip install --no-warn-script-location uv
if !ERRORLEVEL! neq 0 (
    echo Failed to install UV package manager.
    exit /b 1
)

REM Install ruff
echo Installing ruff...
"%VENV_DIR%\\python.exe" -m pip install --no-warn-script-location ruff
if !ERRORLEVEL! neq 0 (
    echo Failed to install ruff.
    exit /b 1
)

REM Install TOML support
echo Installing TOML support...
"%VENV_DIR%\\python.exe" -m pip install --no-warn-script-location "tomli>=1.2.0" "tomli-w>=1.0.0"
if !ERRORLEVEL! neq 0 (
    echo Warning: Failed to install TOML support.
)

echo Python environment setup complete!
exit /b 0

:install_dependencies
echo Installing project dependencies...

REM Check if pyproject.toml exists
if not exist "%SCRIPT_DIR%\\pyproject.toml" (
    echo No pyproject.toml found. Skipping dependency installation.
    exit /b 0
)

REM Parse and install main dependencies
echo Reading dependencies from pyproject.toml...
powershell -Command "& {{
    try {{
        $content = Get-Content '%SCRIPT_DIR%\\pyproject.toml' -Raw
        $inDeps = $false
        $deps = @()
        
        $content -split '\\n' | ForEach-Object {{
            $line = $_.Trim()
            if ($line -match '^dependencies\\s*=\\s*\\[') {{
                $inDeps = $true
                if ($line -match '\\]') {{
                    $inDeps = $false
                }}
            }} elseif ($inDeps) {{
                if ($line -match '\\]') {{
                    $inDeps = $false
                }} elseif ($line -match '^\"(.+)\"') {{
                    $deps += $matches[1]
                }}
            }}
        }}
        
        if ($deps.Count -gt 0) {{
            Write-Output 'Found dependencies:'
            $deps | ForEach-Object {{ Write-Output \"  $_\" }}
            
            # Install using UV
            $cmd = @('%VENV_DIR%\\python.exe', '-m', 'uv', 'pip', 'install') + $deps
            & $cmd[0] $cmd[1..($cmd.Length-1)]
            
            if ($LASTEXITCODE -eq 0) {{
                Write-Output 'Dependencies installed successfully!'
            }} else {{
                Write-Output 'Failed to install some dependencies.'
                exit 1
            }}
        }} else {{
            Write-Output 'No dependencies found in pyproject.toml'
        }}
    }} catch {{
        Write-Output 'Error parsing pyproject.toml: $_'
        Write-Output 'Continuing without installing dependencies...'
    }}
}}"

exit /b 0

:success
echo.
echo {project_name} completed successfully!
goto :end

:error
echo.
echo An error occurred. Check the output above for details.
echo Press any key to exit...
pause >nul
exit /b 1

:end
if !ERRORLEVEL! neq 0 (
    echo.
    echo Press any key to exit...
    pause >nul
)
endlocal
'''

    def create_readme(self, project_name):
        """Create README.md"""
        return f'''# {project_name}

A portable Python project created with pybox for Windows.

## Getting Started

This project uses pybox with UV package manager for fast dependency management and distribution of portable Python applications on Windows.

### Quick Start

1. **Double-click `run.bat`** or run `pybox setup && pybox run` in command prompt
2. The first run will automatically set up the embedded Python environment and install dependencies

### Commands

- `pybox setup` - Setup the embedded Python environment and install dependencies
- `pybox run` - Run the project  
- `pybox add <package>` - Add dependencies (updates pyproject.toml)
- `pybox remove <package>` - Remove dependencies (updates pyproject.toml)
- `pybox sync` - Sync dependencies from pyproject.toml
- `pybox test` - Run tests with pytest
- `pybox check` - Check code with ruff
- `pybox format` - Format code with ruff
- `pybox pack` - Package for distribution

### Project Structure

```
{project_name}/
├── pyproject.toml (dependencies managed here)
├── README.md
├── run.bat (Windows runner with auto-setup)
├── src/
│   └── main.py
├── tests/
└── .venv/ (embedded Python environment + dependencies)
```

## Dependencies

Dependencies are managed in `pyproject.toml` and automatically installed using UV package manager in the embedded Python environment located in the `.venv` directory.

## Distribution

Your project is fully portable - just zip the entire folder and share it. Recipients can run it by double-clicking `run.bat` which will auto-setup the environment if needed.

## License

MIT License
'''

    def create_gitignore(self):
        """Create .gitignore"""
        return '''# pybox
.venv/
dist/
*.pyc
__pycache__/
*.pyo
*.pyd
.Python
env/
venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.pytest_cache/
htmlcov/
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
uv.lock

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
'''

    def new_project(self, project_name, no_git=False):
        """Create a new pybox project"""
        self.print_header()
        
        if platform.system() != "Windows":
            print(f"{Colors.FAIL}❌ pybox is designed for Windows only!{Colors.ENDC}")
            return False
        
        if os.path.exists(project_name):
            print(f"{Colors.FAIL}❌ Project '{project_name}' already exists!{Colors.ENDC}")
            return False
            
        # Get Python version from user
        print(f"{Colors.OKCYAN}🐍 Select Python version:{Colors.ENDC}")
        print(f"{Colors.WARNING}Available versions:{Colors.ENDC}")
        for i, version in enumerate(self.python_versions.keys(), 1):
            marker = " (default)" if version == "3.12.10" else ""
            print(f"  {i}. {version}{marker}")
        
        print(f"\n{Colors.WARNING}Press Enter for default (3.12.10) or enter version number:{Colors.ENDC}")
        choice = input(f"{Colors.OKBLUE}> {Colors.ENDC}").strip()
        
        python_version = "3.12.10"  # default
        if choice:
            try:
                version_list = list(self.python_versions.keys())
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(version_list):
                        python_version = version_list[idx]
                elif choice in self.python_versions:
                    python_version = choice
            except (ValueError, IndexError):
                print(f"{Colors.WARNING}⚠️  Invalid choice, using default 3.12.10{Colors.ENDC}")

        print(f"{Colors.OKGREEN}✨ Creating project '{project_name}' with Python {python_version}...{Colors.ENDC}")
        
        # Create project structure
        os.makedirs(project_name)
        os.makedirs(f"{project_name}/src")
        os.makedirs(f"{project_name}/tests")
        
        # Create files
        files_to_create = [
            ("pyproject.toml", self.create_pyproject_toml(project_name, python_version)),
            ("src/main.py", self.create_main_py()),
            ("README.md", self.create_readme(project_name)),
            (".gitignore", self.create_gitignore()),
            ("run.bat", self.create_run_bat(project_name)),
            ("tests/__init__.py", ""),
            ("tests/test_main.py", f'''import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import main

def test_main():
    """Test main function runs without error"""
    main()  # Should not raise an exception
''')
        ]
        
        for filename, content in files_to_create:
            filepath = Path(project_name) / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"{Colors.OKGREEN}✅ Project '{project_name}' created successfully!{Colors.ENDC}")
        
        # Initialize git repository if git is available and not disabled
        if not no_git:
            try:
                # Check if git is available
                subprocess.run(["git", "--version"], check=True, capture_output=True)
                print(f"{Colors.OKCYAN}📁 Initializing git repository...{Colors.ENDC}")
                
                # Change to project directory and initialize git
                original_dir = os.getcwd()
                os.chdir(project_name)
                
                subprocess.run(["git", "init"], check=True, capture_output=True)
                subprocess.run(["git", "add", "."], check=True, capture_output=True)
                subprocess.run(["git", "commit", "-m", "Initial commit"], check=True, capture_output=True)
                
                os.chdir(original_dir)
                print(f"{Colors.OKGREEN}✅ Git repository initialized with initial commit!{Colors.ENDC}")
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"{Colors.WARNING}⚠️  Git not found or failed to initialize repository{Colors.ENDC}")
        
        print(f"{Colors.OKCYAN}📁 Navigate to your project: cd {project_name}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}🚀 Setup and run: pybox setup && pybox run (or double-click run.bat){Colors.ENDC}")
        return True

    def setup_embedded_python(self, python_version="3.12.10"):
        """Download and setup embedded Python for Windows"""
        if platform.system() != "Windows":
            print(f"{Colors.FAIL}❌ pybox requires Windows!{Colors.ENDC}")
            return None
            
        venv_dir = Path(".venv")
        python_exe = venv_dir / "python.exe"
        
        if python_exe.exists():
            print(f"{Colors.OKGREEN}✅ Using existing embedded Python{Colors.ENDC}")
            return str(python_exe)
            
        print(f"{Colors.OKCYAN}📦 Setting up embedded Python {python_version} for Windows...{Colors.ENDC}")
        
        if python_version not in self.python_versions:
            print(f"{Colors.FAIL}❌ Unsupported Python version: {python_version}{Colors.ENDC}")
            print(f"{Colors.WARNING}Available versions: {', '.join(self.python_versions.keys())}{Colors.ENDC}")
            return None
            
        url = self.python_versions[python_version]
        venv_dir.mkdir(exist_ok=True)
        
        # Download embedded Python
        zip_path = venv_dir / "python-embed.zip"
        print(f"{Colors.OKCYAN}⬇️ Downloading Python {python_version}...{Colors.ENDC}")
        
        try:
            urlretrieve(url, zip_path)
            print(f"{Colors.OKGREEN}✅ Download complete{Colors.ENDC}")
            
            # Extract
            print(f"{Colors.OKCYAN}📂 Extracting embedded Python...{Colors.ENDC}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(venv_dir)
            zip_path.unlink()
            
            # Setup pip and uv
            if self.setup_pip_and_uv_windows(venv_dir, python_version):
                print(f"{Colors.OKGREEN}✅ Embedded Python {python_version} with UV ready!{Colors.ENDC}")
                return str(python_exe)
            else:
                print(f"{Colors.FAIL}❌ Failed to setup pip and UV{Colors.ENDC}")
                return None
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to setup embedded Python: {e}{Colors.ENDC}")
            # Clean up on failure
            if venv_dir.exists():
                shutil.rmtree(venv_dir, ignore_errors=True)
            return None

    def setup_pip_and_uv_windows(self, venv_dir, python_version):
        """Setup pip and UV for embedded Python on Windows"""
        python_exe = venv_dir / "python.exe"
        
        try:
            # Create pth file to enable site-packages and fix encoding issues
            print(f"{Colors.OKCYAN}🔧 Configuring Python paths...{Colors.ENDC}")
            pth_files = list(venv_dir.glob("*._pth"))
            if pth_files:
                pth_file = pth_files[0]
                content = pth_file.read_text()
                
                # Check if site is already enabled and add required paths
                if "import site" not in content or "#import site" in content:
                    # Remove commented import site and add uncommented version
                    lines = content.split('\n')
                    new_lines = []
                    site_added = False
                    
                    for line in lines:
                        # Remove any commented import site lines
                        if line.strip().startswith('#import site'):
                            continue
                        # Skip existing uncommented import site to avoid duplicates
                        elif line.strip() == 'import site':
                            if not site_added:
                                new_lines.append('import site')
                                site_added = True
                        else:
                            new_lines.append(line)
                    
                    # Add import site if not already added
                    if not site_added:
                        new_lines.append('import site')
                    
                    # Add Lib path to fix encoding issues
                    if 'Lib' not in content:
                        new_lines.append('Lib')
                        new_lines.append('Lib/site-packages')
                    
                    # Write back the modified content
                    pth_file.write_text('\n'.join(new_lines))
                    print(f"{Colors.OKGREEN}✅ Enabled 'import site' and fixed paths in {pth_file.name}{Colors.ENDC}")
                else:
                    print(f"{Colors.OKGREEN}✅ Site module already enabled{Colors.ENDC}")
            
            # Verify site module is working
            result = subprocess.run([str(python_exe), "-c", "import site; print('Site module working')"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{Colors.FAIL}❌ Site module not working: {result.stderr}{Colors.ENDC}")
                return False
            
            # Install pip
            print(f"{Colors.OKCYAN}📦 Installing pip...{Colors.ENDC}")
            get_pip_path = venv_dir / "get-pip.py"
            if not get_pip_path.exists():
                urlretrieve("https://bootstrap.pypa.io/get-pip.py", get_pip_path)
            
            result = subprocess.run([str(python_exe), str(get_pip_path)], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"{Colors.FAIL}❌ Pip installation failed: {result.stderr}{Colors.ENDC}")
                return False
            print(f"{Colors.OKGREEN}✅ Pip installed successfully{Colors.ENDC}")
            
            # Install UV package manager
            print(f"{Colors.OKCYAN}📦 Installing UV package manager...{Colors.ENDC}")
            result = subprocess.run([str(python_exe), "-m", "pip", "install", "--no-warn-script-location", "uv"], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"{Colors.FAIL}❌ UV installation failed: {result.stderr}{Colors.ENDC}")
                return False
            print(f"{Colors.OKGREEN}✅ UV package manager installed successfully{Colors.ENDC}")
            
            # Install ruff using pip (as it's a dev tool)
            print(f"{Colors.OKCYAN}📦 Installing ruff...{Colors.ENDC}")
            result = subprocess.run([str(python_exe), "-m", "pip", "install", "--no-warn-script-location", "ruff"], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"{Colors.FAIL}❌ Ruff installation failed: {result.stderr}{Colors.ENDC}")
                return False
            print(f"{Colors.OKGREEN}✅ Ruff installed successfully{Colors.ENDC}")
            
            # Install TOML dependencies for pyproject.toml management
            print(f"{Colors.OKCYAN}📦 Installing TOML support...{Colors.ENDC}")
            toml_packages = ["tomli>=1.2.0", "tomli-w>=1.0.0"]
            result = subprocess.run([str(python_exe), "-m", "pip", "install", "--no-warn-script-location"] + toml_packages, 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"{Colors.WARNING}⚠️  TOML support installation failed: {result.stderr}{Colors.ENDC}")
                # Continue anyway as this is not critical for basic functionality
            
            # Verify UV is working
            result = subprocess.run([str(python_exe), "-m", "uv", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{Colors.FAIL}❌ UV verification failed: {result.stderr}{Colors.ENDC}")
                return False
            
            print(f"{Colors.OKGREEN}✅ UV is working: {result.stdout.strip()}{Colors.ENDC}")
            return True
                
        except subprocess.TimeoutExpired:
            print(f"{Colors.FAIL}❌ Installation timed out{Colors.ENDC}")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ Setup failed: {e}{Colors.ENDC}")
            return False

    def get_python_version(self):
        """Get Python version from pyproject.toml"""
        if not Path("pyproject.toml").exists():
            return "3.12.10"
        
        try:
            import tomllib
        except ImportError:
            # For Python < 3.11
            try:
                import tomli as tomllib
            except ImportError:
                return "3.12.10"
        
        try:
            with open("pyproject.toml", "rb") as f:
                data = tomllib.load(f)
            return data.get("tool", {}).get("pybox", {}).get("python_version", "3.12.10")
        except:
            return "3.12.10"

    def get_python_exe(self):
        """Get the Python executable path"""
        venv_dir = Path(".venv")
        python_exe = venv_dir / "python.exe"
        
        if python_exe.exists():
            return str(python_exe)
        return None

    def setup_project(self):
        """Setup the project environment and install dependencies"""
        if not Path("pyproject.toml").exists():
            print(f"{Colors.FAIL}❌ No pyproject.toml found. Are you in a pybox project directory?{Colors.ENDC}")
            return False
        
        python_version = self.get_python_version()
        python_exe = self.setup_embedded_python(python_version)
        
        if not python_exe:
            print(f"{Colors.FAIL}❌ Failed to setup Python environment{Colors.ENDC}")
            return False
        
        # Install project dependencies using UV
        return self.sync_dependencies()

    def run_project(self):
        """Run the project"""
        if not Path("src/main.py").exists():
            print(f"{Colors.FAIL}❌ No src/main.py found. Are you in a pybox project directory?{Colors.ENDC}")
            return False
        
        python_exe = self.get_python_exe()
        if not python_exe:
            print(f"{Colors.WARNING}⚠️  No Python environment found. Setting up automatically...{Colors.ENDC}")
            if not self.setup_project():
                return False
            python_exe = self.get_python_exe()
        
        print(f"{Colors.OKGREEN}🚀 Running project...{Colors.ENDC}")
        
        # Add src to Python path and run
        env = os.environ.copy()
        current_pythonpath = env.get("PYTHONPATH", "")
        src_path = str(Path("src").absolute())
        env["PYTHONPATH"] = f"{src_path};{current_pythonpath}" if current_pythonpath else src_path
        
        try:
            result = subprocess.run([python_exe, "src/main.py"], env=env)
            return result.returncode == 0
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to run project: {e}{Colors.ENDC}")
            return False

    def ensure_toml_dependencies(self):
        """Ensure TOML parsing dependencies are available"""
        python_exe = self.get_python_exe()
        if not python_exe:
            return False
        
        # Check if we can import tomllib (Python 3.11+) or tomli
        try:
            subprocess.run([python_exe, "-c", "import tomllib"], check=True, capture_output=True)
            has_tomllib = True
        except subprocess.CalledProcessError:
            has_tomllib = False
        
        if not has_tomllib:
            try:
                subprocess.run([python_exe, "-c", "import tomli"], check=True, capture_output=True)
                has_tomli = True
            except subprocess.CalledProcessError:
                has_tomli = False
                
                print(f"{Colors.OKCYAN}📦 Installing tomli for TOML support...{Colors.ENDC}")
                try:
                    subprocess.run([python_exe, "-m", "uv", "pip", "install", "tomli>=1.2.0"], check=True, timeout=60)
                    print(f"{Colors.OKGREEN}✅ tomli installed successfully{Colors.ENDC}")
                except subprocess.CalledProcessError:
                    print(f"{Colors.FAIL}❌ Failed to install tomli{Colors.ENDC}")
                    return False
        
        # Check for tomli-w
        try:
            subprocess.run([python_exe, "-c", "import tomli_w"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"{Colors.OKCYAN}📦 Installing tomli-w for TOML writing...{Colors.ENDC}")
            try:
                subprocess.run([python_exe, "-m", "uv", "pip", "install", "tomli-w>=1.0.0"], check=True, timeout=60)
                print(f"{Colors.OKGREEN}✅ tomli-w installed successfully{Colors.ENDC}")
            except subprocess.CalledProcessError:
                print(f"{Colors.FAIL}❌ Failed to install tomli-w{Colors.ENDC}")
                return False
        
        return True

    def update_pyproject_dependencies(self, packages, operation="add"):
        """Update pyproject.toml dependencies"""
        if not self.ensure_toml_dependencies():
            print(f"{Colors.FAIL}❌ Cannot update pyproject.toml - missing TOML dependencies{Colors.ENDC}")
            return False
        
        try:
            # Import the TOML libraries
            try:
                import tomllib
            except ImportError:
                import tomli as tomllib
            import tomli_w
        except ImportError:
            print(f"{Colors.FAIL}❌ TOML libraries not available after installation{Colors.ENDC}")
            return False
        
        try:
            with open("pyproject.toml", "rb") as f:
                data = tomllib.load(f)
            
            # Ensure dependencies list exists
            if "project" not in data:
                data["project"] = {}
            if "dependencies" not in data["project"]:
                data["project"]["dependencies"] = []
            
            dependencies = data["project"]["dependencies"]
            
            for package in packages:
                package_name = package.split('==')[0].split('>=')[0].split('<=')[0].split('!=')[0].split('~=')[0].split('[')[0]
                
                if operation == "add":
                    # Remove existing version of package
                    dependencies = [dep for dep in dependencies if not dep.startswith(package_name)]
                    dependencies.append(package)
                    print(f"{Colors.OKGREEN}➕ Added {package} to pyproject.toml{Colors.ENDC}")
                elif operation == "remove":
                    original_length = len(dependencies)
                    dependencies = [dep for dep in dependencies if not dep.startswith(package_name)]
                    if len(dependencies) < original_length:
                        print(f"{Colors.OKGREEN}➖ Removed {package_name} from pyproject.toml{Colors.ENDC}")
                    else:
                        print(f"{Colors.WARNING}⚠️  {package_name} not found in pyproject.toml{Colors.ENDC}")
            
            data["project"]["dependencies"] = sorted(dependencies)
            
            with open("pyproject.toml", "wb") as f:
                tomli_w.dump(data, f)
            
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to update pyproject.toml: {e}{Colors.ENDC}")
            return False

    def add_packages(self, packages):
        """Add packages using UV and update pyproject.toml"""
        if not Path("pyproject.toml").exists():
            print(f"{Colors.FAIL}❌ No pyproject.toml found. Are you in a pybox project directory?{Colors.ENDC}")
            return False
        
        python_exe = self.get_python_exe()
        if not python_exe:
            print(f"{Colors.WARNING}⚠️  No Python environment found. Setting up automatically...{Colors.ENDC}")
            if not self.setup_project():
                return False
            python_exe = self.get_python_exe()
        
        print(f"{Colors.OKCYAN}📦 Adding packages: {' '.join(packages)}{Colors.ENDC}")
        
        try:
            # Install using UV
            cmd = [python_exe, "-m", "uv", "pip", "install"] + packages
            result = subprocess.run(cmd, check=True, timeout=300, capture_output=True, text=True)
            print(f"{Colors.OKGREEN}✅ Packages installed successfully with UV!{Colors.ENDC}")
            
            # Update pyproject.toml
            if self.update_pyproject_dependencies(packages, "add"):
                print(f"{Colors.OKGREEN}✅ Updated pyproject.toml{Colors.ENDC}")
            
            # Test if packages can be imported
            for package in packages:
                # Handle common package name variations
                import_name = package.split('==')[0].split('>=')[0].split('<=')[0].split('!=')[0].split('~=')[0].split('[')[0]
                test_result = subprocess.run([python_exe, "-c", f"import {import_name}; print('{import_name} imported successfully')"], 
                                           capture_output=True, text=True)
                if test_result.returncode == 0:
                    print(f"{Colors.OKGREEN}✅ {import_name} is ready to use{Colors.ENDC}")
                else:
                    print(f"{Colors.WARNING}⚠️  {import_name} installed but import test failed{Colors.ENDC}")
            
            return True
        except subprocess.TimeoutExpired:
            print(f"{Colors.FAIL}❌ Package installation timed out{Colors.ENDC}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}❌ Failed to install packages: {e}{Colors.ENDC}")
            if e.stderr:
                print(f"{Colors.FAIL}Error: {e.stderr}{Colors.ENDC}")
            return False

    def remove_packages(self, packages):
        """Remove packages using UV and update pyproject.toml"""
        if not Path("pyproject.toml").exists():
            print(f"{Colors.FAIL}❌ No pyproject.toml found. Are you in a pybox project directory?{Colors.ENDC}")
            return False
        
        python_exe = self.get_python_exe()
        if not python_exe:
            print(f"{Colors.FAIL}❌ No embedded Python found. Run 'pybox setup' first.{Colors.ENDC}")
            return False
        
        print(f"{Colors.OKCYAN}🗑️ Removing packages: {' '.join(packages)}{Colors.ENDC}")
        
        try:
            # Remove using UV
            cmd = [python_exe, "-m", "uv", "pip", "uninstall", "-y"] + packages
            result = subprocess.run(cmd, check=True, timeout=120)
            print(f"{Colors.OKGREEN}✅ Packages removed successfully with UV!{Colors.ENDC}")
            
            # Update pyproject.toml
            if self.update_pyproject_dependencies(packages, "remove"):
                print(f"{Colors.OKGREEN}✅ Updated pyproject.toml{Colors.ENDC}")
            
            return True
        except subprocess.TimeoutExpired:
            print(f"{Colors.FAIL}❌ Package removal timed out{Colors.ENDC}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}❌ Failed to remove packages: {e}{Colors.ENDC}")
            return False

    def sync_dependencies(self):
        """Sync dependencies from pyproject.toml using UV"""
        if not Path("pyproject.toml").exists():
            print(f"{Colors.FAIL}❌ No pyproject.toml found. Are you in a pybox project directory?{Colors.ENDC}")
            return False
        
        python_exe = self.get_python_exe()
        if not python_exe:
            print(f"{Colors.FAIL}❌ No embedded Python found. Run 'pybox setup' first.{Colors.ENDC}")
            return False
        
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                print(f"{Colors.WARNING}⚠️  Cannot read pyproject.toml - missing tomllib/tomli{Colors.ENDC}")
                return True  # Skip dependency sync but don't fail
        
        try:
            with open("pyproject.toml", "rb") as f:
                data = tomllib.load(f)
            
            dependencies = data.get("project", {}).get("dependencies", [])
            dev_dependencies = data.get("tool", {}).get("uv", {}).get("dev-dependencies", [])
            
            if not dependencies and not dev_dependencies:
                print(f"{Colors.OKGREEN}✅ No dependencies to sync{Colors.ENDC}")
                return True
            
            print(f"{Colors.OKCYAN}🔄 Syncing dependencies with UV...{Colors.ENDC}")
            
            # Install main dependencies
            if dependencies:
                print(f"{Colors.OKCYAN}📦 Installing project dependencies...{Colors.ENDC}")
                cmd = [python_exe, "-m", "uv", "pip", "install"] + dependencies
                result = subprocess.run(cmd, check=True, timeout=300, capture_output=True, text=True)
                print(f"{Colors.OKGREEN}✅ Project dependencies installed{Colors.ENDC}")
            
            # Install dev dependencies
            if dev_dependencies:
                print(f"{Colors.OKCYAN}🛠️ Installing dev dependencies...{Colors.ENDC}")
                cmd = [python_exe, "-m", "uv", "pip", "install"] + dev_dependencies
                result = subprocess.run(cmd, check=True, timeout=300, capture_output=True, text=True)
                print(f"{Colors.OKGREEN}✅ Dev dependencies installed{Colors.ENDC}")
            
            return True
            
        except subprocess.TimeoutExpired:
            print(f"{Colors.FAIL}❌ Dependency sync timed out{Colors.ENDC}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}❌ Failed to sync dependencies: {e}{Colors.ENDC}")
            if e.stderr:
                print(f"{Colors.FAIL}Error: {e.stderr}{Colors.ENDC}")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to read dependencies: {e}{Colors.ENDC}")
            return False

    def run_tests(self):
        """Run tests using pytest"""
        python_exe = self.get_python_exe()
        if not python_exe:
            print(f"{Colors.FAIL}❌ No embedded Python found. Run 'pybox setup' first.{Colors.ENDC}")
            return False
        
        # Check if pytest is available (should be installed as dev dependency)
        try:
            subprocess.run([python_exe, "-c", "import pytest"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"{Colors.OKCYAN}📦 Installing pytest...{Colors.ENDC}")
            try:
                subprocess.run([python_exe, "-m", "uv", "pip", "install", "pytest"], check=True)
            except subprocess.CalledProcessError:
                print(f"{Colors.FAIL}❌ Failed to install pytest{Colors.ENDC}")
                return False
        
        print(f"{Colors.OKCYAN}🧪 Running tests...{Colors.ENDC}")
        
        env = os.environ.copy()
        current_pythonpath = env.get("PYTHONPATH", "")
        src_path = str(Path("src").absolute())
        env["PYTHONPATH"] = f"{src_path};{current_pythonpath}" if current_pythonpath else src_path
        
        try:
            result = subprocess.run([python_exe, "-m", "pytest", "tests/"], env=env)
            return result.returncode == 0
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to run tests: {e}{Colors.ENDC}")
            return False

    def check_code(self):
        """Check code using ruff"""
        python_exe = self.get_python_exe()
        if not python_exe:
            print(f"{Colors.FAIL}❌ No embedded Python found. Run 'pybox setup' first.{Colors.ENDC}")
            return False
        
        # Ruff should already be installed during setup
        print(f"{Colors.OKCYAN}🔍 Checking code with ruff...{Colors.ENDC}")
        
        try:
            result = subprocess.run([python_exe, "-m", "ruff", "check", "src/"])
            return result.returncode == 0
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to check code: {e}{Colors.ENDC}")
            return False

    def format_code(self):
        """Format code using ruff"""
        python_exe = self.get_python_exe()
        if not python_exe:
            print(f"{Colors.FAIL}❌ No embedded Python found. Run 'pybox setup' first.{Colors.ENDC}")
            return False
        
        # Ruff should already be installed during setup
        print(f"{Colors.OKCYAN}✨ Formatting code with ruff...{Colors.ENDC}")
        
        try:
            result = subprocess.run([python_exe, "-m", "ruff", "format", "src/"])
            print(f"{Colors.OKGREEN}✅ Code formatted successfully!{Colors.ENDC}")
            return result.returncode == 0
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to format code: {e}{Colors.ENDC}")
            return False

    def pack_project(self):
        """Pack project into a distributable zip"""
        if not Path("pyproject.toml").exists():
            print(f"{Colors.FAIL}❌ No pyproject.toml found. Are you in a pybox project directory?{Colors.ENDC}")
            return False
        
        # Get project name
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                print(f"{Colors.FAIL}❌ Cannot read pyproject.toml{Colors.ENDC}")
                return False
        
        try:
            with open("pyproject.toml", "rb") as f:
                data = tomllib.load(f)
            project_name = data["project"]["name"]
            version = data["project"]["version"]
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to read project info: {e}{Colors.ENDC}")
            return False
        
        # Create dist directory
        dist_dir = Path("dist")
        dist_dir.mkdir(exist_ok=True)
        
        zip_name = dist_dir / f"{project_name}-{version}.zip"
        print(f"{Colors.OKCYAN}📦 Packing project into {zip_name}...{Colors.ENDC}")
        
        try:
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files except ignored files
                ignore_patterns = ['.git', '__pycache__', '*.pyc', '*.zip', 'dist', 'uv.lock']
                
                for root, dirs, files in os.walk('.'):
                    # Skip ignored directories
                    dirs[:] = [d for d in dirs if not any(d.startswith(pattern.rstrip('*')) for pattern in ignore_patterns)]
                    
                    for file in files:
                        # Skip ignored files
                        if any(file.endswith(pattern.lstrip('*')) for pattern in ignore_patterns):
                            continue
                        
                        file_path = Path(root) / file
                        arcname = str(file_path.relative_to('.'))
                        zipf.write(file_path, arcname)
            
            print(f"{Colors.OKGREEN}✅ Project packed successfully as {zip_name}!{Colors.ENDC}")
            print(f"{Colors.OKCYAN}📋 Recipients can run by extracting and double-clicking run.bat{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to pack project: {e}{Colors.ENDC}")
            return False


def main():
    if platform.system() != "Windows":
        print(f"{Colors.FAIL}❌ pybox is designed for Windows only!{Colors.ENDC}")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="pybox - Portable Python Project Manager for Windows")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # New project command
    new_parser = subparsers.add_parser('new', help='Create a new pybox project')
    new_parser.add_argument('name', help='Project name')
    new_parser.add_argument('--no-git', action='store_true', help='Skip git repository initialization')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup the project environment and install dependencies')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the project')
    
    # Add packages command
    add_parser = subparsers.add_parser('add', help='Add packages (updates pyproject.toml)')
    add_parser.add_argument('packages', nargs='+', help='Package names to install')
    
    # Remove packages command
    remove_parser = subparsers.add_parser('remove', help='Remove packages (updates pyproject.toml)')
    remove_parser.add_argument('packages', nargs='+', help='Package names to remove')
    
    # Sync dependencies command
    sync_parser = subparsers.add_parser('sync', help='Sync dependencies from pyproject.toml')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests with pytest')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check code with ruff')
    
    # Format command
    format_parser = subparsers.add_parser('format', help='Format code with ruff')
    
    # Pack command
    pack_parser = subparsers.add_parser('pack', help='Package project for distribution')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    pybox = pybox()
    
    if args.command == 'new':
        pybox.new_project(args.name, args.no_git)
    elif args.command == 'setup':
        pybox.setup_project()
    elif args.command == 'run':
        pybox.run_project()
    elif args.command == 'add':
        pybox.add_packages(args.packages)
    elif args.command == 'remove':
        pybox.remove_packages(args.packages)
    elif args.command == 'sync':
        pybox.sync_dependencies()
    elif args.command == 'test':
        pybox.run_tests()
    elif args.command == 'check':
        pybox.check_code()
    elif args.command == 'format':
        pybox.format_code()
    elif args.command == 'pack':
        pybox.pack_project()


if __name__ == "__main__":
    main()