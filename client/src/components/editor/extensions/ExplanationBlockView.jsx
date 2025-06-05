import React from 'react';
import { NodeViewWrapper, NodeViewContent } from '@tiptap/react';
import { MessageSquare } from 'lucide-react';
const ExplanationBlockView = () => {
  return (
    <NodeViewWrapper className="explanation-block-wrapper">
      <div className="explanation-block-header">
        <MessageSquare className="w-4 h-4" />
        <span>Explanation</span>
      </div>
      <NodeViewContent className="explanation-block-content" />
    </NodeViewWrapper>
  );
};
export default ExplanationBlockView;