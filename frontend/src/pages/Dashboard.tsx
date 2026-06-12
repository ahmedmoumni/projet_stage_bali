import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../api/AuthContext';

export const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user?.role === 'admin') {
      console.log('Admin connecté');
    } else {
      console.log('User connecté');
    }
  }, [user]);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Bienvenue!</h1>

        <div className="bg-green-100 border border-green-300 rounded-lg p-4 mb-6">
          <p className="text-green-800 font-semibold">
            {user?.role === 'admin' ? 'Admin connecté' : 'Utilisateur connecté'}
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 mb-6 space-y-2 text-left">
          <p><span className="font-semibold">Pseudo:</span> {user?.username}</p>
          <p><span className="font-semibold">Rôle:</span> {user?.role?.toUpperCase()}</p>
        </div>

        {user?.role === 'admin' && (
          <button
            onClick={() => navigate('/upload')}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition mb-3"
          >
            📤 Upload Document
          </button>
        )}

        <button
          onClick={handleLogout}
          className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          Déconnexion
        </button>
      </div>
    </div>
  );
};
