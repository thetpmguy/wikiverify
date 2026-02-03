# Code Quality Standards

## Overview

This document outlines the code quality standards and patterns used in WikiVerify.

## Code Style

### Type Hints
All functions should have type hints:
```python
def function(param: str) -> Optional[Dict[str, Any]]:
    ...
```

### Docstrings
All public functions should have docstrings:
```python
def function(param: str) -> Optional[Dict[str, Any]]:
    """
    Brief description.
    
    Args:
        param: Description of parameter
    
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When this exception is raised
    """
```

### Constants
Use constants module instead of magic values:
```python
# ❌ Bad
if status == 'broken_link':
    severity = 'high'

# ✅ Good
from core.constants import ProblemType, Severity
if status == ProblemType.BROKEN_LINK:
    severity = Severity.HIGH
```

## Logging

### Use Proper Logging
```python
# ❌ Bad
print("Error occurred")
print(f"Processing {item}")

# ✅ Good
from core.logger import get_logger
logger = get_logger(__name__)
logger.error("Error occurred")
logger.info(f"Processing {item}")
```

### Log Levels
- **DEBUG**: Detailed diagnostic info (e.g., "Checking citation 123")
- **INFO**: General information (e.g., "Agent started", "Found 5 issues")
- **WARNING**: Non-critical issues (e.g., "Could not create snapshot")
- **ERROR**: Errors that need attention (e.g., "Database connection failed")

## Error Handling

### Pattern
```python
# ✅ Good
try:
    result = risky_operation()
    if not result:
        logger.warning("Operation returned None")
        return None
    return result
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    return None
```

### Don't Swallow Errors
```python
# ❌ Bad
try:
    operation()
except:
    pass

# ✅ Good
try:
    operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    # Handle appropriately
```

## HTTP Requests

### Use HTTPClient
```python
# ❌ Bad
self._rate_limit()
response = self.session.get(url)

# ✅ Good
response = self.client.get(url)
if not response:
    return None
```

## Code Organization

### Imports Order
1. Standard library
2. Third-party packages
3. Local modules

```python
# Standard library
import time
from typing import Dict, Any

# Third-party
import requests

# Local
from core.config import Config
from core.utils import HTTPClient
```

### Class Organization
1. `__init__`
2. Private methods (`_method`)
3. Public methods
4. Properties

## Testing

### Testable Code
- Functions should be pure when possible
- Dependencies should be injectable
- Use dependency injection for testability

## Performance

### Rate Limiting
Always use HTTPClient which handles rate limiting automatically.

### Database Queries
- Use parameterized queries (prevents SQL injection)
- Use LIMIT clauses for large datasets
- Index frequently queried columns

## Security

### SQL Injection Prevention
```python
# ❌ Bad
query = f"SELECT * FROM table WHERE id = {user_id}"

# ✅ Good
query = "SELECT * FROM table WHERE id = %s"
execute_query(query, (user_id,))
```

### API Keys
Never commit API keys. Use `.env` file and `Config` class.

## Documentation

### Inline Comments
Use comments to explain "why", not "what":
```python
# ❌ Bad
# Increment counter
counter += 1

# ✅ Good
# Rate limit: PubMed allows max 3 requests/second
time.sleep(0.34)
```

## Refactoring Checklist

When refactoring code, ensure:
- [ ] Uses HTTPClient for HTTP requests
- [ ] Uses logger instead of print()
- [ ] Uses constants instead of magic values
- [ ] Has proper error handling
- [ ] Has type hints
- [ ] Has docstrings
- [ ] Follows import order
- [ ] No code duplication
