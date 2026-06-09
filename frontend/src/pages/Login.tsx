import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../api/AuthContext';
import './Login.css';

export const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 
        'Identifiants incorrects';
      setError(errorMessage);
      setPassword('');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* Header */}
      <div className="login-header">
        <div className="login-header-content">
          <h1>NLP Knowledge</h1>
          <p>Desa Punggul, Bali</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="login-main">
        <div className="login-card">
          {/* Error Message */}
          {error && (
            <div className="login-error">
              <p>{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="login-form">
            {/* Username Field */}
            <div className="login-field">
              <label htmlFor="username">Pseudo</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Entrez votre pseudo"
                required
              />
            </div>

            {/* Password Field */}
            <div className="login-field">
              <label htmlFor="password">Mot de passe</label>
              <input
                id="password"
                type="text"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Entrez votre mot de passe"
                required
              />
            </div>

            {/* Submit Button */}
            <button type="submit" disabled={isLoading} className="login-btn">
              {isLoading ? 'Connexion en cours...' : 'Se connecter'}
            </button>
          </form>

          {/* Sign Up Link */}
          <div className="login-footer">
            <p>
              Vous n'avez pas de compte?
              <button onClick={() => navigate('/signup')} className="login-footer-link">
                S'inscrire
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
