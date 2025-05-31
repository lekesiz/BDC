import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    supportFile: 'cypress/support/e2e.js',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    fixturesFolder: 'cypress/fixtures',
    screenshotsFolder: 'cypress/screenshots',
    videosFolder: 'cypress/videos',
    setupNodeEvents(on, config) {
      // Import database seeding utilities
      const DatabaseSeeder = require('./cypress/support/database-seeding');
      const seeder = new DatabaseSeeder();

      // Database seeding tasks
      on('task', {
        async seedDatabase() {
          try {
            const result = await seeder.seedAll();
            return result;
          } catch (error) {
            console.error('Database seeding failed:', error);
            throw error;
          }
        },
        async clearDatabase() {
          try {
            await seeder.clearDatabase();
            return null;
          } catch (error) {
            console.error('Database clearing failed:', error);
            throw error;
          }
        },
        async createTestUser(userData) {
          try {
            const result = await seeder.createTestUser(userData);
            return result;
          } catch (error) {
            console.error('Test user creation failed:', error);
            throw error;
          }
        },
        async seedUsers() {
          try {
            await seeder.seedUsers();
            return seeder.seededData.users;
          } catch (error) {
            console.error('User seeding failed:', error);
            throw error;
          }
        },
        async seedBeneficiaries() {
          try {
            await seeder.seedBeneficiaries();
            return seeder.seededData.beneficiaries;
          } catch (error) {
            console.error('Beneficiary seeding failed:', error);
            throw error;
          }
        },
        async seedPrograms() {
          try {
            await seeder.seedPrograms();
            return seeder.seededData.programs;
          } catch (error) {
            console.error('Program seeding failed:', error);
            throw error;
          }
        },
        async seedEvaluations() {
          try {
            await seeder.seedEvaluations();
            return seeder.seededData.evaluations;
          } catch (error) {
            console.error('Evaluation seeding failed:', error);
            throw error;
          }
        },
        async getSeededData() {
          return seeder.getSeededData();
        },
        log(message) {
          console.log(message);
          return null;
        }
      });

      // Browser launch options
      on('before:browser:launch', (browser, launchOptions) => {
        if (browser.name === 'chrome' && browser.isHeadless) {
          launchOptions.args.push('--disable-gpu');
          launchOptions.args.push('--no-sandbox');
          launchOptions.args.push('--disable-dev-shm-usage');
        }
        return launchOptions;
      });

      // Set environment variables based on NODE_ENV
      if (config.env.NODE_ENV === 'ci') {
        config.baseUrl = 'http://localhost:3000';
        config.env.apiUrl = 'http://localhost:3001/api';
      }

      return config;
    },
    // Test retry configuration
    retries: {
      runMode: 2,
      openMode: 0
    },
    // Experimental features
    experimentalStudio: true,
    experimentalWebKitSupport: true,
  },
  // Component testing configuration
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
    specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/component.js'
  },
  // Global configuration
  viewportWidth: 1280,
  viewportHeight: 720,
  video: true,
  videoCompression: 32,
  screenshotOnRunFailure: true,
  defaultCommandTimeout: 10000,
  requestTimeout: 15000,
  responseTimeout: 15000,
  pageLoadTimeout: 30000,
  // Test isolation
  testIsolation: true,
  // Environment variables
  env: {
    apiUrl: 'http://localhost:5001/api',
    dbUrl: 'mongodb://localhost:27017/bdc_test',
    coverage: false,
    // Test user credentials
    adminEmail: 'admin@bdc.test',
    adminPassword: 'Admin123!Test',
    trainerEmail: 'trainer@bdc.test',
    trainerPassword: 'Trainer123!Test',
    studentEmail: 'student@bdc.test',
    studentPassword: 'Student123!Test',
    tenantEmail: 'tenant@bdc.test',
    tenantPassword: 'Tenant123!Test',
  },
});