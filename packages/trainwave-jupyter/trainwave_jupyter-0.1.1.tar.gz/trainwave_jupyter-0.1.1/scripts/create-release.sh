#!/bin/bash

# Create Release Script for Trainwave Jupyter Extension
# This script creates a git tag and triggers the release pipeline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Trainwave Jupyter Extension Release Script${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Error: git is not installed${NC}"
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo -e "${BLUE}📦 Current version: ${CURRENT_VERSION}${NC}"

# Get the latest tag and suggest next version
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LATEST_TAG" ]; then
    # Remove 'v' prefix if present
    LATEST_VERSION=${LATEST_TAG#v}
    echo -e "${BLUE}🏷️  Latest tag: ${LATEST_TAG}${NC}"

    # Parse version components
    IFS='.' read -r MAJOR MINOR PATCH <<< "$LATEST_VERSION"

    # Suggest patch version increment by default
    SUGGESTED_VERSION="${MAJOR}.${MINOR}.$((PATCH + 1))"
    echo -e "${GREEN}💡 Suggested next version: ${SUGGESTED_VERSION}${NC}"
else
    echo -e "${YELLOW}⚠️  No previous tags found${NC}"
    SUGGESTED_VERSION="0.1.0"
    echo -e "${GREEN}💡 Suggested first version: ${SUGGESTED_VERSION}${NC}"
fi

# Get new version from user
echo ""
echo -e "${YELLOW}Enter the new version (e.g., 0.1.1, 1.0.0):${NC}"
read -p "New version [${SUGGESTED_VERSION}]: " NEW_VERSION

# Use suggested version if user just pressed Enter
if [ -z "$NEW_VERSION" ]; then
    NEW_VERSION="$SUGGESTED_VERSION"
    echo -e "${BLUE}Using suggested version: ${NEW_VERSION}${NC}"
fi

# Validate version format (basic semantic versioning check)
if [[ ! $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}❌ Error: Invalid version format. Please use semantic versioning (e.g., 0.1.1, 1.0.0)${NC}"
    exit 1
fi

# Check if version is different
if [ "$CURRENT_VERSION" = "$NEW_VERSION" ]; then
    echo -e "${YELLOW}⚠️  Warning: New version is the same as current version${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Check if tag already exists
if git tag -l | grep -q "^v${NEW_VERSION}$"; then
    echo -e "${RED}❌ Error: Tag v${NEW_VERSION} already exists${NC}"
    exit 1
fi

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ Error: There are uncommitted changes. Please commit or stash them first.${NC}"
    git status --short
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠️  Warning: You're not on the main branch (currently on: ${CURRENT_BRANCH})${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Update version in files
echo -e "${BLUE}📝 Updating version in configuration files...${NC}"

# Update pyproject.toml
sed -i.bak "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
rm pyproject.toml.bak

# Update package.json
sed -i.bak "s/\"version\": .*/\"version\": \"$NEW_VERSION\",/" package.json
rm package.json.bak

echo -e "${GREEN}✅ Version updated to ${NEW_VERSION}${NC}"

# Commit the version changes
echo -e "${BLUE}📝 Committing version changes...${NC}"
git add pyproject.toml package.json
git commit -m "Bump version to ${NEW_VERSION}"

# Create and push the tag
echo -e "${BLUE}🏷️  Creating and pushing tag v${NEW_VERSION}...${NC}"
git tag -a "v${NEW_VERSION}" -m "Release version ${NEW_VERSION}"
git push origin main
git push origin "v${NEW_VERSION}"

echo ""
echo -e "${GREEN}🎉 Release v${NEW_VERSION} created successfully!${NC}"
echo ""
echo -e "${BLUE}📋 What happens next:${NC}"
echo -e "  1. GitLab CI will automatically detect the new tag"
echo -e "  2. The auto-release job will run"
echo -e "  3. The build:package job will run automatically"
echo -e "  4. The publish:pypi and publish:npm jobs will run automatically"
echo ""
echo -e "${BLUE}🔗 Monitor the pipeline:${NC}"
echo -e "  - Go to GitLab CI/CD → Pipelines"
echo -e "  - Look for the pipeline triggered by tag v${NEW_VERSION}"
echo ""
echo -e "${BLUE}📦 After successful publishing:${NC}"
echo -e "  - PyPI: https://pypi.org/project/trainwave-jupyter/"
echo -e "  - NPM: https://www.npmjs.com/package/trainwave-jupyter"
echo ""
echo -e "${GREEN}✨ Happy releasing!${NC}"
