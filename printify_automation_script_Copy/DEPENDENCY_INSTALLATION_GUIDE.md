# 🔧 Dependency Installation Guide - Printify Automation Tool

**Version**: 2.0  
**Last Updated**: June 18, 2025  

## 📋 Overview

This guide provides comprehensive instructions for installing all required dependencies for the Enhanced Printify Automation Tool across different environments and systems.

---

## 🎯 Quick Installation (Recommended)

### Method 1: Standard pip Installation
```bash
# Install all dependencies at once
pip install gradio>=4.0.0 pillow>=9.0.0 pandas>=1.5.0 psutil>=5.9.0 pydantic>=1.10.0 watchdog>=3.0.0 requests>=2.28.0 pyyaml>=6.0

# Or install from requirements.txt
pip install -r requirements.txt
```

### Method 2: User Installation (If pip restrictions exist)
```bash
# Install to user directory
pip install --user gradio pillow pandas psutil pydantic watchdog requests pyyaml

# With system override if needed
pip install --user --break-system-packages gradio pillow pandas psutil pydantic watchdog requests pyyaml
```

---

## 🐧 Linux System Installation

### Ubuntu/Debian Systems
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-full

# Install dependencies via apt (system packages)
sudo apt install python3-gradio python3-pil python3-pandas python3-psutil python3-pydantic python3-watchdog python3-requests python3-yaml

# Or via pip
pip3 install gradio pillow pandas psutil pydantic watchdog requests pyyaml
```

### CentOS/RHEL/Fedora Systems
```bash
# Install Python and pip
sudo yum install python3 python3-pip  # CentOS/RHEL
sudo dnf install python3 python3-pip  # Fedora

# Install dependencies
pip3 install gradio pillow pandas psutil pydantic watchdog requests pyyaml
```

### Arch Linux
```bash
# Install via pacman (system packages)
sudo pacman -S python python-pip python-pillow python-pandas python-psutil python-pydantic python-watchdog python-requests python-yaml

# Install gradio via pip (not in official repos)
pip install gradio
```

---

## 🍎 macOS Installation

### Using Homebrew (Recommended)
```bash
# Install Python if not already installed
brew install python

# Install dependencies
pip3 install gradio pillow pandas psutil pydantic watchdog requests pyyaml
```

### Using MacPorts
```bash
# Install Python
sudo port install python39 +universal

# Install dependencies
pip3 install gradio pillow pandas psutil pydantic watchdog requests pyyaml
```

---

## 🖥️ Windows Installation

### Using Windows Package Manager (winget)
```powershell
# Install Python
winget install Python.Python.3

# Restart terminal, then install dependencies
pip install gradio pillow pandas psutil pydantic watchdog requests pyyaml
```

### Using Chocolatey
```powershell
# Install Python
choco install python

# Install dependencies
pip install gradio pillow pandas psutil pydantic watchdog requests pyyaml
```

### Manual Installation
1. Download Python from https://python.org/downloads/
2. Install with "Add to PATH" option checked
3. Open Command Prompt and run:
   ```cmd
   pip install gradio pillow pandas psutil pydantic watchdog requests pyyaml
   ```

---

## 🐳 Docker Installation

### Option 1: Use Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t printify-automation .
docker run -p 7860:7860 printify-automation
```

### Option 2: Use docker-compose
```yaml
version: '3.8'
services:
  printify-automation:
    build: .
    ports:
      - "7860:7860"
    volumes:
      - ./config.json:/app/config.json
      - ./uploads:/app/uploads
```

Run:
```bash
docker-compose up
```

---

## 🔧 Virtual Environment Setup

### Using venv (Recommended)
```bash
# Create virtual environment
python3 -m venv printify_env

# Activate virtual environment
source printify_env/bin/activate  # Linux/macOS
# OR
printify_env\Scripts\activate     # Windows

# Install dependencies
pip install gradio pillow pandas psutil pydantic watchdog requests pyyaml

# Deactivate when done
deactivate
```

### Using conda
```bash
# Create conda environment
conda create -n printify python=3.11

# Activate environment
conda activate printify

# Install dependencies
conda install pillow pandas psutil pyyaml requests
pip install gradio pydantic watchdog

# Deactivate when done
conda deactivate
```

### Using pipenv
```bash
# Install pipenv if not installed
pip install pipenv

# Install dependencies from Pipfile
pipenv install

# Activate shell
pipenv shell

# Run application
python app.py
```

---

## 🚨 Troubleshooting Common Issues

### Issue: "pip: command not found"
**Solution:**
```bash
# Linux/macOS
sudo apt install python3-pip  # Ubuntu/Debian
brew install python           # macOS

# Windows
# Download get-pip.py from https://bootstrap.pypa.io/get-pip.py
python get-pip.py
```

### Issue: "Permission denied" during installation
**Solutions:**
```bash
# Option 1: User installation
pip install --user package_name

# Option 2: Virtual environment
python -m venv myenv
source myenv/bin/activate
pip install package_name

# Option 3: System override (use carefully)
pip install --break-system-packages package_name
```

### Issue: "externally-managed-environment"
**Solution:**
```bash
# Use virtual environment (recommended)
python3 -m venv printify_env
source printify_env/bin/activate
pip install -r requirements.txt

# Or use --break-system-packages flag
pip install --break-system-packages -r requirements.txt
```

