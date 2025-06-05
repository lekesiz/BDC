import { Node, mergeAttributes } from '@tiptap/core';
import { ReactNodeViewRenderer } from '@tiptap/react';
import MathematicsView from './MathematicsView';
export const Mathematics = Node.create({
  name: 'mathematics',
  group: 'inline',
  inline: true,
  atom: true,
  addAttributes() {
    return {
      latex: {
        default: '',
      },
      display: {
        default: false,
      },
    };
  },
  parseHTML() {
    return [
      {
        tag: 'span[data-math]',
        getAttrs: (dom) => ({
          latex: dom.getAttribute('data-latex') || '',
          display: dom.getAttribute('data-display') === 'true',
        }),
      },
      {
        tag: 'span.math-inline',
        getAttrs: (dom) => ({
          latex: dom.getAttribute('data-latex') || '',
          display: false,
        }),
      },
      {
        tag: 'div.math-block',
        getAttrs: (dom) => ({
          latex: dom.getAttribute('data-latex') || '',
          display: true,
        }),
      },
    ];
  },
  renderHTML({ node, HTMLAttributes }) {
    const { latex, display } = node.attrs;
    return [
      display ? 'div' : 'span',
      mergeAttributes(
        this.options.HTMLAttributes,
        HTMLAttributes,
        {
          'data-math': true,
          'data-latex': latex,
          'data-display': display,
          class: display ? 'math-block' : 'math-inline',
        }
      ),
    ];
  },
  addCommands() {
    return {
      insertMath:
        (options = {}) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: {
              latex: options.latex || '',
              display: options.display || false,
            },
          });
        },
      updateMath:
        (options) =>
        ({ commands }) => {
          return commands.updateAttributes(this.name, options);
        },
    };
  },
  addKeyboardShortcuts() {
    return {
      'Mod-Shift-m': () => this.editor.commands.insertMath(),
    };
  },
  addNodeView() {
    return ReactNodeViewRenderer(MathematicsView);
  },
});