import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const SimpleLoginPage = () => {
  const [email, setEmail] = useState('admin@bdc.com');
  const [password, setPassword] = useState('admin123');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('http://localhost:5001/api/auth/login', {
        email,
        password,
        remember: false
      });

      setResult(response.data);
      
      // Store token
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        
        // Redirect based on role
        if (response.data.user.role === 'student') {
          navigate('/portal');
        } else {
          navigate('/');
        }
      }
    } catch (err) {
      setError({
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Simple Login Test
          </h2>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Sign in
            </button>
          </div>
        </form>

        {result && (
          <div className="mt-4 p-4 bg-green-100 border border-green-400 rounded">
            <h3 className="font-bold text-green-800">Success!</h3>
            <pre className="mt-2 text-sm text-green-700">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-100 border border-red-400 rounded">
            <h3 className="font-bold text-red-800">Error!</h3>
            <pre className="mt-2 text-sm text-red-700">{JSON.stringify(error, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default SimpleLoginPage;