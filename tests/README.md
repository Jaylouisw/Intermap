# Tests directory

Unit tests for the Distributed Internet Topology Mapper.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_graph.py

# Verbose output
pytest -v
```

## Test Structure

- `test_traceroute.py` - Traceroute functionality tests
- `test_graph.py` - Graph and GEXF generation tests
- `test_utils.py` - Utility function tests
- `conftest.py` - Pytest configuration

