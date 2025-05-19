// Proposed update for App.jsx

// Import the new RoleBasedRedirect component
import RoleBasedRedirect from './components/common/RoleBasedRedirect';

// Update the route structure
<Route
  path="/"
  element={
    <ProtectedRoute>
      <DashboardLayout />
    </ProtectedRoute>
  }
>
  {/* Replace DashboardPageV3 with RoleBasedRedirect */}
  <Route index element={<RoleBasedRedirect />} />
  
  {/* Add explicit dashboard route for consistency */}
  <Route path="dashboard" element={<DashboardPageV3 />} />
  
  {/* ... rest of the routes remain the same ... */}
</Route>

// Alternative: Add a separate dashboard route outside of the layout
<Route 
  path="/dashboard" 
  element={
    <ProtectedRoute>
      <Navigate to="/" replace />
    </ProtectedRoute>
  } 
/>