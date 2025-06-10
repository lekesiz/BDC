// TODO: i18n - processed
import React from 'react';
import { NodeViewWrapper, NodeViewContent } from '@tiptap/react';
import { MessageSquare } from 'lucide-react';import { useTranslation } from "react-i18next";
const ExplanationBlockView = () => {const { t } = useTranslation();
  return (
    <NodeViewWrapper className="explanation-block-wrapper">
      <div className="explanation-block-header">
        <MessageSquare className="w-4 h-4" />
        <span>{t("components.explanation")}</span>
      </div>
      <NodeViewContent className="explanation-block-content" />
    </NodeViewWrapper>);

};
export default ExplanationBlockView;