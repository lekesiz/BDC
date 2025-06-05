import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { useForm, useFieldArray } from 'react-hook-form';
import { QUESTION_TYPES } from '@/lib/constants';
import QuestionEditor from '@/components/evaluation/QuestionEditor';
// Mock react-hook-form
vi.mock('react-hook-form', () => ({
  useFieldArray: vi.fn().mockReturnValue({
    fields: [],
    append: vi.fn(),
    remove: vi.fn(),
  }),
}));
// Test component that wraps QuestionEditor with react-hook-form
const TestComponent = ({ defaultValues, questionType }) => {
  const { register, control, formState, watch, setValue, trigger } = useForm({
    defaultValues,
  });
  return (
    <QuestionEditor
      register={register}
      control={control}
      index={0}
      errors={formState.errors}
      watch={watch}
      setValue={setValue}
      trigger={trigger}
    />
  );
};
describe('QuestionEditor', () => {
  const mockRegister = vi.fn().mockReturnValue({});
  const mockWatch = vi.fn();
  const mockSetValue = vi.fn();
  const mockTrigger = vi.fn();
  const mockAppend = vi.fn();
  const mockRemove = vi.fn();
  beforeEach(() => {
    vi.clearAllMocks();
    // Setup mock for useFieldArray
    useFieldArray.mockImplementation(({ name }) => {
      if (name === 'questions.0.options') {
        return {
          fields: [
            { id: 'option1', text: 'Option 1', is_correct: false },
            { id: 'option2', text: 'Option 2', is_correct: false },
          ],
          append: mockAppend,
          remove: mockRemove,
        };
      }
      if (name === 'questions.0.matches') {
        return {
          fields: [
            { id: 'match1', left: 'Left 1', right: 'Right 1' },
            { id: 'match2', left: 'Left 2', right: 'Right 2' },
          ],
          append: mockAppend,
          remove: mockRemove,
        };
      }
      if (name === 'questions.0.order_items') {
        return {
          fields: [
            { id: 'item1', text: 'Item 1', position: 0 },
            { id: 'item2', text: 'Item 2', position: 1 },
          ],
          append: mockAppend,
          remove: mockRemove,
        };
      }
      return {
        fields: [],
        append: mockAppend,
        remove: mockRemove,
      };
    });
    // Setup mock for watch function
    mockWatch.mockImplementation((path) => {
      if (path === 'questions.0.question_type') {
        return QUESTION_TYPES.MULTIPLE_CHOICE;
      }
      if (path.includes('is_correct')) {
        return false;
      }
      return '';
    });
  });
  it('renders with multiple choice question type correctly', () => {
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Check for multiple choice specific elements
    expect(screen.getByText('Options*')).toBeInTheDocument();
    expect(screen.getByText('Add Option')).toBeInTheDocument();
  });
  it('handles adding a new multiple choice option', () => {
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Click add option button
    fireEvent.click(screen.getByText('Add Option'));
    // Should call append function
    expect(mockAppend).toHaveBeenCalledWith({ text: '', is_correct: false });
  });
  it('handles removing a multiple choice option', () => {
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Get remove buttons (should be two)
    const removeButtons = screen.getAllByRole('button', { name: /minus/i });
    // Click first remove button
    fireEvent.click(removeButtons[0]);
    // Should call remove function with index 0
    expect(mockRemove).toHaveBeenCalledWith(0);
  });
  it('handles setting a multiple choice option as correct', () => {
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Get radio buttons
    const radioButtons = screen.getAllByRole('radio');
    // Click first radio button
    fireEvent.click(radioButtons[0]);
    // Should call setValue with updated options array
    expect(mockSetValue).toHaveBeenCalledWith('questions.0.options', [
      { text: '', is_correct: true },
      { text: '', is_correct: false },
    ]);
  });
  it('renders text question type correctly when question type changes', () => {
    // Override watch for this test
    mockWatch.mockImplementation((path) => {
      if (path === 'questions.0.question_type') {
        return QUESTION_TYPES.TEXT;
      }
      return '';
    });
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Check for text question specific elements
    expect(screen.getByText('Correct Answer*')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter the expected answer')).toBeInTheDocument();
  });
  it('renders true/false question type correctly when question type changes', () => {
    // Override watch for this test
    mockWatch.mockImplementation((path) => {
      if (path === 'questions.0.question_type') {
        return QUESTION_TYPES.TRUE_FALSE;
      }
      if (path.includes('options.0.is_correct')) {
        return false;
      }
      if (path.includes('options.1.is_correct')) {
        return false;
      }
      return '';
    });
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Check for true/false question specific elements
    expect(screen.getByText('Correct Answer*')).toBeInTheDocument();
    expect(screen.getByText('True')).toBeInTheDocument();
    expect(screen.getByText('False')).toBeInTheDocument();
  });
  it('handles selecting true as correct answer for true/false question', () => {
    // Override watch for this test
    mockWatch.mockImplementation((path) => {
      if (path === 'questions.0.question_type') {
        return QUESTION_TYPES.TRUE_FALSE;
      }
      if (path.includes('options.0.is_correct')) {
        return false;
      }
      if (path.includes('options.1.is_correct')) {
        return false;
      }
      return '';
    });
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Get true radio button
    const trueRadio = screen.getAllByRole('radio')[0];
    // Click true radio button
    fireEvent.click(trueRadio);
    // Should call setValue twice to set true as correct and false as not correct
    expect(mockSetValue).toHaveBeenCalledWith('questions.0.options.0.is_correct', true);
    expect(mockSetValue).toHaveBeenCalledWith('questions.0.options.1.is_correct', false);
  });
  it('renders matching question type correctly when question type changes', () => {
    // Override watch for this test
    mockWatch.mockImplementation((path) => {
      if (path === 'questions.0.question_type') {
        return QUESTION_TYPES.MATCHING;
      }
      return '';
    });
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Check for matching question specific elements
    expect(screen.getByText('Matching Pairs*')).toBeInTheDocument();
    expect(screen.getByText('Add Pair')).toBeInTheDocument();
    expect(screen.getByText('Left Items')).toBeInTheDocument();
    expect(screen.getByText('Right Items')).toBeInTheDocument();
  });
  it('handles adding a new matching pair', () => {
    // Override watch for this test
    mockWatch.mockImplementation((path) => {
      if (path === 'questions.0.question_type') {
        return QUESTION_TYPES.MATCHING;
      }
      return '';
    });
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Click add pair button
    fireEvent.click(screen.getByText('Add Pair'));
    // Should call append function with empty pair
    expect(mockAppend).toHaveBeenCalledWith({ left: '', right: '' });
  });
  it('renders ordering question type correctly when question type changes', () => {
    // Override watch for this test
    mockWatch.mockImplementation((path) => {
      if (path === 'questions.0.question_type') {
        return QUESTION_TYPES.ORDERING;
      }
      return '';
    });
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Check for ordering question specific elements
    expect(screen.getByText('Items to Order*')).toBeInTheDocument();
    expect(screen.getByText('Add Item')).toBeInTheDocument();
    expect(screen.getByText('Arrange items in the correct order. The order below will be the correct answer.')).toBeInTheDocument();
  });
  it('handles adding a new ordering item', () => {
    // Override watch for this test
    mockWatch.mockImplementation((path) => {
      if (path === 'questions.0.question_type') {
        return QUESTION_TYPES.ORDERING;
      }
      return '';
    });
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Click add item button
    fireEvent.click(screen.getByText('Add Item'));
    // Should call append function with new item
    expect(mockAppend).toHaveBeenCalledWith({ 
      text: '', 
      position: 2 // Since there are already 2 items
    });
  });
  it('handles moving an ordering item up', () => {
    // Override watch for this test
    mockWatch.mockImplementation((path) => {
      if (path === 'questions.0.question_type') {
        return QUESTION_TYPES.ORDERING;
      }
      return '';
    });
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Get up arrow buttons
    const upButtons = screen.getAllByRole('button', { name: /arrow-up/i });
    // Click second up button (first item can't go up)
    fireEvent.click(upButtons[1]);
    // Should call setValue with reordered items
    expect(mockSetValue).toHaveBeenCalledWith('questions.0.order_items', [
      { id: 'item2', text: 'Item 2', position: 0 },
      { id: 'item1', text: 'Item 1', position: 1 },
    ]);
  });
  it('handles moving an ordering item down', () => {
    // Override watch for this test
    mockWatch.mockImplementation((path) => {
      if (path === 'questions.0.question_type') {
        return QUESTION_TYPES.ORDERING;
      }
      return '';
    });
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Get down arrow buttons
    const downButtons = screen.getAllByRole('button', { name: /arrow-down/i });
    // Click first down button (last item can't go down)
    fireEvent.click(downButtons[0]);
    // Should call setValue with reordered items
    expect(mockSetValue).toHaveBeenCalledWith('questions.0.order_items', [
      { id: 'item2', text: 'Item 2', position: 0 },
      { id: 'item1', text: 'Item 1', position: 1 },
    ]);
  });
  it('updates form when question type changes', () => {
    // Setup effect
    const useEffectSpy = vi.spyOn(React, 'useEffect');
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={{}}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Should call useEffect
    expect(useEffectSpy).toHaveBeenCalled();
    // Should call trigger to validate form
    expect(mockTrigger).toHaveBeenCalledWith('questions.0');
  });
  it('shows validation errors when they exist', () => {
    const errors = {
      questions: [
        {
          question_text: { message: 'Question text is required' },
          options: [
            { text: { message: 'Option text is required' } }
          ]
        }
      ]
    };
    render(
      <QuestionEditor
        register={mockRegister}
        control={{}}
        index={0}
        errors={errors}
        watch={mockWatch}
        setValue={mockSetValue}
        trigger={mockTrigger}
      />
    );
    // Should show validation errors
    expect(screen.getByText('Question text is required')).toBeInTheDocument();
  });
});