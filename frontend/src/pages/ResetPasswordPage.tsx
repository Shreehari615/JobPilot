import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowRight, CheckCircle, Eye, EyeOff, Lock } from 'lucide-react';
import { api } from '../api/client';

export const ResetPasswordPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    setLoading(true);
    try {
      await api.resetPassword(token, password);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid or expired reset link. Please request a new one.');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
        <div className="text-center" style={{ color: 'var(--color-text-muted)' }}>
          <p className="mb-4">Invalid reset link.</p>
          <Link to="/forgot-password" className="font-semibold" style={{ color: 'var(--color-primary)' }}>
            Request a new one →
          </Link>
        </div>
      </div>
    );
  }

  const inputStyle: React.CSSProperties = {
    background: 'var(--color-surface)',
    border: '1px solid var(--color-border-strong)',
    color: 'var(--color-text)',
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 mesh-gradient-bg">
      <div
        className="w-full max-w-md p-8 rounded-3xl"
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          boxShadow: 'var(--shadow-lg)',
        }}
      >
        <div className="text-center mb-8">
          <div
            className="w-12 h-12 rounded-2xl mx-auto flex items-center justify-center mb-3"
            style={{
              background: success ? 'rgba(22,163,74,0.1)' : 'rgba(239,68,68,0.1)',
              color: success ? '#16a34a' : '#ef4444',
            }}
          >
            {success ? <CheckCircle className="w-6 h-6" /> : <Lock className="w-6 h-6" />}
          </div>
          <h2 className="text-2xl font-extrabold" style={{ color: 'var(--color-text)' }}>
            {success ? 'Password Updated!' : 'Set New Password'}
          </h2>
          <p className="text-sm mt-1" style={{ color: 'var(--color-text-muted)' }}>
            {success
              ? 'Redirecting you to login…'
              : 'Choose a strong password for your account.'}
          </p>
        </div>

        {success ? (
          <div
            className="p-4 rounded-xl text-sm text-center"
            style={{ background: 'rgba(22,163,74,0.08)', color: '#16a34a' }}
          >
            Your password has been reset successfully.{' '}
            <Link to="/login" className="font-bold hover:underline">Sign in now →</Link>
          </div>
        ) : (
          <>
            {error && (
              <div
                className="mb-5 p-3.5 rounded-xl text-xs"
                style={{ background: 'var(--color-error-light)', border: '1px solid #fecdca', color: '#b42318' }}
              >
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* New password */}
              <div>
                <label
                  className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  New Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3.5 top-3" style={{ color: 'var(--color-text-muted)' }} />
                  <input
                    id="reset-password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min. 8 characters"
                    className="w-full pl-10 pr-10 py-2.5 rounded-xl text-sm transition focus:outline-none"
                    style={inputStyle}
                    onFocus={(e) => { e.target.style.borderColor = 'var(--color-primary)'; e.target.style.boxShadow = '0 0 0 3px rgba(19,102,214,0.12)'; }}
                    onBlur={(e) => { e.target.style.borderColor = 'var(--color-border-strong)'; e.target.style.boxShadow = 'none'; }}
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-3"
                    style={{ color: 'var(--color-text-muted)' }}
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Confirm password */}
              <div>
                <label
                  className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3.5 top-3" style={{ color: 'var(--color-text-muted)' }} />
                  <input
                    id="reset-confirm-password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your password"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm transition focus:outline-none"
                    style={inputStyle}
                    onFocus={(e) => { e.target.style.borderColor = 'var(--color-primary)'; e.target.style.boxShadow = '0 0 0 3px rgba(19,102,214,0.12)'; }}
                    onBlur={(e) => { e.target.style.borderColor = 'var(--color-border-strong)'; e.target.style.boxShadow = 'none'; }}
                  />
                </div>
              </div>

              <button
                id="reset-submit"
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-3 rounded-xl font-bold text-sm text-white transition flex items-center justify-center gap-2 hover:opacity-95"
                style={{
                  background: 'linear-gradient(135deg,#dc2626,#ef4444)',
                  boxShadow: '0 4px 16px -4px rgba(239,68,68,0.35)',
                }}
              >
                <span>{loading ? 'Updating…' : 'Reset Password'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          </>
        )}

        <p className="text-center text-xs mt-6" style={{ color: 'var(--color-text-muted)' }}>
          <Link to="/login" className="font-semibold hover:underline" style={{ color: 'var(--color-primary)' }}>
            ← Back to Sign In
          </Link>
        </p>
      </div>
    </div>
  );
};
