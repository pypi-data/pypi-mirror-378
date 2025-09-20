# Testing Guide for Trainwave JupyterLab Extension

This document provides comprehensive information about testing the Trainwave JupyterLab extension.

## Test Structure

The project includes multiple types of tests:

### 1. Python Backend Tests (`trainwave_jupyter/tests/`)

- **`test_handlers.py`** - Tests for HTTP handlers and authentication logic
- **`test_io.py`** - Tests for file I/O operations and tarball creation
- **`test_init.py`** - Tests for extension initialization
- **`test_integration.py`** - Integration tests for complete workflows

### 2. TypeScript Frontend Tests (`src/__tests__/`)

- **`trainwave.spec.ts`** - Core functionality tests for API client and auth service
- **`components.spec.tsx`** - React component tests
- **`setup.ts`** - Jest test environment configuration

### 3. UI Integration Tests (`ui-tests/tests/`)

- **`trainwave-integration.spec.ts`** - End-to-end UI tests using Playwright

## Running Tests

### Python Tests

```bash
# Run all Python tests
pytest

# Run with coverage
pytest --cov=trainwave_jupyter --cov-report=html

# Run specific test file
pytest trainwave_jupyter/tests/test_handlers.py

# Run tests with specific markers
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Run only integration tests
```

### TypeScript Tests

```bash
# Run all TypeScript tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests for CI
npm run test:ci

# Run with coverage
npm test -- --coverage
```

### UI Tests

```bash
# Run UI tests (requires JupyterLab to be running)
npm run test:ui

# Run UI tests in headed mode (visible browser)
npm run test:ui:headed

# Debug UI tests
npm run test:ui:debug
```

## Test Configuration

### Python (pytest)

Configuration is in `pyproject.toml`:

- **Coverage threshold**: 80% minimum
- **Test discovery**: `test_*.py` and `*_test.py` files
- **Markers**: `slow`, `integration`, `unit`, `e2e`
- **Coverage reports**: HTML, XML, and terminal output

### TypeScript (Jest)

Configuration is in `jest.config.js`:

- **Test environment**: jsdom for React component testing
- **Coverage threshold**: 80% minimum
- **Setup file**: `src/__tests__/setup.ts`
- **Module mapping**: CSS and asset files are mocked

### UI Tests (Playwright)

Configuration is in `ui-tests/playwright.config.js`:

- **Browser**: Chromium, Firefox, WebKit
- **Base URL**: `http://localhost:8888/lab`
- **Timeout**: 30 seconds per test

## Test Categories

### Unit Tests

Test individual functions and classes in isolation:

```python
# Example: Testing a single method
def test_create_mock_auth_session(self, auth_handler):
    result = auth_handler._create_mock_auth_session("test-device")
    assert "url" in result
    assert "token" in result
```

### Integration Tests

Test interactions between components:

```python
# Example: Testing complete authentication flow
@pytest.mark.asyncio
async def test_authentication_flow_integration(self, jp_fetch):
    # Create session
    response = await jp_fetch("trainwave-jupyter", "auth/create_session", ...)
    # Check status
    response = await jp_fetch("trainwave-jupyter", "auth/session_status", ...)
```

### Component Tests

Test React components with user interactions:

```typescript
// Example: Testing component behavior
it('should handle authentication success', async () => {
  mockAuthService.authenticate.mockResolvedValue(true);

  render(<AuthDialog authService={mockAuthService} />);

  const loginButton = screen.getByText('Login with Trainwave');
  fireEvent.click(loginButton);

  await waitFor(() => {
    expect(mockOnAuthSuccess).toHaveBeenCalled();
  });
});
```

### End-to-End Tests

Test complete user workflows:

```typescript
// Example: Testing UI workflow
test('should show trainwave dropdown in notebook toolbar', async ({ page }) => {
  await page.click('[data-command="notebook:create-new"]');
  await page.waitForSelector('.jp-NotebookPanel');

  const trainwaveDropdown = page.locator('.trainwave-dropdown-widget');
  await expect(trainwaveDropdown).toBeVisible();
});
```

