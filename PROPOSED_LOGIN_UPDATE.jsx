// Proposed update for LoginPage.jsx

// Add this helper function to determine redirect path based on role
const getRedirectPath = (user, from) => {
  // If there's a specific 'from' location, use it (unless it's the login page)
  if (from && from !== '/login') {
    return from;
  }
  
  // Otherwise, redirect based on role
  switch (user.role) {
    case 'student':
      return '/portal';
    case 'super_admin':
    case 'tenant_admin':
    case 'trainer':
      return '/';
    default:
      return '/';
  }
};

// Update the handleSubmit function
const handleSubmit = async (e) => {
  e.preventDefault();
  
  if (!validateForm()) {
    return;
  }
  
  try {
    setIsLoading(true);
    
    const user = await login(email, password, remember);
    
    addToast({
      type: 'success',
      title: 'Login successful',
      message: `Welcome back, ${user.first_name}!`,
    });
    
    // Use role-based redirect
    const redirectPath = getRedirectPath(user, from);
    navigate(redirectPath, { replace: true });
  } catch (err) {
    console.error('Login error:', err);
    
    addToast({
      type: 'error',
      title: 'Login failed',
      message: err.response?.data?.message || 'Failed to login. Please check your credentials.',
    });
  } finally {
    setIsLoading(false);
  }
};