import React, { useState, useEffect, useRef } from 'react';
import { NodeViewWrapper } from '@tiptap/react';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import { Calculator, Edit3, Check, X } from 'lucide-react';

const MathematicsView = ({ node, updateAttributes, deleteNode, selected }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [latex, setLatex] = useState(node.attrs.latex || '');
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const renderMath = () => {
    try {
      const html = katex.renderToString(node.attrs.latex || '', {
        displayMode: node.attrs.display,
        throwOnError: false,
        errorColor: '#cc0000',
      });
      return { __html: html };
    } catch (e) {
      return { __html: `<span class="math-error">Invalid LaTeX</span>` };
    }
  };

  const handleSave = () => {
    try {
      // Validate LaTeX
      katex.renderToString(latex, { throwOnError: true });
      updateAttributes({ latex });
      setIsEditing(false);
      setError('');
    } catch (e) {
      setError(e.message);
    }
  };

  const handleCancel = () => {
    setLatex(node.attrs.latex || '');
    setIsEditing(false);
    setError('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  if (isEditing) {
    return (
      <NodeViewWrapper
        className={`math-node-wrapper editing ${selected ? 'selected' : ''}`}
        contentEditable={false}
      >
        <div className="math-editor">
          <div className="math-editor-header">
            <Calculator className="w-4 h-4" />
            <span>LaTeX Formula</span>
          </div>
          <textarea
            ref={inputRef}
            value={latex}
            onChange={(e) => setLatex(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter LaTeX formula (e.g., x^2 + y^2 = z^2)"
            className="math-input"
            rows={3}
          />
          {error && <div className="math-error-message">{error}</div>}
          <div className="math-preview">
            <div className="math-preview-label">Preview:</div>
            <div
              dangerouslySetInnerHTML={{
                __html: katex.renderToString(latex || '\\text{Enter formula above}', {
                  displayMode: node.attrs.display,
                  throwOnError: false,
                  errorColor: '#cc0000',
                }),
              }}
            />
          </div>
          <div className="math-editor-actions">
            <button onClick={handleSave} className="math-button save">
              <Check className="w-4 h-4" />
              Save
            </button>
            <button onClick={handleCancel} className="math-button cancel">
              <X className="w-4 h-4" />
              Cancel
            </button>
          </div>
        </div>
      </NodeViewWrapper>
    );
  }

  return (
    <NodeViewWrapper
      className={`math-node-wrapper ${node.attrs.display ? 'block' : 'inline'} ${
        selected ? 'selected' : ''
      }`}
      contentEditable={false}
      onClick={() => setIsEditing(true)}
    >
      {!node.attrs.latex ? (
        <span className="math-placeholder">
          <Calculator className="w-4 h-4" />
          Click to add formula
        </span>
      ) : (
        <>
          <span dangerouslySetInnerHTML={renderMath()} />
          {selected && (
            <button
              className="math-edit-button"
              onClick={(e) => {
                e.stopPropagation();
                setIsEditing(true);
              }}
            >
              <Edit3 className="w-3 h-3" />
            </button>
          )}
        </>
      )}
    </NodeViewWrapper>
  );
};

export default MathematicsView;