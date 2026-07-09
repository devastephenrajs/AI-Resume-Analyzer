import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import ThemeToggle from './components/ThemeToggle';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import History from './pages/History';
import Compare from './pages/Compare';

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const closeMenu = () => setIsMenuOpen(false);

  return (
    <ThemeProvider>
      <Router>
        <div className="app-root">
          <header className="app-header">
            <div className="header-inner">
              <NavLink to="/" className="app-logo" onClick={closeMenu}>
                <span className="logo-icon">◆</span>
                AI Resume Analyzer
              </NavLink>
              
              <button 
                className={`mobile-menu-btn ${isMenuOpen ? 'open' : ''}`}
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                aria-label="Toggle menu"
              >
                <span></span>
                <span></span>
                <span></span>
              </button>

              <nav className={`app-nav ${isMenuOpen ? 'nav-open' : ''}`}>
                <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'nav-active' : ''}`} onClick={closeMenu}>
                  Upload
                </NavLink>
                <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'nav-active' : ''}`} onClick={closeMenu}>
                  Dashboard
                </NavLink>
                <NavLink to="/history" className={({ isActive }) => `nav-link ${isActive ? 'nav-active' : ''}`} onClick={closeMenu}>
                  History
                </NavLink>
                <NavLink to="/compare" className={({ isActive }) => `nav-link ${isActive ? 'nav-active' : ''}`} onClick={closeMenu}>
                  Compare
                </NavLink>
                <ThemeToggle />
              </nav>
            </div>
          </header>

          <main className="app-main">
            <Routes>
              <Route path="/" element={<Upload />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/history" element={<History />} />
              <Route path="/compare" element={<Compare />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
