# BDC Mobile App Development Guide

## Overview
This guide outlines the development plan for creating native mobile applications for the BDC platform on iOS and Android.

## Mobile App Architecture

### Technology Stack Options

#### Option 1: React Native (Recommended)
- **Pros**: Code reuse from web app, single codebase, good performance
- **Cons**: Some platform-specific features need native modules
- **Stack**: React Native, Redux/Context API, React Navigation

#### Option 2: Flutter
- **Pros**: Excellent performance, beautiful UI, single codebase
- **Cons**: Different language (Dart), less code reuse
- **Stack**: Flutter, Provider/Bloc, Flutter Navigation

#### Option 3: Native Development
- **iOS**: Swift, SwiftUI, Combine
- **Android**: Kotlin, Jetpack Compose, Coroutines
- **Pros**: Best performance, full platform features
- **Cons**: Two separate codebases, more expensive

## React Native Implementation Plan

### 1. Project Setup
```bash
# Create new React Native project
npx react-native init BDCMobile --template react-native-template-typescript

# Install dependencies
cd BDCMobile
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context
npm install @reduxjs/toolkit react-redux
npm install axios react-native-keychain
npm install react-native-vector-icons
npm install react-native-paper

# iOS specific
cd ios && pod install
```

### 2. Project Structure
```
BDCMobile/
├── src/
│   ├── components/
│   │   ├── common/
│   │   ├── auth/
│   │   └── beneficiary/
│   ├── screens/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── beneficiary/
│   │   └── settings/
│   ├── navigation/
│   │   ├── AuthNavigator.tsx
│   │   ├── AppNavigator.tsx
│   │   └── RootNavigator.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── storage.ts
│   ├── store/
│   │   ├── index.ts
│   │   ├── authSlice.ts
│   │   └── beneficiarySlice.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   └── helpers.ts
│   └── types/
│       └── index.ts
├── android/
├── ios/
└── index.js
```

### 3. Core Components

#### Authentication Service
```typescript
// src/services/auth.ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import Keychain from 'react-native-keychain';
import api from './api';

class AuthService {
  async login(email: string, password: string) {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, refresh_token, user } = response.data;
      
      // Store tokens securely
      await Keychain.setInternetCredentials(
        'bdc_api',
        'tokens',
        JSON.stringify({ access_token, refresh_token })
      );
      
      // Store user data
      await AsyncStorage.setItem('user', JSON.stringify(user));
      
      return { user, access_token };
    } catch (error) {
      throw new Error('Login failed');
    }
  }
  
  async logout() {
    await Keychain.resetInternetCredentials('bdc_api');
    await AsyncStorage.removeItem('user');
  }
  
  async getToken() {
    const credentials = await Keychain.getInternetCredentials('bdc_api');
    if (credentials) {
      const tokens = JSON.parse(credentials.password);
      return tokens.access_token;
    }
    return null;
  }
}

export default new AuthService();
```

#### API Client
```typescript
// src/services/api.ts
import axios from 'axios';
import AuthService from './auth';
import Config from 'react-native-config';

const api = axios.create({
  baseURL: Config.API_URL || 'https://api.yourdomain.com',
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(async (config) => {
  const token = await AuthService.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await AuthService.logout();
      // Navigate to login screen
    }
    return Promise.reject(error);
  }
);

export default api;
```

#### Navigation Setup
```typescript
// src/navigation/RootNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useSelector } from 'react-redux';

import AuthNavigator from './AuthNavigator';
import AppNavigator from './AppNavigator';
import { RootState } from '../store';

const Stack = createStackNavigator();

const RootNavigator = () => {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);
  
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="App" component={AppNavigator} />
        ) : (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default RootNavigator;
```

### 4. Key Screens

#### Login Screen
```typescript
// src/screens/auth/LoginScreen.tsx
import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import {
  TextInput,
  Button,
  Text,
  useTheme,
} from 'react-native-paper';
import { useDispatch } from 'react-redux';
import { login } from '../../store/authSlice';

const LoginScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const theme = useTheme();
  const dispatch = useDispatch();
  
  const handleLogin = async () => {
    setLoading(true);
    try {
      await dispatch(login({ email, password })).unwrap();
    } catch (error) {
      // Show error message
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.logoContainer}>
          <Text variant="headlineLarge">BDC</Text>
        </View>
        
        <View style={styles.formContainer}>
          <TextInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
            style={styles.input}
          />
          
          <TextInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            style={styles.input}
          />
          
          <Button
            mode="contained"
            onPress={handleLogin}
            loading={loading}
            style={styles.button}
          >
            Login
          </Button>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  formContainer: {
    width: '100%',
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 16,
  },
});

export default LoginScreen;
```

