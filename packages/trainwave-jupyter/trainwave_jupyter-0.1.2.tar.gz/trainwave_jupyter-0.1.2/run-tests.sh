#!/bin/bash

# Test runner script for Trainwave JupyterLab Extension
# This script runs all tests in the correct order

set -e  # Exit on any error

echo "🧪 Running Trainwave Extension Tests"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables for JupyterLab management
JUPYTER_PID=""
JUPYTER_PORT=8888
JUPYTER_TOKEN=""
JUPYTER_URL=""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to check if JupyterLab is already running
check_jupyter_running() {
    if check_port $JUPYTER_PORT; then
        # Check if it's actually JupyterLab by making a request
        if curl -s "http://localhost:$JUPYTER_PORT/lab" >/dev/null 2>&1; then
            return 0  # JupyterLab is running
        fi
    fi
    return 1  # JupyterLab is not running
}

# Function to start JupyterLab
start_jupyter() {
    print_status "Starting JupyterLab for UI tests..."

    # Generate a random token for security
    JUPYTER_TOKEN=$(openssl rand -hex 32)
    JUPYTER_URL="http://localhost:$JUPYTER_PORT/lab?token=$JUPYTER_TOKEN"

    # Start JupyterLab in the background
    nohup jupyter lab \
        --port=$JUPYTER_PORT \
        --no-browser \
        --allow-root \
        --ip=127.0.0.1 \
        --ServerApp.token=$JUPYTER_TOKEN \
        --ServerApp.disable_check_xsrf=True \
        --ServerApp.allow_origin="*" \
        --ServerApp.allow_remote_access=True \
        --log-level=WARN \
        > jupyter_test.log 2>&1 &

    JUPYTER_PID=$!

    # Wait for JupyterLab to start
    print_status "Waiting for JupyterLab to start..."
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -s "http://localhost:$JUPYTER_PORT/lab?token=$JUPYTER_TOKEN" >/dev/null 2>&1; then
            print_success "JupyterLab started successfully on $JUPYTER_URL"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done

    print_error "Failed to start JupyterLab after $max_attempts attempts"
    return 1
}

# Function to stop JupyterLab
stop_jupyter() {
    if [ -n "$JUPYTER_PID" ] && kill -0 $JUPYTER_PID 2>/dev/null; then
        print_status "Stopping JupyterLab (PID: $JUPYTER_PID)..."
        kill $JUPYTER_PID
        wait $JUPYTER_PID 2>/dev/null || true
        print_success "JupyterLab stopped"
    fi

    # Clean up log file
    if [ -f "jupyter_test.log" ]; then
        rm -f jupyter_test.log
    fi
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    stop_jupyter
}

# Set up trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Parse command line arguments
RUN_PYTHON=true
RUN_TYPESCRIPT=true
RUN_UI=true
COVERAGE=true
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --python-only)
            RUN_PYTHON=true
            RUN_TYPESCRIPT=false
            RUN_UI=false
            shift
            ;;
        --typescript-only)
            RUN_PYTHON=false
            RUN_TYPESCRIPT=true
            RUN_UI=false
            shift
            ;;
        --ui-only)
            RUN_PYTHON=false
            RUN_TYPESCRIPT=false
            RUN_UI=true
            shift
            ;;
        --no-ui)
            RUN_UI=false
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --python-only      Run only Python tests"
            echo "  --typescript-only  Run only TypeScript tests"
            echo "  --ui-only          Run only UI tests"
            echo "  --no-ui            Skip UI tests (default: run all tests)"
            echo "  --no-coverage      Skip coverage reports"
            echo "  --verbose          Verbose output"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Run all tests (Python, TypeScript, UI)"
            echo "  $0 --no-ui         # Run Python and TypeScript tests only"
            echo "  $0 --ui-only       # Run only UI tests"
            echo "  $0 --python-only   # Run only Python tests"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check dependencies
print_status "Checking dependencies..."

