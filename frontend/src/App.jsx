import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import People from './pages/People'
import PersonDetail from './pages/PersonDetail'
import Loans from './pages/Loans'
import LoanDetail from './pages/LoanDetail'
import Alerts from './pages/Alerts'
import Restore from './pages/Restore'
import Backup from './pages/Backup'
import Help from './pages/Help';

export default function App() {
  return (
    <>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="people" element={<People />} />
          <Route path="people/:id" element={<PersonDetail />} />
          <Route path="loans" element={<Loans />} />
          <Route path="loans/:id" element={<LoanDetail />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="restore" element={<Restore />} />
          <Route path="backup" element={<Backup />} />
          {/* 👇 Here is the newly added Help Route 👇 */}
          <Route path="help" element={<Help />} />
        </Route>
        {/* Fallback route to catch 404s */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}
