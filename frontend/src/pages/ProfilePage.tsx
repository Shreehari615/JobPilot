import React, { useEffect, useState } from 'react';
import {
  Briefcase,
  CheckCircle2,
  DollarSign,
  Globe,
  MapPin,
  Save,
  Sliders,
  User,
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Profile, UserPreferences } from '../types';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<Profile>({
    full_name: '',
    phone: '',
    location: '',
    bio: '',
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
    experience_years: 0,
    experience_level: 'junior',
    expected_salary_min: 800000,
    expected_salary_max: 1800000,
  });

  const [prefs, setPrefs] = useState<UserPreferences>({
    preferred_roles: ['Software Engineer', 'Full Stack Developer'],
    preferred_locations: ['Bengaluru', 'Remote'],
    remote_preference: 'hybrid',
    employment_type: 'full-time',
  });

  const [roleInput, setRoleInput] = useState('');
  const [locInput, setLocInput] = useState('');
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  useEffect(() => {
    const loadProfileAndPrefs = async () => {
      try {
        const [profData, prefsData] = await Promise.all([
          api.getProfile().catch(() => null),
          api.getPreferences().catch(() => null),
        ]);
        if (profData) setProfile((prev) => ({ ...prev, ...profData }));
        if (prefsData) {
          setPrefs({
            preferred_roles: prefsData.preferred_roles || [],
            preferred_locations: prefsData.preferred_locations || [],
            remote_preference: prefsData.remote_preference || 'any',
            employment_type: prefsData.employment_type || 'any',
            min_salary: prefsData.min_salary,
            max_salary: prefsData.max_salary,
          });
        }
      } catch (err) {
        console.error('Failed to load profile data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadProfileAndPrefs();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);
    try {
      await Promise.all([api.updateProfile(profile), api.updatePreferences(prefs)]);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 4000);
    } catch (err) {
      console.error('Error saving profile:', err);
    } finally {
      setSaving(false);
    }
  };

  const addRole = () => {
    if (roleInput.trim() && !prefs.preferred_roles.includes(roleInput.trim())) {
      setPrefs({ ...prefs, preferred_roles: [...prefs.preferred_roles, roleInput.trim()] });
      setRoleInput('');
    }
  };

  const removeRole = (role: string) => {
    setPrefs({ ...prefs, preferred_roles: prefs.preferred_roles.filter((r) => r !== role) });
  };

  const addLocation = () => {
    if (locInput.trim() && !prefs.preferred_locations.includes(locInput.trim())) {
      setPrefs({ ...prefs, preferred_locations: [...prefs.preferred_locations, locInput.trim()] });
      setLocInput('');
    }
  };

  const removeLocation = (loc: string) => {
    setPrefs({
      ...prefs,
      preferred_locations: prefs.preferred_locations.filter((l) => l !== loc),
    });
  };

  const inputStyle = {
    background: 'var(--color-surface)',
    border: '1px solid var(--color-border-strong)',
    color: 'var(--color-text)',
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
      {/* Header */}
      <div
        className="p-6 rounded-2xl"
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <h1 className="text-2xl font-extrabold flex items-center gap-2" style={{ color: 'var(--color-text)' }}>
          <User className="w-6 h-6" style={{ color: 'var(--color-primary)' }} />
          Candidate Profile & Preferences
        </h1>
        <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>
          These attributes directly tune your 5-factor matching algorithm weights.
        </p>
      </div>

      {savedSuccess && (
        <div
          className="p-4 rounded-2xl text-xs flex items-center gap-2 animate-fade-in"
          style={{
            background: 'var(--color-success-light)',
            border: '1px solid #abefc6',
            color: '#067647',
          }}
        >
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>Profile and matching preferences saved successfully!</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Personal Details Card */}
        <div
          className="p-6 rounded-2xl space-y-4"
          style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <h2 className="text-base font-bold flex items-center gap-2" style={{ color: 'var(--color-text)' }}>
            <User className="w-4 h-4" style={{ color: 'var(--color-primary)' }} />
            Basic Information
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--color-text-secondary)' }}>
                Full Name
              </label>
              <input
                type="text"
                value={profile.full_name || ''}
                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl text-sm focus:outline-none transition"
                style={inputStyle}
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

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--color-text-secondary)' }}>
                Email (Account)
              </label>
              <input
                type="email"
                disabled
                value={user?.email || ''}
                className="w-full px-3.5 py-2.5 rounded-xl text-sm cursor-not-allowed"
                style={{
                  background: 'var(--color-surface-hover)',
                  border: '1px solid var(--color-border)',
                  color: 'var(--color-text-muted)',
                }}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--color-text-secondary)' }}>
                Phone Number
              </label>
              <input
                type="text"
                value={profile.phone || ''}
                onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                placeholder="+91 98765 43210"
                className="w-full px-3.5 py-2.5 rounded-xl text-sm focus:outline-none transition"
                style={inputStyle}
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

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--color-text-secondary)' }}>
                Current City / Location
              </label>
              <input
                type="text"
                value={profile.location || ''}
                onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                placeholder="Bengaluru, Karnataka"
                className="w-full px-3.5 py-2.5 rounded-xl text-sm focus:outline-none transition"
                style={inputStyle}
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

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--color-text-secondary)' }}>
                Total Experience (Years)
              </label>
              <input
                type="number"
                step="0.5"
                min="0"
                value={profile.experience_years || 0}
                onChange={(e) =>
                  setProfile({ ...profile, experience_years: parseFloat(e.target.value) || 0 })
                }
                className="w-full px-3.5 py-2.5 rounded-xl text-sm focus:outline-none transition"
                style={inputStyle}
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

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--color-text-secondary)' }}>
                Seniority Level
              </label>
              <select
                value={profile.experience_level || 'junior'}
                onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl text-sm focus:outline-none transition"
                style={inputStyle}
                onFocus={(e) => {
                  e.target.style.borderColor = 'var(--color-primary)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(19,102,214,0.12)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--color-border-strong)';
                  e.target.style.boxShadow = 'none';
                }}
              >
                <option value="fresher">Fresher (0 years)</option>
                <option value="junior">Junior (1 - 2 years)</option>
                <option value="mid">Mid-Level (3 - 5 years)</option>
                <option value="senior">Senior (5+ years)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Career Matching Preferences Card */}
        <div
          className="p-6 rounded-2xl space-y-4"
          style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <h2 className="text-base font-bold flex items-center gap-2" style={{ color: 'var(--color-text)' }}>
            <Sliders className="w-4 h-4" style={{ color: 'var(--color-primary)' }} />
            AI Recommendation Preferences
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--color-text-secondary)' }}>
                Work Mode
              </label>
              <select
                value={prefs.remote_preference}
                onChange={(e) => setPrefs({ ...prefs, remote_preference: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl text-sm focus:outline-none transition"
                style={inputStyle}
                onFocus={(e) => {
                  e.target.style.borderColor = 'var(--color-primary)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(19,102,214,0.12)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--color-border-strong)';
                  e.target.style.boxShadow = 'none';
                }}
              >
                <option value="any">Any (Remote, Hybrid, Onsite)</option>
                <option value="remote">Remote Only</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">Onsite Only</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: 'var(--color-text-secondary)' }}>
                Employment Type
              </label>
              <select
                value={prefs.employment_type}
                onChange={(e) => setPrefs({ ...prefs, employment_type: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl text-sm focus:outline-none transition"
                style={inputStyle}
                onFocus={(e) => {
                  e.target.style.borderColor = 'var(--color-primary)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(19,102,214,0.12)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--color-border-strong)';
                  e.target.style.boxShadow = 'none';
                }}
              >
                <option value="any">Any (Full-time, Contract)</option>
                <option value="full-time">Full-Time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
              </select>
            </div>
          </div>

          {/* Preferred Roles Tags */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
              Preferred Roles
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={roleInput}
                onChange={(e) => setRoleInput(e.target.value)}
                placeholder="e.g. Backend Developer"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addRole();
                  }
                }}
                className="flex-1 px-3 py-2 rounded-xl text-xs focus:outline-none transition"
                style={inputStyle}
                onFocus={(e) => {
                  e.target.style.borderColor = 'var(--color-primary)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(19,102,214,0.12)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--color-border-strong)';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <button
                type="button"
                onClick={addRole}
                className="px-3 py-2 rounded-xl text-xs font-semibold transition"
                style={{
                  background: 'var(--color-primary-light)',
                  color: 'var(--color-primary)',
                  border: '1px solid var(--color-primary-border)',
                }}
              >
                Add Role
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {prefs.preferred_roles.map((role) => (
                <span
                  key={role}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium"
                  style={{
                    background: 'var(--color-primary-light)',
                    color: 'var(--color-primary)',
                    border: '1px solid var(--color-primary-border)',
                  }}
                >
                  <span>{role}</span>
                  <button
                    type="button"
                    onClick={() => removeRole(role)}
                    className="hover:opacity-80 transition"
                    style={{ color: 'var(--color-primary)' }}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Preferred Locations Tags */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
              Target Locations
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={locInput}
                onChange={(e) => setLocInput(e.target.value)}
                placeholder="e.g. Bengaluru"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addLocation();
                  }
                }}
                className="flex-1 px-3 py-2 rounded-xl text-xs focus:outline-none transition"
                style={inputStyle}
                onFocus={(e) => {
                  e.target.style.borderColor = 'var(--color-primary)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(19,102,214,0.12)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--color-border-strong)';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <button
                type="button"
                onClick={addLocation}
                className="px-3 py-2 rounded-xl text-xs font-semibold transition"
                style={{
                  background: 'var(--color-primary-light)',
                  color: 'var(--color-primary)',
                  border: '1px solid var(--color-primary-border)',
                }}
              >
                Add City
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {prefs.preferred_locations.map((loc) => (
                <span
                  key={loc}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium"
                  style={{
                    background: '#f4ebff',
                    color: '#6941c6',
                    border: '1px solid #d6bbfb',
                  }}
                >
                  <span>{loc}</span>
                  <button
                    type="button"
                    onClick={() => removeLocation(loc)}
                    className="hover:opacity-80 transition"
                    style={{ color: '#6941c6' }}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-3 rounded-xl gradient-bg font-bold text-sm text-white transition flex items-center gap-2 hover:opacity-95"
            style={{ boxShadow: '0 4px 16px -4px rgba(19,102,214,0.35)' }}
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save Profile Changes'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
