# Contributing to BDC (Beneficiary Development Center)

We welcome contributions to the BDC project! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** and clone your fork
   ```bash
   git clone https://github.com/your-username/BDC.git
   cd BDC
   ```

2. **Set up the development environment**
   ```bash
   # Install dependencies
   npm install
   cd server && pip install -r requirements.txt
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Process

1. **Check existing issues** before starting new work
2. **Create an issue** for bugs or feature requests if one doesn't exist
3. **Assign yourself** to the issue you're working on
4. **Keep your fork up to date** with the main repository
   ```bash
   git remote add upstream https://github.com/original/BDC.git
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

## Code Style Guidelines

### JavaScript/React (Frontend)
- Use ESLint configuration provided
- Follow React best practices
- Use functional components and hooks
- Implement proper error boundaries
- Use TypeScript for new components when possible

```javascript
// Good
const UserCard = ({ user }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  return (
    <div className="user-card">
      {user.name}
    </div>
  );
};

// Bad
class UserCard extends React.Component {
  render() {
    return <div>{this.props.user.name}</div>
  }
}
```

### Python (Backend)
- Follow PEP 8 guidelines
- Use type hints for function parameters
- Implement proper error handling
- Write docstrings for all functions

```python
# Good
def get_user_by_id(user_id: int) -> dict:
    """
    Retrieve user information by ID.
    
    Args:
        user_id: The ID of the user to retrieve
        
    Returns:
        dict: User information
        
    Raises:
        UserNotFoundError: If user doesn't exist
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user.to_dict()
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise
```

### CSS/Tailwind
- Use Tailwind utility classes
- Follow mobile-first design
- Maintain consistent spacing and colors
- Use CSS modules for component-specific styles

## Commit Guidelines

We follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

### Examples:
```bash
feat(auth): add password reset functionality
fix(dashboard): resolve loading state bug
docs(api): update endpoint documentation
test(users): add unit tests for user service
```

## Pull Request Process

1. **Ensure all tests pass**
   ```bash
   npm test
   cd server && python -m pytest
   ```

2. **Update documentation** if needed

3. **Create a pull request** with a clear title and description
   - Reference the issue number
   - Include screenshots for UI changes
   - List any breaking changes

4. **Pull Request Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed

   ## Screenshots (if applicable)
   
   ## Checklist
   - [ ] My code follows the project style guidelines
   - [ ] I have performed a self-review
   - [ ] I have commented my code where necessary
   - [ ] I have updated the documentation
   - [ ] My changes generate no new warnings
   - [ ] I have added tests for my changes
   - [ ] All tests pass locally
   ```

5. **Code Review**
   - At least one maintainer must review
   - Address all feedback
   - Keep discussions professional

## Testing Guidelines

### Frontend Testing
- Write unit tests for utility functions
- Write component tests for React components
- Write integration tests for critical user flows

```javascript
// Example test
describe('UserCard', () => {
  it('should display user name', () => {
    const user = { name: 'John Doe' };
    render(<UserCard user={user} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

### Backend Testing
- Write unit tests for all services
- Write integration tests for API endpoints
- Use fixtures for database testing

```python
# Example test
def test_get_user_by_id(client, auth_headers):
    response = client.get('/api/users/1', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['name'] == 'Test User'
```

## Documentation

- Update README.md for significant changes
- Document all API endpoints
- Include JSDoc comments for JavaScript functions
- Include docstrings for Python functions
- Update user guides when adding features

## Issue Reporting

When reporting issues, please include:

1. **Bug Reports**:
   - Clear description of the bug
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots/error messages
   - Environment details

2. **Feature Requests**:
   - Clear description of the feature
   - Use case / problem it solves
   - Proposed implementation (optional)
   - Mockups/wireframes (if applicable)

## Questions or Need Help?

- Check the [documentation](./README.md)
- Search existing issues
- Create a new issue with the `question` label
- Contact maintainers via email

Thank you for contributing to BDC!