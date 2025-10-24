import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useCurrentUser } from '../api/hooks';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * ProtectedRoute component that requires authentication.
 * Redirects to login if no valid token is found.
 */
export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const location = useLocation();
  const token = localStorage.getItem('access_token');
  const { data: currentUser, isLoading, isError } = useCurrentUser();

  // If no token, redirect to login immediately
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Show loading state while fetching user
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-green-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If error or no user, redirect to login
  if (isError || !currentUser) {
    localStorage.removeItem('access_token');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // User is authenticated, render children
  return <>{children}</>;
}
