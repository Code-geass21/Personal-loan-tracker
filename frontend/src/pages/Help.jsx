import React, { useState } from 'react';

function Help() {
  const [activeTab, setActiveTab] = useState('user');

  // --- Smooth Scroll Function ---
  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const yOffset = -25;
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  };

  // --- Inline Styles (Theme Aware) ---
  const containerStyle = { maxWidth: 1100, margin: '0 auto', padding: '30px', paddingBottom: '120px' };

  const tabContainerStyle = {
    display: 'flex', gap: '15px', marginBottom: '30px',
    borderBottom: '3px solid var(--border-color)', paddingBottom: '15px'
  };

  const getTabStyle = (tabName) => ({
    padding: '14px 28px', fontSize: '17px', fontWeight: '800', cursor: 'pointer',
    background: activeTab === tabName ? 'var(--primary-color)' : 'transparent',
    color: activeTab === tabName ? '#ffffff' : 'var(--text-secondary)',
    border: 'none', borderRadius: '8px', transition: 'all 0.2s', letterSpacing: '0.5px'
  });

  const tocCardStyle = {
    background: 'var(--bg-secondary)', borderRadius: 10, padding: 30, marginBottom: 40,
    border: '1px solid var(--border-color)', borderTop: '5px solid var(--primary-color)',
    boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
  };

  const tocItemStyle = {
    color: 'var(--primary-color)', cursor: 'pointer', fontWeight: '600',
    fontSize: '15.5px', display: 'inline-block', textDecoration: 'none',
    padding: '6px 0', transition: 'color 0.2s'
  };

  const cardStyle = {
    background: 'var(--bg-secondary)', borderRadius: 14, padding: 40, marginBottom: 35,
    border: '1px solid var(--border-color)', boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
  };

  const h2Style = {
    fontSize: 26, fontWeight: 800, marginBottom: 20, color: 'var(--text-primary)',
    borderBottom: '3px solid var(--border-color)', paddingBottom: '12px'
  };

  const h3Style = { fontSize: 20, fontWeight: 800, marginTop: 35, marginBottom: 15, color: 'var(--text-primary)' };

  const pStyle = { fontSize: 16, color: 'var(--text-secondary)', lineHeight: 1.8, marginBottom: 18, textAlign: 'justify' };
  const ulStyle = { ...pStyle, paddingLeft: 28, margin: '15px 0 25px 0' };
  const liStyle = { marginBottom: '10px' };

  const codeStyle = {
    fontFamily: 'monospace', background: 'var(--bg-primary)', padding: '3px 8px',
    borderRadius: '5px', border: '1px solid var(--border-color)', fontSize: '14px', color: '#e83e8c'
  };

  const preBlockStyle = {
    fontFamily: 'monospace', background: 'var(--bg-primary)', padding: '20px',
    borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '14px',
    overflowX: 'auto', color: 'var(--text-secondary)', marginBottom: '20px', lineHeight: 1.6
  };

  const highlightStyle = { fontWeight: '800', color: 'var(--text-primary)' };

  return (
    <div style={containerStyle}>
      <h1 style={{ fontSize: 42, fontWeight: 900, marginBottom: 10, color: 'var(--text-primary)', letterSpacing: '-1px' }}>The Comprehensive Master Manual</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 40, fontSize: 18, lineHeight: 1.6 }}>
        The exhaustive, unabridged reference guide detailing every mathematical calculation, strict ledger rule, database constraint, and infrastructure architecture within the Personal Loan Tracker.
      </p>

      {/* --- TAB SELECTOR --- */}
      <div style={tabContainerStyle}>
        <button style={getTabStyle('user')} onClick={() => setActiveTab('user')}>📖 The Big Book (Complete User Manual)</button>
        <button style={getTabStyle('dev')} onClick={() => setActiveTab('dev')}>⚙️ The Under-the-Hood Architecture</button>
      </div>

      {/* ========================================== */}
      {/* USER GUIDE TAB (THE BIG BOOK)              */}
      {/* ========================================== */}
      {activeTab === 'user' && (
        <div className="fade-in">

          <div style={tocCardStyle}>
            <h2 style={{ fontSize: 20, fontWeight: 900, marginBottom: 20, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '1px' }}>
              📚 Master Index
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px' }}>
              <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('user-intro')}>1. Core Concepts & The Math Engine</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('user-ui')}>2. Interface & Global Navigation</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('user-dashboard')}>3. Dashboard Mechanics & Data Aggregation</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('user-people')}>4. The Borrower Database (People)</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('user-loans')}>5. Exhaustive Loan Lifecycle Management</span></li>
              </ul>
              <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('user-payments')}>6. Strict Ledger Payments & Penalty Logic</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('user-alerts')}>7. Asynchronous Notification & Alert System</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('user-targets')}>8. Time Travel & Financial Target Setting</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('user-attachments')}>9. Secure Document Vault & Attachments</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('user-backups')}>10. Data Sovereignty: Backups & Restore</span></li>
              </ul>
            </div>
          </div>

          <div id="user-intro" style={cardStyle}>
            <h2 style={h2Style}>1. Core Concepts & The Math Engine</h2>
            <p style={pStyle}>
              The Personal Loan Tracker is not a simple spreadsheet; it is a rigid, mathematically sound financial CRM (Customer Relationship Manager). Before utilizing the software to manage real-world capital, operators must thoroughly understand the four foundational pillars that govern the backend math engine. The application relies on strict adherence to these definitions to ensure that financial histories remain perfectly balanced over years of data entry.
            </p>
            <ul style={ulStyle}>
              <li style={liStyle}><span style={highlightStyle}>Principal (P):</span> The absolute initial capital disbursed to the borrower. This number forms the baseline of all subsequent calculations. It must represent the exact amount of cash handed over, prior to any fees or advanced interest deductions.</li>
              <li style={liStyle}><span style={highlightStyle}>Interest Rate (R):</span> The cost of borrowing, strictly represented as an Annual Percentage Rate (APR). The backend engine automatically divides this annual rate by 12 to calculate the accurate monthly burden when generating EMI schedules.</li>
              <li style={liStyle}><span style={highlightStyle}>Duration (N):</span> The lifespan of the contract, strictly measured in sequential 30-day blocks (months). A one-year loan must be entered as 12.</li>
              <li style={liStyle}><span style={highlightStyle}>Equated Monthly Installment (EMI):</span> The core mathematical output of the system. The application uses the standard amortized loan formula: <code>EMI = [P x R x (1+R)^N] / [(1+R)^N - 1]</code>. This determines the exact, non-negotiable amount the borrower is expected to deliver every 30 days to systematically reduce their principal and interest to precisely zero by the end of the duration.</li>
            </ul>
          </div>

          <div id="user-ui" style={cardStyle}>
            <h2 style={h2Style}>2. Interface & Global Navigation</h2>
            <p style={pStyle}>
              The application utilizes a persistent left-hand sidebar to ensure global navigation is always accessible regardless of the user's current depth within a specific loan or borrower profile. This menu acts as the primary routing mechanism for the React frontend, allowing seamless, single-page transitions without requiring full browser reloads.
            </p>
            <p style={pStyle}>
              Furthermore, the sidebar houses the <strong>System Alert Badge</strong>. This red numerical indicator is tied directly to the background Python worker. When the badge appears, it indicates that a temporal event has occurred—such as a borrower crossing a payment deadline—requiring immediate manual intervention. Finally, at the very base of the navigation panel, users will find the <strong>Theme Toggle</strong>. This button seamlessly alters the CSS variables across the entire application, swapping the interface from a high-contrast Light Mode to a low-luminosity Dark Mode, which drastically reduces eye strain during late-night auditing sessions. The application inherently remembers this preference across sessions.
            </p>
          </div>

          <div id="user-dashboard" style={cardStyle}>
            <h2 style={h2Style}>3. Dashboard Mechanics & Data Aggregation</h2>
            <p style={pStyle}>
              The Dashboard serves as the central intelligence hub of the application. It does not simply list data; it aggressively queries the PostgreSQL database, compiling millions of potential data points into three highly critical financial metrics designed to give you an instantaneous snapshot of your total lending portfolio.
            </p>
            <h3 style={h3Style}>The Aggregation Metrics</h3>
            <ul style={ulStyle}>
              <li style={liStyle}><span style={highlightStyle}>Active Loans:</span> This is a live count of all database entries in the 'Loans' table where the <code>remaining_balance</code> column is strictly greater than zero. Closed loans, or loans that have been pre-closed via early payments, are instantly filtered out of this metric.</li>
              <li style={liStyle}><span style={highlightStyle}>Total Outstanding Balance:</span> The most critical number on the board. The system loops through every single active loan and sums their remaining balances. This represents your total illiquid net worth currently held by external borrowers. If every borrower paid you back exactly what they owed right at this second, this is the amount of cash you would possess.</li>
              <li style={liStyle}><span style={highlightStyle}>Collected This Month:</span> A temporally-bound metric. The system calculates the sum of all payments logged in the database where the timestamp falls specifically between the 1st and the final day of the currently selected month.</li>
            </ul>
          </div>

          <div id="user-people" style={cardStyle}>
            <h2 style={h2Style}>4. The Borrower Database (People)</h2>
            <p style={pStyle}>
              A fundamental rule of this application's database architecture is that a "Loan" cannot exist in a vacuum; it must be permanently bound to a "Person" via a Foreign Key relationship. This ensures that even if a borrower takes out five different loans over a ten-year period, all of their financial history is tethered to a single, centralized profile.
            </p>
            <h3 style={h3Style}>Profile Creation & Immutability</h3>
            <p style={pStyle}>
              To initiate a new lending relationship, navigate to the <strong>People</strong> tab and execute the "Add Person" command. You are required to input their Full Name, Phone Number, Email, and physical Address. Accuracy here is paramount. If you enter two individuals with the name "John Smith," the system will treat them as entirely separate entities.
            </p>
            <p style={pStyle}>
              If a borrower's real-world circumstances change (e.g., they acquire a new phone number or move to a new house), you do not need to delete them. You simply open their profile and execute the <strong>Edit</strong> command. Because the database links loans to the user's invisible ID number rather than their text name, updating their contact information will instantly and safely cascade across every single active and historical loan attached to them, preserving data integrity.
            </p>
          </div>

          <div id="user-loans" style={cardStyle}>
            <h2 style={h2Style}>5. Exhaustive Loan Lifecycle Management</h2>
            <p style={pStyle}>
              The Loan module is where the core financial contracts are generated, monitored, and eventually retired. The lifecycle of a loan is rigidly structured to prevent accounting errors and ensure that neither the lender nor the borrower is subjected to miscalculated interest.
            </p>
            <h3 style={h3Style}>Initiation Phase (Creating the Contract)</h3>
            <p style={pStyle}>
              Upon clicking "New Loan," the user is prompted to select a pre-existing borrower. You then input the Principal, Rate, and Duration. At the exact moment you click submit, the FastAPI backend intercepts the data, runs the amortization algorithm, calculates the precise EMI, and commits the contract to the database. The loan is immediately flagged with an <code>ACTIVE</code> status. The system also calculates the 'Total Payable' amount, which represents the Principal plus the lifetime accumulation of interest.
            </p>
            <h3 style={h3Style}>The Mechanics of Pre-Closure</h3>
            <p style={pStyle}>
              Often, borrowers experience a windfall of cash and wish to terminate the debt prematurely. This is known as a Pre-Closure. The system handles this gracefully without requiring complex manual overrides. To pre-close a loan, simply view the exact numerical value listed under the <strong>Remaining Balance</strong> metric on the loan's detail page. You then log a standard payment for that exact, specific amount. The backend engine will instantly detect that the remaining balance has been reduced to absolute zero. It will autonomously strip the <code>ACTIVE</code> flag, assign a <code>CLOSED</code> flag, and permanently disable all future automated EMI alerts for that specific contract.
            </p>
          </div>

          <div id="user-payments" style={cardStyle}>
            <h2 style={h2Style}>6. Strict Ledger Payments & Penalty Logic</h2>
            <p style={pStyle}>
              The payment system operates on the principles of a strict, immutable accounting ledger. This design choice guarantees that financial history cannot be accidentally erased or casually modified, providing you with a bulletproof audit trail of every cent that has ever changed hands.
            </p>
            <h3 style={h3Style}>Executing a Payment</h3>
            <p style={pStyle}>
              When cash is physically handed to you, or a bank transfer clears your account, it must be recorded. By navigating to the specific loan and utilizing the <strong>Add Payment</strong> interface, you input the exact amount received. Because this ledger is strict, payments cannot be casually deleted via the UI once submitted—this prevents accidental data loss that could corrupt the remaining balance. Therefore, it is imperative to double-check the typed amount before committing the transaction. Once committed, the amount is instantly subtracted from the borrower's total debt.
            </p>
            <h3 style={h3Style}>The Penalty & Charge Engine</h3>
            <p style={pStyle}>
              Borrowers occasionally incur penalties due to bounced checks, late payments, or contractual breaches. Instead of creating a messy, separate "Penalty Loan," the system allows you to inject charges directly into the existing contract. By clicking <strong>Add Charge</strong> and providing a description and numerical amount, the backend will forcibly add that exact amount directly to the borrower's Remaining Balance. This dynamically increases their debt ceiling, ensuring that the penalty must be paid off before the loan can ever reach a Closed status.
            </p>
          </div>

          <div id="user-alerts" style={cardStyle}>
            <h2 style={h2Style}>7. Asynchronous Notification & Alert System</h2>
            <p style={pStyle}>
              A CRM is useless if it requires the user to manually check every single profile daily to see who owes money. To solve this, the application features an isolated, asynchronous Python background worker. This "night watchman" container operates completely independently of the web interface.
            </p>
            <p style={pStyle}>
              Every few hours, the worker silently wakes up and scans the entire PostgreSQL database. It compares the current date against the scheduled EMI dates of every active loan. If it detects that a payment is due within the next 3 to 7 days, it generates a yellow "Upcoming" alert, allowing you to proactively remind the borrower. More critically, if the system clock passes a scheduled payment date and no payment has been logged in the ledger, the worker generates a severe red "Overdue" alert. These alerts populate the UI badge and will remain persistently active until you manually click the "Dismiss/Resolve" button, forcing you to acknowledge the delinquency.
            </p>
          </div>

          <div id="user-targets" style={cardStyle}>
            <h2 style={h2Style}>8. Time Travel & Financial Target Setting</h2>
            <p style={pStyle}>
              Beyond simply tracking debt, this software functions as a forward-looking financial planner. The core of this planning revolves around the Target system and the revolutionary Time Travel engine.
            </p>
            <h3 style={h3Style}>Global and Individual Targeting</h3>
            <p style={pStyle}>
              On the Dashboard, you are encouraged to establish a <strong>Global Target</strong>. This is your master revenue goal for the current month (e.g., setting a target of ₹100,000). As you log individual payments across various loans, the master progress bar on the Dashboard visually fills up, giving you real-time feedback on your collection efficiency. You may also assign individual targets to specific loans if you wish to track micro-goals for highly volatile borrowers.
            </p>
            <h3 style={h3Style}>The Temporal Logic Engine (Time Travel)</h3>
            <p style={pStyle}>
              Located prominently at the top of the Dashboard is a Month and Year dropdown selector. By default, this is locked to the present day. However, by altering this selector (for instance, changing it to "August 2023"), you engage the Time Travel engine. The React frontend instantly instructs the FastAPI backend to filter all database queries to that specific historical 30-day window. The Dashboard will completely rewrite itself to show you exactly what your target was in August 2023, exactly how much you collected in August 2023, and completely ignore all modern data. This allows for deep, year-over-year seasonal auditing of your lending business.
            </p>
          </div>

          <div id="user-attachments" style={cardStyle}>
            <h2 style={h2Style}>9. Secure Document Vault (Attachments)</h2>
            <p style={pStyle}>
              Paper contracts degrade, get lost, or are destroyed. The software includes a fully integrated, digitized document vault to permanently tether physical evidence to digital records.
            </p>
            <p style={pStyle}>
              At the bottom of every Loan details page is the Attachments drag-and-drop zone. You are highly encouraged to upload scanned PDF copies of physical loan agreements, JPEG photographs of the borrower's government ID cards, and PNG screenshots of digital bank transfer receipts. When uploaded, these files are stripped of malicious metadata and stored deeply within a secure, localized Docker volume on your host machine's hard drive. They are explicitly never transmitted to external cloud servers like AWS or Google Drive, guaranteeing absolute privacy for highly sensitive financial contracts. Any uploaded document can be retrieved and downloaded back to your local machine with a single click.
            </p>
          </div>

          <div id="user-backups" style={cardStyle}>
            <h2 style={h2Style}>10. Data Sovereignty: Backups & Restore</h2>
            <p style={pStyle}>
              Because this application is 100% locally hosted and intentionally isolated from the cloud to protect your privacy, you are the sole custodian of your data. If your computer's hard drive suffers a catastrophic physical failure, the data dies with it unless you have utilized the Backup systems.
            </p>
            <h3 style={h3Style}>The Backup Paradigm</h3>
            <p style={pStyle}>
              By navigating to the <strong>Backup</strong> tab and executing the generation sequence, the backend triggers a complex script. It commands PostgreSQL to dump every single table, relationship, and ledger entry into a perfectly formatted JSON array. It then locates your Document Vault, compresses all PDF and image attachments, and bundles everything into a single, highly portable `.tar.gz` file. You must physically save this file to an external USB drive or secondary computer.
            </p>
            <h3 style={h3Style}>The Resurrection Protocol (Restore)</h3>
            <p style={pStyle}>
              In the event of total hardware loss, recovery is seamless. You simply acquire a new computer, install Docker, and spin up a fresh, empty version of the Loan Tracker application. By navigating to the <strong>Restore</strong> tab and uploading your saved `.tar.gz` backup file, the system will execute a total overwrite. It will inject the JSON data back into the empty PostgreSQL tables, reconstruct the foreign key relationships, and unpack your PDFs back into the Document Vault. Within seconds, your entire application will be restored to the exact state it was in at the moment the backup was generated.
            </p>
          </div>
        </div>
      )}

      {/* ========================================== */}
      {/* DEVELOPER GUIDE TAB (ARCHITECTURE)         */}
      {/* ========================================== */}
      {activeTab === 'dev' && (
        <div className="fade-in">

          <div style={tocCardStyle}>
            <h2 style={{ fontSize: 20, fontWeight: 900, marginBottom: 20, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '1px' }}>
              ⚙️ Developer Index
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px' }}>
              <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('dev-architecture')}>1. Microservices Architecture (The 5 Containers)</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('dev-network')}>2. The Network Flow (Journey of a Packet)</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('dev-frontend')}>3. Frontend Codebase Breakdown (React + Vite)</span></li>
              </ul>
              <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('dev-backend')}>4. Backend Codebase Breakdown (FastAPI + Python)</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('dev-database')}>5. Database Mechanics & Background Worker</span></li>
                <li style={liStyle}><span style={tocItemStyle} onClick={() => scrollToSection('dev-docker')}>6. DevOps, Bind Mounts & Deployment Traps</span></li>
              </ul>
            </div>
          </div>

          <div id="dev-architecture" style={cardStyle}>
            <h2 style={h2Style}>1. Microservices Architecture (The 5 Containers)</h2>
            <p style={pStyle}>
              Welcome to the codebase. If you are a junior developer or system administrator inheriting this project, you must first understand that this is not a monolithic application. It utilizes a modern <strong>Microservices Architecture</strong> orchestrated entirely by Docker and Docker-Compose. The software is fractured into 5 distinct, highly specialized "Containers." Think of a container as a miniature, isolated computer running a lightweight Linux operating system, designed to execute exactly one task with maximum efficiency.
            </p>
            <ul style={ulStyle}>
              <li style={liStyle}><span style={highlightStyle}>1. Nginx (Reverse Proxy):</span> The absolute front-line defender and traffic director. It stands at the main gate, receives all incoming HTTP requests, and decides whether the request is asking for a visual web page or a backend data calculation, routing it accordingly.</li>
              <li style={liStyle}><span style={highlightStyle}>2. Frontend (React/Vite):</span> The presentation layer. This container serves the compiled HTML, CSS, and JavaScript files that paint the user interface, render the charts, and handle user clicks.</li>
              <li style={liStyle}><span style={highlightStyle}>3. Backend (FastAPI):</span> The mathematical brain. Built on Python 3.11, this container receives raw data, validates it against strict schemas, performs complex financial amortization logic, and dictates commands to the database.</li>
              <li style={liStyle}><span style={highlightStyle}>4. Database (PostgreSQL 16):</span> The permanent filing cabinet. A highly structured, relational SQL database responsible for securely persisting all application data to the host machine's hard drive.</li>
              <li style={liStyle}><span style={highlightStyle}>5. Worker (Python):</span> The asynchronous night-watchman. This container runs a perpetual loop, waking up periodically to scan the database for time-sensitive events (like late payments) without requiring user interaction.</li>
            </ul>
          </div>

          <div id="dev-network" style={cardStyle}>
            <h2 style={h2Style}>2. The Network Flow (Journey of a Packet)</h2>
            <p style={pStyle}>
              To truly grasp how the codebase operates, you must understand how data traverses the internal Docker bridge network. Let us trace the exact chronological journey of a single network packet when a user attempts to add a new loan via the interface.
            </p>
            <ol style={ulStyle}>
              <li style={liStyle}><strong>The Browser:</strong> The user fills out the form in the React UI and clicks submit. The Axios library constructs a JSON payload containing the Principal and Rate. React sends this POST request packet to the destination URL: <code>http://localhost:8090/api/loans</code>.</li>
              <li style={liStyle}><strong>Nginx (Port 8090):</strong> The packet hits the Nginx container listening on the host's port 8090. Nginx analyzes the URL path. Because the path begins with the crucial <code>/api</code> prefix, Nginx recognizes this as a backend data request, strips the prefix, and securely proxies the packet deep into the isolated internal Docker network, hurling it at the FastAPI container on port 8000.</li>
              <li style={liStyle}><strong>FastAPI Backend (Port 8000):</strong> Python receives the packet. Before doing any math, the payload is slammed into a <em>Pydantic Schema</em>. If the user maliciously typed the word "Hello" into the numerical Principal field, Pydantic immediately rejects the packet and returns a 422 Validation Error. If the data is clean, the Python Router calculates the exact EMI utilizing the amortization formula.</li>
              <li style={liStyle}><strong>SQLAlchemy ORM:</strong> The Python application does not write SQL directly. It uses SQLAlchemy (an Object-Relational Mapper) to convert the Python variables into a highly optimized, dialect-specific SQL <code>INSERT</code> query, which is then transmitted to the PostgreSQL container via port 5432.</li>
              <li style={liStyle}><strong>PostgreSQL:</strong> The database receives the query, permanently etches the new loan data onto the host machine's physical storage volume, and transmits a "Success 200 OK" signal back up the entire chain, passing through Python and Nginx until it reaches the React frontend, which instantly renders a green success toast on the user's monitor!</li>
            </ol>
          </div>

          <div id="dev-frontend" style={cardStyle}>
            <h2 style={h2Style}>3. Frontend Codebase Breakdown (React + Vite)</h2>
            <p style={pStyle}>
              The presentation layer is located within the <code>/frontend</code> directory. The application was scaffolded using Vite rather than Create-React-App, resulting in vastly superior hot-module-reloading speeds during development and heavily optimized, minified production builds.
            </p>
            <h3 style={h3Style}>Crucial Directory Structures:</h3>
            <ul style={ulStyle}>
              <li style={liStyle}><strong><code>src/pages/</code>:</strong> This directory contains the massive, full-screen view components. When the user clicks a major tab in the sidebar (like Dashboard, People, or Loans), they are loading an entire file from this directory.</li>
              <li style={liStyle}><strong><code>src/components/</code>:</strong> This directory holds small, modular, and reusable UI chunks. The persistent sidebar (<code>Layout.jsx</code>) and specific modal popups are housed here to prevent code duplication across pages.</li>
              <li style={liStyle}><strong><code>src/utils/api.js</code>:</strong> <em>This is arguably the most important file in the frontend.</em> It houses the centralized Axios instance configuration. It rigidly defines the <code>baseURL</code> as <code>/api</code>. Because this path is relative, React inherently knows to bounce all database requests back to whatever domain is hosting it, ensuring Nginx can intercept and route the traffic. Never hardcode <code>localhost:8000</code> here, as it will instantly break the application on mobile devices or cloud servers (CORS errors).</li>
              <li style={liStyle}><strong><code>src/App.jsx</code>:</strong> The application's master map. It utilizes React-Router-Dom to define the exact URL paths that correspond to specific Page components.</li>
            </ul>
          </div>

          <div id="dev-backend" style={cardStyle}>
            <h2 style={h2Style}>4. Backend Codebase Breakdown (FastAPI + Python)</h2>
            <p style={pStyle}>
              The backend logic engine is housed within the <code>/backend</code> directory. It is built upon FastAPI, a modern web framework that utilizes Python's asynchronous (async/await) capabilities to handle massive amounts of concurrent requests without locking the main execution thread.
            </p>
            <h3 style={h3Style}>The Triad Architecture:</h3>
            <ul style={ulStyle}>
              <li style={liStyle}><strong>Models (<code>models.py</code>):</strong> This file dictates the absolute physical structure of the PostgreSQL database. It uses SQLAlchemy classes to define the exact tables, columns, data types (Integer, String, Float), and the critical Foreign Key relationships connecting Loans to People. If you ever need to add a new tracking metric (like "borrower_credit_score"), you must first declare the column here.</li>
              <li style={liStyle}><strong>Schemas (<code>schemas.py</code>):</strong> While Models handle the database, Schemas handle the network layer. Built with Pydantic, these files act as aggressive security bouncers. They validate the shape and type of all incoming JSON payloads from the frontend. This complete separation of concerns ensures that bad data can never even reach the database logic.</li>
              <li style={liStyle}><strong>Routers (<code>api/</code> Directory):</strong> These are the execution endpoints. Files like <code>api/loans.py</code> or <code>api/people.py</code> contain the actual Python functions that are triggered when a specific URL receives a request. They accept validated data from the Schemas, process the business logic (calculating EMIs or checking late penalties), and interact with the Models to save the results.</li>
            </ul>
          </div>

          <div id="dev-database" style={cardStyle}>
            <h2 style={h2Style}>5. Database Mechanics & Background Worker</h2>

            <h3 style={h3Style}>The Database Initialization Trap (init.sql)</h3>
            <p style={pStyle}>
              A massive trap for junior developers involves the database startup sequence. Inside the codebase is a file named <code>backend/migrations/init.sql</code>. This file contains raw SQL commands to build the initial tables. <strong>Crucial Warning:</strong> The official PostgreSQL Docker image is hard-coded to ONLY execute files in the <code>/docker-entrypoint-initdb.d/</code> directory the absolute very first time the container boots up (i.e., when the persistent volume is completely barren and empty).
            </p>
            <p style={pStyle}>
              If you modify the Python Models to add a new column, and then modify <code>init.sql</code> to match, simply restarting Docker via <code>docker-compose restart</code> will accomplish absolutely nothing. The database will ignore the modified file. To force the schema update in a live environment, you must: (1) Execute the backup script to save the JSON data, (2) spin down the stack and permanently DESTROY the persistent data volume using <code>docker-compose down -v</code>, (3) spin the stack back up to force Postgres to finally read the new <code>init.sql</code>, and (4) run the restore script to inject your data back into the newly formed tables.
            </p>

            <h3 style={h3Style}>The Asynchronous Worker (<code>worker.py</code>)</h3>
            <p style={pStyle}>
              APIs are inherently reactionary; they only execute code when a user actively clicks a button or sends a network packet. To solve the problem of generating "Late Payment" alerts while the user is logged out or asleep, the system utilizes <code>worker.py</code>. This container bypasses FastAPI entirely. It contains an infinite <code>while True:</code> loop hooked into Python's <code>time.sleep()</code> module. It periodically connects directly to the SQLAlchemy database engine, compares the system clock against all active loan EMI schedules, writes any detected infractions to the Alerts table, and then goes back to sleep.
            </p>
          </div>

          <div id="dev-docker" style={cardStyle}>
            <h2 style={h2Style}>6. DevOps, Bind Mounts & Deployment Traps</h2>
            <p style={pStyle}>
              If you are tasked with migrating this codebase from a local development laptop to a live, internet-facing production server (like AWS or DigitalOcean), you must strictly adhere to the following DevOps rules, or the application will immediately crash upon deployment.
            </p>

            <h3 style={h3Style}>Trap 1: The `.env` Secrets Omission</h3>
            <p style={pStyle}>
              For absolute security, database passwords, JWT secret keys, and API credentials are stored in a file named <code>.env</code>. The <code>.gitignore</code> file is explicitly programmed to prevent this file from ever being uploaded to GitHub. Therefore, when you clone the repository onto a fresh production server, the code will instantly crash because it lacks credentials. You MUST manually execute <code>cp .env.example .env</code> and inject strong, production-ready passwords before executing the Docker startup commands.
            </p>

            <h3 style={h3Style}>Trap 2: Port Collisions</h3>
            <p style={pStyle}>
              The <code>docker-compose.yml</code> file binds the internal PostgreSQL container to the host machine's port 5432. If your production server is already running an instance of PostgreSQL at the operating system level, Docker will throw a fatal <em>"Bind for 0.0.0.0:5432 failed: port is already allocated"</em> error. You must edit the compose file and shift the external mapping (the left side of the colon) to a free port, such as <code>5433:5432</code>, to resolve the conflict.
            </p>

            <h3 style={h3Style}>Trap 3: Development Bind Mounts vs Production Images</h3>
            <p style={pStyle}>
              In the compose file, you will notice volume definitions mapping local host directories directly into the containers (e.g., <code>- ./backend:/app</code>). This architecture is a double-edged sword. During development, it is incredible; any change you type in your local code editor instantly overwrites the container's code, triggering a live-reload without needing to rebuild the image.
            </p>
            <p style={pStyle}>
              However, <strong>deploying these bind mounts to production is catastrophic.</strong> If the host directory is empty upon initial clone, it will completely overwrite and erase the fully built application residing inside the container's <code>/app</code> folder. Before deploying to production, you MUST comment out all source-code bind mounts within the <code>docker-compose.yml</code> file. This forces the container to execute relying purely on the secure, immutable application code that was baked into the image during the <code>docker build</code> phase. The only volumes that should remain active in production are the persistent <code>postgres_data</code>, <code>uploads</code>, and <code>backups</code> directories.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Help;
