---
layout: page
title: Contributing
permalink: /contributing/
---

# Contributing to JupyterLab Firefox Launcher

We welcome contributions to the JupyterLab Firefox Launcher! This guide will help you get started with contributing to the project, whether you're fixing bugs, adding features, improving documentation, or helping with testing.

## Getting Started

### Ways to Contribute

There are many ways to contribute to the project:

- 🐛 **Bug Reports**: Report issues and help improve stability
- ✨ **Feature Requests**: Suggest new features and enhancements
- 🔧 **Code Contributions**: Fix bugs, implement features, improve performance
- 📚 **Documentation**: Improve docs, add examples, write tutorials
- 🧪 **Testing**: Write tests, test new features, report compatibility issues
- 🌐 **Translation**: Help translate the extension to other languages
- 💬 **Community Support**: Help other users in discussions and issues

### Before You Start

1. **Check existing issues**: Search [GitHub Issues](https://github.com/vantagecompute/jupyterlab-firefox-launcher/issues) to see if your idea or bug has already been reported
2. **Read the documentation**: Familiarize yourself with the [architecture]({{ site.baseurl }}/architecture) and [development guide]({{ site.baseurl }}/development)
3. **Join the discussion**: Participate in [GitHub Discussions](https://github.com/vantagecompute/jupyterlab-firefox-launcher/discussions) to connect with the community

## Setting Up Development Environment

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/jupyterlab-firefox-launcher.git
cd jupyterlab-firefox-launcher

# Add the original repository as upstream
git remote add upstream https://github.com/vantagecompute/jupyterlab-firefox-launcher.git
```

### 2. Development Setup

```bash
# Install system dependencies (see Dependencies guide)
sudo apt install -y xvfb dbus-x11 xpra firefox  # Ubuntu/Debian

# Set up Python environment
uv venv dev-env
source dev-env/bin/activate
uv pip install -e ".[dev]"

# Set up frontend
jlpm install
jupyter labextension develop . --overwrite

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

### 3. Verify Setup

```bash
# Run tests to ensure everything works
pytest
jlpm test

# Start JupyterLab to test the extension
jupyter lab
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Make sure you're on the main branch and up to date
git checkout main
git pull upstream main

# Create a new feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number-description
```

### 2. Make Your Changes

Follow our development guidelines:

#### Code Style Guidelines

**Python Code:**
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://isort.readthedocs.io/) for import sorting
- Add type hints where appropriate
- Write descriptive docstrings

```python
def create_session_directory(port: int) -> Path:
    """Create an isolated session directory for Firefox instance.
    
    Args:
        port: Port number for the session
        
    Returns:
        Path to the created session directory
        
    Raises:
        OSError: If directory creation fails
    """
    # Implementation here
```

**TypeScript Code:**
- Follow JupyterLab coding standards
- Use explicit types where possible
- Use meaningful variable and function names
- Document complex logic with comments

```typescript
interface SessionConfig {
  port: number;
  quality: number;
  dpi: number;
}

/**
 * Create a new Firefox session with specified configuration
 */
async function createSession(config: SessionConfig): Promise<SessionInfo> {
  // Implementation here
}
```

**Commit Message Format:**
Use conventional commit format:
```
type(scope): description

- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: formatting changes
- refactor: code refactoring
- test: adding tests
- chore: maintenance tasks
```

Examples:
```
feat(frontend): add session timeout configuration
fix(handler): resolve memory leak in cleanup process
docs(readme): update installation instructions
test(handler): add unit tests for session management
```

### 3. Testing Your Changes

#### Run All Tests
```bash
# Python tests
pytest

# Python tests with coverage
pytest --cov=jupyterlab_firefox_launcher

# Frontend tests
jlpm test

# Integration tests
python tests/test_integration.py
```

#### Manual Testing
```bash
# Start JupyterLab and test functionality
jupyter lab

# Test with debug logging enabled
FIREFOX_LAUNCHER_DEBUG=1 jupyter lab

# Test multi-session scenarios
# Test cleanup functionality
# Test error handling
```

#### Code Quality Checks
```bash
# Format Python code
black jupyterlab_firefox_launcher/
isort jupyterlab_firefox_launcher/

# Type checking
mypy jupyterlab_firefox_launcher/

# Linting
flake8 jupyterlab_firefox_launcher/

# Frontend linting
jlpm run eslint
```

### 4. Update Documentation

If your changes affect user-facing functionality:

- Update relevant documentation pages
- Add or update code comments
- Update API documentation if needed
- Add examples if applicable

### 5. Commit and Push

```bash
# Add your changes
git add .

# Commit with descriptive message
git commit -m "feat(handler): implement session timeout handling"

# Push to your fork
git push origin feature/your-feature-name
```

## Pull Request Process

### 1. Create Pull Request

- Go to your fork on GitHub
- Click "New Pull Request"
- Select your feature branch
- Fill out the PR template with:
  - Clear description of changes
  - Related issue numbers
  - Testing instructions
  - Screenshots if applicable

### 2. PR Requirements

Your pull request should:

- ✅ **Pass all CI checks**: Tests, linting, type checking
- ✅ **Include tests**: New features should have corresponding tests
- ✅ **Update documentation**: User-facing changes need doc updates
- ✅ **Follow code style**: Use our formatting and style guidelines
- ✅ **Have descriptive commits**: Clear commit messages
- ✅ **Be focused**: One feature or fix per PR

### 3. Review Process

1. **Automated checks** run automatically (tests, linting, build)
2. **Maintainer review** - we'll review your code and provide feedback
3. **Address feedback** - make requested changes
4. **Final approval** - once approved, we'll merge your PR

### 4. After Merge

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Delete the feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

## Types of Contributions

### 🐛 Bug Reports

When reporting bugs, please include:

**Bug Report Template:**
```markdown
## Bug Description
Clear description of what's wrong

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Ubuntu 22.04
- Python: 3.11
- JupyterLab: 4.4.5
- Extension version: 0.1.0
- Browser: Chrome 120

## Additional Context
- Log messages
- Screenshots
- Related issues
```

### ✨ Feature Requests

For feature requests, please provide:

**Feature Request Template:**
```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other approaches you considered

## Additional Context
Mockups, examples, related features
```

### 🔧 Code Contributions

#### Areas for Contribution

**High Priority:**
- Performance improvements
- Bug fixes
- Security enhancements
- Accessibility improvements
- Linux distribution compatibility

**Medium Priority:**
- New features
- UI/UX improvements
- Configuration options
- Integration improvements

**Low Priority:**
- Code refactoring
- Documentation improvements
- Additional tests
- Example notebooks

#### Good First Issues

Look for issues labeled [`good first issue`](https://github.com/vantagecompute/jupyterlab-firefox-launcher/labels/good%20first%20issue) - these are specifically chosen for new contributors.

### 📚 Documentation Contributions

Documentation improvements are always welcome:

- **Fix typos and grammar**
- **Improve clarity and organization**
- **Add missing documentation**
- **Create tutorials and examples**
- **Update outdated information**

#### Documentation Guidelines

- Use clear, concise language
- Include code examples where helpful
- Test all instructions before submitting
- Follow the existing documentation structure
- Use proper Markdown formatting

### 🧪 Testing Contributions

Help improve test coverage:

- Write unit tests for untested code
- Add integration tests
- Test on different Linux distributions
- Performance testing
- Accessibility testing

#### Testing Guidelines

```python
# Example test structure
def test_feature_name():
    """Test description explaining what is being tested."""
    # Arrange - set up test data
    
    # Act - perform the action being tested
    
    # Assert - verify the results
    assert expected == actual
```

## Community Guidelines

### Code of Conduct

We follow a code of conduct to ensure a welcoming environment:

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome people of all backgrounds and identities
- **Be collaborative**: Work together constructively
- **Be patient**: Help others learn and grow
- **Be constructive**: Provide helpful feedback

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Request Reviews**: For code feedback
- **Email**: For private matters ([james@vantagecompute.ai](mailto:james@vantagecompute.ai))

### Getting Help

If you need help with contributing:

1. **Check the documentation**: Most questions are answered here
2. **Search existing issues**: Someone might have asked already
3. **Ask in discussions**: Use GitHub Discussions for questions
4. **Contact maintainers**: Email us for complex issues

## Recognition

We appreciate all contributions! Contributors are recognized in several ways:

- **Contributors list**: Your GitHub profile will be listed as a contributor
- **Changelog**: Significant contributions are mentioned in release notes
- **Special recognition**: Outstanding contributors may be invited as maintainers

## Release Process

Understanding our release process can help you time your contributions:

### Release Schedule

- **Major releases** (x.0.0): New features, breaking changes
- **Minor releases** (x.y.0): New features, improvements
- **Patch releases** (x.y.z): Bug fixes, security updates

### Contribution Timing

- **Feature freeze**: 2 weeks before major releases
- **Code freeze**: 1 week before any release
- **Documentation**: Can be updated anytime

## Advanced Contributing

### Becoming a Maintainer

Active contributors may be invited to become maintainers. Maintainers have additional responsibilities:

- **Code review**: Review and approve pull requests
- **Issue triage**: Label and prioritize issues
- **Release management**: Help with releases
- **Community management**: Help maintain project health

### Project Governance

The project follows a maintainer-driven governance model:

- **Lead maintainer**: Makes final decisions on direction and architecture
- **Core maintainers**: Review PRs, triage issues, make technical decisions
- **Contributors**: Submit PRs, report issues, participate in discussions

## Resources

### Development Resources

- **[Development Guide]({{ site.baseurl }}/development)**: Detailed development setup and workflows
- **[Architecture Documentation]({{ site.baseurl }}/architecture)**: Understanding the system design
- **[API Reference]({{ site.baseurl }}/api-reference)**: Detailed API documentation
- **[Dependencies]({{ site.baseurl }}/dependencies)**: Required dependencies and versions

### External Resources

- **[JupyterLab Extension Development](https://jupyterlab.readthedocs.io/en/stable/extension/extension_dev.html)**: Official JupyterLab docs
- **[Python Packaging](https://packaging.python.org/)**: Python packaging best practices
- **[TypeScript Handbook](https://www.typescriptlang.org/docs/)**: TypeScript documentation
- **[Git Workflow](https://guides.github.com/introduction/flow/)**: GitHub workflow guide

## Questions?

If you have questions about contributing, please:

1. Check this contributing guide
2. Look through [existing issues](https://github.com/vantagecompute/jupyterlab-firefox-launcher/issues)
3. Start a [discussion](https://github.com/vantagecompute/jupyterlab-firefox-launcher/discussions)
4. Contact maintainers at [james@vantagecompute.ai](mailto:james@vantagecompute.ai)

Thank you for your interest in contributing to JupyterLab Firefox Launcher! 🚀
