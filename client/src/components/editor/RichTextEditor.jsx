// TODO: i18n - processed
import React, { useCallback, useEffect, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Bold from '@tiptap/extension-bold';
import Italic from '@tiptap/extension-italic';
import Underline from '@tiptap/extension-underline';
import Strike from '@tiptap/extension-strike';
import Heading from '@tiptap/extension-heading';
import BulletList from '@tiptap/extension-bullet-list';
import OrderedList from '@tiptap/extension-ordered-list';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import Image from '@tiptap/extension-image';
import Table from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import Link from '@tiptap/extension-link';
import TextAlign from '@tiptap/extension-text-align';
import History from '@tiptap/extension-history';
import Highlight from '@tiptap/extension-highlight';
import Color from '@tiptap/extension-color';
import TextStyle from '@tiptap/extension-text-style';
import { lowlight } from 'lowlight/lib/core';
import javascript from 'highlight.js/lib/languages/javascript';
import python from 'highlight.js/lib/languages/python';
import java from 'highlight.js/lib/languages/java';
import cpp from 'highlight.js/lib/languages/cpp';
import css from 'highlight.js/lib/languages/css';
import xml from 'highlight.js/lib/languages/xml';
import sql from 'highlight.js/lib/languages/sql';
import bash from 'highlight.js/lib/languages/bash';
// Custom extensions
import { QuestionHint } from './extensions/QuestionHint';
import { CorrectAnswer } from './extensions/CorrectAnswer';
import { ExplanationBlock } from './extensions/ExplanationBlock';
import { Mathematics } from './extensions/Mathematics';
// Toolbar component
import EditorToolbar from './EditorToolbar';
// Styles
import './RichTextEditor.css';
// Utils
import { htmlToMarkdown } from './utils/markdownConverter';
// Register languages for syntax highlighting
import { useTranslation } from "react-i18next";lowlight.registerLanguage('javascript', javascript);
lowlight.registerLanguage('python', python);
lowlight.registerLanguage('java', java);
lowlight.registerLanguage('cpp', cpp);
lowlight.registerLanguage('css', css);
lowlight.registerLanguage('html', xml);
lowlight.registerLanguage('sql', sql);
lowlight.registerLanguage('bash', bash);
const RichTextEditor = ({
  content = '',
  onChange,
  onImageUpload,
  placeholder = 'Start typing...',
  editable = true,
  showToolbar = true,
  showPreview = false,
  className = '',
  height = 'auto',
  minHeight = '200px',
  maxHeight = '600px',
  darkMode = false,
  onExport,
  exportFormats = ['html', 'markdown']
}) => {const { t } = useTranslation();
  const [isPreviewMode, setIsPreviewMode] = useState(showPreview);
  const [isFocused, setIsFocused] = useState(false);
  const editor = useEditor({
    extensions: [
    StarterKit.configure({
      heading: false,
      bold: false,
      italic: false,
      strike: false,
      bulletList: false,
      orderedList: false,
      history: false,
      codeBlock: false
    }),
    Bold,
    Italic,
    Underline,
    Strike,
    Heading.configure({
      levels: [1, 2, 3, 4, 5, 6]
    }),
    BulletList,
    OrderedList,
    TaskList,
    TaskItem.configure({
      nested: true
    }),
    CodeBlockLowlight.configure({
      lowlight,
      defaultLanguage: 'javascript'
    }),
    Image.configure({
      inline: true,
      allowBase64: true,
      HTMLAttributes: {
        class: 'rich-text-image'
      }
    }),
    Table.configure({
      resizable: true
    }),
    TableRow,
    TableHeader,
    TableCell,
    Link.configure({
      openOnClick: false,
      HTMLAttributes: {
        target: '_blank',
        rel: 'noopener noreferrer',
        class: 'rich-text-link'
      }
    }),
    TextAlign.configure({
      types: ['heading', 'paragraph'],
      alignments: ['left', 'center', 'right', 'justify']
    }),
    History.configure({
      depth: 100
    }),
    Highlight.configure({
      multicolor: true
    }),
    TextStyle,
    Color,
    // Custom extensions
    QuestionHint,
    CorrectAnswer,
    ExplanationBlock,
    Mathematics],

    content,
    editable: editable && !isPreviewMode,
    onUpdate: ({ editor }) => {
      if (onChange) {
        onChange({
          html: editor.getHTML(),
          text: editor.getText(),
          json: editor.getJSON()
        });
      }
    },
    editorProps: {
      attributes: {
        class: `rich-text-editor-content ${darkMode ? 'dark' : ''} ${className}`,
        style: `min-height: ${minHeight}; max-height: ${maxHeight}; height: ${height};`
      }
    }
  });
  // Handle image upload
  const handleImageUpload = useCallback(
    async (file) => {
      if (!onImageUpload) {
        // If no upload handler, convert to base64
        const reader = new FileReader();
        reader.onload = (e) => {
          editor?.chain().focus().setImage({ src: e.target.result }).run();
        };
        reader.readAsDataURL(file);
        return;
      }
      try {
        const url = await onImageUpload(file);
        editor?.chain().focus().setImage({ src: url }).run();
      } catch (error) {
        console.error('Image upload failed:', error);
      }
    },
    [editor, onImageUpload]
  );
  // Handle paste events for images
  useEffect(() => {
    if (!editor) return;
    const handlePaste = (view, event) => {
      const items = Array.from(event.clipboardData?.items || []);
      const imageItem = items.find((item) => item.type.indexOf('image') === 0);
      if (imageItem) {
        event.preventDefault();
        const file = imageItem.getAsFile();
        if (file) {
          handleImageUpload(file);
        }
        return true;
      }
      return false;
    };
    editor.view.dom.addEventListener('paste', handlePaste);
    return () => {
      editor.view.dom.removeEventListener('paste', handlePaste);
    };
  }, [editor, handleImageUpload]);
  // Handle drop events for images
  useEffect(() => {
    if (!editor) return;
    const handleDrop = (event) => {
      const files = Array.from(event.dataTransfer?.files || []);
      const imageFile = files.find((file) => file.type.startsWith('image/'));
      if (imageFile) {
        event.preventDefault();
        handleImageUpload(imageFile);
        return true;
      }
      return false;
    };
    editor.view.dom.addEventListener('drop', handleDrop);
    return () => {
      editor.view.dom.removeEventListener('drop', handleDrop);
    };
  }, [editor, handleImageUpload]);
  // Export functionality
  const handleExport = useCallback(
    (format) => {
      if (!editor || !onExport) return;
      let content;
      switch (format) {
        case 'html':
          content = editor.getHTML();
          break;
        case 'markdown':
          content = htmlToMarkdown(editor.getHTML());
          break;
        case 'json':
          content = JSON.stringify(editor.getJSON(), null, 2);
          break;
        default:
          content = editor.getText();
      }
      onExport(format, content);
    },
    [editor, onExport]
  );
  // Update editor content when prop changes
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content);
    }
  }, [content, editor]);
  // Toggle preview mode
  const togglePreview = useCallback(() => {
    setIsPreviewMode((prev) => !prev);
    if (editor) {
      editor.setEditable(!isPreviewMode);
    }
  }, [editor, isPreviewMode]);
  if (!editor) {
    return (
      <div className="rich-text-editor-loading">
        <div className="spinner" />
      </div>);

  }
  return (
    <div
      className={`rich-text-editor ${darkMode ? 'dark' : ''} ${
      isFocused ? 'focused' : ''} ${
      className}`}>

      {showToolbar && !isPreviewMode &&
      <EditorToolbar
        editor={editor}
        onImageUpload={handleImageUpload}
        onTogglePreview={togglePreview}
        onExport={handleExport}
        exportFormats={exportFormats}
        darkMode={darkMode} />

      }
      <div className="rich-text-editor-wrapper">
        <EditorContent
          editor={editor}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)} />

        {!content && !isFocused && editable &&
        <div className="rich-text-editor-placeholder">{placeholder}</div>
        }
      </div>
      {isPreviewMode &&
      <div className="rich-text-editor-preview-banner">
          <span>{t("components.preview_mode")}</span>
          <button onClick={togglePreview} className="preview-toggle-btn">{t("components.exit_preview")}

        </button>
        </div>
      }
    </div>);

};
export default RichTextEditor;