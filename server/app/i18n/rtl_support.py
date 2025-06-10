"""
RTL Support
Provides Right-to-Left language support utilities
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from .config import I18nConfig

class RTLSupport:
    """Support for Right-to-Left languages."""
    
    def __init__(self):
        """Initialize RTL support."""
        self.config = I18nConfig()
        self.rtl_languages = set(self.config.RTL_LANGUAGES)
        
        # RTL Unicode ranges
        self.rtl_ranges = [
            (0x0590, 0x05FF),  # Hebrew
            (0x0600, 0x06FF),  # Arabic
            (0x0700, 0x074F),  # Syriac
            (0x0750, 0x077F),  # Arabic Supplement
            (0x0780, 0x07BF),  # Thaana
            (0x07C0, 0x07FF),  # N'Ko
            (0x0800, 0x083F),  # Samaritan
            (0x0840, 0x085F),  # Mandaic
            (0x08A0, 0x08FF),  # Arabic Extended-A
            (0xFB1D, 0xFB4F),  # Hebrew presentation forms
            (0xFB50, 0xFDFF),  # Arabic presentation forms A
            (0xFE70, 0xFEFF),  # Arabic presentation forms B
        ]
        
        # Directional marks
        self.ltr_mark = '\u200E'  # LEFT-TO-RIGHT MARK
        self.rtl_mark = '\u200F'  # RIGHT-TO-LEFT MARK
        self.ltr_embedding = '\u202A'  # LEFT-TO-RIGHT EMBEDDING
        self.rtl_embedding = '\u202B'  # RIGHT-TO-LEFT EMBEDDING
        self.pop_directional = '\u202C'  # POP DIRECTIONAL FORMATTING
        self.ltr_override = '\u202D'  # LEFT-TO-RIGHT OVERRIDE
        self.rtl_override = '\u202E'  # RIGHT-TO-LEFT OVERRIDE
    
    def is_rtl_language(self, language_code: str) -> bool:
        """Check if a language is RTL."""
        return language_code in self.rtl_languages
    
    def get_rtl_info(self, language_code: str) -> Dict[str, Any]:
        """Get RTL information for a language."""
        is_rtl = self.is_rtl_language(language_code)
        
        return {
            'is_rtl': is_rtl,
            'direction': 'rtl' if is_rtl else 'ltr',
            'alignment': 'right' if is_rtl else 'left',
            'opposite_alignment': 'left' if is_rtl else 'right',
            'start': 'right' if is_rtl else 'left',
            'end': 'left' if is_rtl else 'right',
            'margin_start': 'margin-right' if is_rtl else 'margin-left',
            'margin_end': 'margin-left' if is_rtl else 'margin-right',
            'padding_start': 'padding-right' if is_rtl else 'padding-left',
            'padding_end': 'padding-left' if is_rtl else 'padding-right',
            'border_start': 'border-right' if is_rtl else 'border-left',
            'border_end': 'border-left' if is_rtl else 'border-right',
            'float_start': 'right' if is_rtl else 'left',
            'float_end': 'left' if is_rtl else 'right',
            'text_align': 'right' if is_rtl else 'left'
        }
    
    def detect_text_direction(self, text: str) -> str:
        """
        Detect the primary direction of a text string.
        
        Args:
            text: Text to analyze
            
        Returns:
            'rtl', 'ltr', or 'neutral'
        """
        if not text:
            return 'neutral'
        
        rtl_count = 0
        ltr_count = 0
        
        for char in text:
            char_code = ord(char)
            
            # Check if character is in RTL range
            is_rtl = False
            for start, end in self.rtl_ranges:
                if start <= char_code <= end:
                    is_rtl = True
                    break
            
            if is_rtl:
                rtl_count += 1
            elif char.isalpha():
                # Latin characters are LTR
                ltr_count += 1
        
        total_directional = rtl_count + ltr_count
        
        if total_directional == 0:
            return 'neutral'
        
        rtl_percentage = rtl_count / total_directional
        
        if rtl_percentage > 0.6:
            return 'rtl'
        elif rtl_percentage < 0.4:
            return 'ltr'
        else:
            return 'mixed'
    
    def add_direction_marks(self, text: str, direction: str = 'auto') -> str:
        """
        Add directional marks to text for proper display.
        
        Args:
            text: Text to process
            direction: 'ltr', 'rtl', or 'auto'
            
        Returns:
            Text with directional marks
        """
        if not text:
            return text
        
        if direction == 'auto':
            direction = self.detect_text_direction(text)
        
        if direction == 'rtl':
            return f"{self.rtl_mark}{text}{self.rtl_mark}"
        elif direction == 'ltr':
            return f"{self.ltr_mark}{text}{self.ltr_mark}"
        else:
            return text
    
    def wrap_mixed_content(self, text: str, base_direction: str = 'ltr') -> str:
        """
        Wrap mixed directional content for proper display.
        
        Args:
            text: Text containing mixed directional content
            base_direction: Base direction of the document
            
        Returns:
            Text with proper directional formatting
        """
        if not text:
            return text
        
        # Pattern to match potential RTL text
        rtl_pattern = r'[\u0590-\u08FF\uFB1D-\uFEFF]+'
        
        def replace_rtl(match):
            rtl_text = match.group(0)
            if base_direction == 'ltr':
                # Wrap RTL text in LTR context
                return f"{self.rtl_embedding}{rtl_text}{self.pop_directional}"
            else:
                # Just add RTL marks
                return f"{self.rtl_mark}{rtl_text}{self.rtl_mark}"
        
        # Replace RTL segments
        result = re.sub(rtl_pattern, replace_rtl, text)
        
        # Pattern to match potential LTR text (Latin letters and numbers)
        ltr_pattern = r'[A-Za-z0-9]+'
        
        def replace_ltr(match):
            ltr_text = match.group(0)
            if base_direction == 'rtl':
                # Wrap LTR text in RTL context
                return f"{self.ltr_embedding}{ltr_text}{self.pop_directional}"
            else:
                # Just add LTR marks
                return f"{self.ltr_mark}{ltr_text}{self.ltr_mark}"
        
        # Only process LTR in RTL context
        if base_direction == 'rtl':
            result = re.sub(ltr_pattern, replace_ltr, result)
        
        return result
    
    def mirror_punctuation(self, text: str, is_rtl: bool) -> str:
        """
        Mirror punctuation marks for RTL languages.
        
        Args:
            text: Text containing punctuation
            is_rtl: Whether to mirror for RTL
            
        Returns:
            Text with mirrored punctuation
        """
        if not is_rtl or not text:
            return text
        
        # Punctuation pairs to mirror
        mirror_map = {
            '(': ')',
            ')': '(',
            '[': ']',
            ']': '[',
            '{': '}',
            '}': '{',
            '<': '>',
            '>': '<',
            '«': '»',
            '»': '«',
            '‹': '›',
            '›': '‹',
        }
        
        result = []
        for char in text:
            if char in mirror_map:
                result.append(mirror_map[char])
            else:
                result.append(char)
        
        return ''.join(result)
    
    def convert_css_for_rtl(self, css_rules: Dict[str, str]) -> Dict[str, str]:
        """
        Convert CSS rules for RTL layout.
        
        Args:
            css_rules: Dictionary of CSS property-value pairs
            
        Returns:
            Converted CSS rules
        """
        rtl_rules = {}
        
        # Properties to swap
        swap_properties = {
            'left': 'right',
            'right': 'left',
            'margin-left': 'margin-right',
            'margin-right': 'margin-left',
            'padding-left': 'padding-right',
            'padding-right': 'padding-left',
            'border-left': 'border-right',
            'border-right': 'border-left',
            'border-left-width': 'border-right-width',
            'border-right-width': 'border-left-width',
            'border-left-color': 'border-right-color',
            'border-right-color': 'border-left-color',
            'border-left-style': 'border-right-style',
            'border-right-style': 'border-left-style',
            'border-top-left-radius': 'border-top-right-radius',
            'border-top-right-radius': 'border-top-left-radius',
            'border-bottom-left-radius': 'border-bottom-right-radius',
            'border-bottom-right-radius': 'border-bottom-left-radius'
        }
        
        for prop, value in css_rules.items():
            # Swap properties
            if prop in swap_properties:
                # Check if the opposite property exists
                opposite = swap_properties[prop]
                if opposite in css_rules:
                    # Swap values
                    rtl_rules[prop] = css_rules[opposite]
                    rtl_rules[opposite] = value
                else:
                    # Just rename the property
                    rtl_rules[opposite] = value
            
            # Handle text-align
            elif prop == 'text-align':
                if value == 'left':
                    rtl_rules[prop] = 'right'
                elif value == 'right':
                    rtl_rules[prop] = 'left'
                else:
                    rtl_rules[prop] = value
            
            # Handle float
            elif prop == 'float':
                if value == 'left':
                    rtl_rules[prop] = 'right'
                elif value == 'right':
                    rtl_rules[prop] = 'left'
                else:
                    rtl_rules[prop] = value
            
            # Handle clear
            elif prop == 'clear':
                if value == 'left':
                    rtl_rules[prop] = 'right'
                elif value == 'right':
                    rtl_rules[prop] = 'left'
                else:
                    rtl_rules[prop] = value
            
            # Handle background-position
            elif prop == 'background-position' and isinstance(value, str):
                if 'left' in value:
                    rtl_rules[prop] = value.replace('left', 'right')
                elif 'right' in value:
                    rtl_rules[prop] = value.replace('right', 'left')
                else:
                    rtl_rules[prop] = value
            
            # Handle transform
            elif prop == 'transform' and isinstance(value, str):
                # Mirror translateX values
                if 'translateX' in value:
                    rtl_rules[prop] = re.sub(
                        r'translateX\(([-\d.]+)([a-z%]*)\)',
                        lambda m: f'translateX({-float(m.group(1))}{m.group(2)})',
                        value
                    )
                else:
                    rtl_rules[prop] = value
            
            # Default: keep as is
            else:
                if prop not in swap_properties.values():
                    rtl_rules[prop] = value
        
        return rtl_rules
    
    def get_bidi_class_names(self, base_class: str, is_rtl: bool) -> List[str]:
        """
        Get bidirectional class names for CSS.
        
        Args:
            base_class: Base CSS class name
            is_rtl: Whether RTL is active
            
        Returns:
            List of class names to apply
        """
        classes = [base_class]
        
        if is_rtl:
            classes.extend([
                f"{base_class}-rtl",
                'rtl'
            ])
        else:
            classes.extend([
                f"{base_class}-ltr",
                'ltr'
            ])
        
        return classes