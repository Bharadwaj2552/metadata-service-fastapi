# Contributing Guidelines

Thank you for your interest in contributing to the Metadata Service! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and professional
- Welcome diverse perspectives
- Provide constructive feedback
- Report issues responsibly

## Getting Started

### 1. Setup Development Environment

```bash
# Clone repository
git clone <repo-url>
cd metadata-service

# Setup environment
cp .env.example .env
poetry install

# Setup pre-commit hooks
pre-commit install
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/issue-description
```

## Development Workflow

### Code Quality Requirements

Before submitting a PR, ensure:

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make type-check

# Run tests
make test

# All checks
make quality
```

### Writing Tests

- Add tests for new features in `tests/`
- Aim for >80% code coverage
- Use descriptive test names
- Follow existing test patterns

Example:
```python
def test_create_dataset_success():
    """Should create dataset with valid data"""
    # Arrange
    dataset_data = {...}
    
    # Act
    response = create_dataset(dataset_data)
    
    # Assert
    assert response.status_code == 201
```

### Commit Messages

Follow conventional commits format:

```
type(scope): description

- feat: new feature
- fix: bug fix
- docs: documentation
- refactor: code refactoring
- test: adding tests
- chore: maintenance

Examples:
- feat(search): add full-text search support
- fix(lineage): prevent cycle on parallel paths
- docs(readme): add quickstart guide
```

## Adding New Features

### 1. Propose the Feature

Create an issue describing:
- Problem being solved
- Proposed solution
- Alternative approaches

### 2. Implement Feature

Follow the architecture:
- **Models**: Define data structure in `app/models/`
- **Schemas**: Add Pydantic validation in `app/schemas/`
- **Repository**: Add database operations in `app/repository/`
- **Service**: Add business logic in `app/services/`
- **Routes**: Add API endpoints in `app/api/`

### 3. Database Changes

For schema changes:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Review migration file
# Verify it's correct

# Test locally
alembic upgrade head
alembic downgrade -1
```

### 4. Documentation

- Add docstrings to functions
- Update README if behavior changes
- Add examples in EXAMPLES.md
- Include type hints

```python
def search_datasets(db: Session, query: str) -> SearchResponse:
    """
    Search for datasets by various criteria.
    
    Args:
        db: Database session
        query: Search query string
        
    Returns:
        SearchResponse with prioritized results
        
    Raises:
        ValueError: If query is empty
    """
```

## Submitting Changes

### Git Workflow

```bash
# Make changes
git add .

# Commit with conventional format
git commit -m "feat(scope): description"

# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change

## Related Issues
Closes #issue-number

## Testing Done
- [ ] Unit tests added/updated
- [ ] Integration tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Code Review Process

1. **Automated Checks**
   - Tests must pass
   - Coverage should not decrease
   - Code must pass linters

2. **Manual Review**
   - At least one approval required
   - Architecture review
   - Performance considerations
   - Security review

3. **Ready to Merge**
   - All checks pass
   - Approved by maintainers
   - Conflicts resolved

## Reporting Issues

### Bug Reports

Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Error logs/screenshots

### Feature Requests

Include:
- Use case
- Benefits
- Alternative solutions considered
- Examples

### Template

```markdown
## Description
Clear description of issue

## Steps to Reproduce
1. ...
2. ...
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: 
- Python: 
- Docker: 
```

## Documentation Improvements

Help by:
- Fixing typos
- Clarifying confusing sections
- Adding examples
- Improving code comments
- Creating tutorials

## Testing

### Local Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app

# Run specific test
pytest tests/test_api.py::TestDatasetEndpoints -v
```

### Docker Testing

```bash
# Build and test in container
docker-compose build
docker-compose up -d
docker-compose exec api pytest tests/ -v
```

## Performance Optimization

When improving performance:
- Add benchmarks if relevant
- Include before/after metrics
- Document trade-offs
- Update architecture docs

## Security

For security issues:
- Do NOT create public issues
- Email security@example.com
- Include reproduction steps
- Allow time for patch

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

## Getting Help

- Review existing issues
- Check discussions
- Read documentation
- Contact: maintainers@example.com

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

---

Thank you for contributing! 🎉