## Mocking and Test Doubles

### Python Mocks

```python
# Mock external API calls
with patch('aiohttp.ClientSession') as mock_session:
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
```

### TypeScript Mocks

```typescript
// Mock JupyterLab services
jest.mock('@jupyterlab/services', () => ({
  ServerConnection: {
    makeSettings: jest.fn(),
    makeRequest: jest.fn()
  }
}));

// Mock API responses
(require('../handler').requestAPI as jest.Mock).mockResolvedValue(mockResponse);
```

## Test Data and Fixtures

### Python Fixtures

```python
@pytest.fixture
def auth_handler(self, mock_request):
    handler = AuthHandler()
    handler.request = mock_request
    handler.set_status = MagicMock()
    handler.finish = MagicMock()
    return handler
```

### TypeScript Mocks

```typescript
const mockAuthService = {
  isAuthenticated: jest.fn(),
  authenticate: jest.fn(),
  logout: jest.fn()
} as any;
```

## Coverage Reports

### Python Coverage

- **HTML Report**: `htmlcov/index.html`
- **XML Report**: `coverage.xml`
- **Terminal**: Shows missing lines

### TypeScript Coverage

- **HTML Report**: `coverage/lcov-report/index.html`
- **LCOV Report**: `coverage/lcov.info`
- **Terminal**: Shows coverage summary

## Continuous Integration

### GitHub Actions Example

```yaml
- name: Run Python Tests
  run: |
    pip install -e ".[test]"
    pytest --cov=trainwave_jupyter --cov-report=xml

- name: Run TypeScript Tests
  run: |
    npm ci
    npm run test:ci

- name: Run UI Tests
  run: |
    npm run test:ui
```

## Debugging Tests

### Python Debugging

```bash
# Run with verbose output
pytest -v -s

# Run specific test with debugging
pytest -v -s trainwave_jupyter/tests/test_handlers.py::TestAuthHandler::test_create_mock_auth_session

# Use pdb for debugging
pytest --pdb
```

### TypeScript Debugging

```bash
# Run with debugging
npm test -- --verbose

# Run specific test file
npm test -- trainwave.spec.ts

# Use Node.js debugger
node --inspect-brk node_modules/.bin/jest --runInBand
```

### UI Test Debugging

```bash
# Run with debug mode
npm run test:ui:debug

# Run specific test
npx playwright test trainwave-integration.spec.ts --debug
```

## Best Practices

### Test Organization

1. **Group related tests** in classes or describe blocks
2. **Use descriptive test names** that explain the expected behavior
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Keep tests independent** - no shared state between tests

### Test Data

1. **Use realistic test data** that matches production scenarios
2. **Create reusable fixtures** for common test objects
3. **Clean up resources** in teardown methods
4. **Use factories** for generating test data

### Assertions

1. **Use specific assertions** rather than generic ones
2. **Test both positive and negative cases**
3. **Verify error conditions** and edge cases
4. **Check side effects** in addition to return values

### Performance

1. **Mark slow tests** with appropriate markers
2. **Use parallel execution** where possible
3. **Mock external dependencies** to avoid network calls
4. **Clean up resources** to prevent memory leaks

## Troubleshooting

### Common Issues

1. **Import errors**: Check module paths and dependencies
2. **Async test failures**: Ensure proper use of `await` and `async`
3. **Mock not working**: Verify mock setup and call expectations
4. **UI test timeouts**: Increase timeout or check element selectors

### Getting Help

1. **Check test logs** for detailed error messages
2. **Run tests individually** to isolate issues
3. **Use debug mode** to step through failing tests
4. **Review test configuration** for setup issues

## Contributing

When adding new tests:

1. **Follow existing patterns** and naming conventions
2. **Add appropriate test markers** (unit, integration, etc.)
3. **Update documentation** if adding new test types
4. **Ensure tests pass** in CI environment
5. **Maintain coverage thresholds** (80% minimum)
