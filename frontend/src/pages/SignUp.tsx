import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import './SignUp.css';

export const SignUp = () => {
  const [formData, setFormData] = useState({
    pseudo: '',
    age: '',
    email: '',
    adresse: '',
    numero: '',
    password: '',
  });

  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await apiClient.post('/register', {
        username: formData.pseudo,
        age: formData.age,
        email: formData.email,
        adresse: formData.adresse,
        numero: formData.numero,
        password: formData.password,
        role: 'public',
      });

      navigate('/');
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 
        'Registration error';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="signup-container">
      {/* Header */}
      <div className="signup-header">
        <div className="signup-header-content">
          <h1>NLP Knowledge</h1>
          <p>Sign Up</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="signup-main">
        <div className="signup-card">
          {/* Error Message */}
          {error && (
            <div className="signup-error">
              <p>{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="signup-form">
            {/* Grid Layout */}
            <div className="signup-grid">
              {/* Pseudo */}
              <div className="signup-field">
                <label htmlFor="pseudo">Username</label>
                <input
                  id="pseudo"
                  type="text"
                  name="pseudo"
                  value={formData.pseudo}
                  onChange={handleChange}
                  placeholder="Your username"
                  required
                />
              </div>

              {/* Age */}
              <div className="signup-field">
                <label htmlFor="age">Age</label>
                <input
                  id="age"
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  placeholder="Your age"
                  required
                  min="1"
                  max="120"
                />
              </div>

              {/* Email */}
              <div className="signup-field">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Your email"
                  required
                />
              </div>

              {/* Address */}
              <div className="signup-field">
                <label htmlFor="adresse">Address</label>
                <input
                  id="adresse"
                  type="text"
                  name="adresse"
                  value={formData.adresse}
                  onChange={handleChange}
                  placeholder="Your address"
                  required
                />
              </div>

              {/* Phone */}
              <div className="signup-field">
                <label htmlFor="numero">Phone</label>
                <input
                  id="numero"
                  type="tel"
                  name="numero"
                  value={formData.numero}
                  onChange={handleChange}
                  placeholder="Your phone number"
                  required
                />
              </div>
            </div>

            {/* Password - Full Width */}
            <div className="signup-field signup-full">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="text"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                required
                minLength={6}
              />
            </div>

            {/* Submit Button */}
            <button type="submit" disabled={isLoading} className="signup-btn">
              {isLoading ? 'Signing up...' : 'Sign Up'}
            </button>
          </form>

          {/* Login Link */}
          <div className="signup-footer">
            <p>
              Already have an account?
              <button onClick={() => navigate('/')} className="signup-footer-link">
                Sign In
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
