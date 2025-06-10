// TODO: i18n - processed
import DocumentViewer from './DocumentViewer';
import DocumentUploader from './DocumentUploader';
import DocumentShare from './DocumentShare';
import DocumentService from './DocumentService';import { useTranslation } from "react-i18next";
export {
  DocumentViewer,
  DocumentUploader,
  DocumentShare,
  DocumentService };

export default {
  Viewer: DocumentViewer,
  Uploader: DocumentUploader,
  Share: DocumentShare,
  Service: DocumentService
};