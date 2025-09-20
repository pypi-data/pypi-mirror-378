# GitLab CI/CD Setup for Trainwave Jupyter Extension

This document explains the GitLab CI/CD pipeline configuration for the Trainwave Jupyter Extension.

## Overview

The CI/CD pipeline is configured to:

1. **Run tests automatically** on all commits and merges to `main` (excluding UI tests)
2. **Package the extension** manually when ready for release
3. **Publish to PyPI** under the name `trainwave-jupyter` manually

## Pipeline Stages

### 1. Test Stage (Automatic)

**Triggers**: All commits to `main`, merge requests, and branch pushes

- **`test:python`**: Runs Python tests using pytest with coverage
- **`test:typescript`**: Runs TypeScript/JavaScript tests using Jest with coverage

**Excluded**: UI tests (Playwright) are excluded from automatic runs for faster feedback

### 2. Build Stage (Manual)

**Trigger**: Manual trigger on `main` branch only

- **`build:package`**: Builds both the JupyterLab extension and Python package

### 3. Publish Stage (Manual)

**Trigger**: Manual trigger on `main` branch only

- **`publish:pypi`**: Publishes the Python package to PyPI as `trainwave-jupyter`
- **`publish:npm`**: Publishes the npm package (optional)

## How to Use

### Running Tests

Tests run automatically on every commit and merge request. You can also manually trigger them:

1. Go to **CI/CD** → **Pipelines** in your GitLab project
2. Click **Run pipeline** on the `main` branch

### Publishing a Release

1. **Update version numbers** in both `package.json` and `pyproject.toml`
2. **Commit and push** to the `main` branch
3. **Wait for tests** to pass automatically
4. **Manually trigger** the `build:package` job:
   - Go to **CI/CD** → **Pipelines**
   - Find the latest pipeline
   - Click the play button (▶️) next to `build:package`
5. **Manually trigger** the `publish:pypi` job:
   - After the build completes successfully
   - Click the play button (▶️) next to `publish:pypi`

### Running UI Tests (Optional)

UI tests can be run manually when needed:

1. Go to **CI/CD** → **Pipelines**
2. Click the play button (▶️) next to `test:ui`

## Required Setup

Before the pipeline can work, you need to configure environment variables in GitLab:

1. Go to **Settings** → **CI/CD** → **Variables**
2. Add the required variables (see `.gitlab-ci-variables.md` for details)

**Required variables:**

- `PYPI_TOKEN`: For publishing to PyPI

**Optional variables:**

- `NPM_TOKEN`: For publishing to npm (if needed)

## File Structure

- `.gitlab-ci.yml`: Main CI/CD configuration
- `.gitlab-ci-variables.md`: Documentation for required environment variables
- `CI-SETUP.md`: This file - overview and usage instructions

## Benefits

- **Fast feedback**: Tests run automatically on every commit
- **Quality assurance**: Coverage reports ensure code quality
- **Controlled releases**: Manual triggers prevent accidental publishes
- **Comprehensive testing**: Both Python and TypeScript code is tested
- **Flexible**: UI tests can be run when needed without slowing down regular development

## Troubleshooting

### Common Issues

1. **Tests failing**: Check the pipeline logs for specific error messages
2. **Publishing failing**: Verify that environment variables are set correctly
3. **Version conflicts**: Make sure to increment version numbers before publishing

### Getting Help

- Check the GitLab CI/CD logs for detailed error messages
- Review the `.gitlab-ci-variables.md` file for setup requirements
- Ensure all dependencies are properly configured in `package.json` and `pyproject.toml`
