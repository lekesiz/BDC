import React, { useState } from 'react';
import { 
  Eye, 
  Volume2, 
  Keyboard, 
  Type, 
  Palette, 
  Settings,
  RotateCcw,
  Save,
  Moon,
  Sun,
  VolumeX,
  MousePointer,
  Focus,
  Contrast,
  ZoomIn,
  Play,
  Pause
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { ResponsiveContainer, ResponsiveCard } from '@/components/responsive/ResponsiveContainer';
import { useAccessibility } from './AccessibilityProvider';
import { cn } from '@/lib/utils';

const AccessibilitySettings = ({ isOpen, onClose }) => {
  const { settings, updateSetting, updateSettings, resetSettings, announce } = useAccessibility();
  const [activeTab, setActiveTab] = useState('visual');
  const [hasChanges, setHasChanges] = useState(false);

  const tabs = [
    { id: 'visual', label: 'Visual', icon: Eye },
    { id: 'audio', label: 'Audio', icon: Volume2 },
    { id: 'navigation', label: 'Navigation', icon: Keyboard },
    { id: 'content', label: 'Content', icon: Type },
    { id: 'advanced', label: 'Advanced', icon: Settings }
  ];

  const handleSettingChange = (key, value) => {
    updateSetting(key, value);
    setHasChanges(true);
    announce(`${key} setting changed to ${value}`);
  };

  const handleSave = () => {
    setHasChanges(false);
    announce('Accessibility settings saved');
    if (onClose) onClose();
  };

  const handleReset = () => {
    resetSettings();
    setHasChanges(false);
    announce('Accessibility settings reset to defaults');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <ResponsiveContainer className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <ResponsiveCard>
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>Accessibility Settings</span>
              </CardTitle>
              <div className="flex items-center space-x-2">
                {hasChanges && (
                  <span className="text-sm text-orange-600 bg-orange-100 px-2 py-1 rounded">
                    Unsaved changes
                  </span>
                )}
                <Button variant="ghost" size="sm" onClick={onClose}>
                  ×
                </Button>
              </div>
            </div>
          </CardHeader>

          <CardContent className="p-0">
            <div className="flex flex-col md:flex-row">
              {/* Sidebar Navigation */}
              <div className="w-full md:w-64 border-b md:border-b-0 md:border-r">
                <nav className="p-4">
                  <ul className="space-y-1">
                    {tabs.map((tab) => {
                      const Icon = tab.icon;
                      return (
                        <li key={tab.id}>
                          <button
                            onClick={() => setActiveTab(tab.id)}
                            className={cn(
                              'w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors',
                              activeTab === tab.id
                                ? 'bg-blue-100 text-blue-700'
                                : 'hover:bg-gray-100'
                            )}
                            aria-current={activeTab === tab.id ? 'page' : undefined}
                          >
                            <Icon className="h-4 w-4" />
                            <span className="text-sm font-medium">{tab.label}</span>
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </nav>
              </div>

              {/* Settings Content */}
              <div className="flex-1 p-6">
                {activeTab === 'visual' && (
                  <VisualSettings settings={settings} onChange={handleSettingChange} />
                )}
                {activeTab === 'audio' && (
                  <AudioSettings settings={settings} onChange={handleSettingChange} />
                )}
                {activeTab === 'navigation' && (
                  <NavigationSettings settings={settings} onChange={handleSettingChange} />
                )}
                {activeTab === 'content' && (
                  <ContentSettings settings={settings} onChange={handleSettingChange} />
                )}
                {activeTab === 'advanced' && (
                  <AdvancedSettings settings={settings} onChange={handleSettingChange} />
                )}
              </div>
            </div>
          </CardContent>

          {/* Footer */}
          <div className="border-t p-4 flex items-center justify-between">
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset to Defaults
            </Button>
            
            <div className="flex items-center space-x-2">
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button onClick={handleSave}>
                <Save className="h-4 w-4 mr-2" />
                Save Settings
              </Button>
            </div>
          </div>
        </ResponsiveCard>
      </ResponsiveContainer>
    </div>
  );
};

// Visual Settings Component
const VisualSettings = ({ settings, onChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Visual Preferences</h3>
        
        {/* Font Size */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Font Size
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {['small', 'medium', 'large', 'extra-large'].map((size) => (
                <button
                  key={size}
                  onClick={() => onChange('fontSize', size)}
                  className={cn(
                    'p-3 text-center border rounded-lg transition-colors',
                    settings.fontSize === size
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-blue-300'
                  )}
                >
                  <ZoomIn className="h-4 w-4 mx-auto mb-1" />
                  <span className="text-xs font-medium capitalize">{size}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Contrast */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contrast & Theme
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              {[
                { value: 'normal', label: 'Normal', icon: Sun },
                { value: 'high', label: 'High Contrast', icon: Contrast },
                { value: 'dark', label: 'Dark Theme', icon: Moon }
              ].map((option) => {
                const Icon = option.icon;
                return (
                  <button
                    key={option.value}
                    onClick={() => onChange('contrast', option.value)}
                    className={cn(
                      'p-3 text-center border rounded-lg transition-colors',
                      settings.contrast === option.value
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-300 hover:border-blue-300'
                    )}
                  >
                    <Icon className="h-4 w-4 mx-auto mb-1" />
                    <span className="text-xs font-medium">{option.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Color Blind Mode */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Color Vision
            </label>
            <select
              value={settings.colorBlindMode}
              onChange={(e) => onChange('colorBlindMode', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="none">Normal vision</option>
              <option value="protanopia">Protanopia (Red-blind)</option>
              <option value="deuteranopia">Deuteranopia (Green-blind)</option>
              <option value="tritanopia">Tritanopia (Blue-blind)</option>
            </select>
          </div>

          {/* Motion and Animation */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Reduce Motion</label>
              <p className="text-xs text-gray-500">Minimize animations and transitions</p>
            </div>
            <Switch
              checked={settings.reducedMotion}
              onCheckedChange={(checked) => onChange('reducedMotion', checked)}
            />
          </div>

          {/* Focus Indicators */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Enhanced Focus</label>
              <p className="text-xs text-gray-500">Show prominent focus indicators</p>
            </div>
            <Switch
              checked={settings.focusIndicators}
              onCheckedChange={(checked) => onChange('focusIndicators', checked)}
            />
          </div>

          {/* Underline Links */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Underline Links</label>
              <p className="text-xs text-gray-500">Always underline clickable links</p>
            </div>
            <Switch
              checked={settings.underlineLinks}
              onCheckedChange={(checked) => onChange('underlineLinks', checked)}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Audio Settings Component
const AudioSettings = ({ settings, onChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Audio Preferences</h3>
        
        <div className="space-y-4">
          {/* Sound Effects */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Sound Effects</label>
              <p className="text-xs text-gray-500">Play sounds for UI interactions</p>
            </div>
            <Switch
              checked={settings.soundEffects}
              onCheckedChange={(checked) => onChange('soundEffects', checked)}
            />
          </div>

          {/* Voice Announcements */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Voice Announcements</label>
              <p className="text-xs text-gray-500">Speak important notifications aloud</p>
            </div>
            <Switch
              checked={settings.voiceAnnouncements}
              onCheckedChange={(checked) => onChange('voiceAnnouncements', checked)}
            />
          </div>

          {/* Audio Descriptions */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Audio Descriptions</label>
              <p className="text-xs text-gray-500">Describe visual content with audio</p>
            </div>
            <Switch
              checked={settings.audioDescriptions}
              onCheckedChange={(checked) => onChange('audioDescriptions', checked)}
            />
          </div>

          {/* Test Audio */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Test Audio Settings</h4>
            <div className="flex items-center space-x-2">
              <Button size="sm" variant="outline">
                <Play className="h-3 w-3 mr-1" />
                Test Sound
              </Button>
              <Button size="sm" variant="outline">
                <Volume2 className="h-3 w-3 mr-1" />
                Test Voice
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Navigation Settings Component
const NavigationSettings = ({ settings, onChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Navigation Preferences</h3>
        
        <div className="space-y-4">
          {/* Keyboard Navigation */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Keyboard Navigation</label>
              <p className="text-xs text-gray-500">Enable keyboard shortcuts and navigation</p>
            </div>
            <Switch
              checked={settings.keyboardNavigation}
              onCheckedChange={(checked) => onChange('keyboardNavigation', checked)}
            />
          </div>

          {/* Skip Links */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Skip Links</label>
              <p className="text-xs text-gray-500">Show links to skip to main content</p>
            </div>
            <Switch
              checked={settings.skipLinks}
              onCheckedChange={(checked) => onChange('skipLinks', checked)}
            />
          </div>

          {/* Breadcrumbs */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Breadcrumbs</label>
              <p className="text-xs text-gray-500">Show navigation breadcrumbs</p>
            </div>
            <Switch
              checked={settings.breadcrumbs}
              onCheckedChange={(checked) => onChange('breadcrumbs', checked)}
            />
          </div>

          {/* Heading Navigation */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Heading Navigation</label>
              <p className="text-xs text-gray-500">Navigate by headings with Alt+H</p>
            </div>
            <Switch
              checked={settings.headingNavigation}
              onCheckedChange={(checked) => onChange('headingNavigation', checked)}
            />
          </div>

          {/* Keyboard Shortcuts */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-blue-900 mb-2">Keyboard Shortcuts</h4>
            <div className="text-xs text-blue-800 space-y-1">
              <div><kbd className="px-1 bg-white rounded">Alt + S</kbd> Skip to content</div>
              <div><kbd className="px-1 bg-white rounded">Alt + H</kbd> Next heading</div>
              <div><kbd className="px-1 bg-white rounded">Tab</kbd> Next focusable element</div>
              <div><kbd className="px-1 bg-white rounded">Shift + Tab</kbd> Previous element</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Content Settings Component
const ContentSettings = ({ settings, onChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Preferences</h3>
        
        <div className="space-y-4">
          {/* Simplified UI */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Simplified Interface</label>
              <p className="text-xs text-gray-500">Show fewer UI elements and distractions</p>
            </div>
            <Switch
              checked={settings.simplifiedUI}
              onCheckedChange={(checked) => onChange('simplifiedUI', checked)}
            />
          </div>

          {/* Reading Mode */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Reading Mode</label>
              <p className="text-xs text-gray-500">Optimize text for better readability</p>
            </div>
            <Switch
              checked={settings.readingMode}
              onCheckedChange={(checked) => onChange('readingMode', checked)}
            />
          </div>

          {/* Dyslexia Font */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Dyslexia-Friendly Font</label>
              <p className="text-xs text-gray-500">Use fonts designed for dyslexia</p>
            </div>
            <Switch
              checked={settings.dyslexiaFont}
              onCheckedChange={(checked) => onChange('dyslexiaFont', checked)}
            />
          </div>

          {/* Line Height */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Line Height
            </label>
            <div className="grid grid-cols-3 gap-2">
              {['normal', 'relaxed', 'loose'].map((height) => (
                <button
                  key={height}
                  onClick={() => onChange('lineHeight', height)}
                  className={cn(
                    'p-2 text-center border rounded-lg transition-colors',
                    settings.lineHeight === height
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-blue-300'
                  )}
                >
                  <span className="text-xs font-medium capitalize">{height}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Letter Spacing */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Letter Spacing
            </label>
            <div className="grid grid-cols-3 gap-2">
              {['normal', 'wide', 'wider'].map((spacing) => (
                <button
                  key={spacing}
                  onClick={() => onChange('letterSpacing', spacing)}
                  className={cn(
                    'p-2 text-center border rounded-lg transition-colors',
                    settings.letterSpacing === spacing
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-blue-300'
                  )}
                >
                  <span className="text-xs font-medium capitalize">{spacing}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Auto-play */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Auto-play Media</label>
              <p className="text-xs text-gray-500">Automatically play videos and audio</p>
            </div>
            <Switch
              checked={settings.autoplay}
              onCheckedChange={(checked) => onChange('autoplay', checked)}
            />
          </div>

          {/* Tooltips */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Tooltips</label>
              <p className="text-xs text-gray-500">Show helpful tooltips on hover</p>
            </div>
            <Switch
              checked={settings.tooltips}
              onCheckedChange={(checked) => onChange('tooltips', checked)}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Advanced Settings Component
const AdvancedSettings = ({ settings, onChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Advanced Settings</h3>
        
        <div className="space-y-4">
          {/* Screen Reader */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Screen Reader Mode</label>
              <p className="text-xs text-gray-500">Optimize for screen reader users</p>
            </div>
            <Switch
              checked={settings.screenReader}
              onCheckedChange={(checked) => onChange('screenReader', checked)}
            />
          </div>

          {/* ARIA Live */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ARIA Live Announcements
            </label>
            <select
              value={settings.ariaLive}
              onChange={(e) => onChange('ariaLive', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="off">Off</option>
              <option value="polite">Polite</option>
              <option value="assertive">Assertive</option>
            </select>
          </div>

          {/* Role Descriptions */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Role Descriptions</label>
              <p className="text-xs text-gray-500">Provide detailed role information</p>
            </div>
            <Switch
              checked={settings.roleDescriptions}
              onCheckedChange={(checked) => onChange('roleDescriptions', checked)}
            />
          </div>

          {/* Landmark Labels */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Landmark Labels</label>
              <p className="text-xs text-gray-500">Label page landmarks for navigation</p>
            </div>
            <Switch
              checked={settings.landmarkLabels}
              onCheckedChange={(checked) => onChange('landmarkLabels', checked)}
            />
          </div>

          {/* Alternative Text */}
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Alternative Text</label>
              <p className="text-xs text-gray-500">Show alt text for images</p>
            </div>
            <Switch
              checked={settings.alternativeText}
              onCheckedChange={(checked) => onChange('alternativeText', checked)}
            />
          </div>

          {/* Accessibility Info */}
          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-green-900 mb-2">Accessibility Standards</h4>
            <p className="text-xs text-green-800">
              These settings help ensure compliance with WCAG 2.1 AA accessibility guidelines.
              For additional assistance, contact our support team.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccessibilitySettings;