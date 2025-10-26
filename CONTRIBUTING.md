# Contributing to Intermap

Thank you for your interest in contributing to Intermap! This document provides guidelines and instructions for contributing to the project.

## 🌟 Ways to Contribute

### 1. Run a Node (Easiest!)

The simplest way to contribute is to run an Intermap node:

```bash
docker run -d --network host --cap-add NET_ADMIN --cap-add NET_RAW --name intermap YOUR_USERNAME/intermap:latest
```

Leave it running 24/7 to continuously map your network and contribute to the global topology!

### 2. Report Bugs

Found a bug? Please [open an issue](https://github.com/YOUR_USERNAME/intermap/issues/new) with:

- **Clear title**: Summarize the problem
- **Description**: What happened vs. what you expected
- **Steps to reproduce**: How can we replicate it?
- **Environment**: OS, Docker version, Python version
- **Logs**: Include relevant error messages

### 3. Suggest Features

Have an idea? [Start a discussion](https://github.com/YOUR_USERNAME/intermap/discussions) or open an issue with:

- **Use case**: Why is this feature needed?
- **Proposed solution**: How would it work?
- **Alternatives**: Other approaches you considered
- **Additional context**: Screenshots, diagrams, examples

### 4. Contribute Code

We welcome pull requests! See below for developer setup and guidelines.

## 🛠️ Development Setup

### Prerequisites

- **Python 3.9+**: [Download](https://www.python.org/downloads/)
- **Node.js 16+**: [Download](https://nodejs.org/)
- **IPFS**: [Install IPFS Desktop](https://docs.ipfs.io/install/ipfs-desktop/) or [CLI](https://docs.ipfs.io/install/command-line/)
- **Git**: For version control
- **Docker** (optional): For testing container builds

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/intermap.git
cd intermap

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Run tests
pytest tests/

# Start IPFS daemon (in separate terminal)
ipfs daemon

# Run the application
python src/main.py
```

The web interface will be available at http://localhost:8000

### Project Structure

```
intermap/
├── src/
│   ├── main.py              # Application entry point
│   ├── cli.py               # Command-line interface
│   ├── api_server.py        # REST API server
│   ├── bandwidth/
│   │   └── bandwidth_tester.py   # iperf3 bandwidth testing
│   ├── graph/
│   │   └── gexf_generator.py     # GEXF graph generation
│   ├── ipfs/
│   │   └── client.py             # IPFS integration
│   ├── node/
│   │   └── node.py               # Main node orchestration
│   └── traceroute/
│       └── tracer.py             # Traceroute and ping sweep
├── frontend/
│   ├── src/
│   │   ├── App.js                # Main React component
│   │   ├── components/
│   │   │   ├── NetworkGraph.js   # vis.js visualization
│   │   │   └── BandwidthLegend.js
│   │   └── utils/
│   │       └── gexfLoader.js     # GEXF parser
│   └── public/
├── tests/                   # Unit and integration tests
├── config/
│   └── default.yaml        # Default configuration
├── Dockerfile              # Container image
├── docker-compose.yml      # Multi-container setup
└── requirements.txt        # Python dependencies
```

## 📝 Coding Guidelines

### Python Code Style

- **Follow PEP 8**: Use `black` for formatting and `flake8` for linting
- **Type hints**: Add type annotations to function signatures
- **Docstrings**: Use Google-style docstrings for all public functions/classes
- **Logging**: Use Python logging module (not print statements)
- **Async/await**: Use async for I/O operations (IPFS, network calls)

Example:

```python
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

async def perform_traceroute(
    target: str,
    max_hops: int = 30,
    timeout: float = 2.0
) -> Dict:
    """
    Perform a traceroute to the specified target.
    
    Args:
        target: IP address or hostname
        max_hops: Maximum number of hops to trace
        timeout: Timeout per hop in seconds
        
    Returns:
        Dictionary containing hop data
        
    Raises:
        ValueError: If target is invalid
    """
    logger.info(f"Starting traceroute to {target}")
    # Implementation...
```

### JavaScript/React Code Style

- **ES6+**: Use modern JavaScript features
- **Functional components**: Prefer hooks over class components
- **Prettier**: Use for code formatting
- **ESLint**: Follow standard linting rules
- **Comments**: Explain complex logic

Example:

```javascript
import React, { useState, useEffect } from 'react';

/**
 * NetworkGraph component displays the topology visualization
 * @param {Object} props - Component props
 * @param {Array} props.nodes - Network nodes
 * @param {Array} props.edges - Network edges
 */
const NetworkGraph = ({ nodes, edges }) => {
  const [selectedNode, setSelectedNode] = useState(null);
  
  useEffect(() => {
    // Initialize visualization
  }, [nodes, edges]);
  
  return (
    <div className="network-graph">
      {/* Render graph */}
    </div>
  );
};
```

### Git Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no functional change)
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(bandwidth): add support for 100 Gbps speed testing

- Add new bandwidth color categories for datacenter speeds
- Update GEXF generator to handle high-speed connections
- Add cyan/blue colors for 10-100 Gbps ranges

Closes #42
```

```
fix(traceroute): prevent duplicate hops in graph

- Check if hop already exists before adding
- Add unique constraint on (source, target) tuple

Fixes #38
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_traceroute.py

# Run specific test
pytest tests/test_traceroute.py::test_ping_sweep
```

### Writing Tests

- **Location**: Place tests in `tests/` directory
- **Naming**: Test files should start with `test_`
- **Structure**: Use pytest fixtures and parametrize for reusability

Example:

```python
import pytest
from src.traceroute.tracer import Traceroute

@pytest.fixture
def tracer():
    """Create a Traceroute instance for testing."""
    return Traceroute(max_hops=15, timeout=1.0)

def test_ping_target_success(tracer):
    """Test successful ping to reachable host."""
    result = tracer._ping_target("8.8.8.8")
    assert result is True

def test_ping_target_failure(tracer):
    """Test ping to unreachable host."""
    result = tracer._ping_target("192.0.2.1")  # TEST-NET-1
    assert result is False

@pytest.mark.parametrize("target,expected", [
    ("8.8.8.8", True),
    ("1.1.1.1", True),
    ("192.0.2.1", False),
])
def test_ping_multiple_targets(tracer, target, expected):
    """Test ping against multiple targets."""
    result = tracer._ping_target(target)
    assert result == expected
```

## 🔄 Pull Request Process

1. **Fork the repository** and create a feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes** following coding guidelines

3. **Add tests** for new functionality

4. **Update documentation** if needed (README, docstrings, etc.)

5. **Run tests and linting**:
   ```bash
   pytest tests/
   black src/
   flake8 src/
   ```

6. **Commit your changes** with clear commit messages

7. **Push to your fork**:
   ```bash
   git push origin feat/your-feature-name
   ```

8. **Open a Pull Request** with:
   - **Title**: Clear summary of changes
   - **Description**: What, why, and how
   - **Linked issues**: Reference related issues
   - **Screenshots**: If UI changes
   - **Testing**: Describe how you tested

9. **Respond to review feedback** and make requested changes

10. **Squash commits** if requested before merge

## 🎯 Priority Areas for Contribution

We especially need help with:

### High Priority

- **IPv6 Support**: Add traceroute and mapping for IPv6 addresses
- **Performance Optimization**: Improve traceroute parallelization
- **Mobile Apps**: iOS/Android apps for mobile mapping
- **AS Number Lookup**: Display autonomous system information
- **Geolocation**: Add approximate geographic locations for IPs

### Medium Priority

- **Better Visualizations**: Improve graph layouts and interactivity
- **Export Formats**: Add JSON, GraphML, CSV exports
- **Statistics Dashboard**: Show network statistics and trends
- **Historical Data**: Track topology changes over time
- **API Documentation**: OpenAPI/Swagger docs

### Low Priority

- **Themes**: Dark mode, custom color schemes
- **Internationalization**: Multi-language support
- **CLI Improvements**: More commands and better output
- **Docker Optimization**: Smaller image size

## 📖 Resources

- **Python Documentation**: https://docs.python.org/3/
- **React Documentation**: https://react.dev/
- **IPFS Documentation**: https://docs.ipfs.io/
- **vis.js Documentation**: https://visjs.org/
- **GEXF Format Spec**: https://gexf.net/

## ❓ Questions?

- **GitHub Discussions**: [Ask questions](https://github.com/YOUR_USERNAME/intermap/discussions)
- **GitHub Issues**: [Report problems](https://github.com/YOUR_USERNAME/intermap/issues)
- **Wiki**: [Check the wiki](https://github.com/YOUR_USERNAME/intermap/wiki)

## 📜 License

By contributing to Intermap, you agree that your contributions will be licensed under the CC BY-NC-SA 4.0 license.

---

**Thank you for contributing to Intermap!** 🌐 Together we're mapping the internet!
