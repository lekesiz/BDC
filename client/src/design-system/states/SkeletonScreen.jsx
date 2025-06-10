// TODO: i18n - processed
// Skeleton Screen Components
import React from 'react';
import { motion } from 'framer-motion';
import './states.css';

// Base Skeleton Component
import { useTranslation } from "react-i18next";export const SkeletonBase = ({
  width = '100%',
  height = '20px',
  borderRadius = '4px',
  className = '',
  animate = true,
  ...props
}) => {const { t } = useTranslation();
  return (
    <div
      className={`ds-skeleton-base ${animate ? 'ds-skeleton-base--animated' : ''} ${className}`}
      style={{
        width,
        height,
        borderRadius
      }}
      aria-hidden="true"
      {...props} />);


};

// Text Skeleton
export const SkeletonText = ({
  lines = 3,
  width = '100%',
  lastLineWidth = '60%',
  spacing = '8px',
  animate = true,
  ...props
}) => {const { t } = useTranslation();
  return (
    <div className="ds-skeleton-text" {...props}>
      {Array.from({ length: lines }).map((_, index) =>
      <SkeletonBase
        key={index}
        width={index === lines - 1 ? lastLineWidth : width}
        height="16px"
        animate={animate}
        style={{
          marginBottom: index < lines - 1 ? spacing : 0
        }} />

      )}
    </div>);

};

// Avatar Skeleton
export const SkeletonAvatar = ({
  size = 'md',
  shape = 'circle',
  animate = true,
  ...props
}) => {const { t } = useTranslation();
  const sizes = {
    sm: 32,
    md: 40,
    lg: 56,
    xl: 72
  };

  return (
    <SkeletonBase
      width={sizes[size]}
      height={sizes[size]}
      borderRadius={shape === 'circle' ? '50%' : '8px'}
      animate={animate}
      className="ds-skeleton-avatar"
      {...props} />);


};

// Button Skeleton
export const SkeletonButton = ({
  width = '120px',
  height = '40px',
  animate = true,
  ...props
}) => {const { t } = useTranslation();
  return (
    <SkeletonBase
      width={width}
      height={height}
      borderRadius="4px"
      animate={animate}
      className="ds-skeleton-button"
      {...props} />);


};

// Image Skeleton
export const SkeletonImage = ({
  width = '100%',
  height = '200px',
  aspectRatio,
  animate = true,
  ...props
}) => {const { t } = useTranslation();
  const style = aspectRatio ?
  { width, aspectRatio } :
  { width, height };

  return (
    <SkeletonBase
      {...style}
      borderRadius="8px"
      animate={animate}
      className="ds-skeleton-image"
      {...props} />);


};

// Card Skeleton
export const SkeletonCard = ({
  showImage = true,
  showAvatar = true,
  showActions = true,
  animate = true,
  ...props
}) => {const { t } = useTranslation();
  return (
    <div className="ds-skeleton-card" {...props}>
      {showImage &&
      <SkeletonImage
        height="180px"
        animate={animate}
        style={{ marginBottom: '16px' }} />

      }
      
      <div className="ds-skeleton-card__header">
        {showAvatar &&
        <SkeletonAvatar
          size="md"
          animate={animate}
          style={{ marginRight: '12px' }} />

        }
        <div style={{ flex: 1 }}>
          <SkeletonBase
            width="60%"
            height="20px"
            animate={animate}
            style={{ marginBottom: '8px' }} />

          <SkeletonBase
            width="40%"
            height="16px"
            animate={animate} />

        </div>
      </div>
      
      <div className="ds-skeleton-card__content">
        <SkeletonText
          lines={3}
          animate={animate}
          style={{ margin: '16px 0' }} />

      </div>
      
      {showActions &&
      <div className="ds-skeleton-card__actions">
          <SkeletonButton
          width="100px"
          height="36px"
          animate={animate}
          style={{ marginRight: '8px' }} />

          <SkeletonButton
          width="100px"
          height="36px"
          animate={animate} />

        </div>
      }
    </div>);

};

