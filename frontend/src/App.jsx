import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import {
  FileText,
  UploadCloud,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Sparkles,
  History,
  RotateCcw,
  Download,
  Trash2,
  Briefcase,
  Zap,
  Tag,
  ArrowRight,
  ExternalLink,
  Percent,
  Check,
  ChevronRight,
  Layers,
  Search,
  Sliders,
  Plus,
  Wand2,
  Filter,
  Code2
} from 'lucide-react';
import './App.css';

const API_BASE = '/api';

const BUILDER_AVAILABLE_SKILLS = [
  'React', 'TypeScript', 'JavaScript', 'Next.js', 'Vue.js', 'HTML5', 'CSS3', 'Tailwind CSS', 'Redux',
  'Python', 'FastAPI', 'Django', 'Flask', 'Node.js', 'Express.js', 'RESTful APIs', 'WebSockets',
  'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite', 'SQL',
  'Docker', 'Kubernetes', 'AWS', 'Google Cloud (GCP)', 'Microsoft Azure', 'CI/CD', 'Git', 'Linux',
  'PyTest', 'Jest', 'Unit Testing', 'Scikit-Learn', 'PyTorch', 'TensorFlow', 'Natural Language Processing', 'Machine Learning', 'Large Language Models (LLMs)'
];

export default function App() {
  // Input states
  const [resumeFile, setResumeFile] = useState(null);
  const [isSampleResumeLoaded, setIsSampleResumeLoaded] = useState(false);
  const [useRawText, setUseRawText] = useState(false);
  const [rawResumeText, setRawResumeText] = useState('');
  const [jobTitle, setJobTitle] = useState('Senior Full Stack Engineer');
  const [jobDescription, setJobDescription] = useState('');
  const [sampleJDs, setSampleJDs] = useState([]);
  const [activeSampleId, setActiveSampleId] = useState('');

  // Category & Custom Builder states
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [showCustomBuilder, setShowCustomBuilder] = useState(false);
  const [customRoleTitle, setCustomRoleTitle] = useState('Junior Full Stack Developer');
  const [customExpLevel, setCustomExpLevel] = useState('Junior (0-2 yrs)');
  const [selectedTechSkills, setSelectedTechSkills] = useState([
    'React', 'JavaScript', 'HTML5', 'CSS3', 'Python', 'SQL', 'Git'
  ]);

  // Processing & Results
  const [loading, setLoading] = useState(false);
  const [progressMsg, setProgressMsg] = useState('');
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  // History modal
  const [historyList, setHistoryList] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [activeSkillTab, setActiveSkillTab] = useState('all');

  const fileInputRef = useRef(null);

  // Fetch initial sample job descriptions & history on mount
  useEffect(() => {
    fetchSampleJobDescriptions();
    fetchHistory();
  }, []);

  const fetchSampleJobDescriptions = async () => {
    try {
      const res = await fetch(`${API_BASE}/sample-job-descriptions`);
      if (res.ok) {
        const data = await res.json();
        setSampleJDs(data);
        if (data.length > 0) {
          // Pre-populate with first sample
          setActiveSampleId(data[0].id);
          setJobTitle(data[0].title);
          setJobDescription(data[0].description);
        }
      }
    } catch (err) {
      console.warn('Could not load sample job descriptions:', err);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/history`);
      if (res.ok) {
        const data = await res.json();
        setHistoryList(data);
      }
    } catch (err) {
      console.warn('Could not load analysis history:', err);
    }
  };

  const handleSelectSampleJD = (sample) => {
    setActiveSampleId(sample.id);
    setJobTitle(sample.title);
    setJobDescription(sample.description);
    setShowCustomBuilder(false);
  };

  const handleToggleTechSkill = (skill) => {
    setSelectedTechSkills((prev) =>
      prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]
    );
  };

  const handleGenerateCustomJD = () => {
    const title = customRoleTitle.trim() || 'Software Developer';
    const exp = customExpLevel;
    const skillsList = selectedTechSkills.length > 0 ? selectedTechSkills : ['React', 'Python', 'Git'];

    const skillsBullets = skillsList
      .map((s) => `- Hands-on experience or working knowledge of ${s}.`)
      .join('\n');

    const generated = (
      `We are seeking a motivated ${title} (${exp}) to join our collaborative engineering team.\n\n` +
      `Key Responsibilities:\n` +
      `- Design, develop, test, and maintain high-quality application features.\n` +
      `- Collaborate with frontend and backend developers in an Agile/Scrum environment.\n` +
      `- Write clean, readable code and participate in peer code reviews.\n` +
      `- Debug application issues and optimize performance for a seamless user experience.\n\n` +
      `Requirements & Technical Skills:\n` +
      `- Experience level: ${exp} of relevant software development experience or strong project portfolio.\n` +
      `${skillsBullets}\n` +
      `- Strong problem-solving abilities, eagerness to learn, and excellent team communication.`
    );

    setJobTitle(title);
    setJobDescription(generated);
    setActiveSampleId('');
    setShowCustomBuilder(false);
  };

  const handleClearJD = () => {
    setJobTitle('');
    setJobDescription('');
    setActiveSampleId('');
  };

  const handleLoadSampleResume = async () => {
    try {
      const res = await fetch(`${API_BASE}/sample-resume-download`);
      if (res.ok) {
        const blob = await res.blob();
        const file = new File([blob], 'sample_resume.pdf', { type: 'application/pdf' });
        setResumeFile(file);
        setIsSampleResumeLoaded(true);
        setUseRawText(false);
      } else {
        // Fallback: set flag
        setIsSampleResumeLoaded(true);
      }
    } catch (err) {
      console.error('Error fetching sample resume:', err);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setResumeFile(file);
      setIsSampleResumeLoaded(false);
      setErrorMsg('');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf') || file.name.endsWith('.txt')) {
        setResumeFile(file);
        setIsSampleResumeLoaded(false);
        setErrorMsg('');
      } else {
        setErrorMsg('Please upload a PDF or text file.');
      }
    }
  };

  const handleClearResume = () => {
    setResumeFile(null);
    setIsSampleResumeLoaded(false);
    setRawResumeText('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleAnalyze = async () => {
    setErrorMsg('');
    if (!useRawText && !resumeFile && !isSampleResumeLoaded) {
      setErrorMsg('Please upload a resume PDF or paste resume text.');
      return;
    }
    if (useRawText && !rawResumeText.trim()) {
      setErrorMsg('Please enter resume text to analyze.');
      return;
    }
    if (!jobDescription.trim()) {
      setErrorMsg('Please paste a job description.');
      return;
    }

    setLoading(true);

    // Multi-step animated progress indicators
    const steps = [
      'Extracting resume text...',
      'Running NLP tokenization & stopword removal...',
      'Vectorizing text & computing TF-IDF cosine similarity...',
      'Matching required vs available skills...',
      'Synthesizing AI improvement recommendations...'
    ];

    let stepIdx = 0;
    setProgressMsg(steps[0]);
    const progressTimer = setInterval(() => {
      stepIdx++;
      if (stepIdx < steps.length) {
        setProgressMsg(steps[stepIdx]);
      }
    }, 450);

    try {
      let response;
      if (useRawText) {
        response = await fetch(`${API_BASE}/analyze-text`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            resume_text: rawResumeText,
            job_description: jobDescription,
            job_title: jobTitle
          })
        });
      } else {
        const formData = new FormData();
        formData.append('file', resumeFile);
        formData.append('job_description', jobDescription);
        formData.append('job_title', jobTitle);

        response = await fetch(`${API_BASE}/analyze`, {
          method: 'POST',
          body: formData
        });
      }

      clearInterval(progressTimer);

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Analysis failed. Please try again.');
      }

      const data = await response.json();
      setResult(data);
      fetchHistory(); // Refresh SQLite history

      // If match score is strong, trigger celebratory confetti
      if (data.match_percentage >= 70) {
        confetti({
          particleCount: 65,
          spread: 70,
          origin: { y: 0.6 }
        });
      }

      // Smooth scroll to results
      setTimeout(() => {
        document.getElementById('results-section')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);

    } catch (err) {
      clearInterval(progressTimer);
      setErrorMsg(err.message || 'An unexpected error occurred during analysis.');
    } finally {
      setLoading(false);
      setProgressMsg('');
    }
  };

  const handleSelectHistoryItem = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/history/${id}`);
      if (res.ok) {
        const data = await res.json();
        setResult(data);
        setShowHistory(false);
        setTimeout(() => {
          document.getElementById('results-section')?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    } catch (err) {
      console.error('Failed to load history record:', err);
    }
  };

  const handleDeleteHistoryItem = async (e, id) => {
    e.stopPropagation();
    try {
      await fetch(`${API_BASE}/history/${id}`, { method: 'DELETE' });
      setHistoryList((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error('Failed to delete history record:', err);
    }
  };

  const handleClearAllHistory = async () => {
    try {
      await fetch(`${API_BASE}/history`, { method: 'DELETE' });
      setHistoryList([]);
    } catch (err) {
      console.error('Failed to clear history:', err);
    }
  };

  const handleDownloadJSON = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `resume_match_report_${result.id || 'analysis'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Helper for match score color
  const getScoreColor = (score) => {
    if (score >= 75) return '#10b981';
    if (score >= 50) return '#f59e0b';
    return '#f43f5e';
  };

  const getVerdictInfo = (score) => {
    if (score >= 75) return { label: 'High Alignment', className: 'verdict-high' };
    if (score >= 50) return { label: 'Moderate Match', className: 'verdict-med' };
    return { label: 'Skill Gap Detected', className: 'verdict-low' };
  };

  return (
    <div className="app-container">
      {/* Navbar */}
      <nav className="navbar">
        <div className="brand">
          <div className="brand-icon-box">
            <Sparkles size={24} />
          </div>
          <div>
            <h1 className="brand-title">AI-Resume-Matcher</h1>
            <p className="brand-subtitle">NLP & TF-IDF Skills Gap Analyzer</p>
          </div>
        </div>

        <div className="nav-actions">
          <button
            className="btn-secondary"
            onClick={() => setShowHistory(true)}
            title="View Analysis History"
          >
            <History size={16} />
            <span>History</span>
            {historyList.length > 0 && (
              <span className="badge-count">{historyList.length}</span>
            )}
          </button>

          {result && (
            <button
              className="btn-secondary"
              onClick={() => {
                setResult(null);
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
            >
              <RotateCcw size={15} />
              <span>Reset</span>
            </button>
          )}
        </div>
      </nav>

      {/* Hero Header */}
      <header className="hero">
        <div className="hero-pill">
          <Zap size={14} />
          <span>Powered by Scikit-learn TF-IDF & NLP Tokenization</span>
        </div>
        <h2 className="hero-heading">Optimize Your Resume for Any Job</h2>
        <p className="hero-subtext">
          Upload your resume, paste the target job description, and get instant similarity scores,
          missing skill identification, and ATS optimization recommendations.
        </p>
      </header>

      {/* Error Banner */}
      {errorMsg && (
        <div style={{
          background: 'rgba(244, 63, 94, 0.15)',
          border: '1px solid rgba(244, 63, 94, 0.4)',
          color: '#fda4af',
          padding: '12px 18px',
          borderRadius: '12px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <AlertTriangle size={18} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Two-Column Input Workspace */}
      <div className="workspace-grid">
        {/* Left Column: Resume Input */}
        <section className="card">
          <div className="card-header">
            <div className="card-title-group">
              <FileText size={20} className="card-icon" />
              <h3 className="card-title">1. Your Resume</h3>
            </div>
            <button
              className="pill-btn"
              onClick={() => setUseRawText(!useRawText)}
            >
              {useRawText ? 'Switch to PDF Upload' : 'Paste Text Instead'}
            </button>
          </div>

          {!useRawText ? (
            <>
              {resumeFile ? (
                <div className="file-selected-box">
                  <div className="file-info">
                    <FileText size={28} color="#818cf8" />
                    <div>
                      <div className="file-name">{resumeFile.name}</div>
                      <div className="file-size">
                        {(resumeFile.size / 1024).toFixed(1)} KB • Ready for analysis
                      </div>
                    </div>
                  </div>
                  <button
                    className="btn-icon-clear"
                    onClick={handleClearResume}
                    title="Remove file"
                  >
                    <XCircle size={20} />
                  </button>
                </div>
              ) : (
                <div
                  className="dropzone"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    accept=".pdf,.txt"
                    style={{ display: 'none' }}
                  />
                  <div className="dropzone-icon">
                    <UploadCloud size={28} />
                  </div>
                  <div className="dropzone-prompt">Click or drag & drop Resume PDF</div>
                  <div className="dropzone-sub">Supports PDF and TXT formats</div>
                </div>
              )}

              <button
                type="button"
                className="quick-sample-btn"
                onClick={handleLoadSampleResume}
              >
                <Sparkles size={15} />
                <span>Load Sample Resume (Alex Morgan - Senior Full Stack & AI)</span>
              </button>
            </>
          ) : (
            <textarea
              className="textarea-field"
              placeholder="Paste raw resume text here (Summary, Skills, Work Experience, Projects)..."
              value={rawResumeText}
              onChange={(e) => setRawResumeText(e.target.value)}
              rows={10}
            />
          )}
        </section>

        {/* Right Column: Job Description */}
        <section className="card">
          <div className="card-header">
            <div className="card-title-group">
              <Briefcase size={20} className="card-icon" />
              <h3 className="card-title">2. Target Job Description</h3>
            </div>
            <div style={{ display: 'flex', gap: '6px' }}>
              <button
                type="button"
                className={`pill-btn ${showCustomBuilder ? 'active' : ''}`}
                onClick={() => setShowCustomBuilder(!showCustomBuilder)}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}
                title="Open Custom Role Generator"
              >
                <Wand2 size={13} />
                <span>{showCustomBuilder ? 'Close Generator' : '✨ Custom Role Generator'}</span>
              </button>
              {(jobTitle || jobDescription) && (
                <button
                  type="button"
                  className="pill-btn"
                  onClick={handleClearJD}
                  title="Clear Job Description"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Interactive Custom Role Builder Panel */}
          {showCustomBuilder && (
            <div className="custom-builder-box">
              <div className="builder-header">
                <span className="builder-title">
                  <Wand2 size={15} color="#818cf8" />
                  Customize Any Role & Tech Stack
                </span>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  {selectedTechSkills.length} skills selected
                </span>
              </div>

              <div className="builder-grid-inputs">
                <div>
                  <label className="input-label">Custom Role Title</label>
                  <input
                    type="text"
                    className="text-input"
                    value={customRoleTitle}
                    onChange={(e) => setCustomRoleTitle(e.target.value)}
                    placeholder="e.g. Junior Full Stack Developer, Frontend Dev..."
                    style={{ marginBottom: 0 }}
                  />
                </div>
                <div>
                  <label className="input-label">Experience Level</label>
                  <select
                    className="builder-select"
                    value={customExpLevel}
                    onChange={(e) => setCustomExpLevel(e.target.value)}
                  >
                    <option value="Junior (0-2 yrs)">Junior (0-2 yrs)</option>
                    <option value="Mid-Level (2-4 yrs)">Mid-Level (2-4 yrs)</option>
                    <option value="Senior (4+ yrs)">Senior (4+ yrs)</option>
                    <option value="Lead / Architect (6+ yrs)">Lead / Architect (6+ yrs)</option>
                  </select>
                </div>
              </div>

              <div className="builder-chips-section">
                <span className="builder-chips-title">Select Required Skills for This Role:</span>
                <div className="builder-chips-wrap">
                  {BUILDER_AVAILABLE_SKILLS.map((skill) => {
                    const isSelected = selectedTechSkills.includes(skill);
                    return (
                      <button
                        key={skill}
                        type="button"
                        className={`tech-select-chip ${isSelected ? 'selected' : ''}`}
                        onClick={() => handleToggleTechSkill(skill)}
                      >
                        {isSelected ? <Check size={11} /> : <Plus size={11} />}
                        <span>{skill}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="builder-actions-row">
                <button
                  type="button"
                  className="pill-btn"
                  onClick={() => setSelectedTechSkills([])}
                  style={{ fontSize: '0.72rem' }}
                >
                  Deselect All
                </button>
                <button
                  type="button"
                  className="btn-builder-apply"
                  onClick={handleGenerateCustomJD}
                >
                  <Zap size={14} />
                  <span>Generate & Apply Custom JD</span>
                </button>
              </div>
            </div>
          )}

          <label className="input-label">Job Title / Target Position</label>
          <input
            type="text"
            className="text-input"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            placeholder="e.g. Junior Full Stack Developer or Frontend Engineer"
          />

          {/* Category Filter Tabs */}
          {sampleJDs.length > 0 && (
            <>
              <div className="category-tabs-row">
                {['All', 'Full Stack', 'Frontend', 'Backend', 'AI & Data', 'Cloud & DevOps'].map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    className={`category-tab ${selectedCategory === cat ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              {/* Filtered Preset Pills */}
              <div className="preset-pills-container">
                {sampleJDs
                  .filter((sample) => selectedCategory === 'All' || sample.category === selectedCategory)
                  .map((sample) => (
                    <button
                      key={sample.id}
                      type="button"
                      className={`preset-pill-item ${activeSampleId === sample.id ? 'active' : ''}`}
                      onClick={() => handleSelectSampleJD(sample)}
                    >
                      <span>{sample.title.split('(')[0].trim()}</span>
                      {sample.level && <span className="preset-level-tag">{sample.level.split(' ')[0]}</span>}
                    </button>
                  ))}
              </div>
            </>
          )}

          <textarea
            className="textarea-field"
            placeholder="Paste job posting description, key qualifications, and technical requirements..."
            value={jobDescription}
            onChange={(e) => {
              setJobDescription(e.target.value);
              setActiveSampleId('');
            }}
          />
          <div className="char-counter">
            {jobDescription.split(/\s+/).filter(Boolean).length} words • {jobDescription.length} characters
          </div>
        </section>
      </div>

      {/* Action Execution Bar */}
      <div className="action-bar">
        <button
          className="btn-primary-action"
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? (
            <>
              <div className="animate-spin" style={{ width: 20, height: 20, border: '2px solid white', borderTopColor: 'transparent', borderRadius: '50%' }} />
              <span>Analyzing Documents...</span>
            </>
          ) : (
            <>
              <Zap size={20} />
              <span>Analyze Resume Compatibility</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>

        {loading && progressMsg && (
          <div className="progress-indicator">
            <Sparkles size={16} />
            <span>{progressMsg}</span>
          </div>
        )}
      </div>

      {/* Results Dashboard */}
      {result && (
        <main id="results-section" className="results-container animate-fade-in">
          {/* Header Score Card */}
          <div className="results-header-card">
            {/* Circular Score Gauge */}
            <div className="gauge-wrapper">
              <svg width="190" height="190" className="gauge-svg">
                <circle
                  cx="95"
                  cy="95"
                  r="78"
                  fill="none"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="16"
                />
                <circle
                  cx="95"
                  cy="95"
                  r="78"
                  fill="none"
                  stroke={getScoreColor(result.match_percentage)}
                  strokeWidth="16"
                  strokeDasharray={2 * Math.PI * 78}
                  strokeDashoffset={2 * Math.PI * 78 * (1 - result.match_percentage / 100)}
                  strokeLinecap="round"
                  style={{ transition: 'stroke-dashoffset 1s ease-out' }}
                />
              </svg>
              <div className="gauge-center-text">
                <div
                  className="gauge-percentage"
                  style={{ color: getScoreColor(result.match_percentage) }}
                >
                  {result.match_percentage}%
                </div>
                <div className="gauge-label">Match Score</div>
              </div>
            </div>

            {/* Score Breakdown Details */}
            <div className="score-details">
              <div className="score-title-row">
                <div>
                  <h3 className="role-badge-title">{result.job_title || 'Role Compatibility'}</h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Analyzed against: {result.filename || 'Uploaded Resume'}
                  </p>
                </div>
                <div className={`match-verdict-badge ${getVerdictInfo(result.match_percentage).className}`}>
                  <Check size={14} />
                  <span>{getVerdictInfo(result.match_percentage).label}</span>
                </div>
              </div>

              {/* 3 Metric Summary Boxes */}
              <div className="metrics-row">
                <div className="metric-box">
                  <div className="metric-title">TF-IDF Similarity</div>
                  <div className="metric-value">{result.tfidf_score}%</div>
                  <div className="metric-sub">Semantic Vector Overlap</div>
                </div>

                <div className="metric-box">
                  <div className="metric-title">Skill Alignment</div>
                  <div className="metric-value">{result.skill_score}%</div>
                  <div className="metric-sub">
                    {result.matched_skills?.length || 0} of {result.jd_skills?.length || 0} Skills
                  </div>
                </div>

                <div className="metric-box">
                  <div className="metric-title">Missing Skills</div>
                  <div className="metric-value" style={{ color: result.missing_skills?.length > 0 ? '#fb7185' : '#34d399' }}>
                    {result.missing_skills?.length || 0}
                  </div>
                  <div className="metric-sub">Required Gaps</div>
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '10px', marginTop: '8px', flexWrap: 'wrap' }}>
                <button className="btn-secondary" onClick={handleDownloadJSON}>
                  <Download size={15} />
                  <span>Export Report (JSON)</span>
                </button>
                <button className="btn-secondary" onClick={() => window.print()}>
                  <ExternalLink size={15} />
                  <span>Print / Save View</span>
                </button>
              </div>
            </div>
          </div>

          {/* Skills Breakdown Section */}
          <div className="skills-grid">
            {/* Matched Skills Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-title-group">
                  <CheckCircle2 size={20} color="#10b981" />
                  <h4 className="card-title">Skills Available in Resume</h4>
                </div>
                <span className="card-badge" style={{ color: '#34d399', background: 'var(--accent-emerald-bg)' }}>
                  {result.matched_skills?.length || 0} Found
                </span>
              </div>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                These required skills were successfully identified in your resume:
              </p>
              <div className="badge-list">
                {result.matched_skills && result.matched_skills.length > 0 ? (
                  result.matched_skills.map((skill, idx) => (
                    <span key={idx} className="skill-tag matched">
                      <Check size={13} />
                      <span>{skill}</span>
                    </span>
                  ))
                ) : (
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-subtle)' }}>
                    No exact required skills matched yet.
                  </p>
                )}
              </div>
            </div>

            {/* Missing Skills Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-title-group">
                  <XCircle size={20} color="#f43f5e" />
                  <h4 className="card-title">Missing Skills for This Job</h4>
                </div>
                <span className="card-badge" style={{ color: '#fb7185', background: 'var(--accent-rose-bg)' }}>
                  {result.missing_skills?.length || 0} Gaps
                </span>
              </div>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                The job posting requests these skills, but they were not found in your resume:
              </p>
              <div className="badge-list">
                {result.missing_skills && result.missing_skills.length > 0 ? (
                  result.missing_skills.map((skill, idx) => (
                    <span key={idx} className="skill-tag missing">
                      <XCircle size={13} />
                      <span>{skill}</span>
                    </span>
                  ))
                ) : (
                  <span className="skill-tag matched">
                    <Check size={13} />
                    <span>All required skills are covered!</span>
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Bonus / Additional Skills in Resume */}
          {result.additional_skills && result.additional_skills.length > 0 && (
            <div className="card" style={{ marginBottom: '28px' }}>
              <div className="card-header">
                <div className="card-title-group">
                  <Layers size={20} color="#818cf8" />
                  <h4 className="card-title">Additional / Bonus Skills in Resume</h4>
                </div>
                <span className="card-badge">
                  {result.additional_skills.length} Bonus Skills
                </span>
              </div>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                Extra skills detected on your resume that add value beyond the explicit job requirements:
              </p>
              <div className="badge-list">
                {result.additional_skills.map((skill, idx) => (
                  <span key={idx} className="skill-tag additional">
                    <Sparkles size={12} />
                    <span>{skill}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Relevant Keywords Matrix */}
          {result.keywords && result.keywords.length > 0 && (
            <div className="card keywords-section">
              <div className="card-header">
                <div className="card-title-group">
                  <Tag size={20} className="card-icon" />
                  <h4 className="card-title">Relevant Keywords & TF-IDF Importance</h4>
                </div>
                <span className="card-badge">Top JD Terms</span>
              </div>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                Key vocabulary extracted from the job description with TF-IDF relevance weights:
              </p>
              <div className="keyword-chips-wrap">
                {result.keywords.map((item, idx) => (
                  <div
                    key={idx}
                    className={`kw-chip ${item.in_resume ? 'present' : 'absent'}`}
                  >
                    {item.in_resume ? (
                      <Check size={13} color="#10b981" />
                    ) : (
                      <XCircle size={13} color="#f43f5e" />
                    )}
                    <span style={{ fontWeight: 600 }}>{item.keyword}</span>
                    <span className="kw-weight">{item.importance}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Improvement Suggestions */}
          {result.suggestions && result.suggestions.length > 0 && (
            <div className="card">
              <div className="card-header">
                <div className="card-title-group">
                  <Sparkles size={20} color="#6366f1" />
                  <h4 className="card-title">AI Suggestions to Improve Your Resume</h4>
                </div>
                <span className="card-badge">
                  {result.suggestions.length} Recommendations
                </span>
              </div>
              <div className="suggestions-grid">
                {result.suggestions.map((sug, idx) => (
                  <div key={idx} className={`suggestion-card ${sug.severity || 'medium'}`}>
                    <div className="suggestion-header">
                      <span className="suggestion-title">{sug.title}</span>
                      <span className={`severity-pill ${sug.severity || 'medium'}`}>
                        {sug.severity || 'Recommendation'}
                      </span>
                    </div>
                    <p className="suggestion-desc">{sug.description}</p>
                    <div className="suggestion-action-box">
                      <strong>Action Item:</strong> {sug.action}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      )}

      {/* History Modal */}
      {showHistory && (
        <div className="modal-overlay" onClick={() => setShowHistory(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <History size={20} color="#6366f1" />
                <h3 className="modal-title">Analysis History (SQLite)</h3>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                {historyList.length > 0 && (
                  <button
                    className="btn-secondary"
                    style={{ fontSize: '0.78rem', padding: '5px 10px', color: '#fda4af' }}
                    onClick={handleClearAllHistory}
                  >
                    Clear All
                  </button>
                )}
                <button
                  className="btn-icon-clear"
                  onClick={() => setShowHistory(false)}
                >
                  <XCircle size={22} />
                </button>
              </div>
            </div>

            <div className="modal-body">
              {historyList.length === 0 ? (
                <div className="empty-state">
                  <History size={40} style={{ opacity: 0.3, marginBottom: '10px' }} />
                  <p>No previous analyses recorded in SQLite yet.</p>
                </div>
              ) : (
                historyList.map((item) => (
                  <div
                    key={item.id}
                    className="history-item-row"
                    onClick={() => handleSelectHistoryItem(item.id)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="history-item-info">
                      <div className="history-item-title">{item.job_title}</div>
                      <div className="history-item-meta">
                        {item.filename} • {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {item.matched_count} matched / {item.missing_count} missing
                      </div>
                    </div>

                    <div className="history-actions">
                      <span
                        className="history-score-pill"
                        style={{
                          color: getScoreColor(item.match_percentage),
                          background: item.match_percentage >= 75 ? 'var(--accent-emerald-bg)' : item.match_percentage >= 50 ? 'var(--accent-amber-bg)' : 'var(--accent-rose-bg)'
                        }}
                      >
                        {item.match_percentage}%
                      </span>
                      <button
                        className="btn-icon-clear"
                        onClick={(e) => handleDeleteHistoryItem(e, item.id)}
                        title="Delete record"
                      >
                        <Trash2 size={16} />
                      </button>
                      <ChevronRight size={18} color="var(--text-muted)" />
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
