# PWA Icons Directory

This directory contains all the icons and images needed for the Progressive Web App functionality.

## Required Icons

### Standard Icons (any purpose)
- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

### Maskable Icons (for adaptive icons)
- maskable-icon-72x72.png
- maskable-icon-96x96.png
- maskable-icon-128x128.png
- maskable-icon-144x144.png
- maskable-icon-152x152.png
- maskable-icon-192x192.png
- maskable-icon-384x384.png
- maskable-icon-512x512.png

### Shortcut Icons
- shortcut-dashboard-96x96.png
- shortcut-beneficiaries-96x96.png
- shortcut-evaluations-96x96.png
- shortcut-calendar-96x96.png

### Notification Icons
- badge-72x72.png
- checkmark.png
- xmark.png

## Icon Guidelines

1. **Standard Icons**: Should have padding and work well on any background
2. **Maskable Icons**: Should fill the entire canvas and work when cropped in different shapes
3. **High Contrast**: Ensure icons work in both light and dark themes
4. **SVG Source**: Keep SVG source files for easy regeneration at different sizes

## Tools for Icon Generation

- [PWA Icon Generator](https://www.pwabuilder.com/imageGenerator)
- [Maskable.app](https://maskable.app/) for testing maskable icons
- [Favicon Generator](https://realfavicongenerator.net/)

## Testing

Test icons using:
- Chrome DevTools > Application > Manifest
- [Maskable.app](https://maskable.app/)
- Actual device installation