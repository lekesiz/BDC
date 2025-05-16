# Client Tests

This directory contains all client-side tests for the BDC application.

## Structure

```
tests/
├── README.md
├── __mocks__/        # Mock implementations
├── accessibility/    # Accessibility tests
├── components/       # Component tests
│   ├── ui/          # UI component tests
│   └── ...          # Other component tests
├── hooks/           # Hook tests
├── pages/           # Page component tests
│   ├── auth/        # Auth page tests
│   ├── beneficiaries/ # Beneficiaries page tests
│   └── ...          # Other page tests
├── services/        # Service tests
└── setup.js         # Test setup file
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- Button.test.jsx
```

## Test Categories

### Unit Tests
- Component tests (`components/`)
- Hook tests (`hooks/`)
- Service tests (`services/`)

### Integration Tests
- Page tests (`pages/`)

### Accessibility Tests
- A11y tests (`accessibility/`)

## Writing Tests

1. Create test file with `.test.jsx` or `.test.js` extension
2. Use descriptive test names
3. Follow AAA pattern (Arrange, Act, Assert)
4. Mock external dependencies
5. Test both success and error cases

Example:
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import Button from '@/components/ui/button';

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalled();
  });
});
```