#### Dashboard Screen
```typescript
// src/screens/dashboard/DashboardScreen.tsx
import React, { useEffect, useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  useTheme,
} from 'react-native-paper';
import { useSelector, useDispatch } from 'react-redux';
import { fetchDashboardData } from '../../store/dashboardSlice';

const DashboardScreen = () => {
  const [refreshing, setRefreshing] = useState(false);
  const theme = useTheme();
  const dispatch = useDispatch();
  const { stats, loading } = useSelector(state => state.dashboard);
  
  useEffect(() => {
    loadDashboardData();
  }, []);
  
  const loadDashboardData = async () => {
    await dispatch(fetchDashboardData());
  };
  
  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };
  
  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.statsContainer}>
        <Card style={styles.statCard}>
          <Card.Content>
            <Title>{stats.totalBeneficiaries}</Title>
            <Paragraph>Total Beneficiaries</Paragraph>
          </Card.Content>
        </Card>
        
        <Card style={styles.statCard}>
          <Card.Content>
            <Title>{stats.activePrograms}</Title>
            <Paragraph>Active Programs</Paragraph>
          </Card.Content>
        </Card>
      </View>
      
      {/* Add more dashboard content */}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 16,
  },
  statCard: {
    flex: 1,
    marginHorizontal: 8,
  },
});

export default DashboardScreen;
```

### 5. Push Notifications

#### Setup Push Notifications
```typescript
// src/services/notifications.ts
import messaging from '@react-native-firebase/messaging';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from './api';

class NotificationService {
  async initialize() {
    // Request permission
    const authStatus = await messaging().requestPermission();
    const enabled =
      authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
      authStatus === messaging.AuthorizationStatus.PROVISIONAL;
    
    if (enabled) {
      // Get FCM token
      const token = await messaging().getToken();
      await this.saveTokenToServer(token);
      
      // Listen for token refresh
      messaging().onTokenRefresh(async (newToken) => {
        await this.saveTokenToServer(newToken);
      });
    }
  }
  
  async saveTokenToServer(token: string) {
    try {
      await api.post('/notifications/register', { token });
      await AsyncStorage.setItem('fcmToken', token);
    } catch (error) {
      console.error('Failed to save token:', error);
    }
  }
  
  setupNotificationHandlers() {
    // Foreground notifications
    messaging().onMessage(async (remoteMessage) => {
      console.log('Foreground notification:', remoteMessage);
      // Show local notification
    });
    
    // Background/quit notifications
    messaging().setBackgroundMessageHandler(async (remoteMessage) => {
      console.log('Background notification:', remoteMessage);
    });
  }
}

export default new NotificationService();
```

### 6. Offline Support

#### Offline Storage
```typescript
// src/services/offline.ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import api from './api';

class OfflineService {
  private queue: any[] = [];
  
  constructor() {
    this.loadQueue();
    this.setupNetworkListener();
  }
  
  async loadQueue() {
    const stored = await AsyncStorage.getItem('offline_queue');
    if (stored) {
      this.queue = JSON.parse(stored);
    }
  }
  
  async saveQueue() {
    await AsyncStorage.setItem('offline_queue', JSON.stringify(this.queue));
  }
  
  setupNetworkListener() {
    NetInfo.addEventListener((state) => {
      if (state.isConnected && this.queue.length > 0) {
        this.syncQueue();
      }
    });
  }
  
  async queueRequest(config: any) {
    this.queue.push({
      ...config,
      timestamp: Date.now(),
    });
    await this.saveQueue();
  }
  
  async syncQueue() {
    while (this.queue.length > 0) {
      const request = this.queue.shift();
      try {
        await api(request);
      } catch (error) {
        // Requeue if still offline
        if (!await NetInfo.fetch().then(state => state.isConnected)) {
          this.queue.unshift(request);
          break;
        }
      }
    }
    await this.saveQueue();
  }
}

export default new OfflineService();
```

### 7. Security Implementation