// List Item Skeleton
export const SkeletonListItem = ({
  showAvatar = true,
  showSecondaryText = true,
  showAction = false,
  animate = true,
  ...props
}) => {const { t } = useTranslation();
  return (
    <div className="ds-skeleton-list-item" {...props}>
      {showAvatar &&
      <SkeletonAvatar
        size="md"
        animate={animate}
        style={{ marginRight: '16px' }} />

      }
      
      <div className="ds-skeleton-list-item__content">
        <SkeletonBase
          width="70%"
          height="18px"
          animate={animate}
          style={{ marginBottom: showSecondaryText ? '8px' : 0 }} />

        {showSecondaryText &&
        <SkeletonBase
          width="40%"
          height="14px"
          animate={animate} />

        }
      </div>
      
      {showAction &&
      <SkeletonBase
        width="24px"
        height="24px"
        borderRadius="4px"
        animate={animate}
        style={{ marginLeft: 'auto' }} />

      }
    </div>);

};

// Table Skeleton
export const SkeletonTable = ({
  rows = 5,
  columns = 4,
  showHeader = true,
  columnWidths = [],
  animate = true,
  ...props
}) => {const { t } = useTranslation();
  const getColumnWidth = (index) => {
    return columnWidths[index] || `${100 / columns}%`;
  };

  return (
    <div className="ds-skeleton-table" {...props}>
      {showHeader &&
      <div className="ds-skeleton-table__header">
          {Array.from({ length: columns }).map((_, index) =>
        <SkeletonBase
          key={index}
          width={getColumnWidth(index)}
          height="16px"
          animate={animate}
          style={{ marginRight: index < columns - 1 ? '16px' : 0 }} />

        )}
        </div>
      }
      
      <div className="ds-skeleton-table__body">
        {Array.from({ length: rows }).map((_, rowIndex) =>
        <div key={rowIndex} className="ds-skeleton-table__row">
            {Array.from({ length: columns }).map((_, colIndex) =>
          <SkeletonBase
            key={colIndex}
            width={getColumnWidth(colIndex)}
            height="20px"
            animate={animate}
            style={{ marginRight: colIndex < columns - 1 ? '16px' : 0 }} />

          )}
          </div>
        )}
      </div>
    </div>);

};

// Form Skeleton
export const SkeletonForm = ({
  fields = 4,
  showLabels = true,
  showButton = true,
  animate = true,
  ...props
}) => {const { t } = useTranslation();
  return (
    <div className="ds-skeleton-form" {...props}>
      {Array.from({ length: fields }).map((_, index) =>
      <div key={index} className="ds-skeleton-form__field">
          {showLabels &&
        <SkeletonBase
          width="120px"
          height="14px"
          animate={animate}
          style={{ marginBottom: '8px' }} />

        }
          <SkeletonBase
          width="100%"
          height="40px"
          borderRadius="4px"
          animate={animate} />

        </div>
      )}
      
      {showButton &&
      <SkeletonButton
        width="120px"
        height="40px"
        animate={animate}
        style={{ marginTop: '24px' }} />

      }
    </div>);

};

// Dashboard Skeleton
export const SkeletonDashboard = ({
  showStats = true,
  showChart = true,
  showTable = true,
  animate = true,
  ...props
}) => {const { t } = useTranslation();
  return (
    <div className="ds-skeleton-dashboard" {...props}>
      {showStats &&
      <div className="ds-skeleton-dashboard__stats">
          {Array.from({ length: 4 }).map((_, index) =>
        <div key={index} className="ds-skeleton-dashboard__stat">
              <SkeletonBase
            width="80px"
            height="14px"
            animate={animate}
            style={{ marginBottom: '8px' }} />

              <SkeletonBase
            width="120px"
            height="32px"
            animate={animate} />

            </div>
        )}
        </div>
      }
      
      {showChart &&
      <div className="ds-skeleton-dashboard__chart">
          <SkeletonBase
          width="100%"
          height="300px"
          borderRadius="8px"
          animate={animate} />

        </div>
      }
      
      {showTable &&
      <SkeletonTable
        rows={5}
        columns={5}
        animate={animate}
        style={{ marginTop: '24px' }} />

      }
    </div>);

};

// Export all skeleton components
export const SkeletonScreen = {
  Base: SkeletonBase,
  Text: SkeletonText,
  Avatar: SkeletonAvatar,
  Button: SkeletonButton,
  Image: SkeletonImage,
  Card: SkeletonCard,
  ListItem: SkeletonListItem,
  Table: SkeletonTable,
  Form: SkeletonForm,
  Dashboard: SkeletonDashboard
};