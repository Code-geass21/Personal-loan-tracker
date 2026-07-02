import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { getAlerts, dismissAlert, dismissAllAlerts } from '../utils/api'
import { formatDate, formatRelative } from '../utils/format'
import { Bell, BellOff, CheckCheck } from 'lucide-react'

export default function Alerts() {
  const [alerts, setAlerts]   = useState([])
  const [loading, setLoading] = useState(true)
  const [showDismissed, setShowDismissed] = useState(false)

  const load = () => {
    setLoading(true)
    getAlerts()
      .then(r => setAlerts(r.data))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const dismiss = async (id) => {
    try {
      await dismissAlert(id)
      toast.success('Alert dismissed')
      load()
    } catch { toast.error('Failed to dismiss') }
  }

  const dismissAll = async () => {
    if (!confirm('Dismiss all alerts?')) return
    try {
      await dismissAllAlerts()
      toast.success('All alerts dismissed')
      load()
    } catch { toast.error('Failed to dismiss all') }
  }

  const filtered = alerts.filter(a => showDismissed ? a.is_dismissed : !a.is_dismissed)
  const activeCount = alerts.filter(a => !a.is_dismissed).length

  const alertStyle = (type) => {
    switch (type) {
      case 'overdue':          return { bg: 'var(--alert-red-bg)', border: 'var(--alert-red-border)', icon: '🔴', label: 'Overdue' }
      case 'due_soon':         return { bg: 'var(--alert-yellow-bg)', border: 'var(--alert-yellow-border)', icon: '🟡', label: 'Due Soon' }
      case 'partial_reminder': return { bg: 'var(--alert-blue-bg)', border: 'var(--alert-blue-border)', icon: '🔵', label: 'Partial Reminder' }
      default:                 return { bg: '#f8fafc', border: '#e2e8f0', icon: '⚪', label: type }
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">Alerts</div>
          <div className="page-sub">{activeCount} active alerts</div>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary"
            onClick={() => setShowDismissed(!showDismissed)}>
            {showDismissed ? <Bell size={14} /> : <BellOff size={14} />}
            {showDismissed ? 'Show Active' : 'Show Dismissed'}
          </button>
          {activeCount > 0 && (
            <button className="btn btn-secondary" onClick={dismissAll}>
              <CheckCheck size={14} /> Dismiss All
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="spinner-wrap"><div className="spinner" /></div>
      ) : filtered.length === 0 ? (
        <div className="empty">
          <div className="empty-icon">{showDismissed ? '📭' : '✅'}</div>
          <div className="empty-text">
            {showDismissed ? 'No dismissed alerts' : 'No active alerts — all clear!'}
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {filtered.map(alert => {
            const style = alertStyle(alert.alert_type)
            return (
              <div key={alert.id} style={{
                background: style.bg, border: `1px solid ${style.border}`,
                borderRadius: 12, padding: '14px 16px',
                display: 'flex', alignItems: 'flex-start', gap: 14,
                opacity: alert.is_dismissed ? 0.6 : 1
              }}>
                <div style={{ fontSize: 22, flexShrink: 0 }}>{style.icon}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <span style={{ fontWeight: 600, fontSize: 13 }}>{style.label}</span>
                    <span style={{ fontSize: 11, color: '#64748b' }}>· {formatDate(alert.trigger_date)}</span>
                    {alert.is_dismissed && (
                      <span className="badge badge-gray">Dismissed</span>
                    )}
                  </div>
                  <div style={{ fontSize: 14, color: 'var(--text-primary)', marginBottom: 6 }}>{alert.message}</div>
                  <Link to={`/loans/${alert.loan_id}`}
                    style={{ fontSize: 12, color: '#2563eb' }}>
                    View loan →
                  </Link>
                </div>
                {!alert.is_dismissed && (
                  <button className="btn btn-secondary btn-sm" onClick={() => dismiss(alert.id)}
                    title="Dismiss">
                    <CheckCheck size={13} />
                  </button>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