#### Biometric Authentication
```typescript
// src/services/biometric.ts
import TouchID from 'react-native-touch-id';
import AsyncStorage from '@react-native-async-storage/async-storage';

class BiometricService {
  async isAvailable() {
    try {
      const biometryType = await TouchID.isSupported();
      return biometryType !== null;
    } catch (error) {
      return false;
    }
  }
  
  async authenticate(reason: string = 'Authenticate to access BDC') {
    const optionalConfigObject = {
      title: 'Authentication Required',
      imageColor: '#e00606',
      imageErrorColor: '#ff0000',
      sensorDescription: 'Touch sensor',
      sensorErrorDescription: 'Failed',
      cancelText: 'Cancel',
      fallbackLabel: 'Show Passcode',
      unifiedErrors: false,
      passcodeFallback: false,
    };
    
    try {
      await TouchID.authenticate(reason, optionalConfigObject);
      return true;
    } catch (error) {
      console.error('Biometric authentication failed:', error);
      return false;
    }
  }
  
  async setBiometricEnabled(enabled: boolean) {
    await AsyncStorage.setItem('biometric_enabled', enabled.toString());
  }
  
  async isBiometricEnabled() {
    const enabled = await AsyncStorage.getItem('biometric_enabled');
    return enabled === 'true';
  }
}

export default new BiometricService();
```

#### Certificate Pinning
```typescript
// src/services/security.ts
import { NetworkingModule } from 'react-native';
import CertificatePinner from 'react-native-certificate-pinner';

class SecurityService {
  setupCertificatePinning() {
    CertificatePinner.initialize({
      'api.yourdomain.com': {
        pins: [
          'sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
          'sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB='
        ],
        expirationDate: '2025-12-31'
      }
    });
  }
  
  setupRootDetection() {
    // Implement root/jailbreak detection
    // Use react-native-jail-monkey
  }
  
  encryptSensitiveData(data: string): string {
    // Implement encryption
    return data; // Placeholder
  }
  
  decryptSensitiveData(encryptedData: string): string {
    // Implement decryption
    return encryptedData; // Placeholder
  }
}

export default new SecurityService();
```

### 8. Performance Optimization

#### Image Optimization
```typescript
// src/components/common/OptimizedImage.tsx
import React from 'react';
import FastImage from 'react-native-fast-image';
import { View, ActivityIndicator } from 'react-native';

interface OptimizedImageProps {
  source: { uri: string };
  style?: any;
  resizeMode?: 'contain' | 'cover' | 'stretch' | 'center';
}

const OptimizedImage: React.FC<OptimizedImageProps> = ({
  source,
  style,
  resizeMode = 'cover',
}) => {
  const [loading, setLoading] = React.useState(true);
  
  return (
    <View style={style}>
      <FastImage
        style={style}
        source={{
          uri: source.uri,
          priority: FastImage.priority.normal,
          cache: FastImage.cacheControl.immutable,
        }}
        resizeMode={FastImage.resizeMode[resizeMode]}
        onLoadEnd={() => setLoading(false)}
      />
      {loading && (
        <ActivityIndicator
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: [{ translateX: -10 }, { translateY: -10 }],
          }}
        />
      )}
    </View>
  );
};

export default OptimizedImage;
```

#### List Optimization
```typescript
// src/components/common/OptimizedList.tsx
import React from 'react';
import { FlatList, FlatListProps } from 'react-native';

interface OptimizedListProps<T> extends FlatListProps<T> {
  itemHeight?: number;
}

function OptimizedList<T>({
  itemHeight,
  ...props
}: OptimizedListProps<T>) {
  const getItemLayout = itemHeight
    ? (data: any, index: number) => ({
        length: itemHeight,
        offset: itemHeight * index,
        index,
      })
    : undefined;
  
  return (
    <FlatList
      {...props}
      getItemLayout={getItemLayout}
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      updateCellsBatchingPeriod={10}
      windowSize={10}
      initialNumToRender={10}
    />
  );
}

export default OptimizedList;
```

### 9. Testing

#### Unit Testing
```typescript
// __tests__/auth.test.ts
import { renderHook, act } from '@testing-library/react-hooks';
import { useAuth } from '../src/hooks/useAuth';
import AuthService from '../src/services/auth';

jest.mock('../src/services/auth');

describe('useAuth', () => {
  it('should login successfully', async () => {
    const mockUser = { id: 1, email: 'test@example.com' };
    AuthService.login.mockResolvedValue({
      user: mockUser,
      access_token: 'token',
    });
    
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });
    
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
  });
});
```

