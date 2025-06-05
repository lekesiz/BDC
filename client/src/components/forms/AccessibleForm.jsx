import React, { useRef, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { announceToScreenReader } from '@/utils/accessibility';
/**
 * Accessible form component with proper ARIA attributes and keyboard navigation
 * This serves as an example for creating accessible forms
 */
const AccessibleForm = ({ 
  onSubmit, 
  initialValues = {},
  isLoading = false,
  formTitle = "Form",
  submitButtonText = "Submit",
  cancelButtonText = "Cancel",
  onCancel
}) => {
  const formRef = useRef(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isSubmitted },
    setFocus,
    reset
  } = useForm({
    defaultValues: initialValues
  });
  // Focus first error field
  useEffect(() => {
    const firstError = Object.keys(errors)[0];
    if (firstError) {
      setFocus(firstError);
      // Announce error to screen readers
      announceToScreenReader(`Error in ${firstError} field`, 'assertive');
    }
  }, [errors, setFocus]);
  // Announce form submission status
  useEffect(() => {
    if (isSubmitted && !isSubmitting) {
      if (Object.keys(errors).length === 0) {
        announceToScreenReader('Form submitted successfully', 'polite');
      } else {
        announceToScreenReader(`Form has ${Object.keys(errors).length} errors`, 'assertive');
      }
    }
  }, [isSubmitted, isSubmitting, errors]);
  const onSubmitHandler = async (data) => {
    try {
      await onSubmit(data);
      reset();
      announceToScreenReader('Form submitted successfully', 'polite');
    } catch (error) {
      announceToScreenReader('Form submission failed. Please try again.', 'assertive');
    }
  };
  return (
    <form
      ref={formRef}
      onSubmit={handleSubmit(onSubmitHandler)}
      className="space-y-6"
      noValidate
      aria-label={formTitle}
    >
      <fieldset className="space-y-4">
        <legend className="text-lg font-semibold text-gray-900 mb-4">
          {formTitle}
        </legend>
        {/* Name field */}
        <div>
          <Input
            {...register('name', {
              required: 'Name is required',
              minLength: {
                value: 2,
                message: 'Name must be at least 2 characters'
              }
            })}
            label="Name"
            type="text"
            error={errors.name?.message}
            required
            autoComplete="name"
            placeholder="Enter your name"
            helpText="Please enter your full name"
          />
        </div>
        {/* Email field */}
        <div>
          <Input
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address'
              }
            })}
            label="Email"
            type="email"
            error={errors.email?.message}
            required
            autoComplete="email"
            placeholder="Enter your email"
            helpText="We'll never share your email"
          />
        </div>
        {/* Phone field */}
        <div>
          <Input
            {...register('phone', {
              pattern: {
                value: /^[\d\s\-\+\(\)]+$/,
                message: 'Invalid phone number'
              }
            })}
            label="Phone (optional)"
            type="tel"
            error={errors.phone?.message}
            autoComplete="tel"
            placeholder="Enter your phone number"
          />
        </div>
        {/* Message field */}
        <div>
          <label 
            htmlFor="message" 
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Message
            <span className="text-red-500 ml-1" aria-label="required">*</span>
          </label>
          <textarea
            {...register('message', {
              required: 'Message is required',
              minLength: {
                value: 10,
                message: 'Message must be at least 10 characters'
              }
            })}
            id="message"
            rows={4}
            className={`
              w-full px-3 py-2 border rounded-md text-sm
              focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
              ${errors.message ? 'border-red-500' : 'border-gray-300'}
            `}
            placeholder="Enter your message"
            aria-invalid={errors.message ? 'true' : 'false'}
            aria-describedby={errors.message ? 'message-error' : 'message-help'}
            aria-required="true"
          />
          {!errors.message && (
            <p id="message-help" className="text-sm text-gray-500 mt-1">
              Please provide details about your inquiry
            </p>
          )}
          {errors.message && (
            <p id="message-error" className="text-sm text-red-500 mt-1" role="alert">
              {errors.message.message}
            </p>
          )}
        </div>
      </fieldset>
      {/* Form actions */}
      <div className="flex justify-end space-x-3 pt-4">
        {onCancel && (
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            {cancelButtonText}
          </Button>
        )}
        <Button
          type="submit"
          isLoading={isSubmitting || isLoading}
          disabled={isSubmitting || isLoading}
          loadingText="Submitting..."
        >
          {submitButtonText}
        </Button>
      </div>
      {/* Screen reader only live region for form status */}
      <div 
        className="sr-only" 
        role="status" 
        aria-live="polite" 
        aria-atomic="true"
      >
        {isSubmitting && 'Form is being submitted'}
        {isSubmitted && !isSubmitting && Object.keys(errors).length === 0 && 'Form submitted successfully'}
        {isSubmitted && !isSubmitting && Object.keys(errors).length > 0 && `Form has ${Object.keys(errors).length} errors`}
      </div>
    </form>
  );
};
export default AccessibleForm;