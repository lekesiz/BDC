// Empty States Components
import React from 'react';
import { motion } from 'framer-motion';
import { animations } from '../animations/animations';
import './states.css';

// Empty State Illustrations
const EmptyIllustrations = {
  default: ({ size = 120 }) => (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none">
      <circle cx="60" cy="60" r="50" stroke="currentColor" strokeWidth="2" opacity="0.2" />
      <rect x="35" y="40" width="50" height="40" rx="4" stroke="currentColor" strokeWidth="2" opacity="0.4" />
      <line x1="45" y1="50" x2="75" y2="50" stroke="currentColor" strokeWidth="2" opacity="0.3" />
      <line x1="45" y1="60" x2="65" y2="60" stroke="currentColor" strokeWidth="2" opacity="0.3" />
      <line x1="45" y1="70" x2="70" y2="70" stroke="currentColor" strokeWidth="2" opacity="0.3" />
    </svg>
  ),
  
  noData: ({ size = 120 }) => (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none">
      <rect x="20" y="30" width="80" height="60" rx="4" stroke="currentColor" strokeWidth="2" opacity="0.4" />
      <path d="M40 50h40M40 60h30M40 70h35" stroke="currentColor" strokeWidth="2" opacity="0.3" strokeLinecap="round" />
      <circle cx="85" cy="35" r="15" fill="currentColor" opacity="0.1" />
      <path d="M85 30v10M85 43v0" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  ),
  
  noResults: ({ size = 120 }) => (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none">
      <circle cx="50" cy="50" r="30" stroke="currentColor" strokeWidth="2" opacity="0.4" />
      <path d="M70 70l20 20" stroke="currentColor" strokeWidth="2" opacity="0.4" strokeLinecap="round" />
      <path d="M40 40l20 20M60 40l-20 20" stroke="currentColor" strokeWidth="2" opacity="0.3" strokeLinecap="round" />
    </svg>
  ),
  
  noMessages: ({ size = 120 }) => (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none">
      <path d="M20 40h80v50H30l-10 10V40z" stroke="currentColor" strokeWidth="2" opacity="0.4" />
      <circle cx="40" cy="65" r="3" fill="currentColor" opacity="0.3" />
      <circle cx="60" cy="65" r="3" fill="currentColor" opacity="0.3" />
      <circle cx="80" cy="65" r="3" fill="currentColor" opacity="0.3" />
    </svg>
  ),
  
  noNotifications: ({ size = 120 }) => (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none">
      <path d="M60 20c-5 0-9 4-9 9v22l-6 12h30l-6-12V29c0-5-4-9-9-9z" stroke="currentColor" strokeWidth="2" opacity="0.4" />
      <path d="M55 90c0 3 2 5 5 5s5-2 5-5" stroke="currentColor" strokeWidth="2" opacity="0.4" />
      <circle cx="80" cy="30" r="15" fill="currentColor" opacity="0.1" />
      <path d="M74 30h12M80 24v12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" transform="rotate(45 80 30)" />
    </svg>
  ),
  
  noFiles: ({ size = 120 }) => (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none">
      <path d="M30 25h40l10 10v55H30V25z" stroke="currentColor" strokeWidth="2" opacity="0.4" />
      <path d="M70 25v10h10" stroke="currentColor" strokeWidth="2" opacity="0.3" />
      <path d="M40 50h30M40 60h20M40 70h25" stroke="currentColor" strokeWidth="2" opacity="0.3" strokeLinecap="round" />
      <circle cx="75" cy="75" r="15" fill="currentColor" opacity="0.1" />
      <path d="M75 70v10M75 83v0" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  ),
  
  noTasks: ({ size = 120 }) => (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none">
      <rect x="30" y="30" width="60" height="60" rx="4" stroke="currentColor" strokeWidth="2" opacity="0.4" />
      <path d="M45 50h30M45 60h20M45 70h25" stroke="currentColor" strokeWidth="2" opacity="0.3" strokeLinecap="round" />
      <rect x="35" y="48" width="4" height="4" rx="1" fill="currentColor" opacity="0.3" />
      <rect x="35" y="58" width="4" height="4" rx="1" fill="currentColor" opacity="0.3" />
      <rect x="35" y="68" width="4" height="4" rx="1" fill="currentColor" opacity="0.3" />
    </svg>
  )
};

