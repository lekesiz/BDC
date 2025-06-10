// TODO: i18n - processed
// Button Component with Advanced Features
import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { microInteractions } from '../animations/microInteractions';
import { Spinner } from '../states/LoadingStates';
import './components.css';import { useTranslation } from "react-i18next";

export const Button = forwardRef(({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  disabled = false,
  loading = false,
  loadingText = 'Loading...',
  icon,
  iconPosition = 'left',
  type = 'button',
  className = '',
  animate = true,
  haptic = true,
  tooltip,
  ariaLabel,
  onClick,
  ...props
}, ref) => {
  const handleClick = (e) => {
    if (disabled || loading) return;

    // Haptic feedback for mobile
    if (haptic && 'vibrate' in navigator) {
      navigator.vibrate(10);
    }

    onClick?.(e);
  };

  const classes = [
  'ds-button',
  `ds-button--${variant}`,
  `ds-button--${size}`,
  fullWidth && 'ds-button--full-width',
  loading && 'ds-button--loading',
  disabled && 'ds-button--disabled',
  icon && !children && 'ds-button--icon-only',
  className].
  filter(Boolean).join(' ');

  const MotionComponent = animate ? motion.button : 'button';
  const animationProps = animate ? {
    whileHover: !disabled && !loading ? microInteractions.button.hover : undefined,
    whileTap: !disabled && !loading ? microInteractions.button.tap : undefined,
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.2 }
  } : {};

  return (
    <MotionComponent
      ref={ref}
      type={type}
      className={classes}
      disabled={disabled || loading}
      onClick={handleClick}
      aria-label={ariaLabel || (typeof children === 'string' ? children : undefined)}
      aria-busy={loading}
      aria-disabled={disabled}
      title={tooltip}
      {...animationProps}
      {...props}>

      {loading &&
      <span className="ds-button__spinner">
          <Spinner size="sm" color={variant === 'primary' ? 'white' : 'primary'} />
        </span>
      }
      
      {icon && iconPosition === 'left' && !loading &&
      <span className="ds-button__icon ds-button__icon--left">
          {icon}
        </span>
      }
      
      <span className={`ds-button__content ${loading ? 'ds-button__content--loading' : ''}`}>
        {loading && loadingText ? loadingText : children}
      </span>
      
      {icon && iconPosition === 'right' && !loading &&
      <span className="ds-button__icon ds-button__icon--right">
          {icon}
        </span>
      }
    </MotionComponent>);

});

Button.displayName = 'Button';

// Button Group Component
export const ButtonGroup = ({
  children,
  orientation = 'horizontal',
  size = 'md',
  className = '',
  ...props
}) => {const { t } = useTranslation();
  const classes = [
  'ds-button-group',
  `ds-button-group--${orientation}`,
  `ds-button-group--${size}`,
  className].
  filter(Boolean).join(' ');

  return (
    <div className={classes} role="group" {...props}>
      {React.Children.map(children, (child, index) => {
        if (React.isValidElement(child) && child.type === Button) {
          return React.cloneElement(child, {
            size,
            className: [
            child.props.className,
            index === 0 && 'ds-button--group-first',
            index === React.Children.count(children) - 1 && 'ds-button--group-last'].
            filter(Boolean).join(' ')
          });
        }
        return child;
      })}
    </div>);

};

// Icon Button Component
export const IconButton = forwardRef(({
  icon,
  label,
  variant = 'ghost',
  size = 'md',
  className = '',
  ...props
}, ref) => {
  return (
    <Button
      ref={ref}
      variant={variant}
      size={size}
      className={`ds-icon-button ${className}`}
      ariaLabel={label}
      tooltip={label}
      {...props}>

      {icon}
    </Button>);

});

IconButton.displayName = 'IconButton';

// Floating Action Button
export const FAB = forwardRef(({
  icon,
  label,
  position = 'bottom-right',
  mini = false,
  extended = false,
  className = '',
  ...props
}, ref) => {
  const classes = [
  'ds-fab',
  `ds-fab--${position}`,
  mini && 'ds-fab--mini',
  extended && 'ds-fab--extended',
  className].
  filter(Boolean).join(' ');

  return (
    <motion.button
      ref={ref}
      className={classes}
      aria-label={label}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: 'spring', stiffness: 260, damping: 20 }}
      {...props}>

      <span className="ds-fab__icon">{icon}</span>
      {extended && <span className="ds-fab__label">{label}</span>}
    </motion.button>);

});

FAB.displayName = 'FAB';