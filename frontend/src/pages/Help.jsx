import React, { useState } from 'react';

function Help() {
  const [activeTab, setActiveTab] = useState('user'); // 'user' or 'dev'

  // --- Inline Styles (Theme Aware) ---
  const containerStyle = { maxWidth: 800, margin: '0 auto', padding: '20px' };

  const tabContainerStyle = {
    display: 'flex', gap: '10px', marginBottom: '24px',
    borderBottom: '2px solid var(--border-color)', paddingBottom: '10px'
  };

  const getTabStyle = (tabName) => ({
    padding: '10px 20px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    background: activeTab === tabName ? 'var(--primary-color)' : 'transparent',
    color: activeTab === tabName ? '#ffffff' : 'var(--text-secondary)',
    border: 'none',
    borderRadius: '6px',
    transition: 'all 0.2s'
  });

  const cardStyle = {
    background: 'var(--bg-secondary)',
    borderRadius: 12, padding: 24, marginBottom: 24,
    border: '1px solid var(--border-color)'
  };

  const h2Style = {
    fontSize: 18, fontWeight: 600, marginBottom: 16,
    color: 'var(--text-primary)'
  };

  const pStyle = {
    fontSize: 14, color: 'var(--text-secondary)',
    lineHeight: 1.6, marginBottom: 12
  };

  return (
    <div style={containerStyle}>
      <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8, color: 'var(--text-primary)' }}>Documentation & Guides</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>Select your view below to access the relevant manuals.</p>

      {/* --- TAB SELECTOR --- */}
      <div style={tabContainerStyle}>
        <button style={getTabStyle('user')} onClick={() => setActiveTab('user')}>👤 Non-Developer (User Guide)</button>
        <button style={getTabStyle('dev')} onClick={() => setActiveTab('dev')}>⚙️ Developer (Architecture)</button>
      </div>

      {/* ========================================== */}
      {/* USER GUIDE TAB                */}
      {/* ========================================== */}
      {activeTab === 'user' && (
        <div>
          <div style={cardStyle}>
            <h2 style={h2Style}>1. Getting Started: Adding a Loan</h2>
            <p style={pStyle}>To start tracking, you first need to add a "Person" (the borrower), and then attach a "Loan" to them.</p>
            <ul style={{ ...pStyle, paddingLeft: 20 }}>
              <li><strong>Principal Amount:</strong> The total amount of money borrowed.</li>
              <li><strong>Interest Rate:</strong> The annual percentage rate (e.g., 12%).</li>
              <li><strong>EMI:</strong> The exact amount due every single month to pay off the loan on time.</li>
            </ul>
          </div>

          <div style={cardStyle}>
            <h2 style={h2Style}>2. Logging Monthly Payments</h2>
            <p style={pStyle}>When a borrower pays you, you must log it so the app can track their remaining balance.</p>
            <ul style={{ ...pStyle, paddingLeft: 20 }}>
              <li>Go to the <strong>Loans</strong> tab and click on a specific loan.</li>
              <li>Scroll down to the <strong>Payment History</strong> section and click "Add Payment."</li>
            </ul>
          </div>

          <div style={cardStyle}>
            <h2 style={h2Style}>3. Setting Targets & Goals</h2>
            <p style={pStyle}>Track your expected monthly collections using the Targets system.</p>
            <ul style={{ ...pStyle, paddingLeft: 20 }}>
              <li><strong>Global Target:</strong> A master goal for all loans combined (Set on the Dashboard).</li>
              <li><strong>Time Travel:</strong> Use the 📅 Dropdown on the Dashboard to look back in time and view historical progress!</li>
            </ul>
          </div>
        </div>
      )}

      {/* ========================================== */}
      {/* DEVELOPER GUIDE TAB             */}
      {/* ========================================== */}
      {activeTab === 'dev' && (
        <div>
          <div style={cardStyle}>
            <h2 style={h2Style}>1. Architecture Stack</h2>
            <p style={pStyle}>This application is 100% containerized and orchestrated via Docker/Portainer.</p>
            <ul style={{ ...pStyle, paddingLeft: 20 }}>
              <li><strong>Frontend:</strong> React + Vite (Routed internally on port 80)</li>
              <li><strong>Backend:</strong> Python + FastAPI (Exposed locally on 8000)</li>
              <li><strong>Database:</strong> PostgreSQL 16 (Exposed locally on 5432)</li>
              <li><strong>Proxy:</strong> Nginx (Handles all public traffic on port 8090)</li>
            </ul>
          </div>

          <div style={cardStyle}>
            <h2 style={h2Style}>2. Critical Deployment Traps</h2>
            <p style={pStyle}>If moving this codebase to a new server, you must avoid the following infrastructure traps:</p>
            <ul style={{ ...pStyle, paddingLeft: 20 }}>
              <li><strong>The Secrets Trap:</strong> You must manually create the <code>.env</code> file. Git ignores it for security.</li>
              <li><strong>The Bind Mount Trap:</strong> Disable local directory mounts (e.g., <code>- ./backend:/app</code>) in <code>docker-compose.yml</code> during production so the container does not crash looking for local dependencies.</li>
              <li><strong>The Proxy Trap:</strong> Never hardcode <code>localhost:8000</code> in the React API calls. Always use relative paths like <code>/api</code> so Nginx handles the routing.</li>
            </ul>
          </div>

          <div style={cardStyle}>
            <h2 style={h2Style}>3. Database Schema & Backups</h2>
            <p style={pStyle}>Postgres only reads <code>init.sql</code> on the very first boot. To force a schema update on a live database without data loss, use the custom backup cycle:</p>
            <ol style={{ ...pStyle, paddingLeft: 20 }}>
              <li>Run <code>bash scripts/backup.sh</code> to export JSON data.</li>
              <li>Run <code>docker-compose down -v</code> to destroy the old volume.</li>
              <li>Reboot containers to trigger the new <code>init.sql</code>.</li>
              <li>Run <code>python app/restore.py</code> inside the backend container to inject the JSON data.</li>
            </ol>
          </div>
        </div>
      )}

    </div>
  );
}

export default Help;
