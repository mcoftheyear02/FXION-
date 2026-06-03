# FXION-ONYX Contribution Guide

Thank you for your interest in contributing to FXION-ONYX!

## Code Standards

### 1. Python Style
- Follow **PEP 8** standards
- Use **Black** for formatting: `black .`
- Use **isort** for import sorting: `isort .`
- Maximum line length: 120 characters

### 2. Type Hints
- Add type hints to function signatures
- Use `mypy` for type checking: `mypy .`

### 3. Documentation
- Add docstrings to all public functions
- Use Google-style docstrings:
  ```python
  def example_function(param1: str, param2: int) -> bool:
      """Brief description.
      
      Longer description if needed.
      
      Args:
          param1: Description of param1
          param2: Description of param2
      
      Returns:
          Description of return value
      
      Raises:
          ValueError: When something is wrong
      """
  ```

### 4. Error Handling
- Use explicit exception types
- Log errors appropriately
- Provide meaningful error messages

```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Validation failed: {e}")
    raise
```

## Testing Requirements

- Write unit tests for all new features
- Run `pytest` before committing: `pytest test_*.py -v`
- Maintain >80% code coverage: `pytest --cov=.`
- All tests must pass on Python 3.9+

## Security Guidelines

- Never hardcode secrets or API keys
- Use environment variables for configuration
- Run `bandit` for security checks: `bandit -r .`
- Validate all user inputs
- Use cryptographic libraries correctly

## Git Workflow

1. Create a feature branch: `git checkout -b feature/description`
2. Make atomic commits with clear messages
3. Format code before committing
4. Push to your fork and create a Pull Request
5. Ensure CI/CD checks pass

## Performance Considerations

- Profile code for bottlenecks
- Use vectorized operations (NumPy) when possible
- Minimize VRAM allocations
- Cache expensive computations
- Monitor GPU temperatures

## Reporting Issues

Include:
- Reproducible steps
- Expected vs actual behavior
- System configuration (Python version, GPU, CUDA version)
- Error logs (with sensitive data removed)
- Proposed solution (if applicable)

## Questions?

Please open an issue or contact the maintainers.

---
**Happy Contributing!** 🚀