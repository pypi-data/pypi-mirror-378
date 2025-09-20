# Publishing Guide for Trainwave Jupyter Extension

This guide explains how to publish the `trainwave-jupyter` package to both PyPI and NPM.

## Package Names

- **PyPI Package**: `trainwave-jupyter`
- **NPM Package**: `trainwave-jupyter`
- **Python Import**: `trainwave_jupyter`
- **Jupyter Extension ID**: `trainwave-jupyter:plugin`

## Prerequisites

### 1. PyPI Account and Token

1. Create an account on [PyPI](https://pypi.org) if you don't have one
2. Generate an API token:
   - Go to your PyPI account settings
   - Navigate to "API tokens"
   - Create a new token with scope "Entire account" or "Specific project: trainwave-jupyter"
3. Add the token to your GitLab CI/CD variables as `PYPI_TOKEN`

### 2. NPM Account and Token

1. Create an account on [NPM](https://www.npmjs.com) if you don't have one
2. Generate an access token:
   - Go to your NPM account settings
   - Navigate to "Access Tokens"
   - Create a new token with type "Automation"
3. Add the token to your GitLab CI/CD variables as `NPM_TOKEN`

## Publishing Process

### Automated Publishing (Recommended)

The GitLab CI/CD pipeline is configured to handle the entire publishing process automatically when you create a git tag:

#### Option 1: Automatic Release (Recommended)

1. **Create a Release**:

   ```bash
   make release
   # or
   ./scripts/create-release.sh
   ```

   - This script will prompt you for the new version
   - It will update version numbers in `pyproject.toml` and `package.json`
   - It will create a git tag (e.g., `v1.0.0`)
   - It will push the tag to trigger the CI pipeline

2. **Automatic Pipeline Execution**:
   - The `auto-release` job will run automatically
   - The `build:package` job will run automatically
   - The `publish:pypi` and `publish:npm` jobs will run automatically
   - All jobs will use the version from the git tag

#### Option 2: Manual Publishing

1. **Build Package** (Manual Trigger):
   - Go to GitLab CI/CD → Pipelines
   - Click "Run pipeline" on the main branch
   - Manually trigger the `build:package` job
   - This will build both the Python package and JupyterLab extension

2. **Publish to PyPI** (Manual Trigger):
   - After the build is complete, manually trigger the `publish:pypi` job
   - This will upload the Python package to PyPI

3. **Publish to NPM** (Manual Trigger):
   - After the build is complete, manually trigger the `publish:npm` job
   - This will publish the NPM package

### Manual Publishing (Local)

If you need to publish manually from your local machine:

#### PyPI Publishing

```bash
# Build the package
npm run build:prod
uv build

# Upload to PyPI (requires twine and PyPI credentials)
uv run twine upload dist/trainwave_jupyter-*
```

#### NPM Publishing

```bash
# Build the extension
npm run build:prod

# Publish to NPM (requires npm login)
npm publish
```

## Installation for Users

### From PyPI (Recommended)

```bash
pip install trainwave-jupyter
```

### From NPM (Alternative)

```bash
npm install trainwave-jupyter
```

### Development Installation

```bash
# Clone the repository
git clone <repository-url>
cd jupyter-extension

# Install in development mode
pip install -e .
jlpm install
jlpm build
```

## Verification

After publishing, verify the packages are available:

- **PyPI**: https://pypi.org/project/trainwave-jupyter/
- **NPM**: https://www.npmjs.com/package/trainwave-jupyter

## Troubleshooting

### Common Issues

1. **Package name conflicts**: Ensure the package name `trainwave-jupyter` is available on both PyPI and NPM
2. **Build failures**: Check that all dependencies are properly installed and the build process completes successfully
3. **Authentication errors**: Verify that the API tokens are correctly set in GitLab CI/CD variables
4. **Version conflicts**: Make sure the version number in `pyproject.toml` and `package.json` match

### Build Verification

Before publishing, verify the build locally:

```bash
# Test Python package build
uv build
ls -la dist/

# Test NPM package build
npm run build:prod
ls -la trainwave_jupyter/labextension/
```

## Version Management

### Automatic Version Management (Recommended)

When using the automated release process:

- The release script automatically updates version in both `pyproject.toml` and `package.json`
- Version is extracted from the git tag (e.g., `v1.0.0` → `1.0.0`)
- Both files are always kept in sync

### Manual Version Management

If updating versions manually:

- Update version in `pyproject.toml` (Python package)
- Update version in `package.json` (NPM package)
- Both should always match
- Use semantic versioning (e.g., 0.1.0, 0.1.1, 1.0.0)

### Release Workflow

1. **Development**: Work on features in branches
2. **Testing**: Run tests and verify build locally
3. **Release**: Use `make release` to create a new version
4. **Publishing**: CI automatically builds and publishes to PyPI and NPM
5. **Verification**: Check that packages are available on PyPI and NPM

## Security Notes

- Never commit API tokens to the repository
- Use GitLab CI/CD variables for sensitive information
- Regularly rotate API tokens
- Use automation tokens for CI/CD, not personal tokens
