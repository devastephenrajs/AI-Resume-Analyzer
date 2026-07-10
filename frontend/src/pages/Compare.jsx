import { useState } from 'react';
import axios from 'axios';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell
} from 'recharts';

const API_BASE = 'https://ai-resume-analyzer-backend-afix.onrender.com/api';

export default function Compare() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleCompare = async (e) => {
    e.preventDefault();
    if (!file1 || !file2) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file1', file1);
    formData.append('file2', file2);

    try {
      const res = await axios.post(`${API_BASE}/compare`, formData);
      setResult(res.data);
    } catch (err) {
      console.error('Comparison failed:', err);
      alert('Comparison failed. Please check the console for details.');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 75) return '#10b981';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  };

  const COLORS = ['#3b82f6', '#8b5cf6'];

  return (
    <div className="page-container">
      <h2 className="page-title">Compare Resumes</h2>
      <p className="page-subtitle">Upload two resumes for a side-by-side analysis</p>

      <form onSubmit={handleCompare} className="compare-upload-form">
        <div className="compare-upload-grid">
          <div className="compare-upload-card">
            <div className="compare-upload-label">Resume 1</div>
            <label className="file-drop-zone">
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => setFile1(e.target.files[0])}
                className="file-input-hidden"
              />
              <div className="file-drop-content">
                <span className="file-drop-icon">📄</span>
                <span className="file-drop-text">
                  {file1 ? file1.name : 'Click to select file'}
                </span>
              </div>
            </label>
          </div>

          <div className="compare-vs">VS</div>

          <div className="compare-upload-card">
            <div className="compare-upload-label">Resume 2</div>
            <label className="file-drop-zone">
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => setFile2(e.target.files[0])}
                className="file-input-hidden"
              />
              <div className="file-drop-content">
                <span className="file-drop-icon">📄</span>
                <span className="file-drop-text">
                  {file2 ? file2.name : 'Click to select file'}
                </span>
              </div>
            </label>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !file1 || !file2}
          className="btn btn-primary btn-lg compare-submit-btn"
        >
          {loading ? (
            <span className="btn-loading">Comparing...</span>
          ) : (
            'Compare Resumes'
          )}
        </button>
      </form>

      {result && (
        <div className="compare-results">
          {/* Score Comparison */}
          <div className="compare-section">
            <h3 className="section-title">Score Comparison</h3>
            <div className="compare-scores-grid">
              {[
                {
                  label: 'ATS Score',
                  val1: result.resume1.ats_score,
                  val2: result.resume2.ats_score,
                  diff: result.comparison.ats_difference
                },
                {
                  label: 'Formatting',
                  val1: result.resume1.formatting.formatting_score,
                  val2: result.resume2.formatting.formatting_score,
                  diff: result.comparison.formatting_difference
                }
              ].map((metric) => (
                <div key={metric.label} className="compare-metric-card">
                  <h4 className="compare-metric-label">{metric.label}</h4>
                  <div className="compare-metric-values">
                    <div className="compare-metric-value">
                      <span className="compare-metric-name">{result.resume1.filename}</span>
                      <span
                        className="compare-metric-score"
                        style={{ color: getScoreColor(metric.val1) }}
                      >
                        {metric.val1}%
                      </span>
                    </div>
                    <div className="compare-metric-divider">
                      <span className={`compare-diff ${metric.diff > 0 ? 'positive' : metric.diff < 0 ? 'negative' : 'neutral'}`}>
                        {metric.diff > 0 ? `+${metric.diff}` : metric.diff}
                      </span>
                    </div>
                    <div className="compare-metric-value">
                      <span className="compare-metric-name">{result.resume2.filename}</span>
                      <span
                        className="compare-metric-score"
                        style={{ color: getScoreColor(metric.val2) }}
                      >
                        {metric.val2}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bar Chart Comparison */}
          <div className="compare-section">
            <h3 className="section-title">Visual Comparison</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={[
                  {
                    name: 'ATS Score',
                    [result.resume1.filename]: result.resume1.ats_score,
                    [result.resume2.filename]: result.resume2.ats_score
                  },
                  {
                    name: 'Formatting',
                    [result.resume1.filename]: result.resume1.formatting.formatting_score,
                    [result.resume2.filename]: result.resume2.formatting.formatting_score
                  },
                  {
                    name: 'Skills Count',
                    [result.resume1.filename]: result.resume1.skills.length,
                    [result.resume2.filename]: result.resume2.skills.length
                  }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="name" stroke="var(--color-text-secondary)" />
                  <YAxis stroke="var(--color-text-secondary)" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--color-surface)',
                      borderColor: 'var(--color-border)',
                      color: 'var(--color-text)',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Bar dataKey={result.resume1.filename} fill={COLORS[0]} radius={[4, 4, 0, 0]} />
                  <Bar dataKey={result.resume2.filename} fill={COLORS[1]} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Skills Venn Diagram (text-based) */}
          <div className="compare-section">
            <h3 className="section-title">Skills Analysis</h3>
            <div className="compare-skills-grid">
              <div className="compare-skills-column">
                <h4 className="compare-skills-header" style={{ color: COLORS[0] }}>
                  Only in {result.resume1.filename}
                  <span className="skills-count-badge">{result.comparison.unique_to_resume1.length}</span>
                </h4>
                <div className="skills-tag-list">
                  {result.comparison.unique_to_resume1.length > 0 ? (
                    result.comparison.unique_to_resume1.map((s, i) => (
                      <span key={i} className="skill-tag skill-tag-blue">{s}</span>
                    ))
                  ) : (
                    <span className="no-skills-text">No unique skills</span>
                  )}
                </div>
              </div>

              <div className="compare-skills-column compare-skills-shared">
                <h4 className="compare-skills-header" style={{ color: '#10b981' }}>
                  Shared Skills
                  <span className="skills-count-badge">{result.comparison.shared_skills.length}</span>
                </h4>
                <div className="skills-tag-list">
                  {result.comparison.shared_skills.length > 0 ? (
                    result.comparison.shared_skills.map((s, i) => (
                      <span key={i} className="skill-tag skill-tag-green">{s}</span>
                    ))
                  ) : (
                    <span className="no-skills-text">No shared skills</span>
                  )}
                </div>
              </div>

              <div className="compare-skills-column">
                <h4 className="compare-skills-header" style={{ color: COLORS[1] }}>
                  Only in {result.resume2.filename}
                  <span className="skills-count-badge">{result.comparison.unique_to_resume2.length}</span>
                </h4>
                <div className="skills-tag-list">
                  {result.comparison.unique_to_resume2.length > 0 ? (
                    result.comparison.unique_to_resume2.map((s, i) => (
                      <span key={i} className="skill-tag skill-tag-purple">{s}</span>
                    ))
                  ) : (
                    <span className="no-skills-text">No unique skills</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Side-by-Side Summaries */}
          <div className="compare-section">
            <h3 className="section-title">Candidate Summaries</h3>
            <div className="compare-summaries-grid">
              <div className="compare-summary-card">
                <h4 className="compare-summary-name">{result.resume1.filename}</h4>
                <p className="compare-summary-text">{result.resume1.summary}</p>
                {result.resume1.ai_generated && (
                  <span className="ai-badge">✨ AI Generated</span>
                )}
              </div>
              <div className="compare-summary-card">
                <h4 className="compare-summary-name">{result.resume2.filename}</h4>
                <p className="compare-summary-text">{result.resume2.summary}</p>
                {result.resume2.ai_generated && (
                  <span className="ai-badge">✨ AI Generated</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
