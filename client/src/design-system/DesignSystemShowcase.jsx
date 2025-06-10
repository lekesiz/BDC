// Design System Showcase Component
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Button, 
  ButtonGroup, 
  IconButton, 
  FAB 
} from './components/Button';
import { 
  LoadingStates, 
  ErrorStates, 
  EmptyStates, 
  SkeletonScreen 
} from './states';
import { useTheme } from './hooks/useTheme';
import { useBreakpoint } from './hooks/useBreakpoint';
import { useAccessibility } from './hooks/useAccessibility';
import { cn } from './utils/cn';
import './showcase.css';

export const DesignSystemShowcase = () => {
  const { currentTheme, toggleTheme } = useTheme();
  const { currentBreakpoint, isMobile } = useBreakpoint();
  const { announce } = useAccessibility();
  const [activeTab, setActiveTab] = useState('components');
  const [showLoading, setShowLoading] = useState(false);
  const [showError, setShowError] = useState(false);

  const sections = {
    components: 'Components',
    states: 'States',
    animations: 'Animations',
    accessibility: 'Accessibility',
    themes: 'Themes'
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    announce(`Switched to ${sections[tab]} section`);
  };

  return (
    <div className="ds-showcase">
      <header className="ds-showcase__header">
        <h1>BDC Design System</h1>
        <p>Comprehensive UI/UX Components with WCAG 2.1 Compliance</p>
        <div className="ds-showcase__controls">
          <Button
            variant="secondary"
            onClick={toggleTheme}
            icon={currentTheme === 'light' ? '🌙' : '☀️'}
          >
            {currentTheme === 'light' ? 'Dark Mode' : 'Light Mode'}
          </Button>
          <span className="ds-showcase__info">
            Current breakpoint: {currentBreakpoint}
          </span>
        </div>
      </header>

      <nav className="ds-showcase__nav">
        {Object.entries(sections).map(([key, label]) => (
          <button
            key={key}
            className={cn(
              'ds-showcase__tab',
              activeTab === key && 'ds-showcase__tab--active'
            )}
            onClick={() => handleTabChange(key)}
            aria-selected={activeTab === key}
            role="tab"
          >
            {label}
          </button>
        ))}
      </nav>

      <main className="ds-showcase__content">
        {activeTab === 'components' && (
          <ComponentsSection />
        )}
        
        {activeTab === 'states' && (
          <StatesSection 
            showLoading={showLoading}
            setShowLoading={setShowLoading}
            showError={showError}
            setShowError={setShowError}
          />
        )}
        
        {activeTab === 'animations' && (
          <AnimationsSection />
        )}
        
        {activeTab === 'accessibility' && (
          <AccessibilitySection />
        )}
        
        {activeTab === 'themes' && (
          <ThemesSection />
        )}
      </main>
    </div>
  );
};

// Components Section
const ComponentsSection = () => {
  const [loading, setLoading] = useState(false);

  return (
    <section className="ds-showcase__section">
      <h2>Components</h2>
      
      <div className="ds-showcase__group">
        <h3>Buttons</h3>
        <div className="ds-showcase__row">
          <Button variant="primary">Primary Button</Button>
          <Button variant="secondary">Secondary Button</Button>
          <Button variant="ghost">Ghost Button</Button>
          <Button variant="danger">Danger Button</Button>
        </div>
        
        <h4>Button Sizes</h4>
        <div className="ds-showcase__row">
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
        </div>
        
        <h4>Button States</h4>
        <div className="ds-showcase__row">
          <Button disabled>Disabled</Button>
          <Button loading loadingText="Processing...">Loading</Button>
          <Button 
            icon="📤" 
            iconPosition="left"
          >
            With Icon
          </Button>
        </div>
        
        <h4>Button Group</h4>
        <ButtonGroup>
          <Button>First</Button>
          <Button>Second</Button>
          <Button>Third</Button>
        </ButtonGroup>
        
        <h4>Icon Buttons</h4>
        <div className="ds-showcase__row">
          <IconButton icon="🔍" label="Search" />
          <IconButton icon="⚙️" label="Settings" variant="primary" />
          <IconButton icon="❌" label="Close" variant="danger" />
        </div>
        
        <h4>Floating Action Button</h4>
        <div style={{ position: 'relative', height: '100px' }}>
          <FAB icon="➕" label="Add" position="bottom-right" />
        </div>
      </div>
    </section>
  );
};

