# FXION-ONYX Error Handling Guide

## Overview

This document outlines the error handling patterns and best practices used throughout the FXION-ONYX system.

## Exception Hierarchy

```python
class FXIONError(Exception):
    """Base exception for all FXION errors"""
    pass

class FXIONConfigError(FXIONError):
    """Configuration-related errors"""
    pass

class FXIONHardwareError(FXIONError):
    """GPU/hardware-related errors"""
    pass

class FXIONCryptographyError(FXIONError):
    """Cryptography validation errors"""
    pass

class FXIONPoolError(FXIONError):
    """Mining pool connection errors"""
    pass
```

## Error Handling Patterns

### Pattern 1: Safe Defaults
```python
def get_gpu_temperature() -> float:
    """Get GPU temperature with safe default."""
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        temp = pynvml.nvmlDeviceGetCurrentTemperature(handle)
        return float(temp)
    except Exception as e:
        logger.warning(f"Failed to get GPU temp: {e}, using default 55.0°C")
        return 55.0  # Safe default
```

## Best Practices

✅ **DO:**
- Catch specific exceptions, not generic `Exception`
- Log sufficient context for debugging
- Provide meaningful error messages
- Use try-finally for cleanup
- Use context managers for resource management
- Implement retry logic with exponential backoff
- Validate input early

❌ **DON'T:**
- Use bare `except:` clauses
- Silently ignore exceptions
- Log sensitive data (keys, passwords, tokens)
- Mix different error handling strategies
- Raise generic exceptions
- Leave resources uncleaned on error

---

**Version:** 1.0  
**Last Updated:** 2026-06-03