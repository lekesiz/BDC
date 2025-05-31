import { Mark, mergeAttributes } from '@tiptap/core';

export const QuestionHint = Mark.create({
  name: 'questionHint',

  addOptions() {
    return {
      HTMLAttributes: {
        class: 'question-hint',
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'span[data-hint]',
      },
      {
        tag: 'span.question-hint',
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'span',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-hint': true,
      }),
      0,
    ];
  },

  addCommands() {
    return {
      setQuestionHint:
        () =>
        ({ commands }) => {
          return commands.setMark(this.name);
        },
      toggleQuestionHint:
        () =>
        ({ commands }) => {
          return commands.toggleMark(this.name);
        },
      unsetQuestionHint:
        () =>
        ({ commands }) => {
          return commands.unsetMark(this.name);
        },
    };
  },

  addKeyboardShortcuts() {
    return {
      'Mod-Shift-h': () => this.editor.commands.toggleQuestionHint(),
    };
  },
});