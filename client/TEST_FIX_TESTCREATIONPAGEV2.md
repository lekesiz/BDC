# TestCreationPageV2 Test Fix Documentation

## Overview

The TestCreationPageV2 component test had several issues that needed to be addressed:

1. Import path errors - The test was using incorrect paths with '@/lib/api' and '@/hooks/useToast' aliases that weren't properly resolved
2. Improper mocking of external dependencies - The useToast hook and DragDropContext were not mocked correctly
3. Missing test cases for essential functionality, such as file uploads and template application
4. Incomplete API response mocking - API responses for various endpoints needed to be mocked properly

## Issues Found

1. **Import Path Errors**: The test was using module path aliases (`@/lib/api` and `@/hooks/useToast`) that weren't properly configured in the test environment, causing import failures.

2. **Incomplete useToast Mock**: The toast functionality wasn't properly mocked, causing errors when attempting to display toast notifications.

3. **DragDropContext Mock**: The DragDropContext from `@hello-pangea/dnd` wasn't correctly mocked, causing rendering issues for the drag-and-drop functionality.

4. **Insufficient API Mocking**: The test lacked proper mocks for various API endpoints used by the component, including categories, templates, and AI suggestions.

5. **Missing Test Cases**: Several key features weren't being tested, including language switching, applying templates, and file uploads.

## Solution Approach

### 1. Fixed Import Paths

Updated import statements to use relative paths instead of aliases:

```javascript
// Before
import axios from '@/lib/api';
import { useToast } from '@/hooks/useToast';

// After
import axios from '../../../lib/api';
import * as useToastModule from '../../../hooks/useToast';
```

### 2. Implemented Proper useToast Mocking

Created a comprehensive mock for the useToast hook that handles all toast functionality:

```javascript
// Before (incomplete or missing)
vi.mock('@/hooks/useToast');

// After
vi.mock('../../../hooks/useToast', () => ({
  useToast: vi.fn().mockReturnValue({
    toast: vi.fn()
  }),
  toast: vi.fn(),
  __esModule: true,
  default: { toast: vi.fn() }
}));
```

### 3. Added DragDropContext Mock

Implemented a complete mock for the drag-and-drop library:

```javascript
vi.mock('@hello-pangea/dnd', () => ({
  DragDropContext: ({ children, onDragEnd }) => {
    return <div data-testid="drag-drop-context">{children}</div>;
  },
  Droppable: ({ children }) => children({ droppableProps: {}, innerRef: vi.fn() }),
  Draggable: ({ children }) => children({ innerRef: vi.fn(), draggableProps: {}, dragHandleProps: {} }, { isDragging: false }),
}));
```

### 4. Enhanced API Response Mocking

Created detailed mock data for all API endpoints used by the component:

```javascript
// Mock API responses
axios.get.mockImplementation((url) => {
  if (url.includes('/categories')) {
    return Promise.resolve({ data: mockCategories });
  }
  if (url.includes('/templates')) {
    return Promise.resolve({ data: mockTemplates });
  }
  if (url.includes('/bank')) {
    return Promise.resolve({ data: mockQuestionBank });
  }
  return Promise.reject(new Error('Unknown URL'));
});

axios.post.mockImplementation((url) => {
  if (url.includes('/ai/suggestions')) {
    return Promise.resolve({ data: mockAiSuggestions });
  }
  if (url.includes('/evaluations')) {
    return Promise.resolve({ data: { id: 'new-test-id' } });
  }
  if (url.includes('/upload')) {
    return Promise.resolve({ data: { url: 'https://example.com/uploaded-file.jpg' } });
  }
  return Promise.reject(new Error('Unknown URL'));
});
```

### 5. Added Missing Test Cases

Developed comprehensive test cases for previously untested functionality:

- Language switching (English/Turkish)
- Template application
- AI suggestion generation
- File uploads for questions
- Form validation
- Edit mode functionality
- Preview mode

## Key Learnings

1. **Use Consistent Import Strategies**: Avoid mixing module path aliases and relative imports. If using aliases, ensure they're properly configured in the test environment.

2. **Mock External Dependencies Completely**: When mocking hooks and external libraries, ensure all functions and properties are properly mocked, including those that may be rarely used but still present in the code.

3. **Create Realistic Test Data**: Mock data should closely resemble actual API responses, including nested objects and localized content, to properly test all rendering paths.

4. **Test All Major Functionality**: Identify all major features of a component and ensure they have corresponding test cases, especially complex interactions like drag-and-drop, file uploads, and form submissions.

5. **Isolate Test Environments**: Each test should start with a clean environment, with all mocks cleared to prevent cross-test contamination.

## Conclusion

The TestCreationPageV2 component tests were fixed by addressing import path issues, implementing proper mocking for external dependencies, and adding comprehensive test coverage for all major features. The tests now provide adequate coverage of both the component's rendering and its functionality, including complex interactions like file uploads, AI suggestions, and form validation.

This approach can be applied to other complex component tests: identify all external dependencies, create realistic mock data, and develop test cases for all major user flows and interactions within the component.