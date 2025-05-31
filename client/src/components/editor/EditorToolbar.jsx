import React, { useRef, useState } from 'react';
import {
  Bold,
  Italic,
  Underline,
  Strikethrough,
  Heading1,
  Heading2,
  Heading3,
  Heading4,
  Heading5,
  Heading6,
  List,
  ListOrdered,
  ListTodo,
  Code,
  FileCode,
  Image as ImageIcon,
  Table,
  Link,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  Undo,
  Redo,
  Highlighter,
  Palette,
  Eye,
  Download,
  HelpCircle,
  CheckSquare,
  MessageSquare,
  Calculator,
  ChevronDown,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dropdown, DropdownItem } from '@/components/ui/dropdown';
import { Tooltip } from '@/components/ui/tooltip';

const EditorToolbar = ({
  editor,
  onImageUpload,
  onTogglePreview,
  onExport,
  exportFormats = ['html', 'markdown'],
  darkMode = false,
}) => {
  const fileInputRef = useRef(null);
  const [showLinkDialog, setShowLinkDialog] = useState(false);
  const [linkUrl, setLinkUrl] = useState('');

  if (!editor) {
    return null;
  }

  const handleImageClick = () => {
    fileInputRef.current?.click();
  };

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (file && onImageUpload) {
      onImageUpload(file);
    }
  };

  const setLink = () => {
    if (linkUrl) {
      editor.chain().focus().setLink({ href: linkUrl }).run();
      setLinkUrl('');
      setShowLinkDialog(false);
    }
  };

  const addTable = () => {
    editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run();
  };

  const ToolbarButton = ({ onClick, isActive, disabled, children, tooltip }) => (
    <Tooltip content={tooltip} position="top">
      <Button
        onClick={onClick}
        disabled={disabled}
        variant={isActive ? 'default' : 'ghost'}
        size="sm"
        className={`toolbar-button ${isActive ? 'active' : ''}`}
      >
        {children}
      </Button>
    </Tooltip>
  );

  const ToolbarSeparator = () => <div className="toolbar-separator" />;

  return (
    <div className={`editor-toolbar ${darkMode ? 'dark' : ''}`}>
      <div className="toolbar-section">
        {/* Text formatting */}
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBold().run()}
          isActive={editor.isActive('bold')}
          tooltip="Bold (Ctrl+B)"
        >
          <Bold className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleItalic().run()}
          isActive={editor.isActive('italic')}
          tooltip="Italic (Ctrl+I)"
        >
          <Italic className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          isActive={editor.isActive('underline')}
          tooltip="Underline (Ctrl+U)"
        >
          <Underline className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleStrike().run()}
          isActive={editor.isActive('strike')}
          tooltip="Strikethrough"
        >
          <Strikethrough className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarSeparator />

        {/* Headings */}
        <Dropdown
          trigger={
            <div className="toolbar-button flex items-center">
              <Heading1 className="w-4 h-4 mr-1" />
              <ChevronDown className="w-3 h-3" />
            </div>
          }
        >
          <DropdownItem onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}>
            <div className="flex items-center">
              <Heading1 className="w-4 h-4 mr-2" /> Heading 1
            </div>
          </DropdownItem>
          <DropdownItem onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}>
            <div className="flex items-center">
              <Heading2 className="w-4 h-4 mr-2" /> Heading 2
            </div>
          </DropdownItem>
          <DropdownItem onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}>
            <div className="flex items-center">
              <Heading3 className="w-4 h-4 mr-2" /> Heading 3
            </div>
          </DropdownItem>
          <DropdownItem onClick={() => editor.chain().focus().toggleHeading({ level: 4 }).run()}>
            <div className="flex items-center">
              <Heading4 className="w-4 h-4 mr-2" /> Heading 4
            </div>
          </DropdownItem>
          <DropdownItem onClick={() => editor.chain().focus().toggleHeading({ level: 5 }).run()}>
            <div className="flex items-center">
              <Heading5 className="w-4 h-4 mr-2" /> Heading 5
            </div>
          </DropdownItem>
          <DropdownItem onClick={() => editor.chain().focus().toggleHeading({ level: 6 }).run()}>
            <div className="flex items-center">
              <Heading6 className="w-4 h-4 mr-2" /> Heading 6
            </div>
          </DropdownItem>
        </Dropdown>

        <ToolbarSeparator />

        {/* Lists */}
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          isActive={editor.isActive('bulletList')}
          tooltip="Bullet List"
        >
          <List className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          isActive={editor.isActive('orderedList')}
          tooltip="Numbered List"
        >
          <ListOrdered className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleTaskList().run()}
          isActive={editor.isActive('taskList')}
          tooltip="Task List"
        >
          <ListTodo className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarSeparator />

        {/* Code */}
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCode().run()}
          isActive={editor.isActive('code')}
          tooltip="Inline Code"
        >
          <Code className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCodeBlock().run()}
          isActive={editor.isActive('codeBlock')}
          tooltip="Code Block"
        >
          <FileCode className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarSeparator />

        {/* Alignment */}
        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('left').run()}
          isActive={editor.isActive({ textAlign: 'left' })}
          tooltip="Align Left"
        >
          <AlignLeft className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('center').run()}
          isActive={editor.isActive({ textAlign: 'center' })}
          tooltip="Align Center"
        >
          <AlignCenter className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('right').run()}
          isActive={editor.isActive({ textAlign: 'right' })}
          tooltip="Align Right"
        >
          <AlignRight className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('justify').run()}
          isActive={editor.isActive({ textAlign: 'justify' })}
          tooltip="Justify"
        >
          <AlignJustify className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarSeparator />

        {/* Insert items */}
        <ToolbarButton
          onClick={handleImageClick}
          tooltip="Insert Image"
        >
          <ImageIcon className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={addTable}
          tooltip="Insert Table"
        >
          <Table className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => setShowLinkDialog(true)}
          isActive={editor.isActive('link')}
          tooltip="Insert Link"
        >
          <Link className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarSeparator />

        {/* Custom extensions */}
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleQuestionHint().run()}
          isActive={editor.isActive('questionHint')}
          tooltip="Add Hint"
        >
          <HelpCircle className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCorrectAnswer().run()}
          isActive={editor.isActive('correctAnswer')}
          tooltip="Highlight Correct Answer"
        >
          <CheckSquare className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleExplanationBlock().run()}
          isActive={editor.isActive('explanationBlock')}
          tooltip="Add Explanation"
        >
          <MessageSquare className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().insertMath().run()}
          tooltip="Insert Math Formula"
        >
          <Calculator className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarSeparator />

        {/* Colors */}
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHighlight().run()}
          isActive={editor.isActive('highlight')}
          tooltip="Highlight"
        >
          <Highlighter className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarSeparator />

        {/* History */}
        <ToolbarButton
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          tooltip="Undo (Ctrl+Z)"
        >
          <Undo className="w-4 h-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          tooltip="Redo (Ctrl+Y)"
        >
          <Redo className="w-4 h-4" />
        </ToolbarButton>
      </div>

      <div className="toolbar-section">
        {/* Preview and Export */}
        {onTogglePreview && (
          <ToolbarButton
            onClick={onTogglePreview}
            tooltip="Toggle Preview"
          >
            <Eye className="w-4 h-4" />
          </ToolbarButton>
        )}

        {onExport && exportFormats.length > 0 && (
          <Dropdown
            trigger={
              <Tooltip content="Export" position="top">
                <div className="toolbar-button">
                  <Download className="w-4 h-4" />
                </div>
              </Tooltip>
            }
          >
            {exportFormats.includes('html') && (
              <DropdownItem onClick={() => onExport('html')}>
                Export as HTML
              </DropdownItem>
            )}
            {exportFormats.includes('markdown') && (
              <DropdownItem onClick={() => onExport('markdown')}>
                Export as Markdown
              </DropdownItem>
            )}
            {exportFormats.includes('json') && (
              <DropdownItem onClick={() => onExport('json')}>
                Export as JSON
              </DropdownItem>
            )}
          </Dropdown>
        )}
      </div>

      {/* Hidden file input for image upload */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleImageChange}
        style={{ display: 'none' }}
      />

      {/* Link dialog */}
      {showLinkDialog && (
        <div className="link-dialog">
          <input
            type="url"
            value={linkUrl}
            onChange={(e) => setLinkUrl(e.target.value)}
            placeholder="Enter URL..."
            className="link-input"
            autoFocus
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                setLink();
              } else if (e.key === 'Escape') {
                setShowLinkDialog(false);
                setLinkUrl('');
              }
            }}
          />
          <Button onClick={setLink} size="sm">Add Link</Button>
          <Button
            onClick={() => {
              setShowLinkDialog(false);
              setLinkUrl('');
            }}
            variant="ghost"
            size="sm"
          >
            Cancel
          </Button>
        </div>
      )}
    </div>
  );
};

export default EditorToolbar;