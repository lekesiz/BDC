import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import {
  Form,
  FormGroup,
  FormLabel,
  FormControl,
  FormHelper,
  Checkbox,
  Radio,
  Select
} from '@/components/ui/form';

describe('Form Components', () => {
  describe('Form', () => {
    it('renders form with children', () => {
      render(
        <Form>
          <input type="text" />
          <button type="submit">Submit</button>
        </Form>
      );

      expect(screen.getByRole('textbox')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument();
    });

    it('handles form submission', async () => {
      const handleSubmit = vi.fn();
      const user = userEvent.setup();

      render(
        <Form onSubmit={handleSubmit}>
          <button type="submit">Submit</button>
        </Form>
      );

      await user.click(screen.getByRole('button', { name: 'Submit' }));
      
      expect(handleSubmit).toHaveBeenCalledTimes(1);
      expect(handleSubmit).toHaveBeenCalledWith(expect.any(Object));
    });

    it('prevents default form submission', async () => {
      const handleSubmit = vi.fn();
      const user = userEvent.setup();

      render(
        <Form onSubmit={handleSubmit}>
          <button type="submit">Submit</button>
        </Form>
      );

      const form = screen.getByRole('form');
      const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
      
      form.dispatchEvent(submitEvent);
      
      expect(submitEvent.defaultPrevented).toBe(true);
    });

    it('applies custom className', () => {
      const { container } = render(
        <Form className="custom-form">
          <input />
        </Form>
      );

      const form = container.querySelector('form');
      expect(form).toHaveClass('custom-form');
      expect(form).toHaveClass('space-y-4'); // default class
    });
  });

  describe('FormGroup', () => {
    it('renders children in a group', () => {
      render(
        <FormGroup>
          <FormLabel>Name</FormLabel>
          <input type="text" />
        </FormGroup>
      );

      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('applies spacing classes', () => {
      const { container } = render(
        <FormGroup>
          <input />
        </FormGroup>
      );

      const group = container.firstChild;
      expect(group).toHaveClass('space-y-2');
    });
  });

  describe('FormLabel', () => {
    it('renders label with text', () => {
      render(<FormLabel htmlFor="test-input">Test Label</FormLabel>);
      
      const label = screen.getByText('Test Label');
      expect(label).toBeInTheDocument();
      expect(label).toHaveAttribute('for', 'test-input');
    });

    it('shows required indicator when required', () => {
      render(<FormLabel required>Required Field</FormLabel>);
      
      expect(screen.getByText('*')).toBeInTheDocument();
      expect(screen.getByText('*')).toHaveClass('text-red-500');
    });

    it('does not show required indicator when not required', () => {
      render(<FormLabel>Optional Field</FormLabel>);
      
      expect(screen.queryByText('*')).not.toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(<FormLabel className="custom-label">Label</FormLabel>);
      
      const label = screen.getByText('Label');
      expect(label).toHaveClass('custom-label');
      expect(label).toHaveClass('block'); // default class
    });
  });

  describe('FormControl', () => {
    it('passes props to child element', () => {
      render(
        <FormControl id="test" name="test-input" invalid={false}>
          <input type="text" />
        </FormControl>
      );

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('id', 'test');
      expect(input).toHaveAttribute('name', 'test-input');
      expect(input).toHaveAttribute('aria-invalid', 'false');
    });

    it('applies error styles when invalid', () => {
      render(
        <FormControl invalid>
          <input type="text" />
        </FormControl>
      );

      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('border-red-500');
      expect(input).toHaveAttribute('aria-invalid', 'true');
    });
  });

  describe('FormHelper', () => {
    it('renders helper text', () => {
      render(<FormHelper>This is help text</FormHelper>);
      
      expect(screen.getByText('This is help text')).toBeInTheDocument();
    });

    it('renders with correct id when provided', () => {
      render(<FormHelper id="input">Help text</FormHelper>);
      
      const helper = screen.getByText('Help text');
      expect(helper).toHaveAttribute('id', 'input-helper');
    });

    it('applies error styles when error prop is true', () => {
      render(<FormHelper error>Error message</FormHelper>);
      
      const helper = screen.getByText('Error message');
      expect(helper).toHaveClass('text-red-600');
    });

    it('applies normal styles when error prop is false', () => {
      render(<FormHelper>Help text</FormHelper>);
      
      const helper = screen.getByText('Help text');
      expect(helper).toHaveClass('text-gray-500');
    });
  });

  describe('Checkbox', () => {
    it('renders checkbox with label', () => {
      render(
        <Checkbox
          id="terms"
          name="terms"
          label="I agree to terms"
          checked={false}
          onChange={() => {}}
        />
      );

      expect(screen.getByRole('checkbox')).toBeInTheDocument();
      expect(screen.getByLabelText('I agree to terms')).toBeInTheDocument();
    });

    it('handles checked state', () => {
      const { rerender } = render(
        <Checkbox
          id="terms"
          name="terms"
          checked={false}
          onChange={() => {}}
        />
      );

      expect(screen.getByRole('checkbox')).not.toBeChecked();

      rerender(
        <Checkbox
          id="terms"
          name="terms"
          checked={true}
          onChange={() => {}}
        />
      );

      expect(screen.getByRole('checkbox')).toBeChecked();
    });

    it('calls onChange when clicked', async () => {
      const handleChange = vi.fn();
      const user = userEvent.setup();

      render(
        <Checkbox
          id="terms"
          name="terms"
          label="Terms"
          checked={false}
          onChange={handleChange}
        />
      );

      await user.click(screen.getByRole('checkbox'));
      expect(handleChange).toHaveBeenCalledTimes(1);
    });

    it('renders without label', () => {
      render(
        <Checkbox
          id="terms"
          name="terms"
          checked={false}
          onChange={() => {}}
        />
      );

      expect(screen.getByRole('checkbox')).toBeInTheDocument();
      expect(screen.queryByRole('label')).not.toBeInTheDocument();
    });
  });

  describe('Radio', () => {
    it('renders radio button with label', () => {
      render(
        <Radio
          id="option1"
          name="options"
          label="Option 1"
          checked={false}
          onChange={() => {}}
        />
      );

      expect(screen.getByRole('radio')).toBeInTheDocument();
      expect(screen.getByLabelText('Option 1')).toBeInTheDocument();
    });

    it('handles checked state', () => {
      const { rerender } = render(
        <Radio
          id="option1"
          name="options"
          checked={false}
          onChange={() => {}}
        />
      );

      expect(screen.getByRole('radio')).not.toBeChecked();

      rerender(
        <Radio
          id="option1"
          name="options"
          checked={true}
          onChange={() => {}}
        />
      );

      expect(screen.getByRole('radio')).toBeChecked();
    });

    it('calls onChange when clicked', async () => {
      const handleChange = vi.fn();
      const user = userEvent.setup();

      render(
        <Radio
          id="option1"
          name="options"
          label="Option 1"
          checked={false}
          onChange={handleChange}
        />
      );

      await user.click(screen.getByRole('radio'));
      expect(handleChange).toHaveBeenCalledTimes(1);
    });
  });

  describe('Select', () => {
    const options = [
      { value: 'apple', label: 'Apple' },
      { value: 'banana', label: 'Banana' },
      { value: 'orange', label: 'Orange' }
    ];

    it('renders select with options', () => {
      render(
        <Select
          id="fruit"
          name="fruit"
          options={options}
          onChange={() => {}}
        />
      );

      const select = screen.getByRole('combobox');
      expect(select).toBeInTheDocument();
      expect(screen.getByText('Apple')).toBeInTheDocument();
      expect(screen.getByText('Banana')).toBeInTheDocument();
      expect(screen.getByText('Orange')).toBeInTheDocument();
    });

    it('renders with placeholder', () => {
      render(
        <Select
          id="fruit"
          name="fruit"
          options={options}
          placeholder="Choose a fruit"
          onChange={() => {}}
        />
      );

      expect(screen.getByText('Choose a fruit')).toBeInTheDocument();
    });

    it('calls onChange when selection changes', async () => {
      const handleChange = vi.fn();
      const user = userEvent.setup();

      render(
        <Select
          id="fruit"
          name="fruit"
          options={options}
          onChange={handleChange}
        />
      );

      const select = screen.getByRole('combobox');
      await user.selectOptions(select, 'banana');

      expect(handleChange).toHaveBeenCalledTimes(1);
      expect(handleChange).toHaveBeenCalledWith(expect.any(Object));
    });

    it('renders with default placeholder when none provided', () => {
      render(
        <Select
          id="fruit"
          name="fruit"
          options={options}
          onChange={() => {}}
        />
      );

      expect(screen.getByText('Select an option')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <Select
          id="fruit"
          name="fruit"
          options={options}
          className="custom-select"
          onChange={() => {}}
        />
      );

      const select = screen.getByRole('combobox');
      expect(select).toHaveClass('custom-select');
      expect(select).toHaveClass('block'); // default class
    });
  });
});