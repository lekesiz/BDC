import { Mark, mergeAttributes } from '@tiptap/core';
export const CorrectAnswer = Mark.create({
  name: 'correctAnswer',
  addOptions() {
    return {
      HTMLAttributes: {
        class: 'correct-answer',
      },
    };
  },
  parseHTML() {
    return [
      {
        tag: 'span[data-correct-answer]',
      },
      {
        tag: 'span.correct-answer',
      },
    ];
  },
  renderHTML({ HTMLAttributes }) {
    return [
      'span',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-correct-answer': true,
      }),
      0,
    ];
  },
  addCommands() {
    return {
      setCorrectAnswer:
        () =>
        ({ commands }) => {
          return commands.setMark(this.name);
        },
      toggleCorrectAnswer:
        () =>
        ({ commands }) => {
          return commands.toggleMark(this.name);
        },
      unsetCorrectAnswer:
        () =>
        ({ commands }) => {
          return commands.unsetMark(this.name);
        },
    };
  },
  addKeyboardShortcuts() {
    return {
      'Mod-Shift-c': () => this.editor.commands.toggleCorrectAnswer(),
    };
  },
});