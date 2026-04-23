import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import StationInspector from './pages/StationInspector';
import AlertSystem from './pages/AlertSystem';
import RemediationEngine from './pages/RemediationEngine';
import Analytics from './pages/Analytics';
import Reports from './pages/Reports';

function App() {
  return (
    <Router>
      <div className="flex bg-slate-50 min-h-screen">
        <Sidebar />
        <div className="flex-1 ml-64">
          <Routes>
            {/* Redirect the base URL to the Overview page */}
            <Route path="/" element={<Navigate to="/overview" replace />} />
            
            {/* Our active pages */}
            <Route path="/overview" element={<Overview />} />
            <Route path="/inspector" element={<StationInspector />} />
            <Route path="/alerts" element={<AlertSystem />} />
            <Route path="/remediation" element={<RemediationEngine />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;