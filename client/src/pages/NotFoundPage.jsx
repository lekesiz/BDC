import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

/**
 * 404 Not Found page component
 */
const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-white flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-9xl font-extrabold text-primary">404</h1>
          <h2 className="mt-4 text-3xl font-bold text-gray-900">Page Not Found</h2>
          <p className="mt-2 text-base text-gray-500">
            We couldn't find the page you're looking for.
          </p>
          <div className="mt-6">
            <Link
              to="/"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Go back home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;