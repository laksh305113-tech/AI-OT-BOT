import { useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext.jsx';
import './LoginPage.css';

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth(); const navigate = useNavigate(); const location = useLocation();
  const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const [submitting, setSubmitting] = useState(false);
  if (isAuthenticated) return <Navigate to="/" replace />;
  const submit = async (event) => { event.preventDefault(); setError(''); setSubmitting(true); try { await login(email, password); navigate(location.state?.from?.pathname || '/', { replace: true }); } catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to sign in. Check the backend connection and credentials.'); } finally { setSubmitting(false); } };
  return <main className="login-shell"><section className="login-panel"><div className="login-brand"><span className="brand-mark">A</span><span>AI-<b>OT</b></span></div><p className="section-kicker">SECURE PROTOTYPE ACCESS</p><h1>Welcome back</h1><p className="login-copy">Sign in to the simulated Operating Theatre command center.</p><form onSubmit={submit}><label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="username" required /></label><label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required /></label>{error && <p className="login-error" role="alert">{error}</p>}<button className="login-submit" disabled={submitting}>{submitting ? 'Signing in…' : 'Sign in'}</button></form><p className="login-notice">Synthetic demo accounts only. This prototype is not for clinical use.</p></section></main>;
}
