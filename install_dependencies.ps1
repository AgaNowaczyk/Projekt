# install_dependencies.ps
# PowerShell script to install required Python packages for this project

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed. Please install Python before running this script."
    exit 1
}

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "Installing required Python packages..."
python -m pip install pytest playwright pytest-playwright pytest-xdist pytest-playwright-visual

Write-Host "All Python dependencies installed successfully."
