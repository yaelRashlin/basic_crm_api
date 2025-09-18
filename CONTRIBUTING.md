# Contributing to User Management Flask Server

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## 🚀 Getting Started

### Prerequisites
- Python 3.13 or higher
- Docker (optional, for containerized development)
- Git

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/yourusername/user-management-flask-server.git
   cd user-management-flask-server
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   python scripts/init_database.py --init
   ```

5. **Run tests to ensure everything works:**
   ```bash
   python scripts/run_tests.py
   ```

## 🔄 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Write clean, readable code
- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes
```bash
# Run all tests
python scripts/run_tests.py

# Run specific test modules
python -m unittest tests.test_your_module -v

# Test with pytest
pytest tests/ -v

# Test Docker functionality
python scripts/test_docker.py
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: add your feature description"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 📝 Code Style Guidelines

### Python Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Example Function:
```python
def validate_israeli_id(id_number: str) -> tuple[bool, str | None]:
    """
    Validate Israeli ID using official checksum algorithm.
    
    Args:
        id_number: The Israeli ID number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Implementation here
    pass
```

### Commit Message Format
Use conventional commit format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or modifications
- `refactor:` - Code refactoring
- `style:` - Code style changes
- `chore:` - Maintenance tasks

Examples:
```
feat: add user update endpoint
fix: resolve Israeli ID validation edge case
docs: update API documentation
test: add integration tests for user creation
```

## 🧪 Testing Guidelines

### Test Requirements
- All new features must include tests
- Maintain or improve test coverage
- Tests should be clear and well-documented
- Use descriptive test names

### Test Structure
```python
def test_feature_description(self):
    """Test that feature works correctly under normal conditions."""
    # Arrange
    test_data = {...}
    
    # Act
    result = function_under_test(test_data)
    
    # Assert
    self.assertEqual(result, expected_value)
```

### Running Tests
```bash
# All tests
python scripts/run_tests.py

# Specific test file
python -m unittest tests.test_validators -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

## 📚 Documentation Guidelines

### Code Documentation
- Add docstrings to all public functions and classes
- Use clear, concise language
- Include parameter types and return values
- Provide usage examples for complex functions

### README Updates
- Update README.md if you add new features
- Include usage examples
- Update the project structure if you add new directories

### API Documentation
- Document new endpoints in README.md
- Include request/response examples
- Specify required parameters and validation rules

## 🐳 Docker Development

### Development with Docker
```bash
# Start development environment
docker-compose -f docker/docker-compose.dev.yml up

# Run tests in container
docker-compose -f docker/docker-compose.dev.yml exec flask-server-dev python scripts/run_tests.py
```

### Docker Guidelines
- Test both development and production Docker configurations
- Ensure Docker builds are optimized
- Update Docker documentation if you change configurations

## 🔍 Code Review Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Docker builds successfully
- [ ] No sensitive information in commits

### Pull Request Requirements
- Clear description of changes
- Reference related issues
- Include screenshots for UI changes
- List any breaking changes

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues
2. Reproduce the bug
3. Test with latest version

### Bug Report Template
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Environment**
- OS: [e.g., Windows 10, macOS, Ubuntu]
- Python version: [e.g., 3.13.0]
- Docker version: [if applicable]

**Additional Context**
Any other relevant information.
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Feature Description**
A clear description of the feature.

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Any other relevant information.
```

## 📋 Project Areas for Contribution

### High Priority
- [ ] Additional validation rules
- [ ] Performance optimizations
- [ ] Enhanced error handling
- [ ] More comprehensive tests

### Medium Priority
- [ ] Additional database backends
- [ ] Caching layer
- [ ] Metrics and monitoring
- [ ] API versioning

### Low Priority
- [ ] Web UI for administration
- [ ] Bulk operations
- [ ] Import/export functionality
- [ ] Advanced logging

## 🤝 Community Guidelines

### Be Respectful
- Use welcoming and inclusive language
- Respect different viewpoints and experiences
- Accept constructive criticism gracefully

### Be Collaborative
- Help others learn and grow
- Share knowledge and resources
- Provide constructive feedback

### Be Professional
- Keep discussions focused and on-topic
- Avoid personal attacks or harassment
- Follow the project's code of conduct

## 📞 Getting Help

If you need help with contributing:

1. **Documentation**: Check the [docs/](docs/) directory
2. **Issues**: Search existing [GitHub issues](https://github.com/yourusername/user-management-flask-server/issues)
3. **Discussions**: Start a [GitHub discussion](https://github.com/yourusername/user-management-flask-server/discussions)

## 🎉 Recognition

Contributors will be recognized in:
- README.md acknowledgments
- Release notes
- GitHub contributors list

Thank you for contributing to User Management Flask Server! 🚀