### Issue: Package installation fails
**Solutions:**
```bash
# Update pip first
pip install --upgrade pip

# Try with different index
pip install -i https://pypi.org/simple/ package_name

# Install specific versions
pip install package_name==version_number

# Clear cache and retry
pip cache purge
pip install package_name
```

### Issue: "No module named 'gradio'" after installation
**Solutions:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Check if package is installed in correct location
pip show gradio

# Reinstall with --force-reinstall
pip install --force-reinstall gradio

# Use python -m pip instead of pip
python -m pip install gradio
```

---

## ✅ Verification & Testing

### Check Installation Success
```bash
# Test all imports
python3 -c "
import gradio as gr
import PIL
import pandas as pd
import psutil
import pydantic
import watchdog
import requests
import yaml
print('✅ All dependencies successfully installed!')
print(f'Gradio: {gr.__version__}')
print(f'PIL: {PIL.__version__}')
print(f'Pandas: {pd.__version__}')
print(f'psutil: {psutil.__version__}')
print(f'pydantic: {pydantic.__version__}')
"
```

### Test Application Startup
```bash
# Start the application
python3 app.py

# Should see output like:
# Running on local URL:  http://127.0.0.1:7860
# To create a public link, set `share=True` in `launch()`.
```

### Run Test Suite
```bash
# Test core functionality
python3 tests/test_config_manager.py
python3 tests/test_tag_generator.py
python3 tests/test_pricing_monitor.py

# Run full test suite
python3 tests/run_tests.py
```

---

## 📦 Dependency Details

### Core Dependencies
| Package | Purpose | Minimum Version | Installation Priority |
|---------|---------|-----------------|---------------------|
| **gradio** | Web interface framework | >=4.0.0 | 🔴 Critical |
| **pillow** | Image processing | >=9.0.0 | 🔴 Critical |
| **requests** | HTTP API client | >=2.28.0 | 🔴 Critical |
| **pyyaml** | Configuration files | >=6.0 | 🟡 Important |

### Analytics Dependencies
| Package | Purpose | Minimum Version | Installation Priority |
|---------|---------|-----------------|---------------------|
| **pandas** | Data analysis | >=1.5.0 | 🟡 Important |
| **psutil** | Performance monitoring | >=5.9.0 | 🟢 Optional |

### Development Dependencies
| Package | Purpose | Minimum Version | Installation Priority |
|---------|---------|-----------------|---------------------|
| **pydantic** | Data validation | >=1.10.0 | 🟡 Important |
| **watchdog** | File monitoring | >=3.0.0 | 🟢 Optional |

### Testing Dependencies (Optional)
| Package | Purpose | Minimum Version | Installation Priority |
|---------|---------|-----------------|---------------------|
| **pytest** | Testing framework | >=7.0.0 | 🟢 Optional |
| **black** | Code formatting | >=22.0.0 | 🟢 Optional |
| **flake8** | Code linting | >=5.0.0 | 🟢 Optional |

---

## 🔄 Alternative Installation Methods

### Using Poetry
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate shell
poetry shell

# Run application
python app.py
```

### Using Anaconda
```bash
# Create environment from environment.yml
conda env create -f environment.yml

# Activate environment
conda activate printify

# Run application
python app.py
```

### Using System Package Managers

#### Debian/Ubuntu APT
```bash
sudo apt install python3-gradio python3-pil python3-pandas python3-psutil
```

#### Fedora DNF
```bash
sudo dnf install python3-pillow python3-pandas python3-psutil
```

#### openSUSE Zypper
```bash
sudo zypper install python3-Pillow python3-pandas python3-psutil
```

---

## 📊 Minimal vs Full Installation

### Minimal Installation (Core Functionality Only)
```bash
# Basic functionality - ~50MB
pip install requests pyyaml

# Enables: Configuration, API client, basic testing
```

### Standard Installation (Recommended)
```bash
# Full web interface - ~200MB
pip install gradio pillow requests pyyaml pydantic

# Enables: Web interface, image processing, data validation
```

### Complete Installation (All Features)
```bash
# Everything including analytics - ~500MB
pip install gradio pillow pandas psutil pydantic watchdog requests pyyaml

# Enables: All features, analytics, monitoring, development tools
```

---

## 🎯 Installation Success Checklist

- [ ] Python 3.8+ installed and accessible
- [ ] pip or alternative package manager available
- [ ] Core dependencies installed (gradio, pillow, requests, pyyaml)
- [ ] Application starts without errors (`python3 app.py`)
- [ ] Web interface accessible at `http://localhost:7860`
- [ ] Configuration tab loads properly
- [ ] Image upload functionality works
- [ ] Test suite passes (`python3 tests/run_tests.py`)

---

## 🆘 Getting Help

If you encounter issues:

1. **Check Python Version**: `python3 --version` (must be 3.8+)
2. **Verify pip**: `pip --version` or `python3 -m pip --version`
3. **Test Basic Import**: `python3 -c "import sys; print(sys.version)"`
4. **Run Diagnostic**: `python3 tests/test_config_manager.py`
5. **Check Logs**: Look for error messages in terminal output

**Common Solutions:**
- Use virtual environments to avoid conflicts
- Update pip: `pip install --upgrade pip`
- Clear pip cache: `pip cache purge`
- Use user installation: `pip install --user package_name`

---

*This guide covers installation for the Enhanced Printify Automation Tool v2.0. For usage instructions, see USER_WORKFLOW_GUIDE.md.*