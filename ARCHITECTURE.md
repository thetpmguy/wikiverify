# WikiVerify Architecture

## Overview

WikiVerify follows a clean, modular architecture with clear separation of concerns.

## Architecture Principles

1. **DRY (Don't Repeat Yourself)**: Shared utilities eliminate code duplication
2. **Single Responsibility**: Each module has one clear purpose
3. **Dependency Injection**: Components are loosely coupled
4. **Error Handling**: Consistent error handling patterns
5. **Logging**: Proper logging instead of print statements
6. **Type Safety**: Type hints throughout
7. **Constants**: Magic numbers/strings in constants module

## Project Structure

```
wiki-verify/
├── agents/              # Verification agents (business logic)
├── core/                # Core utilities and infrastructure
│   ├── config.py        # Configuration management
│   ├── constants.py     # Constants and enums
│   ├── database.py      # Database operations
│   ├── logger.py        # Logging setup
│   ├── parser.py        # Citation parsing
│   ├── snapshot.py      # Snapshot management
│   ├── utils.py         # Shared utilities (HTTP, rate limiting)
│   └── content_extractor.py  # Content extraction
├── integrations/        # External API clients
├── llm/                 # LLM integration
├── output/              # Output formatting
└── scripts/             # Utility scripts
```

## Core Components

### 1. Shared Utilities (`core/utils.py`)

**HTTPClient**: Unified HTTP client with:
- Rate limiting built-in
- Error handling
- Consistent timeout management
- Session management

**RateLimiter**: Reusable rate limiting logic

**Benefits**:
- Eliminates code duplication across integrations
- Consistent error handling
- Easy to test and mock

### 2. Logging System (`core/logger.py`)

**Features**:
- Structured logging with levels
- File and console output
- Consistent formatting
- Easy to configure

**Usage**:
```python
from core.logger import get_logger
logger = get_logger(__name__)
logger.info("Message")
logger.error("Error message")
```

### 3. Constants Module (`core/constants.py`)

**Purpose**: Centralized constants and enums

**Benefits**:
- Type safety with enums
- No magic strings/numbers
- Easy to refactor
- IDE autocomplete support

**Example**:
```python
from core.constants import ProblemType, Severity

problem_type = ProblemType.BROKEN_LINK
severity = Severity.HIGH
```

### 4. Database Layer (`core/database.py`)

**Features**:
- Context manager for connections
- Automatic transaction handling
- Error logging
- Type hints

**Pattern**:
```python
with get_connection() as conn:
    # Database operations
    # Auto-commits on success, rolls back on error
```

### 5. Base Agent (`agents/base_agent.py`)

**Features**:
- Abstract base class
- Shared logging
- Common finding saving logic
- Consistent interface

## Integration Pattern

All integrations follow the same pattern:

```python
class Integration:
    def __init__(self):
        self.client = HTTPClient(
            base_url="...",
            user_agent="...",
            rate_limit_delay=...
        )
    
    def method(self):
        response = self.client.get(url, params=params)
        if not response:
            return None
        # Process response
```

## Agent Pattern

All agents follow this pattern:

```python
class Agent(BaseAgent):
    def __init__(self, use_llm_triage=True):
        super().__init__("agent_name")
        self.client = HTTPClient(...)
        self.llm_triage = LLMTriage(enabled=use_llm_triage)
    
    def check_citation(self, citation):
        # Check logic
        finding = {...}
        
        # LLM triage if enabled
        if self.llm_triage:
            if not self.llm_triage.is_real_problem(...):
                return None
            finding['details'] = self.llm_triage.explain_finding(...)
        
        return finding
    
    def run(self):
        # Main execution logic
        # Uses self.log() for logging
        # Handles errors gracefully
```

## Error Handling

**Pattern**:
- Try/except blocks around risky operations
- Log errors with context
- Return None/empty list on error (fail gracefully)
- Don't crash the entire agent on single citation error

**Example**:
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Context: {e}")
    return None  # Fail gracefully
```

## Logging Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (failures)

## Code Quality Improvements

### Before Refactoring:
- ❌ Code duplication (rate limiting in 7 places)
- ❌ print() statements everywhere
- ❌ Magic strings and numbers
- ❌ Inconsistent error handling
- ❌ No type hints in some places
- ❌ Each integration creates its own session

### After Refactoring:
- ✅ Shared HTTPClient eliminates duplication
- ✅ Proper logging system
- ✅ Constants module for magic values
- ✅ Consistent error handling
- ✅ Type hints throughout
- ✅ Shared utilities reduce code by ~30%

## Testing

The architecture supports easy testing:
- Mock HTTPClient for integration tests
- Mock database for unit tests
- Dependency injection allows easy mocking

## Future Enhancements

1. **Repository Pattern**: Abstract database operations
2. **Factory Pattern**: For creating agents
3. **Observer Pattern**: For event-driven architecture
4. **Strategy Pattern**: For different checking strategies

## Best Practices

1. **Always use HTTPClient** for HTTP requests
2. **Use logger** instead of print()
3. **Use constants** instead of magic values
4. **Handle errors gracefully** - don't crash on single failure
5. **Add type hints** to all functions
6. **Document with docstrings** - explain what, not how
