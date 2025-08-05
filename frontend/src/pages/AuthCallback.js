import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { showToast } from '../utils/toastUtils';

const AuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { loginWithToken } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      const token = searchParams.get('token');
      const error = searchParams.get('error');

      if (error) {
        showToast.error(`Authentication failed: ${error}`);
        navigate('/login');
        return;
      }

      if (token) {
        try {
          const result = await loginWithToken(token);
          if (result.success) {
            showToast.success('Login successful!');
            navigate('/');
          } else {
            showToast.error('Failed to authenticate with token');
            navigate('/login');
          }
        } catch (err) {
          showToast.error('Authentication error');
          navigate('/login');
        }
      } else {
        showToast.error('No authentication token received');
        navigate('/login');
      }
    };

    handleCallback();
  }, [searchParams, navigate, loginWithToken]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tax-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Completing authentication...</p>
        </div>
      </div>
    </div>
  );
};

export default AuthCallback;