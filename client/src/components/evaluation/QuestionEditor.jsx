import { useEffect, useState } from 'react';
import { useFieldArray } from 'react-hook-form';
import { PlusCircle, Minus, ArrowUp, ArrowDown, GripVertical } from 'lucide-react';
import { QUESTION_TYPES } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { RichTextEditor } from '@/components/editor';
/**
 * Question Editor component for creating and editing test questions
 */
const QuestionEditor = ({ register, control, index, errors, watch, setValue, trigger }) => {
  const [questionContent, setQuestionContent] = useState(watch(`questions.${index}.question_text`) || '');
  // Get the question type for this index
  const questionType = watch(`questions.${index}.question_type`);
  // Field arrays for different question types
  const optionsArray = useFieldArray({
    control,
    name: `questions.${index}.options`,
  });
  const matchesArray = useFieldArray({
    control,
    name: `questions.${index}.matches`,
  });
  const orderItemsArray = useFieldArray({
    control,
    name: `questions.${index}.order_items`,
  });
  // Update form when question type changes
  useEffect(() => {
    switch(questionType) {
      case QUESTION_TYPES.MULTIPLE_CHOICE:
        if (!watch(`questions.${index}.options`) || watch(`questions.${index}.options`).length < 2) {
          setValue(`questions.${index}.options`, [
            { text: '', is_correct: false },
            { text: '', is_correct: false },
          ]);
        }
        setValue(`questions.${index}.matches`, undefined);
        setValue(`questions.${index}.order_items`, undefined);
        setValue(`questions.${index}.correct_answer`, undefined);
        break;
      case QUESTION_TYPES.TEXT:
        setValue(`questions.${index}.options`, undefined);
        setValue(`questions.${index}.matches`, undefined);
        setValue(`questions.${index}.order_items`, undefined);
        setValue(`questions.${index}.correct_answer`, watch(`questions.${index}.correct_answer`) || '');
        break;
      case QUESTION_TYPES.TRUE_FALSE:
        setValue(`questions.${index}.options`, [
          { text: 'True', is_correct: false },
          { text: 'False', is_correct: false },
        ]);
        setValue(`questions.${index}.matches`, undefined);
        setValue(`questions.${index}.order_items`, undefined);
        setValue(`questions.${index}.correct_answer`, undefined);
        break;
      case QUESTION_TYPES.MATCHING:
        if (!watch(`questions.${index}.matches`) || watch(`questions.${index}.matches`).length < 2) {
          setValue(`questions.${index}.matches`, [
            { left: '', right: '' },
            { left: '', right: '' },
          ]);
        }
        setValue(`questions.${index}.options`, undefined);
        setValue(`questions.${index}.order_items`, undefined);
        setValue(`questions.${index}.correct_answer`, undefined);
        break;
      case QUESTION_TYPES.ORDERING:
        if (!watch(`questions.${index}.order_items`) || watch(`questions.${index}.order_items`).length < 2) {
          setValue(`questions.${index}.order_items`, [
            { text: '', position: 0 },
            { text: '', position: 1 },
          ]);
        }
        setValue(`questions.${index}.options`, undefined);
        setValue(`questions.${index}.matches`, undefined);
        setValue(`questions.${index}.correct_answer`, undefined);
        break;
    }
    trigger(`questions.${index}`);
  }, [questionType, index, setValue, watch, trigger]);
  // Add a new multiple choice option
  const handleAddOption = () => {
    optionsArray.append({ text: '', is_correct: false });
  };
  // Remove a multiple choice option
  const handleRemoveOption = (optionIndex) => {
    if (optionsArray.fields.length > 2) {
      optionsArray.remove(optionIndex);
    }
  };
  // Set an option as correct (for multiple choice)
  const handleSetCorrectOption = (optionIndex) => {
    // Update all options to be incorrect
    const updatedOptions = optionsArray.fields.map((_, i) => ({
      text: watch(`questions.${index}.options.${i}.text`),
      is_correct: i === optionIndex,
    }));
    // Set all options at once to avoid multiple rerenders
    setValue(`questions.${index}.options`, updatedOptions);
  };
  // Add a new matching pair
  const handleAddMatch = () => {
    matchesArray.append({ left: '', right: '' });
  };
  // Remove a matching pair
  const handleRemoveMatch = (matchIndex) => {
    if (matchesArray.fields.length > 2) {
      matchesArray.remove(matchIndex);
    }
  };
  // Add a new ordering item
  const handleAddOrderItem = () => {
    orderItemsArray.append({ 
      text: '', 
      position: orderItemsArray.fields.length 
    });
  };
  // Remove an ordering item
  const handleRemoveOrderItem = (itemIndex) => {
    if (orderItemsArray.fields.length > 2) {
      const newItems = orderItemsArray.fields
        .filter((_, i) => i !== itemIndex)
        .map((item, i) => ({
          ...item,
          position: i
        }));
      setValue(`questions.${index}.order_items`, newItems);
    }
  };
  // Move an ordering item up
  const handleMoveItemUp = (itemIndex) => {
    if (itemIndex > 0) {
      const items = [...orderItemsArray.fields];
      [items[itemIndex - 1], items[itemIndex]] = [items[itemIndex], items[itemIndex - 1]];
      const newItems = items.map((item, i) => ({
        ...item,
        position: i
      }));
      setValue(`questions.${index}.order_items`, newItems);
    }
  };
  // Move an ordering item down
  const handleMoveItemDown = (itemIndex) => {
    if (itemIndex < orderItemsArray.fields.length - 1) {
      const items = [...orderItemsArray.fields];
      [items[itemIndex], items[itemIndex + 1]] = [items[itemIndex + 1], items[itemIndex]];
      const newItems = items.map((item, i) => ({
        ...item,
        position: i
      }));
      setValue(`questions.${index}.order_items`, newItems);
    }
  };
  return (
    <div className="space-y-4">
      {/* Question text and type */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <div className="md:col-span-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Question Text*
          </label>
          <RichTextEditor
            content={questionContent}
            onChange={({ html }) => {
              setQuestionContent(html);
              setValue(`questions.${index}.question_text`, html);
              trigger(`questions.${index}.question_text`);
            }}
            placeholder="Enter your question here..."
            minHeight="120px"
            maxHeight="400px"
            className="mb-2"
          />
          {errors.questions?.[index]?.question_text && (
            <p className="mt-1 text-sm text-red-600">{errors.questions[index].question_text.message}</p>
          )}
        </div>
        <div className="md:col-span-1">
          <label className="block text-sm font-medium text-gray-700">
            Question Type*
          </label>
          <select
            {...register(`questions.${index}.question_type`)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          >
            <option value={QUESTION_TYPES.MULTIPLE_CHOICE}>Multiple Choice</option>
            <option value={QUESTION_TYPES.TEXT}>Text Answer</option>
            <option value={QUESTION_TYPES.TRUE_FALSE}>True/False</option>
            <option value={QUESTION_TYPES.MATCHING}>Matching</option>
            <option value={QUESTION_TYPES.ORDERING}>Ordering</option>
          </select>
        </div>
        <div className="md:col-span-1">
          <label className="block text-sm font-medium text-gray-700">
            Points*
          </label>
          <Input
            type="number"
            min="1"
            {...register(`questions.${index}.points`, { valueAsNumber: true })}
            error={errors.questions?.[index]?.points?.message}
          />
        </div>
      </div>
      {/* Multiple choice options */}
      {questionType === QUESTION_TYPES.MULTIPLE_CHOICE && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-medium text-gray-700">
              Options*
            </label>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleAddOption}
              className="flex items-center text-xs"
            >
              <PlusCircle className="w-3 h-3 mr-1" />
              Add Option
            </Button>
          </div>
          {optionsArray.fields.map((field, optionIndex) => (
            <div key={field.id} className="flex items-center space-x-2">
              <input
                type="radio"
                id={`option-${index}-${optionIndex}`}
                name={`question-${index}-correct`}
                checked={watch(`questions.${index}.options.${optionIndex}.is_correct`)}
                onChange={() => handleSetCorrectOption(optionIndex)}
                className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
              />
              <Input
                {...register(`questions.${index}.options.${optionIndex}.text`)}
                placeholder={`Option ${optionIndex + 1}`}
                error={errors.questions?.[index]?.options?.[optionIndex]?.text?.message}
                className="flex-1"
              />
              {optionsArray.fields.length > 2 && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveOption(optionIndex)}
                  className="text-red-500 hover:text-red-700 p-1"
                >
                  <Minus className="w-4 h-4" />
                </Button>
              )}
            </div>
          ))}
          {errors.questions?.[index]?.options && (
            <p className="mt-1 text-sm text-red-600">{errors.questions[index].options.message}</p>
          )}
        </div>
      )}
      {/* Text answer */}
      {questionType === QUESTION_TYPES.TEXT && (
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Correct Answer*
          </label>
          <Input
            {...register(`questions.${index}.correct_answer`)}
            placeholder="Enter the expected answer"
            error={errors.questions?.[index]?.correct_answer?.message}
          />
          <p className="mt-1 text-sm text-gray-500">
            This will be used to automatically grade the question. Multiple correct answers can be separated by commas.
          </p>
        </div>
      )}
      {/* True/False answer */}
      {questionType === QUESTION_TYPES.TRUE_FALSE && (
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Correct Answer*
          </label>
          <div className="flex items-center space-x-4">
            <label className="inline-flex items-center">
              <input
                type="radio"
                name={`question-${index}-tf`}
                checked={watch(`questions.${index}.options.0.is_correct`)}
                onChange={() => {
                  setValue(`questions.${index}.options.0.is_correct`, true);
                  setValue(`questions.${index}.options.1.is_correct`, false);
                }}
                className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
              />
              <span className="ml-2">True</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="radio"
                name={`question-${index}-tf`}
                checked={watch(`questions.${index}.options.1.is_correct`)}
                onChange={() => {
                  setValue(`questions.${index}.options.0.is_correct`, false);
                  setValue(`questions.${index}.options.1.is_correct`, true);
                }}
                className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
              />
              <span className="ml-2">False</span>
            </label>
          </div>
        </div>
      )}
      {/* Matching pairs */}
      {questionType === QUESTION_TYPES.MATCHING && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-medium text-gray-700">
              Matching Pairs*
            </label>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleAddMatch}
              className="flex items-center text-xs"
            >
              <PlusCircle className="w-3 h-3 mr-1" />
              Add Pair
            </Button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="font-medium text-sm">Left Items</div>
            <div className="font-medium text-sm">Right Items</div>
          </div>
          {matchesArray.fields.map((field, matchIndex) => (
            <div key={field.id} className="grid grid-cols-2 gap-4 items-center">
              <Input
                {...register(`questions.${index}.matches.${matchIndex}.left`)}
                placeholder={`Left item ${matchIndex + 1}`}
                error={errors.questions?.[index]?.matches?.[matchIndex]?.left?.message}
              />
              <div className="flex items-center space-x-2">
                <Input
                  {...register(`questions.${index}.matches.${matchIndex}.right`)}
                  placeholder={`Right item ${matchIndex + 1}`}
                  error={errors.questions?.[index]?.matches?.[matchIndex]?.right?.message}
                  className="flex-1"
                />
                {matchesArray.fields.length > 2 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveMatch(matchIndex)}
                    className="text-red-500 hover:text-red-700 p-1"
                  >
                    <Minus className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      {/* Ordering items */}
      {questionType === QUESTION_TYPES.ORDERING && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-medium text-gray-700">
              Items to Order*
            </label>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleAddOrderItem}
              className="flex items-center text-xs"
            >
              <PlusCircle className="w-3 h-3 mr-1" />
              Add Item
            </Button>
          </div>
          <p className="text-xs text-gray-500">Arrange items in the correct order. The order below will be the correct answer.</p>
          {orderItemsArray.fields.map((field, itemIndex) => (
            <div key={field.id} className="flex items-center space-x-2">
              <div className="flex-none flex items-center space-x-1">
                <span className="text-gray-400 w-6 text-center">{itemIndex + 1}</span>
                <GripVertical className="w-4 h-4 text-gray-400" />
              </div>
              <Input
                {...register(`questions.${index}.order_items.${itemIndex}.text`)}
                placeholder={`Item ${itemIndex + 1}`}
                error={errors.questions?.[index]?.order_items?.[itemIndex]?.text?.message}
                className="flex-1"
              />
              <input
                type="hidden"
                {...register(`questions.${index}.order_items.${itemIndex}.position`)}
                value={itemIndex}
              />
              <div className="flex items-center space-x-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => handleMoveItemUp(itemIndex)}
                  disabled={itemIndex === 0}
                  className="p-1 text-gray-500 hover:text-gray-700"
                >
                  <ArrowUp className="w-4 h-4" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => handleMoveItemDown(itemIndex)}
                  disabled={itemIndex === orderItemsArray.fields.length - 1}
                  className="p-1 text-gray-500 hover:text-gray-700"
                >
                  <ArrowDown className="w-4 h-4" />
                </Button>
                {orderItemsArray.fields.length > 2 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveOrderItem(itemIndex)}
                    className="text-red-500 hover:text-red-700 p-1"
                  >
                    <Minus className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
export default QuestionEditor;