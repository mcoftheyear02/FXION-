# FXION-ONYX Security Best Practices

## 1. Cryptographic Security

### Key Management
```python
# ❌ WRONG - Hardcoded keys
KEY = "super_secret_key_12345"

# ✅ CORRECT - Environment variables
import os
KEY = os.getenv("FXION_SECRET_KEY")
if not KEY:
    raise ValueError("FXION_SECRET_KEY environment variable not set")
```

## 2. Input Validation

```python
import re
from typing import Optional

# ✅ Validate wallet addresses
def validate_btc_address(address: str) -> bool:
    """Validate Bitcoin address format (P2PKH, P2SH, Bech32)."""
    if not isinstance(address, str):
        return False
    if len(address) < 26 or len(address) > 35:
        return False
    # P2PKH starts with 1, P2SH with 3, Bech32 with bc1
    pattern = r'^[13bc][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$'
    return bool(re.match(pattern, address))
```

## 3. Secure Communication

```python
import ssl
import requests

# ✅ Always use HTTPS with certificate verification
def secure_api_call(url: str, data: dict) -> dict:
    session = requests.Session()
    # Verify SSL certificates
    session.verify = True
    # Set reasonable timeout
    timeout = 30
    
    try:
        response = session.post(url, json=data, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API call failed: {e}")
        raise
```

## Security Checklist

- [ ] No hardcoded secrets or credentials
- [ ] All API calls use HTTPS/TLS
- [ ] Input validation on all external data
- [ ] HMAC verification for authentication
- [ ] Secure random number generation
- [ ] Rate limiting on sensitive operations
- [ ] Comprehensive audit logging
- [ ] Regular security updates
- [ ] Code review before production
- [ ] Regular penetration testing

---

**Version:** 1.0  
**Last Updated:** 2026-06-03  
**Review Cycle:** Quarterly