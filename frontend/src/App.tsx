import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './api/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Login } from './pages/Login';
import { SignUp } from './pages/SignUp';
import { Dashboard } from './pages/Dashboard';
import { Upload } from './pages/Upload';
import { KnowledgeRules } from './pages/KnowledgeRules';
import { KnowledgeFacts } from './pages/KnowledgeFacts';
import { PendingReview } from './pages/PendingReview';
import { Analytics } from './pages/Analytics';
import './App.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/upload"
            element={
              <ProtectedRoute>
                <Upload />
              </ProtectedRoute>
            }
          />
          <Route
            path="/rules"
            element={
              <ProtectedRoute>
                <KnowledgeRules />
              </ProtectedRoute>
            }
          />
          <Route
            path="/facts"
            element={
              <ProtectedRoute>
                <KnowledgeFacts />
              </ProtectedRoute>
            }
          />
          <Route
            path="/pending-review"
            element={
              <ProtectedRoute>
                <PendingReview />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <Analytics />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;

