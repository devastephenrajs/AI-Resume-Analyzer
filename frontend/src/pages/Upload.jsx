import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_BASE = 'http://localhost:8000/api';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState('');
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const navigate = useNavigate();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // 1. Upload Resume
      const res = await axios.post(`${API_BASE}/upload-resume`, formData);
      const data = res.data;

      let matchData = null;
      // 2. If JD is provided, match JD
      if (jd.trim()) {
        const jdRes = await axios.post(`${API_BASE}/match-jd`, {
          resume_text: data.extracted_text,
          jd_text: jd
        });
        matchData = jdRes.data;
      }

      // Store in local storage to pass to Dashboard
      localStorage.setItem('resumeData', JSON.stringify({
        ...data,
        match: matchData
      }));

      navigate('/dashboard');
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. See console for details.');
    } finally {
      setLoading(false);
    }
  };

  const getFileIcon = (filename) => {
    if (!filename) return '📄';
    const ext = filename.split('.').pop().toLowerCase();
    if (ext === 'pdf') return '📕';
    if (ext === 'docx') return '📘';
    return '📄';
  };

  return (
    <div className="upload-container">
      <div className="upload-hero">
        <h2 className="upload-title">Analyze Your Resume</h2>
        <p className="upload-subtitle">
          Upload your resume for instant AI-powered analysis with ATS scoring, 
          skill detection, and actionable improvements
        </p>
      </div>

      <form onSubmit={handleUpload} className="upload-form">
        {/* File Upload Zone */}
        <div className="form-section">
          <label className="form-label">
            Resume File
            <span className="form-label-hint">PDF, DOCX, or TXT</span>
          </label>
          <label
            className={`file-drop-zone ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(e) => setFile(e.target.files[0])}
              className="file-input-hidden"
              required
            />
            {file ? (
              <div className="file-selected">
                <span className="file-selected-icon">{getFileIcon(file.name)}</span>
                <div className="file-selected-info">
                  <span className="file-selected-name">{file.name}</span>
                  <span className="file-selected-size">
                    {(file.size / 1024).toFixed(1)} KB
                  </span>
                </div>
                <button
                  type="button"
                  className="file-clear-btn"
                  onClick={(e) => { e.preventDefault(); setFile(null); }}
                >
                  ✕
                </button>
              </div>
            ) : (
              <div className="file-drop-content">
                <span className="file-drop-icon">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                </span>
                <span className="file-drop-text">
                  Drag & drop your resume here, or <strong>click to browse</strong>
                </span>
                <span className="file-drop-formats">Supports PDF, DOCX, TXT</span>
              </div>
            )}
          </label>
        </div>

        {/* Job Description */}
        <div className="form-section">
          <label className="form-label">
            Job Description
            <span className="form-label-hint">Optional — for JD matching</span>
          </label>
          <textarea
            rows="5"
            className="form-textarea"
            placeholder="Paste the job description here to see how well your resume matches..."
            value={jd}
            onChange={(e) => setJd(e.target.value)}
          ></textarea>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !file}
          className="btn btn-primary btn-lg upload-submit-btn"
        >
          {loading ? (
            <span className="btn-loading">
              <span className="loading-spinner-small"></span>
              Analyzing...
            </span>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
              Analyze Resume
            </>
          )}
        </button>
      </form>
    </div>
  );
}
