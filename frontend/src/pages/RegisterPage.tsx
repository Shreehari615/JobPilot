import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Bot, CheckCircle, Lock, Mail, RefreshCw, Shield, User } from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

type Step = 'details' | 'otp' | 'success';

export const RegisterPage: React.FC = () => {
  // Step 1 state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Step 2 state
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const otpRefs = useRef<Array<HTMLInputElement | null>>([]);

  // UI state
  const [step, setStep] = useState<Step>('details');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  const { login } = useAuth();
  const navigate = useNavigate();

  // Countdown timer for resend OTP
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setTimeout(() => setResendCooldown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  // ── Step 1: submit details & send OTP ─────────────────────────────────
  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      await api.sendOTP(email);
      setStep('otp');
      setResendCooldown(60);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send verification code. Try again.');
    } finally {
      setLoading(false);
    }
  };

  // ── OTP digit input helpers ────────────────────────────────────────────
  const handleOtpChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);
    if (value && index < 5) otpRefs.current[index + 1]?.focus();
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  const handleOtpPaste = (e: React.ClipboardEvent) => {
    const text = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (text.length === 6) {
      setOtp(text.split(''));
      otpRefs.current[5]?.focus();
    }
  };

  // ── Step 2: verify OTP & register ─────────────────────────────────────
  const handleVerifyAndRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const otpStr = otp.join('');
    if (otpStr.length < 6) {
      setError('Please enter the complete 6-digit code.');
      return;
    }

    setLoading(true);
    try {
      // Verify OTP first
      await api.verifyOTP(email, otpStr);

      // Register account
      await api.register({ email, password, full_name: fullName });

      // Auto-login
      const res = await api.login({ email, password });
      login(res.access_token, {
        id: res.user_id,
        email: res.email,
        is_active: true,
        is_admin: res.is_admin,
        created_at: new Date().toISOString(),
      });

      navigate('/jobs');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // ── Resend OTP ──────────────────────────────────────────────────────────
  const handleResend = async () => {
    if (resendCooldown > 0) return;
    setError(null);
    setLoading(true);
    try {
      await api.sendOTP(email);
      setOtp(['', '', '', '', '', '']);
      setResendCooldown(60);
      otpRefs.current[0]?.focus();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to resend code.');
    } finally {
      setLoading(false);
    }
  };

  const inputBase: React.CSSProperties = {
    background: 'var(--color-surface)',
    border: '1px solid var(--color-border-strong)',
    color: 'var(--color-text)',
  };
  const inputFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    e.target.style.borderColor = 'var(--color-primary)';
    e.target.style.boxShadow = '0 0 0 3px rgba(19,102,214,0.12)';
  };
  const inputBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    e.target.style.borderColor = 'var(--color-border-strong)';
    e.target.style.boxShadow = 'none';
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 mesh-gradient-bg">
      <div
        className="w-full max-w-md p-8 rounded-3xl relative"
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          boxShadow: 'var(--shadow-lg)',
        }}
      >
        {/* Header */}
        <div className="text-center mb-8">
          <div
            className="w-12 h-12 rounded-2xl mx-auto flex items-center justify-center mb-3"
            style={{
              background: step === 'otp' ? 'rgba(99,102,241,0.12)' : 'var(--color-primary-light)',
              color: step === 'otp' ? '#6366f1' : 'var(--color-primary)',
              boxShadow: '0 4px 16px -4px rgba(19,102,214,0.18)',
            }}
          >
            {step === 'otp' ? <Shield className="w-6 h-6" /> : <Bot className="w-6 h-6" />}
          </div>
          <h2 className="text-2xl font-extrabold" style={{ color: 'var(--color-text)' }}>
            {step === 'details' ? 'Create Account' : 'Verify Your Email'}
          </h2>
          <p className="text-sm mt-1" style={{ color: 'var(--color-text-muted)' }}>
            {step === 'details'
              ? 'Discover precision job matches tailored to your skills'
              : `We sent a 6-digit code to ${email}`}
          </p>
        </div>

        {/* Step progress */}
        <div className="flex items-center gap-2 mb-6">
          {(['details', 'otp'] as const).map((s, i) => (
            <React.Fragment key={s}>
              <div
                className="flex items-center gap-1.5"
                style={{ color: step === s || (step === 'otp' && s === 'details') ? 'var(--color-primary)' : 'var(--color-text-muted)' }}
              >
                <div
                  className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                  style={{
                    background:
                      (step === 'otp' && s === 'details')
                        ? 'rgba(19,102,214,0.15)'
                        : step === s
                          ? 'var(--color-primary)'
                          : 'var(--color-border-strong)',
                    color:
                      step === s
                        ? '#fff'
                        : (step === 'otp' && s === 'details')
                          ? 'var(--color-primary)'
                          : 'var(--color-text-muted)',
                  }}
                >
                  {step === 'otp' && s === 'details' ? <CheckCircle className="w-3.5 h-3.5" /> : i + 1}
                </div>
                <span className="text-xs font-medium hidden sm:inline">
                  {s === 'details' ? 'Details' : 'Verify Email'}
                </span>
              </div>
              {i < 1 && (
                <div
                  className="flex-1 h-px"
                  style={{ background: step === 'otp' ? 'var(--color-primary)' : 'var(--color-border-strong)' }}
                />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div
            className="mb-5 p-3.5 rounded-xl text-xs flex items-center gap-2"
            style={{ background: 'var(--color-error-light)', border: '1px solid #fecdca', color: '#b42318' }}
          >
            {error}
          </div>
        )}

        {/* ── Step 1: Details form ─────────────────────────────────────────── */}
        {step === 'details' && (
          <form onSubmit={handleSendOTP} className="space-y-4">
            {/* Full Name */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3.5 top-3" style={{ color: 'var(--color-text-muted)' }} />
                <input
                  id="register-fullname"
                  type="text" required value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Rohan Sharma"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm transition focus:outline-none"
                  style={inputBase} onFocus={inputFocus} onBlur={inputBlur}
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3.5 top-3" style={{ color: 'var(--color-text-muted)' }} />
                <input
                  id="register-email"
                  type="email" required value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="rohan@example.com"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm transition focus:outline-none"
                  style={inputBase} onFocus={inputFocus} onBlur={inputBlur}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3.5 top-3" style={{ color: 'var(--color-text-muted)' }} />
                <input
                  id="register-password"
                  type="password" required value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min. 8 characters"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm transition focus:outline-none"
                  style={inputBase} onFocus={inputFocus} onBlur={inputBlur}
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3.5 top-3" style={{ color: 'var(--color-text-muted)' }} />
                <input
                  id="register-confirm-password"
                  type="password" required value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm password"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm transition focus:outline-none"
                  style={inputBase} onFocus={inputFocus} onBlur={inputBlur}
                />
              </div>
            </div>

            <button
              id="register-send-otp"
              type="submit" disabled={loading}
              className="w-full mt-3 py-3 rounded-xl gradient-bg font-bold text-sm text-white transition flex items-center justify-center gap-2 hover:opacity-95"
              style={{ boxShadow: '0 4px 16px -4px rgba(19,102,214,0.35)' }}
            >
              <span>{loading ? 'Sending code…' : 'Send Verification Code'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        {/* ── Step 2: OTP verification ─────────────────────────────────────── */}
        {step === 'otp' && (
          <form onSubmit={handleVerifyAndRegister} className="space-y-6">
            {/* OTP digit boxes */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-3 text-center" style={{ color: 'var(--color-text-secondary)' }}>
                Enter Verification Code
              </label>
              <div className="flex gap-2 justify-center" onPaste={handleOtpPaste}>
                {otp.map((digit, i) => (
                  <input
                    key={i}
                    id={`otp-digit-${i}`}
                    ref={(el) => { otpRefs.current[i] = el; }}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleOtpChange(i, e.target.value)}
                    onKeyDown={(e) => handleOtpKeyDown(i, e)}
                    className="w-11 h-13 text-center text-xl font-bold rounded-xl transition focus:outline-none"
                    style={{
                      width: '44px',
                      height: '52px',
                      background: digit ? 'rgba(99,102,241,0.08)' : 'var(--color-surface)',
                      border: digit ? '2px solid #6366f1' : '2px solid var(--color-border-strong)',
                      color: 'var(--color-text)',
                      fontSize: '22px',
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#6366f1';
                      e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.15)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = digit ? '#6366f1' : 'var(--color-border-strong)';
                      e.target.style.boxShadow = 'none';
                    }}
                  />
                ))}
              </div>
            </div>

            {/* Security note */}
            <div
              className="flex items-center gap-2 p-3 rounded-xl text-xs"
              style={{ background: 'rgba(99,102,241,0.07)', color: 'var(--color-text-muted)' }}
            >
              <Shield className="w-4 h-4 flex-shrink-0" style={{ color: '#6366f1' }} />
              <span>Never share your verification code with anyone.</span>
            </div>

            <button
              id="register-verify-otp"
              type="submit" disabled={loading || otp.join('').length < 6}
              className="w-full py-3 rounded-xl gradient-bg font-bold text-sm text-white transition flex items-center justify-center gap-2 hover:opacity-95 disabled:opacity-50"
              style={{ boxShadow: '0 4px 16px -4px rgba(19,102,214,0.35)' }}
            >
              <span>{loading ? 'Verifying…' : 'Verify & Create Account'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            {/* Resend + go back */}
            <div className="flex items-center justify-between text-xs" style={{ color: 'var(--color-text-muted)' }}>
              <button
                type="button"
                onClick={() => { setStep('details'); setError(null); setOtp(['', '', '', '', '', '']); }}
                className="hover:underline"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                ← Change email
              </button>
              <button
                id="register-resend-otp"
                type="button"
                disabled={resendCooldown > 0 || loading}
                onClick={handleResend}
                className="flex items-center gap-1 font-semibold hover:underline disabled:opacity-50"
                style={{ color: 'var(--color-primary)' }}
              >
                <RefreshCw className="w-3 h-3" />
                {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend code'}
              </button>
            </div>
          </form>
        )}

        <p className="text-center text-xs mt-6" style={{ color: 'var(--color-text-muted)' }}>
          Already registered?{' '}
          <Link to="/login" className="font-semibold hover:underline" style={{ color: 'var(--color-primary)' }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};