// States Section
const StatesSection = ({ showLoading, setShowLoading, showError, setShowError }) => {
  return (
    <section className="ds-showcase__section">
      <h2>States</h2>
      
      <div className="ds-showcase__group">
        <h3>Loading States</h3>
        <div className="ds-showcase__row">
          <LoadingStates.Spinner size="sm" />
          <LoadingStates.Spinner size="md" />
          <LoadingStates.Spinner size="lg" />
          <LoadingStates.LoadingDots />
        </div>
        
        <div className="ds-showcase__demo">
          <LoadingStates.ProgressBar value={65} max={100} />
        </div>
        
        <div className="ds-showcase__demo">
          <LoadingStates.CircularProgress value={75} max={100} />
        </div>
        
        <h3>Skeleton Screens</h3>
        <div className="ds-showcase__demo">
          <SkeletonScreen.Card />
        </div>
        
        <div className="ds-showcase__demo">
          <SkeletonScreen.ListItem />
          <SkeletonScreen.ListItem />
          <SkeletonScreen.ListItem />
        </div>
        
        <h3>Error States</h3>
        <Button 
          variant="danger" 
          onClick={() => setShowError(true)}
        >
          Show Error State
        </Button>
        
        {showError && (
          <div className="ds-showcase__demo">
            <ErrorStates.ErrorState
              type="error"
              title="Something went wrong"
              message="Please try again or contact support"
              actions={
                <Button onClick={() => setShowError(false)}>
                  Try Again
                </Button>
              }
            />
          </div>
        )}
        
        <h3>Empty States</h3>
        <div className="ds-showcase__demo">
          <EmptyStates.NoData
            onAddData={() => console.log('Add data clicked')}
          />
        </div>
      </div>
    </section>
  );
};

// Animations Section
const AnimationsSection = () => {
  const [showAnimation, setShowAnimation] = useState(false);

  return (
    <section className="ds-showcase__section">
      <h2>Animations & Micro-interactions</h2>
      
      <div className="ds-showcase__group">
        <h3>Entrance Animations</h3>
        <Button 
          onClick={() => setShowAnimation(!showAnimation)}
          variant="primary"
        >
          Toggle Animation Demo
        </Button>
        
        {showAnimation && (
          <div className="ds-showcase__animation-grid">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="ds-showcase__animation-box"
            >
              Fade In
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="ds-showcase__animation-box"
            >
              Slide Up
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="ds-showcase__animation-box"
            >
              Scale In
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, rotate: -10 }}
              animate={{ opacity: 1, rotate: 0 }}
              exit={{ opacity: 0, rotate: 10 }}
              className="ds-showcase__animation-box"
            >
              Rotate In
            </motion.div>
          </div>
        )}
        
        <h3>Hover Effects</h3>
        <div className="ds-showcase__row">
          <motion.div
            className="ds-showcase__hover-box"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Scale on Hover
          </motion.div>
          
          <motion.div
            className="ds-showcase__hover-box"
            whileHover={{ y: -5 }}
          >
            Lift on Hover
          </motion.div>
          
          <motion.div
            className="ds-showcase__hover-box"
            whileHover={{ rotate: 5 }}
          >
            Rotate on Hover
          </motion.div>
        </div>
        
        <h3>Loading Animations</h3>
        <div className="ds-showcase__row">
          <motion.div
            className="ds-showcase__loading-dot"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [1, 0.5, 1]
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          
          <motion.div
            className="ds-showcase__loading-bar"
            animate={{
              scaleX: [0, 1, 0],
              originX: 0
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </div>
      </div>
    </section>
  );
};

