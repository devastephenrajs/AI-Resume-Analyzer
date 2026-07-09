import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export default function History() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_BASE}/history`);
      setAnalyses(res.data.analyses || []);
    } catch (err) {
      console.error('Failed to fetch history:', err);
      setError('Could not connect to the server. Make sure MongoDB and the backend are running.');
    } finally {
      setLoading(false);
    }
  };

  const handleView = async (id) => {
    try {
      const res = await axios.get(`${API_BASE}/history/${id}`);
      localStorage.setItem('resumeData', JSON.stringify(res.data));
      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to load analysis:', err);
      alert('Failed to load this analysis.');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this analysis?')) return;
    try {
      await axios.delete(`${API_BASE}/history/${id}`);
      setAnalyses(prev => prev.filter(a => a.id !== id));
    } catch (err) {
      console.error('Failed to delete:', err);
      alert('Failed to delete this analysis.');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 75) return 'var(--color-success)';
    if (score >= 50) return 'var(--color-warning)';
    return 'var(--color-danger)';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p className="loading-text">Loading history...</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h2 className="page-title">Analysis History</h2>
        <button onClick={fetchHistory} className="btn btn-secondary">
          ↻ Refresh
        </button>
      </div>

      {error && (
        <div className="alert alert-warning">
          <p>{error}</p>
        </div>
      )}

      {analyses.length === 0 && !error ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>No Analyses Yet</h3>
          <p>Upload a resume to get started. Your analyses will appear here.</p>
          <a href="/" className="btn btn-primary">Upload Resume</a>
        </div>
      ) : (
        <div className="history-grid">
          {analyses.map((analysis) => (
            <div key={analysis.id} className="history-card">
              <div className="history-card-header">
                <div className="history-file-info">
                  <span className="history-file-icon">📄</span>
                  <div>
                    <h4 className="history-filename">{analysis.filename}</h4>
                    <span className="history-date">{formatDate(analysis.created_at)}</span>
                  </div>
                </div>
                <div
                  className="history-score-badge"
                  style={{ backgroundColor: getScoreColor(analysis.ats_score) }}
                >
                  {analysis.ats_score}
                </div>
              </div>

              <p className="history-summary">{analysis.summary}</p>

              <div className="history-meta">
                <span className="history-skills-count">
                  {analysis.skills_count} skills detected
                </span>
              </div>

              <div className="history-actions">
                <button
                  onClick={() => handleView(analysis.id)}
                  className="btn btn-primary btn-sm"
                >
                  View Details
                </button>
                <button
                  onClick={() => handleDelete(analysis.id)}
                  className="btn btn-danger btn-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