# Check Python dependencies
if [ "$RUN_PYTHON" = true ]; then
    if ! command -v uv &> /dev/null; then
        print_error "uv is not installed. Please install uv first:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    # Check if pytest is available in the uv environment
    if ! uv run pytest --version &> /dev/null; then
        print_warning "Test dependencies not found. Installing with uv..."
        uv sync --extra test
    fi
fi

# Check Node.js dependencies
if [ "$RUN_TYPESCRIPT" = true ] || [ "$RUN_UI" = true ]; then
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi

    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Installing dependencies..."
        npm install
    fi
fi

# Check Playwright for UI tests
if [ "$RUN_UI" = true ]; then
    if ! npx playwright --version &> /dev/null; then
        print_warning "Playwright not found. Installing..."
        npx playwright install
    fi

    # Check if JupyterLab is available
    if ! command -v jupyter &> /dev/null; then
        print_error "JupyterLab is not installed. Please install it first:"
        echo "  pip install jupyterlab"
        echo "  or"
        echo "  conda install jupyterlab"
        exit 1
    fi
fi

# Run Python tests
if [ "$RUN_PYTHON" = true ]; then
    print_status "Running Python tests..."

    PYTEST_ARGS=""
    if [ "$COVERAGE" = true ]; then
        PYTEST_ARGS="$PYTEST_ARGS --cov=trainwave_jupyter --cov-report=html --cov-report=term-missing"
    fi
    if [ "$VERBOSE" = true ]; then
        PYTEST_ARGS="$PYTEST_ARGS -v"
    fi

    if uv run pytest $PYTEST_ARGS; then
        print_success "Python tests passed!"
    else
        print_error "Python tests failed!"
        exit 1
    fi
fi

# Run TypeScript tests
if [ "$RUN_TYPESCRIPT" = true ]; then
    print_status "Running TypeScript tests..."

    NPM_TEST_ARGS=""
    if [ "$COVERAGE" = true ]; then
        NPM_TEST_ARGS="$NPM_TEST_ARGS -- --coverage"
    fi
    if [ "$VERBOSE" = true ]; then
        NPM_TEST_ARGS="$NPM_TEST_ARGS -- --verbose"
    fi

    if npm run test:ci $NPM_TEST_ARGS; then
        print_success "TypeScript tests passed!"
    else
        print_error "TypeScript tests failed!"
        exit 1
    fi
fi

# Run UI tests
if [ "$RUN_UI" = true ]; then
    print_status "Running UI tests..."

    # Check if JupyterLab is already running
    if check_jupyter_running; then
        print_warning "JupyterLab is already running on port $JUPYTER_PORT"
        print_status "Using existing JupyterLab instance for UI tests"
        JUPYTER_URL="http://localhost:$JUPYTER_PORT/lab"
    else
        # Start JupyterLab for UI tests
        if ! start_jupyter; then
            print_error "Failed to start JupyterLab for UI tests"
            exit 1
        fi
    fi

    # Set environment variable for Playwright tests
    export JUPYTER_URL

    print_status "Running Playwright tests against $JUPYTER_URL"

    if npm run test:ui; then
        print_success "UI tests passed!"
    else
        print_error "UI tests failed!"
        exit 1
    fi
fi

# Summary
echo ""
echo "🎉 All tests completed successfully!"
echo ""

if [ "$COVERAGE" = true ]; then
    echo "📊 Coverage reports generated:"
    if [ "$RUN_PYTHON" = true ]; then
        echo "  - Python: htmlcov/index.html"
    fi
    if [ "$RUN_TYPESCRIPT" = true ]; then
        echo "  - TypeScript: coverage/lcov-report/index.html"
    fi
fi

echo ""
echo "✨ Happy testing!"
echo ""
echo "💡 Tips:"
echo "  - Use --help to see all available options"
echo "  - Use --no-ui to skip UI tests for faster execution"
echo "  - Use --verbose for detailed test output"