// Accessibility Section
const AccessibilitySection = () => {
  const { announce } = useAccessibility();

  return (
    <section className="ds-showcase__section">
      <h2>Accessibility Features</h2>
      
      <div className="ds-showcase__group">
        <h3>WCAG 2.1 Compliance</h3>
        <ul className="ds-showcase__list">
          <li>✅ Level AA color contrast ratios</li>
          <li>✅ Keyboard navigation support</li>
          <li>✅ Screen reader compatibility</li>
          <li>✅ Focus indicators</li>
          <li>✅ Reduced motion support</li>
          <li>✅ Touch target sizes (44x44px minimum)</li>
          <li>✅ ARIA attributes and live regions</li>
          <li>✅ Semantic HTML</li>
        </ul>
        
        <h3>Keyboard Navigation Demo</h3>
        <p>Try navigating with Tab, Arrow keys, Enter, and Escape</p>
        <div className="ds-showcase__keyboard-demo">
          <Button>First</Button>
          <Button>Second</Button>
          <Button>Third</Button>
        </div>
        
        <h3>Screen Reader Announcements</h3>
        <Button
          onClick={() => announce('Action completed successfully!', 'polite')}
        >
          Announce Success
        </Button>
        
        <h3>Focus Management</h3>
        <p>Focus is trapped within modals and returned on close</p>
        
        <h3>High Contrast Mode</h3>
        <p>The design system automatically adapts to high contrast preferences</p>
      </div>
    </section>
  );
};

// Themes Section
const ThemesSection = () => {
  const { currentTheme, setTheme } = useTheme();

  return (
    <section className="ds-showcase__section">
      <h2>Theme System</h2>
      
      <div className="ds-showcase__group">
        <h3>Available Themes</h3>
        <div className="ds-showcase__row">
          <Button
            variant={currentTheme === 'light' ? 'primary' : 'secondary'}
            onClick={() => setTheme('light')}
          >
            Light Theme
          </Button>
          <Button
            variant={currentTheme === 'dark' ? 'primary' : 'secondary'}
            onClick={() => setTheme('dark')}
          >
            Dark Theme
          </Button>
        </div>
        
        <h3>Theme Features</h3>
        <ul className="ds-showcase__list">
          <li>🎨 CSS Variables for easy customization</li>
          <li>🌓 Automatic dark mode detection</li>
          <li>💾 Theme persistence in localStorage</li>
          <li>🎯 Component-level theming</li>
          <li>🔄 Smooth theme transitions</li>
          <li>♿ High contrast mode support</li>
        </ul>
        
        <h3>Color Palette</h3>
        <div className="ds-showcase__colors">
          <div className="ds-showcase__color-group">
            <h4>Primary Colors</h4>
            <div className="ds-showcase__color-swatches">
              <div className="ds-showcase__color-swatch ds-showcase__color-swatch--primary-50">50</div>
              <div className="ds-showcase__color-swatch ds-showcase__color-swatch--primary-100">100</div>
              <div className="ds-showcase__color-swatch ds-showcase__color-swatch--primary-200">200</div>
              <div className="ds-showcase__color-swatch ds-showcase__color-swatch--primary-300">300</div>
              <div className="ds-showcase__color-swatch ds-showcase__color-swatch--primary-400">400</div>
              <div className="ds-showcase__color-swatch ds-showcase__color-swatch--primary-500">500</div>
              <div className="ds-showcase__color-swatch ds-showcase__color-swatch--primary-600">600</div>
              <div className="ds-showcase__color-swatch ds-showcase__color-swatch--primary-700">700</div>
              <div className="ds-showcase__color-swatch ds-showcase__color-swatch--primary-800">800</div>
              <div className="ds-showcase__color-swatch ds-showcase__color-swatch--primary-900">900</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DesignSystemShowcase;