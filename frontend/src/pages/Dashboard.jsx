import { useEffect, useState } from 'react';
import axios from 'axios';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';

const API_BASE = 'https://ai-resume-analyzer-backend-afix.onrender.com/api';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('resumeData');
    if (saved) {
      setData(JSON.parse(saved));
    }
  }, []);

  const handleExportPDF = async () => {
    if (!data) return;
    setExporting(true);
    try {
      const res = await axios.post(`${API_BASE}/export-pdf`, data, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${data.filename || 'resume'}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('PDF export failed. Check the console for details.');
    } finally {
      setExporting(false);
    }
  };

  if (!data) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📊</div>
        <h3>No Data Available</h3>
        <p>Please upload a resume first to see the analysis.</p>
        <a href="/" className="btn btn-primary">Upload Resume</a>
      </div>
    );
  }

  const atsData = [
    { name: 'Score', value: data.ats_score },
    { name: 'Remaining', value: 100 - data.ats_score }
  ];

  const matchData = data.match ? [
    { name: 'Match', value: data.match.match_score },
    { name: 'Missing', value: 100 - data.match.match_score }
  ] : [];

  const formattingData = data.formatting ? [
    { name: 'Score', value: data.formatting.formatting_score },
    { name: 'Remaining', value: 100 - data.formatting.formatting_score }
  ] : [];

  const COLORS = ['#3b82f6', 'var(--color-chart-bg)'];
  const MATCH_COLORS = ['#10b981', 'var(--color-chart-bg)'];
  const FORMAT_COLORS = ['#f59e0b', 'var(--color-chart-bg)'];

  // Prepare keyword density data for charts
  const keywordData = data.keyword_density?.keyword_counts
    ? Object.entries(data.keyword_density.keyword_counts)
        .map(([name, count]) => ({ name: name.length > 12 ? name.slice(0, 10) + '…' : name, count, fullName: name }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 12)
    : [];

  // Prepare radar data from keyword density
  const radarData = keywordData.slice(0, 8).map(item => ({
    skill: item.name,
    count: item.count,
    fullMark: Math.max(...keywordData.map(d => d.count), 5)
  }));

  // Group skills by category
  const skillsByCategory = {};
  if (data.skills) {
    data.skills.forEach(skill => {
      const cat = typeof skill === 'object' ? (skill.category || 'Other') : 'General';
      const name = typeof skill === 'object' ? skill.name : skill;
      if (!skillsByCategory[cat]) skillsByCategory[cat] = [];
      skillsByCategory[cat].push(name);
    });
  }

  const getScoreColor = (score) => {
    if (score >= 75) return '#10b981';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  };

  const getScoreLabel = (score) => {
    if (score >= 75) return 'Excellent';
    if (score >= 50) return 'Good';
    return 'Needs Work';
  };

  return (
    <div className="page-container dashboard">
      {/* Header */}
      <div className="page-header">
        <div>
          <h2 className="page-title">Analysis Dashboard</h2>
          <p className="page-subtitle">
            {data.filename}
            {data.ai_generated && <span className="ai-badge">✨ AI-Powered</span>}
          </p>
        </div>
        <div className="header-actions">
          <button
            onClick={handleExportPDF}
            disabled={exporting}
            className="btn btn-secondary"
            id="export-pdf-btn"
          >
            {exporting ? 'Exporting...' : '📥 Download PDF Report'}
          </button>
          <a href="/" className="btn btn-outline">Upload Another</a>
        </div>
      </div>

      {/* Summary */}
      <div className="summary-card">
        <h3 className="summary-title">
          {data.ai_generated ? '✨ AI Summary' : '📋 Summary'}
        </h3>
        <p className="summary-text">{data.summary}</p>
      </div>

      {/* Score Cards Row */}
      <div className="scores-grid">
        {/* ATS Score */}
        <div className="score-card">
          <h3 className="score-card-title">ATS Score</h3>
          <div className="score-chart-wrapper">
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie
                  data={atsData}
                  innerRadius={55}
                  outerRadius={75}
                  startAngle={90}
                  endAngle={-270}
                  dataKey="value"
                  stroke="none"
                >
                  {atsData.map((entry, index) => (
                    <Cell key={`ats-${index}`} fill={COLORS[index]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--color-surface)',
                    borderColor: 'var(--color-border)',
                    color: 'var(--color-text)',
                    borderRadius: '8px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="score-overlay">
              <span className="score-value" style={{ color: getScoreColor(data.ats_score) }}>
                {data.ats_score}%
              </span>
              <span className="score-label">{getScoreLabel(data.ats_score)}</span>
            </div>
          </div>
        </div>

        {/* Formatting Score */}
        {data.formatting && (
          <div className="score-card">
            <h3 className="score-card-title">Formatting</h3>
            <div className="score-chart-wrapper">
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={formattingData}
                    innerRadius={55}
                    outerRadius={75}
                    startAngle={90}
                    endAngle={-270}
                    dataKey="value"
                    stroke="none"
                  >
                    {formattingData.map((entry, index) => (
                      <Cell key={`fmt-${index}`} fill={FORMAT_COLORS[index]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--color-surface)',
                      borderColor: 'var(--color-border)',
                      color: 'var(--color-text)',
                      borderRadius: '8px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="score-overlay">
                <span className="score-value" style={{ color: getScoreColor(data.formatting.formatting_score) }}>
                  {data.formatting.formatting_score}%
                </span>
                <span className="score-label">{getScoreLabel(data.formatting.formatting_score)}</span>
              </div>
            </div>
          </div>
        )}

        {/* JD Match */}
        {data.match && (
          <div className="score-card">
            <h3 className="score-card-title">JD Match</h3>
            <div className="score-chart-wrapper">
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={matchData}
                    innerRadius={55}
                    outerRadius={75}
                    startAngle={90}
                    endAngle={-270}
                    dataKey="value"
                    stroke="none"
                  >
                    {matchData.map((entry, index) => (
                      <Cell key={`match-${index}`} fill={MATCH_COLORS[index]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--color-surface)',
                      borderColor: 'var(--color-border)',
                      color: 'var(--color-text)',
                      borderRadius: '8px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="score-overlay">
                <span className="score-value" style={{ color: getScoreColor(data.match.match_score) }}>
                  {data.match.match_score}%
                </span>
                <span className="score-label">
                  {data.match.match_score >= 70 ? 'Strong' : data.match.match_score >= 40 ? 'Moderate' : 'Weak'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Keyword Density Charts */}
      {keywordData.length > 0 && (
        <div className="charts-grid">
          {/* Bar Chart */}
          <div className="chart-card">
            <h3 className="section-title">Keyword Frequency</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={keywordData} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis type="number" stroke="var(--color-text-secondary)" />
                  <YAxis
                    type="category"
                    dataKey="name"
                    stroke="var(--color-text-secondary)"
                    width={90}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--color-surface)',
                      borderColor: 'var(--color-border)',
                      color: 'var(--color-text)',
                      borderRadius: '8px'
                    }}
                    formatter={(value, name, props) => [value, props.payload.fullName]}
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Radar Chart */}
          {radarData.length >= 3 && (
            <div className="chart-card">
              <h3 className="section-title">Skills Distribution</h3>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="var(--color-border)" />
                    <PolarAngleAxis dataKey="skill" stroke="var(--color-text-secondary)" tick={{ fontSize: 11 }} />
                    <PolarRadiusAxis stroke="var(--color-border)" />
                    <Radar
                      name="Keyword Count"
                      dataKey="count"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.3}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--color-surface)',
                        borderColor: 'var(--color-border)',
                        color: 'var(--color-text)',
                        borderRadius: '8px'
                      }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Skills & Missing Skills */}
      <div className="two-column-grid">
        {/* Skills by Category */}
        <div className="card">
          <h3 className="section-title">
            <span className="section-dot dot-blue"></span>
            Detected Skills ({data.skills?.length || 0})
          </h3>
          {Object.keys(skillsByCategory).length > 0 ? (
            Object.entries(skillsByCategory).map(([category, skills]) => (
              <div key={category} className="skill-category">
                <h4 className="skill-category-name">{category}</h4>
                <div className="skills-tag-list">
                  {skills.map((skill, i) => (
                    <span key={i} className="skill-tag skill-tag-blue">{skill}</span>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <p className="no-data-text">No specific skills detected.</p>
          )}
        </div>

        {/* Missing Skills */}
        {data.match && (
          <div className="card">
            <h3 className="section-title">
              <span className="section-dot dot-red"></span>
              Missing Skills
            </h3>
            <div className="skills-tag-list">
              {data.match.missing_skills?.length > 0 ? (
                data.match.missing_skills.map((skill, i) => (
                  <span key={i} className="skill-tag skill-tag-red">{skill}</span>
                ))
              ) : (
                <p className="success-text">✅ You have all the required skills!</p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Formatting Details */}
      {data.formatting && (
        <div className="card">
          <h3 className="section-title">
            <span className="section-dot dot-amber"></span>
            Formatting Analysis
          </h3>
          <div className="formatting-grid">
            <div className="formatting-stat">
              <span className="formatting-stat-value">{data.formatting.word_count}</span>
              <span className="formatting-stat-label">Words</span>
            </div>
            <div className="formatting-stat">
              <span className="formatting-stat-value">{data.formatting.page_estimate}</span>
              <span className="formatting-stat-label">Est. Pages</span>
            </div>
            <div className="formatting-stat">
              <span className="formatting-stat-value">{data.formatting.sections_found?.length || 0}</span>
              <span className="formatting-stat-label">Sections Found</span>
            </div>
          </div>
          {data.formatting.sections_found?.length > 0 && (
            <div className="formatting-sections">
              <h4 className="subsection-title">Sections Detected</h4>
              <div className="skills-tag-list">
                {data.formatting.sections_found.map((s, i) => (
                  <span key={i} className="skill-tag skill-tag-green">{s}</span>
                ))}
              </div>
            </div>
          )}
          {data.formatting.issues?.length > 0 && (
            <div className="formatting-issues">
              <h4 className="subsection-title">Feedback</h4>
              <ul className="issues-list">
                {data.formatting.issues.map((issue, i) => (
                  <li key={i} className="issue-item">{issue}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Improvements */}
      {data.improvements?.length > 0 && (
        <div className="card">
          <h3 className="section-title">
            <span className="section-dot dot-green"></span>
            Recommended Improvements
          </h3>
          <ul className="improvements-list">
            {data.improvements.map((imp, i) => (
              <li key={i} className="improvement-item">
                <span className="improvement-icon">💡</span>
                {imp}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