// Generic Empty State Component
export const EmptyState = ({
  variant = 'default',
  title = 'No data',
  message = 'There is no data to display at the moment.',
  icon = true,
  customIcon,
  actions,
  className = '',
  animate = true,
  ...props
}) => {
  const Illustration = customIcon || EmptyIllustrations[variant] || EmptyIllustrations.default;

  return (
    <motion.div
      className={`ds-empty-state ds-empty-state--${variant} ${className}`}
      initial={animate ? { opacity: 0, y: 20 } : {}}
      animate={animate ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.4 }}
      {...props}
    >
      {icon && (
        <motion.div
          className="ds-empty-state__icon"
          animate={animate ? animations.entrance.scaleIn.animate : {}}
          transition={{ delay: 0.1 }}
        >
          <Illustration size={120} />
        </motion.div>
      )}
      
      <motion.h3
        className="ds-empty-state__title"
        initial={animate ? { opacity: 0 } : {}}
        animate={animate ? { opacity: 1 } : {}}
        transition={{ delay: 0.2 }}
      >
        {title}
      </motion.h3>
      
      {message && (
        <motion.p
          className="ds-empty-state__message"
          initial={animate ? { opacity: 0 } : {}}
          animate={animate ? { opacity: 1 } : {}}
          transition={{ delay: 0.3 }}
        >
          {message}
        </motion.p>
      )}
      
      {actions && (
        <motion.div
          className="ds-empty-state__actions"
          initial={animate ? { opacity: 0 } : {}}
          animate={animate ? { opacity: 1 } : {}}
          transition={{ delay: 0.4 }}
        >
          {actions}
        </motion.div>
      )}
    </motion.div>
  );
};

// No Results Empty State
export const NoResults = ({
  searchTerm,
  onClearSearch,
  suggestions = [],
  ...props
}) => {
  return (
    <EmptyState
      variant="noResults"
      title="No results found"
      message={searchTerm ? `No results found for "${searchTerm}"` : 'Try adjusting your search or filters'}
      actions={
        <>
          {onClearSearch && (
            <button
              className="ds-button ds-button--primary"
              onClick={onClearSearch}
            >
              Clear Search
            </button>
          )}
          {suggestions.length > 0 && (
            <div className="ds-empty-state__suggestions">
              <p>Try searching for:</p>
              <div className="ds-empty-state__suggestion-list">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="ds-button ds-button--ghost ds-button--sm"
                    onClick={() => onClearSearch && onClearSearch(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}
        </>
      }
      {...props}
    />
  );
};

// No Data Empty State
export const NoData = ({
  onAddData,
  addLabel = 'Add Data',
  ...props
}) => {
  return (
    <EmptyState
      variant="noData"
      title="No data yet"
      message="Get started by adding your first item"
      actions={
        onAddData && (
          <button
            className="ds-button ds-button--primary"
            onClick={onAddData}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="ds-button__icon">
              <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            {addLabel}
          </button>
        )
      }
      {...props}
    />
  );
};

// No Messages Empty State
export const NoMessages = ({
  onCompose,
  ...props
}) => {
  return (
    <EmptyState
      variant="noMessages"
      title="No messages"
      message="Start a conversation or wait for someone to message you"
      actions={
        onCompose && (
          <button
            className="ds-button ds-button--primary"
            onClick={onCompose}
          >
            Compose Message
          </button>
        )
      }
      {...props}
    />
  );
};

// No Notifications Empty State
export const NoNotifications = ({ ...props }) => {
  return (
    <EmptyState
      variant="noNotifications"
      title="All caught up!"
      message="You have no new notifications"
      {...props}
    />
  );
};

// No Files Empty State
export const NoFiles = ({
  onUpload,
  acceptedFormats = [],
  ...props
}) => {
  return (
    <EmptyState
      variant="noFiles"
      title="No files uploaded"
      message={
        acceptedFormats.length > 0
          ? `Upload files in formats: ${acceptedFormats.join(', ')}`
          : 'Upload your files to get started'
      }
      actions={
        onUpload && (
          <button
            className="ds-button ds-button--primary"
            onClick={onUpload}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="ds-button__icon">
              <path d="M8 11V3M5 6l3-3 3 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M2 13h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            Upload Files
          </button>
        )
      }
      {...props}
    />
  );
};

// No Tasks Empty State
export const NoTasks = ({
  onCreateTask,
  ...props
}) => {
  return (
    <EmptyState
      variant="noTasks"
      title="No tasks yet"
      message="Create your first task to get started"
      actions={
        onCreateTask && (
          <button
            className="ds-button ds-button--primary"
            onClick={onCreateTask}
          >
            Create Task
          </button>
        )
      }
      {...props}
    />
  );
};

// Export all empty states
export const EmptyStates = {
  EmptyState,
  NoResults,
  NoData,
  NoMessages,
  NoNotifications,
  NoFiles,
  NoTasks
};