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

  return (
    <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl glass-panel border border-slate-800">
        <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
          <User className="w-6 h-6 text-indigo-400" />
          Candidate Profile & Preferences
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          These attributes directly tune your 5-factor matching algorithm weights.
        </p>
      </div>

      {savedSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2 animate-fade-in">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>Profile and matching preferences saved successfully!</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Personal Details Card */}
        <div className="p-6 rounded-3xl glass-panel border border-slate-800 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <User className="w-4 h-4 text-indigo-400" />
            Basic Information
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Full Name</label>
              <input
                type="text"
                value={profile.full_name || ''}
                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Email (Account)</label>
              <input
                type="email"
                disabled
                value={user?.email || ''}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/50 border border-slate-800 text-slate-500 text-sm cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Phone Number</label>
              <input
                type="text"
                value={profile.phone || ''}
                onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                placeholder="+91 98765 43210"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Current City / Location</label>
              <input
                type="text"
                value={profile.location || ''}
                onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                placeholder="Bengaluru, Karnataka"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">
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
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Seniority Level</label>
              <select
                value={profile.experience_level || 'junior'}
                onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500"
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
        <div className="p-6 rounded-3xl glass-panel border border-slate-800 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Sliders className="w-4 h-4 text-indigo-400" />
            AI Recommendation Preferences
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Work Mode</label>
              <select
                value={prefs.remote_preference}
                onChange={(e) => setPrefs({ ...prefs, remote_preference: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500"
              >
                <option value="any">Any (Remote, Hybrid, Onsite)</option>
                <option value="remote">Remote Only</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">Onsite Only</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Employment Type</label>
              <select
                value={prefs.employment_type}
                onChange={(e) => setPrefs({ ...prefs, employment_type: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500"
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
            <label className="block text-xs font-medium text-slate-400 mb-1.5">
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
                className="flex-1 px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
              />
              <button
                type="button"
                onClick={addRole}
                className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200"
              >
                Add Role
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {prefs.preferred_roles.map((role) => (
                <span
                  key={role}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 text-xs font-medium"
                >
                  <span>{role}</span>
                  <button
                    type="button"
                    onClick={() => removeRole(role)}
                    className="hover:text-rose-400 text-slate-400"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Preferred Locations Tags */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">
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
                className="flex-1 px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
              />
              <button
                type="button"
                onClick={addLocation}
                className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200"
              >
                Add City
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {prefs.preferred_locations.map((loc) => (
                <span
                  key={loc}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-purple-950/60 border border-purple-500/30 text-purple-300 text-xs font-medium"
                >
                  <span>{loc}</span>
                  <button
                    type="button"
                    onClick={() => removeLocation(loc)}
                    className="hover:text-rose-400 text-slate-400"
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
            className="px-6 py-3 rounded-xl gradient-bg font-bold text-sm text-white shadow-lg shadow-indigo-600/30 hover:opacity-95 transition flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save Profile Changes'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
