// TODO: i18n - processed
import { Node, mergeAttributes } from '@tiptap/core';
import { ReactNodeViewRenderer } from '@tiptap/react';
import ExplanationBlockView from './ExplanationBlockView';import { useTranslation } from "react-i18next";
export const ExplanationBlock = Node.create({
  name: 'explanationBlock',
  group: 'block',
  content: 'block+',
  addOptions() {
    return {
      HTMLAttributes: {
        class: 'explanation-block'
      }
    };
  },
  parseHTML() {
    return [
    {
      tag: 'div[data-explanation-block]'
    },
    {
      tag: 'div.explanation-block'
    }];

  },
  renderHTML({ HTMLAttributes }) {
    return [
    'div',
    mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
      'data-explanation-block': true
    }),
    0];

  },
  addCommands() {
    return {
      setExplanationBlock:
      () =>
      ({ commands }) => {
        return commands.wrapIn(this.name);
      },
      toggleExplanationBlock:
      () =>
      ({ commands }) => {
        return commands.toggleWrap(this.name);
      },
      unsetExplanationBlock:
      () =>
      ({ commands }) => {
        return commands.lift(this.name);
      }
    };
  },
  addKeyboardShortcuts() {
    return {
      'Mod-Shift-e': () => this.editor.commands.toggleExplanationBlock()
    };
  },
  addNodeView() {
    return ReactNodeViewRenderer(ExplanationBlockView);
  }
});