#### E2E Testing with Detox
```javascript
// e2e/login.test.js
describe('Login Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
  });
  
  it('should login successfully', async () => {
    await expect(element(by.id('email-input'))).toBeVisible();
    await element(by.id('email-input')).typeText('test@example.com');
    await element(by.id('password-input')).typeText('password');
    await element(by.id('login-button')).tap();
    
    await expect(element(by.id('dashboard-screen'))).toBeVisible();
  });
});
```

### 10. Deployment

#### iOS Deployment
```bash
# Build for App Store
cd ios
xcodebuild -workspace BDCMobile.xcworkspace \
  -scheme BDCMobile \
  -configuration Release \
  -archivePath ./build/BDCMobile.xcarchive \
  archive

# Export IPA
xcodebuild -exportArchive \
  -archivePath ./build/BDCMobile.xcarchive \
  -exportPath ./build \
  -exportOptionsPlist ExportOptions.plist
```

#### Android Deployment
```bash
# Build APK
cd android
./gradlew assembleRelease

# Build AAB for Play Store
./gradlew bundleRelease

# Sign the AAB
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore release-keystore.jks \
  app/build/outputs/bundle/release/app-release.aab \
  release-key-alias
```

### 11. CI/CD Configuration

#### Fastlane Setup
```ruby
# fastlane/Fastfile
platform :ios do
  desc "Build and deploy to TestFlight"
  lane :beta do
    increment_build_number
    build_app(
      workspace: "ios/BDCMobile.xcworkspace",
      scheme: "BDCMobile"
    )
    upload_to_testflight
  end
end

platform :android do
  desc "Build and deploy to Google Play"
  lane :beta do
    gradle(
      task: "bundle",
      build_type: "Release"
    )
    upload_to_play_store(
      track: "beta"
    )
  end
end
```

### 12. App Store Optimization

#### App Store Connect Metadata
```yaml
app_name: "BDC - Beneficiary Development"
subtitle: "Track your learning progress"
description: |
  BDC Mobile app helps beneficiaries track their learning progress,
  view evaluations, and communicate with trainers.
  
  Features:
  - View course materials
  - Complete evaluations
  - Track progress
  - Schedule appointments
  - Receive notifications

keywords: "education, training, development, learning"
categories: ["Education", "Productivity"]
```

#### Screenshots
Required sizes:
- iPhone 6.5": 1242 x 2688
- iPhone 5.5": 1242 x 2208
- iPad Pro 12.9": 2048 x 2732

### 13. Analytics Integration

```typescript
// src/services/analytics.ts
import analytics from '@react-native-firebase/analytics';

class AnalyticsService {
  async logEvent(eventName: string, params?: any) {
    await analytics().logEvent(eventName, params);
  }
  
  async setUserId(userId: string) {
    await analytics().setUserId(userId);
  }
  
  async setUserProperties(properties: any) {
    for (const [key, value] of Object.entries(properties)) {
      await analytics().setUserProperty(key, value);
    }
  }
  
  // Common events
  async logLogin(method: string) {
    await this.logEvent('login', { method });
  }
  
  async logScreenView(screenName: string) {
    await analytics().logScreenView({
      screen_name: screenName,
      screen_class: screenName,
    });
  }
}

export default new AnalyticsService();
```

### 14. Deep Linking

```typescript
// src/navigation/DeepLinking.ts
const config = {
  screens: {
    App: {
      screens: {
        Dashboard: 'dashboard',
        Beneficiary: {
          screens: {
            Details: 'beneficiary/:id',
          },
        },
        Evaluation: 'evaluation/:id',
      },
    },
    Auth: {
      screens: {
        Login: 'login',
        Register: 'register',
      },
    },
  },
};

const linking = {
  prefixes: ['bdc://', 'https://app.yourdomain.com'],
  config,
};

export default linking;
```

## Maintenance & Updates

### Version Management
```json
{
  "version": "1.0.0",
  "versionCode": 1,
  "minSdkVersion": 21,
  "targetSdkVersion": 31,
  "iosDeploymentTarget": "12.0"
}
```

### Update Strategy
1. **Major Updates**: New features, UI overhaul
2. **Minor Updates**: Bug fixes, performance improvements
3. **Patch Updates**: Critical security fixes

### Monitoring
- Crash reporting with Sentry
- Performance monitoring with Firebase
- User analytics with Mixpanel
- App Store reviews monitoring

## Conclusion

This mobile app development guide provides a comprehensive roadmap for building native mobile applications for the BDC platform. The React Native approach offers the best balance of performance, development speed, and code reuse from the existing web application.