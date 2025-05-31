// ***********************************************
// Component testing support file
// ***********************************************

import './commands';
import { mount } from 'cypress/react18';

// Mount React components
Cypress.Commands.add('mount', mount);

// Example custom mount with providers
Cypress.Commands.add('mountWithProviders', (component, options = {}) => {
  const { providers = [], ...mountOptions } = options;
  
  let wrappedComponent = component;
  
  // Wrap with providers if any
  providers.forEach(Provider => {
    wrappedComponent = Provider({ children: wrappedComponent });
  });
  
  return cy.mount(wrappedComponent, mountOptions);
});