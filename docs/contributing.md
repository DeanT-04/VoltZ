# Contributing to VoltForge

Thank you for your interest in contributing to VoltForge! This guide will help you get started with contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors
- Report any unacceptable behavior to the maintainers

## Getting Started

### Prerequisites
- Python 3.13+
- Git
- Basic understanding of FastAPI, vector databases, and AI/ML concepts

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/voltforge.git`
3. Follow the [Development Guide](./development.md) for setup instructions

## How to Contribute

### Reporting Issues

#### Bug Reports
When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

**Bug Report Template:**
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Windows 11, Ubuntu 20.04]
- Python Version: [e.g., 3.13.1]
- VoltForge Version: [e.g., 1.0.0]

**Additional Context**
Any other context about the problem.
```

#### Feature Requests
For feature requests, please include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation approach (if any)
- Potential impact on existing functionality

### Contributing Code

#### Workflow
1. **Create an Issue**: Discuss your proposed changes first
2. **Fork & Branch**: Create a feature branch from `main`
3. **Develop**: Implement your changes following our guidelines
4. **Test**: Ensure all tests pass and add new tests
5. **Document**: Update documentation as needed
6. **Submit PR**: Create a pull request with clear description

#### Branch Naming
Use descriptive branch names:
- `feature/add-component-search`
- `bugfix/fix-embedding-generation`
- `docs/update-api-documentation`
- `refactor/improve-vector-db-performance`

#### Commit Messages
Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add component search endpoint

Add new endpoint for searching electronic components
with semantic similarity and filtering capabilities.

Closes #123
```

```
fix(vector-db): resolve memory leak in batch operations

Fixed issue where ChromaDB connections weren't properly
closed after batch operations, causing memory usage to
grow over time.

Fixes #456
```

### Code Standards

#### Python Style Guide
We follow PEP 8 with some modifications:
- Line length: 88 characters (Black default)
- Use type hints for all function parameters and return values
- Use docstrings for all public functions and classes

#### Code Formatting
We use automated formatting tools:
```bash
# Format code
black backend/src
isort backend/src

# Check formatting
black backend/src --check
isort backend/src --check-only
```

#### Type Checking
All code should pass type checking:
```bash
mypy backend/src
```

#### Linting
Code should pass linting checks:
```bash
flake8 backend/src
```

### Testing Requirements

#### Test Coverage
- All new code must have tests
- Maintain minimum 90% test coverage
- Include both unit and integration tests

#### Test Types Required
1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test service interactions
3. **API Tests**: Test HTTP endpoints
4. **Performance Tests**: For performance-critical code

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend/src --cov-report=html

# Run specific test categories
pytest -m "not performance"  # Skip slow tests
pytest -m integration        # Run integration tests only
```

### Documentation

#### Required Documentation
- **API Changes**: Update API documentation
- **New Features**: Add usage examples
- **Configuration**: Document new settings
- **Breaking Changes**: Update migration guide

#### Documentation Style
- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Keep documentation up-to-date with code changes

### Pull Request Guidelines

#### PR Description Template
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated existing tests as needed

## Documentation
- [ ] Updated relevant documentation
- [ ] Added docstrings to new functions/classes
- [ ] Updated API documentation if applicable

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] No new warnings introduced
```

#### Review Process
1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one maintainer review required
3. **Testing**: Manual testing for significant changes
4. **Documentation**: Verify documentation is updated

#### Review Criteria
- **Functionality**: Does the code work as intended?
- **Code Quality**: Is the code clean, readable, and maintainable?
- **Performance**: Are there any performance implications?
- **Security**: Are there any security concerns?
- **Testing**: Are tests comprehensive and meaningful?
- **Documentation**: Is documentation clear and complete?

## Development Guidelines

### Architecture Principles
1. **Modularity**: Keep services loosely coupled
2. **Testability**: Design for easy testing
3. **Performance**: Consider performance implications
4. **Scalability**: Design for growth
5. **Security**: Security-first approach

### API Design
- Follow RESTful principles
- Use consistent naming conventions
- Include proper error handling
- Validate all inputs
- Document all endpoints

### Database Design
- Use appropriate data types
- Consider query performance
- Implement proper indexing
- Handle migrations carefully

### Error Handling
- Use appropriate HTTP status codes
- Provide meaningful error messages
- Log errors appropriately
- Handle edge cases gracefully

## Community

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Requests**: Code review and collaboration

### Getting Help
- Check existing issues and documentation first
- Provide detailed information when asking questions
- Be patient and respectful in communications

### Recognition
Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- Project documentation

## Release Process

### Versioning
We follow Semantic Versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation
5. Create release notes
6. Tag release
7. Deploy to production

## Legal

### License
By contributing to VoltForge, you agree that your contributions will be licensed under the same license as the project.

### Copyright
- Retain copyright notices in existing files
- Add copyright notice to new files
- Don't include copyrighted material without permission

### Dependencies
- Only add dependencies with compatible licenses
- Document new dependencies and their licenses
- Keep dependencies up-to-date and secure

## Questions?

If you have questions about contributing:
1. Check this guide and other documentation
2. Search existing issues and discussions
3. Create a new issue with the "question" label
4. Reach out to maintainers if needed

Thank you for contributing to VoltForge! 🚀