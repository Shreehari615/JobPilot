import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, CheckCircle, KeyRound, Mail } from 'lucide-react';
import { api } from '../api/client';

export const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.forgotPassword(email);
      setSubmitted(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
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
        {/* Header icon */}
        <div className="text-center mb-8">
          <div
            className="w-12 h-12 rounded-2xl mx-auto flex items-center justify-center mb-3"
            style={{
              background: submitted ? 'rgba(22,163,74,0.1)' : 'rgba(239,68,68,0.1)',
              color: submitted ? '#16a34a' : '#ef4444',
              boxShadow: '0 4px 16px -4px rgba(239,68,68,0.18)',
            }}
          >
            {submitted ? <CheckCircle className="w-6 h-6" /> : <KeyRound className="w-6 h-6" />}
          </div>
          <h2 className="text-2xl font-extrabold" style={{ color: 'var(--color-text)' }}>
            {submitted ? 'Check your inbox' : 'Forgot Password?'}
          </h2>
          <p className="text-sm mt-1" style={{ color: 'var(--color-text-muted)' }}>
            {submitted
              ? `If ${email} is registered, a reset link has been sent.`
              : "Enter your email and we'll send you a reset link."}
          </p>
        </div>

        {!submitted ? (
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
              <div>
                <label
                  className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3.5 top-3" style={{ color: 'var(--color-text-muted)' }} />
                  <input
                    id="forgot-email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm transition focus:outline-none"
                    style={{
                      background: 'var(--color-surface)',
                      border: '1px solid var(--color-border-strong)',
                      color: 'var(--color-text)',
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = 'var(--color-primary)';
                      e.target.style.boxShadow = '0 0 0 3px rgba(19,102,214,0.12)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = 'var(--color-border-strong)';
                      e.target.style.boxShadow = 'none';
                    }}
                  />
                </div>
              </div>

              <button
                id="forgot-submit"
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl font-bold text-sm text-white transition flex items-center justify-center gap-2 hover:opacity-95"
                style={{
                  background: 'linear-gradient(135deg,#dc2626,#ef4444)',
                  boxShadow: '0 4px 16px -4px rgba(239,68,68,0.35)',
                }}
              >
                {loading ? 'Sending…' : 'Send Reset Link'}
              </button>
            </form>
          </>
        ) : (
          <div
            className="p-4 rounded-xl text-sm text-center"
            style={{ background: 'rgba(22,163,74,0.08)', color: 'var(--color-text-muted)' }}
          >
            Didn't receive it? Check your spam folder or{' '}
            <button
              className="font-semibold hover:underline"
              style={{ color: 'var(--color-primary)' }}
              onClick={() => { setSubmitted(false); setEmail(''); }}
            >
              try again
            </button>
            .
          </div>
        )}

        <p className="text-center text-xs mt-6" style={{ color: 'var(--color-text-muted)' }}>
          <Link
            to="/login"
            className="flex items-center justify-center gap-1 font-semibold hover:underline"
            style={{ color: 'var(--color-primary)' }}
          >
            <ArrowLeft className="w-3 h-3" /> Back to Sign In
          </Link>
        </p>
      </div>
    </div>
  );
};
