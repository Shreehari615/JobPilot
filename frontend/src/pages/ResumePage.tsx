import React, { useEffect, useRef, useState } from 'react';
import {
  AlertCircle,
  Award,
  Briefcase,
  CheckCircle2,
  Clock,
  FileCheck,
  FileText,
  FolderOpen,
  GraduationCap,
  Sparkles,
  Trash2,
  UploadCloud,
  User,
  Zap,
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { SkillTag } from '../components/SkillTag';
import { Resume, ResumeAnalysis } from '../types';

export const ResumePage: React.FC = () => {
  const { user } = useAuth();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<boolean>(false);
  const [activeStep, setActiveStep] = useState<number>(0);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadResumesAndAnalysis = async () => {
    setLoading(true);
    try {
      const list = await api.getResumes();
      setResumes(Array.isArray(list) ? list : list ? [list] : []);

      const normalizedList = Array.isArray(list) ? list : list ? [list] : [];
      if (normalizedList.length > 0) {
        // Load latest analysis
        const latest = await api.getLatestAnalysis().catch(() => null);
        if (latest) {
          setAnalysis(latest);
        } else {
          // If no latest cached, fetch by resume id
          const first = await api.getResumeAnalysis(normalizedList[0].id).catch(() => null);
          if (first) setAnalysis(first);
        }
      }
    } catch (err) {
      console.error('Error loading resumes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResumesAndAnalysis();
  }, []);

  // Animate steps during upload
  useEffect(() => {
    if (!uploading) {
      setActiveStep(0);
      return;
    }
    const steps = [0, 1, 2, 3];
    let idx = 0;
    const interval = setInterval(() => {
      idx = (idx + 1) % steps.length;
      setActiveStep(steps[idx]);
    }, 1200);
    return () => clearInterval(interval);
  }, [uploading]);

  const handleFileUpload = async (file: File) => {
    setError(null);
    setUploadSuccess(false);

    // Validate type
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'pdf' && ext !== 'docx') {
      setError('Only PDF and DOCX formats are supported.');
      return;
    }

    // Validate size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be under 10MB.');
      return;
    }

    setUploading(true);
    try {
      await api.uploadResume(file);
      setUploadSuccess(true);
      setTimeout(() => setUploadSuccess(false), 5000);
      // Refresh analysis
      await loadResumesAndAnalysis();
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Failed to upload and analyze resume. Please try again.'
      );
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteResume = async () => {
    if (!window.confirm('Are you sure you want to remove your resume?')) return;
    setError(null);
    try {
      await api.deleteResume();
      setResumes([]);
      setAnalysis(null);
    } catch (err: any) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        setError('Your session has expired. Please log in again to continue.');
      } else {
        setError(err.response?.data?.detail || 'Failed to delete resume.');
      }
    }
  };


  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '—';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const pipelineSteps = [
    { label: 'Parsing Document', icon: FileText },
    { label: 'Entity Extraction', icon: User },
    { label: 'Skill Matching', icon: Award },
    { label: 'Vectorization', icon: Zap },
  ];

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div
        className="p-6 rounded-2xl"
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="w-5 h-5" style={{ color: 'var(--color-primary)' }} />
          <span
            className="text-xs font-semibold uppercase tracking-wider"
            style={{ color: 'var(--color-primary)' }}
          >
            Intelligent Document Parsing
          </span>
        </div>
        <h1 className="text-2xl font-extrabold" style={{ color: 'var(--color-text)' }}>
          Resume & Skill Extractor
        </h1>
        <p className="text-xs mt-1 max-w-2xl" style={{ color: 'var(--color-text-muted)' }}>
          Upload your resume in PDF or DOCX format. Our intelligent parsing pipeline extracts
          your contact info, education, work experience, and skills — for any industry or role.
        </p>
      </div>

      {/* Upload Box */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
        className="p-10 rounded-2xl border-2 border-dashed transition-all cursor-pointer text-center"
        style={{
          borderColor: dragOver ? 'var(--color-primary)' : 'var(--color-border-strong)',
          background: dragOver ? 'var(--color-primary-light)' : 'var(--color-surface)',
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileUpload(e.target.files[0]);
            }
          }}
        />

        <div
          className="w-16 h-16 rounded-2xl mx-auto flex items-center justify-center mb-4"
          style={{
            background: 'var(--color-primary-light)',
            color: 'var(--color-primary)',
            boxShadow: '0 4px 16px -4px rgba(19,102,214,0.15)',
          }}
        >
          <UploadCloud className={`w-8 h-8 ${uploading ? 'animate-bounce' : ''}`} />
        </div>

        <h3 className="text-base font-bold mb-1" style={{ color: 'var(--color-text)' }}>
          {uploading ? 'Analyzing document with NLP pipeline...' : 'Click to browse or drag & drop'}
        </h3>
        <p className="text-xs max-w-sm mx-auto" style={{ color: 'var(--color-text-muted)' }}>
          Supported formats:{' '}
          <strong style={{ color: 'var(--color-text-secondary)' }}>PDF, DOCX</strong> (Up to 10MB)
        </p>

        {/* Pipeline Steps Animation */}
        {uploading && (
          <div className="mt-6 flex items-center justify-center gap-3">
            {pipelineSteps.map((step, idx) => {
              const StepIcon = step.icon;
              const isActive = activeStep === idx;
              const isDone = activeStep > idx;
              return (
                <React.Fragment key={idx}>
                  {idx > 0 && (
                    <div
                      className="w-6 h-0.5 rounded-full transition-all duration-500"
                      style={{
                        background: isDone || isActive
                          ? 'var(--color-primary)'
                          : 'var(--color-border)',
                      }}
                    />
                  )}
                  <div
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-500"
                    style={{
                      background: isActive
                        ? 'var(--color-primary-light)'
                        : isDone
                          ? 'var(--color-success-light)'
                          : 'var(--color-surface-hover)',
                      color: isActive
                        ? 'var(--color-primary)'
                        : isDone
                          ? 'var(--color-success)'
                          : 'var(--color-text-muted)',
                      border: `1px solid ${isActive ? 'var(--color-primary-border)' : 'transparent'}`,
                      transform: isActive ? 'scale(1.05)' : 'scale(1)',
                    }}
                  >
                    <StepIcon className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">{step.label}</span>
                  </div>
                </React.Fragment>
              );
            })}
          </div>
        )}
      </div>

      {/* Success Message */}
      {uploadSuccess && (
        <div
          className="p-4 rounded-2xl text-xs flex items-center gap-2 animate-fade-in"
          style={{
            background: 'var(--color-success-light)',
            border: '1px solid #abefc6',
            color: '#067647',
          }}
        >
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>Resume uploaded and analyzed successfully! Your skills have been extracted.</span>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div
          className="p-4 rounded-2xl text-xs flex items-center gap-2"
          style={{
            background: 'var(--color-error-light)',
            border: '1px solid #fecdca',
            color: '#b42318',
          }}
        >
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Uploaded Resumes List */}
      {resumes.length > 0 && (
        <div
          className="p-6 rounded-2xl"
          style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <h2
            className="text-base font-bold mb-4 flex items-center gap-2"
            style={{ color: 'var(--color-text)' }}
          >
            <FileText className="w-4 h-4" style={{ color: 'var(--color-primary)' }} />
            Uploaded Resume
          </h2>
          <div className="space-y-3">
            {resumes.map((resume) => (
              <div
                key={resume.id}
                className="flex items-center justify-between p-4 rounded-xl transition-all"
                style={{
                  background: 'var(--color-surface-hover)',
                  border: '1px solid var(--color-border)',
                }}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                    style={{
                      background:
                        resume.file_type === 'pdf'
                          ? 'var(--color-error-light)'
                          : 'var(--color-primary-light)',
                      color:
                        resume.file_type === 'pdf'
                          ? 'var(--color-error)'
                          : 'var(--color-primary)',
                    }}
                  >
                    <FileText className="w-5 h-5" />
                  </div>
                  <div className="min-w-0">
                    <div
                      className="text-sm font-semibold truncate"
                      style={{ color: 'var(--color-text)' }}
                    >
                      {resume.filename}
                    </div>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span
                        className="text-xs"
                        style={{ color: 'var(--color-text-muted)' }}
                      >
                        {formatFileSize(resume.file_size_bytes)}
                      </span>
                      <span
                        className="text-xs"
                        style={{ color: 'var(--color-text-muted)' }}
                      >
                        •
                      </span>
                      <span
                        className="text-xs"
                        style={{ color: 'var(--color-text-muted)' }}
                      >
                        {resume.file_type?.toUpperCase()}
                      </span>
                      <span
                        className="text-xs"
                        style={{ color: 'var(--color-text-muted)' }}
                      >
                        •
                      </span>
                      <span
                        className="text-xs flex items-center gap-1"
                        style={{ color: 'var(--color-text-muted)' }}
                      >
                        <Clock className="w-3 h-3" />
                        {new Date(resume.created_at).toLocaleDateString('en-IN', {
                          day: 'numeric',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className="badge"
                    style={
                      resume.status === 'done'
                        ? {
                            background: 'var(--color-success-light)',
                            borderColor: '#abefc6',
                            color: '#067647',
                          }
                        : resume.status === 'error'
                          ? {
                              background: 'var(--color-error-light)',
                              borderColor: '#fecdca',
                              color: '#b42318',
                            }
                          : resume.status === 'processing'
                            ? {
                                background: 'var(--color-warning-light)',
                                borderColor: '#fedf89',
                                color: '#b54708',
                              }
                            : {}
                    }
                  >
                    {resume.status === 'done' && <CheckCircle2 className="w-3 h-3" />}
                    {resume.status}
                  </span>
                  <button
                    type="button"
                    onClick={handleDeleteResume}
                    title="Delete resume"
                    className="p-1.5 rounded-lg transition-colors text-slate-400 hover:text-rose-600 hover:bg-rose-50"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* NLP Extraction Results */}
      {analysis && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2
              className="text-lg font-bold flex items-center gap-2"
              style={{ color: 'var(--color-text)' }}
            >
              <FileCheck className="w-5 h-5" style={{ color: 'var(--color-success)' }} />
              Verified Extraction Results
            </h2>
            <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
              Extracted from{' '}
              <strong style={{ color: 'var(--color-text-secondary)' }}>
                {resumes[0]?.filename || 'Uploaded Resume'}
              </strong>
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Candidate Summary Card */}
            <div
              className="p-6 rounded-2xl space-y-4"
              style={{
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              <h3
                className="text-sm font-semibold uppercase tracking-wider flex items-center gap-2"
                style={{ color: 'var(--color-primary)' }}
              >
                <User className="w-4 h-4" />
                Contact & Profile
              </h3>
              <div className="space-y-3 text-sm">
                <div>
                  <span
                    className="text-xs block mb-0.5"
                    style={{ color: 'var(--color-text-muted)' }}
                  >
                    Extracted Name
                  </span>
                  <span className="font-semibold" style={{ color: 'var(--color-text)' }}>
                    {analysis.name || 'Not detected in header'}
                  </span>
                </div>
                <div>
                  <span
                    className="text-xs block mb-0.5"
                    style={{ color: 'var(--color-text-muted)' }}
                  >
                    Email Address
                  </span>
                  <span style={{ color: 'var(--color-text-secondary)' }}>
                    {analysis.email || user?.email || 'N/A'}
                  </span>
                </div>
                <div>
                  <span
                    className="text-xs block mb-0.5"
                    style={{ color: 'var(--color-text-muted)' }}
                  >
                    Phone
                  </span>
                  <span style={{ color: 'var(--color-text-secondary)' }}>
                    {analysis.phone || 'N/A'}
                  </span>
                </div>
                <div>
                  <span
                    className="text-xs block mb-0.5"
                    style={{ color: 'var(--color-text-muted)' }}
                  >
                    Detected Experience
                  </span>
                  <span className="font-semibold" style={{ color: 'var(--color-success)' }}>
                    {analysis.total_experience_years.toFixed(1)} Years
                  </span>
                </div>
              </div>
            </div>

            {/* Extracted Skills Card */}
            <div
              className="md:col-span-2 p-6 rounded-2xl space-y-4"
              style={{
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              <div className="flex items-center justify-between">
                <h3
                  className="text-sm font-semibold uppercase tracking-wider flex items-center gap-2"
                  style={{ color: 'var(--color-primary)' }}
                >
                  <Award className="w-4 h-4" />
                  Extracted Skills ({analysis.skills?.length || 0})
                </h3>
                <span
                  className="badge badge-success"
                  style={{ fontSize: '11px', fontFamily: 'monospace' }}
                >
                  Normalized
                </span>
              </div>

              <div className="flex flex-wrap gap-2 max-h-56 overflow-y-auto pr-2">
                {analysis.skills && analysis.skills.length > 0 ? (
                  analysis.skills.map((skill, idx) => (
                    <SkillTag key={idx} name={skill} status="matching" size="md" />
                  ))
                ) : (
                  <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                    No skills recognized. Try re-uploading your resume or ensure it includes a skills section.
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Key Projects & Technical Implementations */}
          {analysis.projects && analysis.projects.length > 0 && (() => {
            // Filter out mis-parsed entries where the "title" is actually a sentence/bullet
            const actionVerbRe = /^(Built|Developed|Implemented|Designed|Created|Integrated|Reduced|Improved|Automated|Trained|Deployed|Optimized|Managed|Led|Collaborated|Used|Worked|Achieved|Processed|Configured|Migrated|Analyzed|Handled)\b/i;
            const validProjects = analysis.projects.filter((proj) => {
              const isObj = typeof proj === 'object' && proj !== null;
              const title = isObj ? proj.title : String(proj);
              if (!title || title.trim().length < 3) return false;
              if (actionVerbRe.test(title.trim())) return false;
              // Skip if title ends with period (sentence-like)
              if (title.trim().endsWith('.')) return false;
              return true;
            });
            if (validProjects.length === 0) return null;
            return (
              <div
                className="p-6 rounded-2xl space-y-4"
                style={{
                  background: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                  boxShadow: 'var(--shadow-sm)',
                }}
              >
                <div className="flex items-center justify-between">
                  <h3
                    className="text-sm font-semibold uppercase tracking-wider flex items-center gap-2"
                    style={{ color: 'var(--color-primary)' }}
                  >
                    <FolderOpen className="w-4 h-4" />
                    Projects & Work Highlights ({validProjects.length})
                  </h3>
                  <span
                    className="badge badge-primary"
                    style={{ fontSize: '11px', fontFamily: 'monospace' }}
                  >
                    Extracted from Resume
                  </span>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  {validProjects.map((proj, idx) => {
                    const isObj = typeof proj === 'object' && proj !== null;
                    const title = isObj ? proj.title : String(proj);
                    const highlights = isObj && Array.isArray(proj.highlights) ? proj.highlights : [];
                    const projSkills = isObj && Array.isArray(proj.skills) ? proj.skills : [];
                    const description = isObj ? proj.description : '';

                    return (
                      <div
                        key={idx}
                        className="p-4 rounded-xl space-y-2 transition-all"
                        style={{
                          background: 'var(--color-surface-hover)',
                          border: '1px solid var(--color-border)',
                        }}
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <span
                            className="font-bold text-sm tracking-wide"
                            style={{ color: 'var(--color-text)' }}
                          >
                            {title}
                          </span>
                          {projSkills.length > 0 && (
                            <div className="flex flex-wrap gap-1.5">
                              {projSkills.map((sk, sIdx) => (
                                <span
                                  key={sIdx}
                                  className="px-2 py-0.5 rounded-md text-[11px] font-medium"
                                  style={{
                                    background: 'rgba(59, 130, 246, 0.12)',
                                    color: 'var(--color-primary)',
                                    border: '1px solid rgba(59, 130, 246, 0.25)',
                                  }}
                                >
                                  {sk}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>

                        {highlights.length > 0 && (
                          <ul className="space-y-1.5 mt-2">
                            {highlights.map((hl, hIdx) => (
                              <li
                                key={hIdx}
                                className="text-xs flex items-start gap-2 leading-relaxed"
                                style={{ color: 'var(--color-text-secondary)' }}
                              >
                                <span
                                  className="mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0"
                                  style={{ background: 'var(--color-primary)' }}
                                />
                                <span>{hl}</span>
                              </li>
                            ))}
                          </ul>
                        )}

                        {highlights.length === 0 && description && (
                          <p className="text-xs leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                            {description}
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })()}

          {/* Experience & Education */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Experience */}
            <div
              className="p-6 rounded-2xl space-y-4"
              style={{
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              <h3
                className="text-sm font-semibold uppercase tracking-wider flex items-center gap-2"
                style={{ color: 'var(--color-primary)' }}
              >
                <Briefcase className="w-4 h-4" />
                Work History & Experience
              </h3>
              {analysis.experience && analysis.experience.length > 0 ? (
                <div className="space-y-3">
                  {analysis.experience.map((exp, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl text-xs"
                      style={{
                        background: 'var(--color-surface-hover)',
                        border: '1px solid var(--color-border)',
                      }}
                    >
                      <div
                        className="font-bold text-sm"
                        style={{ color: 'var(--color-text)' }}
                      >
                        {exp.title || exp.job_title || 'Role'}
                      </div>
                      <div style={{ color: 'var(--color-text-secondary)' }}>
                        {exp.company || 'Company'}
                      </div>
                      {(exp.duration || exp.start) && (
                        <div className="mt-1" style={{ color: 'var(--color-text-muted)' }}>
                          {exp.duration || `${exp.start || ''} - ${exp.end || 'Present'}`}
                        </div>
                      )}
                      {exp.description && (
                        <p className="mt-1.5 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                          {exp.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div
                  className="p-4 rounded-xl text-xs space-y-1"
                  style={{
                    background: 'var(--color-surface-hover)',
                    border: '1px dashed var(--color-border)',
                  }}
                >
                  <p className="font-medium" style={{ color: 'var(--color-text)' }}>
                    No work experience entries detected
                  </p>
                  <p style={{ color: 'var(--color-text-muted)' }}>
                    Academic projects, internships, or other highlights may appear in the Projects section above.
                  </p>
                </div>
              )}
            </div>

            {/* Education */}
            <div
              className="p-6 rounded-2xl space-y-4"
              style={{
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              <h3
                className="text-sm font-semibold uppercase tracking-wider flex items-center gap-2"
                style={{ color: 'var(--color-primary)' }}
              >
                <GraduationCap className="w-4 h-4" />
                Education Credentials ({analysis.education?.length || 0})
              </h3>
              {analysis.education && analysis.education.length > 0 ? (
                <div className="space-y-3">
                  {analysis.education.map((edu, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl text-xs space-y-1.5"
                      style={{
                        background: 'var(--color-surface-hover)',
                        border: '1px solid var(--color-border)',
                      }}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span
                          className="font-bold text-sm"
                          style={{ color: 'var(--color-text)' }}
                        >
                          {edu.degree || 'Degree / Credential'}
                        </span>
                        {edu.grade && (
                          <span
                            className="px-2 py-0.5 rounded-full text-[11px] font-semibold"
                            style={{
                              background: 'rgba(16, 185, 129, 0.12)',
                              color: 'var(--color-success)',
                              border: '1px solid rgba(16, 185, 129, 0.25)',
                            }}
                          >
                            Score: {edu.grade}
                          </span>
                        )}
                      </div>
                      <div className="font-medium" style={{ color: 'var(--color-text-secondary)' }}>
                        {edu.institution || 'Institution / University'}
                      </div>
                      {(edu.year || edu.graduation_year) && (
                        <div style={{ color: 'var(--color-text-muted)' }}>
                          Timeline: {edu.year || edu.graduation_year}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                  No education entries extracted.
                </p>
              )}
            </div>
          </div>
        </div>
      )}


    </div>
  );
};
