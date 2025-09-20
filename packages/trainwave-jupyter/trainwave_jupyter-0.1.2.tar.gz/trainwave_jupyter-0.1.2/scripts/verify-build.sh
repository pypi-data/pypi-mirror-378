#!/bin/bash

# Verify Build Script for Trainwave Jupyter Extension
# This script verifies that the build process works correctly

set -e

echo "🔍 Verifying Trainwave Jupyter Extension Build..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check package names
echo "📦 Checking package names..."

PYTHON_NAME=$(grep '^name = ' pyproject.toml | cut -d'"' -f2)
NPM_NAME=$(grep '"name":' package.json | head -1 | cut -d'"' -f4)

if [ "$PYTHON_NAME" != "trainwave-jupyter" ]; then
    echo "❌ Error: Python package name should be 'trainwave-jupyter', found: $PYTHON_NAME"
    exit 1
fi

if [ "$NPM_NAME" != "trainwave-jupyter" ]; then
    echo "❌ Error: NPM package name should be 'trainwave-jupyter', found: $NPM_NAME"
    exit 1
fi

echo "✅ Package names are correct"

# Check Python package structure
echo "🐍 Checking Python package structure..."

if [ ! -d "trainwave_jupyter" ]; then
    echo "❌ Error: Python package directory 'trainwave_jupyter' not found"
    exit 1
fi

if [ ! -f "trainwave_jupyter/__init__.py" ]; then
    echo "❌ Error: Python package __init__.py not found"
    exit 1
fi

echo "✅ Python package structure is correct"

# Build the extension
echo "🔨 Building the extension..."

# Clean previous builds
rm -rf dist/ trainwave_jupyter/labextension/

# Build NPM package
echo "📦 Building NPM package..."
npm run build:prod

if [ ! -d "trainwave_jupyter/labextension" ]; then
    echo "❌ Error: Labextension directory not created"
    exit 1
fi

echo "✅ NPM build successful"

# Build Python package
echo "🐍 Building Python package..."
uv build

if [ ! -f "dist/trainwave_jupyter-0.1.0-py3-none-any.whl" ]; then
    echo "❌ Error: Python wheel not created"
    exit 1
fi

if [ ! -f "dist/trainwave_jupyter-0.1.0.tar.gz" ]; then
    echo "❌ Error: Python source distribution not created"
    exit 1
fi

echo "✅ Python build successful"

# Test Python import
echo "🧪 Testing Python import..."
python3 -c "import trainwave_jupyter; print('✅ Python import successful')"

# Check extension paths
echo "🔗 Checking extension paths..."
python -c "
import trainwave_jupyter
paths = trainwave_jupyter._jupyter_labextension_paths()
if len(paths) == 1 and paths[0]['dest'] == 'trainwave-jupyter':
    print('✅ Extension paths are correct')
else:
    print('❌ Extension paths are incorrect:', paths)
    exit(1)
"

# Check server extension points
echo "🖥️  Checking server extension points..."
python -c "
import trainwave_jupyter
points = trainwave_jupyter._jupyter_server_extension_points()
if len(points) == 1 and points[0]['module'] == 'trainwave_jupyter':
    print('✅ Server extension points are correct')
else:
    print('❌ Server extension points are incorrect:', points)
    exit(1)
"

echo ""
echo "🎉 All checks passed! The package is ready for publishing."
echo ""
echo "📋 Summary:"
echo "  - Python package: $PYTHON_NAME"
echo "  - NPM package: $NPM_NAME"
echo "  - Python import: trainwave_jupyter"
echo "  - Extension ID: trainwave-jupyter:plugin"
echo ""
echo "📦 Built artifacts:"
ls -la dist/
echo ""
echo "🚀 Ready to publish to PyPI and NPM!"
