import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
// Notice we added createLoanFee to the imports!
import { getLoans, getPersons, createLoan, deleteLoan, cancelLoan, createLoanFee } from '../utils/api'
import { formatCurrency, formatDate, statusColor, directionColor } from '../utils/format'
import { exportLoansCSV, fullBackup } from '../utils/export'
import { Trash2, XCircle, Plus } from 'lucide-react'

const EMPTY_LOAN = {
  person_id: '',
  institution_type: 'non_institutional',
  direction: 'lent',
  principal: '',
  currency: 'INR',
  interest_rate: '0',
  interest_type: 'simple',
  interest_period: 'monthly',
  tenure_months: '', // <--- ADD THIS LINE
  date_issued: new Date().toISOString().split('T')[0],
  emi_start_date: '',
  due_date: '',
  purpose: '',
  notes: '',
  // --- NEW UI FIELDS FOR FEES ---
  fee_name: 'Appraisal Fee',
  fee_amount: ''
}

export default function Loans() {
  const [loans, setLoans]     = useState([])
  const [persons, setPersons] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal]     = useState(false)
  const [form, setForm]       = useState(EMPTY_LOAN)
  const [saving, setSaving]   = useState(false)
  const [search, setSearch]   = useState('')
  const [searchParams]        = useSearchParams()

  const [filters, setFilters] = useState({
    direction: searchParams.get('direction') || '',
    status:    searchParams.get('status')    || '',
    currency:  ''
  })

  const load = () => {
    setLoading(true)
    const params = {}
    if (filters.direction) params.direction = filters.direction
    if (filters.status)    params.status    = filters.status
    if (filters.currency)  params.currency  = filters.currency
    Promise.all([getLoans(params), getPersons()])
      .then(([l, p]) => { setLoans(l.data); setPersons(p.data) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [filters])

  const save = async () => {
    if (!form.person_id) return toast.error('Select a person')
    if (!form.principal) return toast.error('Enter amount')
    setSaving(true)

    const payload = { ...form };
    payload.principal = parseFloat(payload.principal);
    payload.interest_rate = parseFloat(payload.interest_rate) || 0;
    // <--- ADD THESE TWO LINES --->
    if (payload.tenure_months) payload.tenure_months = parseInt(payload.tenure_months, 10);
    else delete payload.tenure_months;
    if (payload.emi_start_date === '') payload.emi_start_date = null;
    if (payload.due_date === '') payload.due_date = null;
    if (payload.purpose === '') payload.purpose = null;
    if (payload.notes === '') payload.notes = null;

    // Remove UI-only fee fields so the backend doesn't reject the main loan payload
    delete payload.fee_name;
    delete payload.fee_amount;

    try {
      // 1. Create the main loan
      const res = await createLoan(payload)
      const newLoanId = res.data.id;

      // 2. If the user typed in a fee, instantly attach it to the new loan!
      if (form.fee_amount && parseFloat(form.fee_amount) > 0) {
        await createLoanFee({
          loan_id: newLoanId,
          fee_name: form.fee_name || 'Appraisal Fee',
          amount: parseFloat(form.fee_amount),
          status: 'pending' // Upfront fees start as pending
        });
      }

      toast.success('Loan created successfully')
      setModal(false)
      setForm(EMPTY_LOAN)
      load()
    } catch (err) {
      console.error("Loan Save failed:", err.response?.data || err.message || err);
      toast.error('Failed to create loan. Check console.')
    } finally { setSaving(false) }
  }

  const remove = async (loan) => {
    if (!confirm('Delete this loan? This cannot be undone.')) return
    try {
      await deleteLoan(loan.id)
      toast.success('Loan deleted')
      load()
    } catch { toast.error('Failed to delete') }
  }

  const cancel = async (loan) => {
    if (!confirm('Cancel this loan?')) return
    try {
      await cancelLoan(loan.id)
      toast.success('Loan cancelled')
      load()
    } catch { toast.error('Failed to cancel') }
  }

  const filtered = loans.filter(l =>
    (l.person_name || '').toLowerCase().includes(search.toLowerCase()) ||
    (l.purpose     || '').toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">Loans</div>
          <div className="page-sub">{loans.length} total</div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary" onClick={exportLoansCSV} title="Export all loans to CSV">
            Export CSV
          </button>
          <button className="btn btn-secondary" onClick={fullBackup} title="Download full backup">
            Backup
          </button>
          <button className="btn btn-primary" onClick={() => { setForm(EMPTY_LOAN); setModal(true) }}>
            <Plus size={14} style={{ marginRight: 4 }} /> New Loan
          </button>
        </div>
      </div>

      <div className="filter-bar">
        <input className="input" style={{ width: 200 }}
          placeholder="Search person or purpose..."
          value={search} onChange={e => setSearch(e.target.value)} />
        <select className="select" value={filters.direction}
          onChange={e => setFilters({...filters, direction: e.target.value})}>
          <option value="">All Directions</option>
          <option value="lent">↑ Lent</option>
          <option value="borrowed">↓ Borrowed</option>
        </select>
        <select className="select" value={filters.status}
          onChange={e => setFilters({...filters, status: e.target.value})}>
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="partial">Partial</option>
          <option value="overdue">Overdue</option>
          <option value="settled">Settled</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <select className="select" value={filters.currency}
          onChange={e => setFilters({...filters, currency: e.target.value})}>
          <option value="">All Currencies</option>
          <option value="INR">INR ₹</option>
          <option value="EUR">EUR €</option>
          <option value="USD">USD $</option>
        </select>
      </div>

      {loading ? (
        <div className="spinner-wrap"><div className="spinner" /></div>
      ) : filtered.length === 0 ? (
        <div className="empty">
          <div className="empty-text">No loans found.</div>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th style={{ paddingLeft: 20 }}>Person</th>
                  <th>Direction</th>
                  <th>Principal</th>
                  <th>Balance Due</th>
                  <th>Interest</th>
                  <th>Due Date</th>
                  <th>Status</th>
                  <th>Purpose</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(loan => (
                  <tr key={loan.id}>
                    <td style={{ paddingLeft: 20 }}>
                      <Link to={`/loans/${loan.id}`} style={{ fontWeight: 600, color: 'var(--text-link, #3b82f6)' }}>
                        {loan.person_name}
                      </Link>
                      {loan.person_nickname && (
                        <div style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>{loan.person_nickname}</div>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${directionColor(loan.direction)}`}>
                        {loan.direction === 'lent' ? '↑ Lent' : '↓ Borrowed'}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{formatCurrency(loan.principal, loan.currency)}</td>
                    <td style={{ fontWeight: 600 }}>
                      <span style={{ color: parseFloat(loan.balance_due) > 0 ? '#dc2626' : '#16a34a' }}>
                        {formatCurrency(loan.balance_due, loan.currency)}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>
                      {parseFloat(loan.interest_rate) > 0
                        ? `${parseFloat(loan.interest_rate)}% ${loan.interest_type}`
                        : 'None'}
                    </td>
                    <td style={{ color: loan.days_overdue ? '#dc2626' : '#64748b' }}>
                      {formatDate(loan.due_date)}
                      {loan.days_overdue > 0 && (
                        <div style={{ fontSize: 11, color: '#dc2626' }}>{loan.days_overdue}d overdue</div>
                      )}
                    </td>
                    <td><span className={`badge ${statusColor(loan.status)}`}>{loan.status}</span></td>
                    <td style={{ color: 'var(--text-secondary)' }}>{loan.purpose || '—'}</td>
                    <td>
                      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                        {loan.status !== 'cancelled' && loan.status !== 'settled' && (
                          <button className="btn btn-secondary btn-sm"
                            onClick={() => cancel(loan)} title="Cancel loan"
                            style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                            <XCircle size={14} /> Cancel
                          </button>
                        )}
                        <button className="btn btn-danger btn-sm"
                          onClick={() => remove(loan)} title="Delete"
                          style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                          <Trash2 size={14} /> Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {modal && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModal(false)}>
          <div className="modal">
            <div className="modal-title">New Loan</div>
            <div className="form-group">
              <label className="label">Person *</label>
              <select className="select" value={form.person_id}
                onChange={e => setForm({...form, person_id: e.target.value})}>
                <option value="">Select person...</option>
                {persons.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.full_name}{p.nickname ? ` (${p.nickname})` : ''}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid-2" style={{ gap: 12 }}>
              <div className="form-group">
                <label className="label">Direction *</label>
                <select className="select" value={form.direction}
                  onChange={e => setForm({...form, direction: e.target.value})}>
                  <option value="lent">↑ I Lent (they owe me)</option>
                  <option value="borrowed">↓ I Borrowed (I owe them)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="label">Institution Type *</label>
                <select className="select" value={form.institution_type}
                  onChange={e => setForm({...form, institution_type: e.target.value})}>
                  <option value="non_institutional">Non-Institutional (Friend / Informal)</option>
                  <option value="institutional">Institutional (Bank / Formal)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="label">Currency</label>
                <select className="select" value={form.currency}
                  onChange={e => setForm({...form, currency: e.target.value})}>
                  <option value="INR">INR ₹</option>
                  <option value="EUR">EUR €</option>
                  <option value="USD">USD $</option>
                  <option value="GBP">GBP £</option>
                </select>
              </div>
              <div className="form-group">
                <label className="label">Principal Amount *</label>
                <input className="input" type="number" min="0" step="0.01"
                  placeholder="0.00" value={form.principal}
                  onChange={e => setForm({...form, principal: e.target.value})} />
              </div>
              <div className="form-group">
                <label className="label">Interest Rate (%)</label>
                <input className="input" type="number" min="0" step="0.01"
                  placeholder="0 = no interest" value={form.interest_rate}
                  onChange={e => setForm({...form, interest_rate: e.target.value})} />
              </div>
              <div className="form-group">
                <label className="label">Interest Type</label>
                <select className="select" value={form.interest_type}
                  onChange={e => setForm({...form, interest_type: e.target.value})}>
                  <option value="simple">Simple</option>
                  <option value="compound">Compound</option>
                </select>
              </div>
              <div className="form-group">
                <label className="label">Interest Period</label>
                <select className="select" value={form.interest_period}
                  onChange={e => setForm({...form, interest_period: e.target.value})}>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>
              {/* --- NEW TENURE INPUT --- */}
              <div className="form-group">
                <label className="label">Tenure (in Months)</label>
                <input className="input" type="number" min="1" step="1"
                  placeholder="e.g. 12" value={form.tenure_months}
                  onChange={e => setForm({...form, tenure_months: e.target.value})} />
              </div>
              {/* ------------------------ */}
              <div className="form-group">
                <label className="label">Date Issued *</label>
                <input className="input" type="date" value={form.date_issued}
                  onChange={e => setForm({...form, date_issued: e.target.value})} />
              </div>

              <div className="form-group">
                <label className="label">EMI Start Date (optional)</label>
                <input className="input" type="date" value={form.emi_start_date}
                  onChange={e => setForm({...form, emi_start_date: e.target.value})} />
              </div>

              <div className="form-group">
                <label className="label">Due Date (optional)</label>
                <input className="input" type="date" value={form.due_date}
                  onChange={e => setForm({...form, due_date: e.target.value})} />
              </div>

              {/* --- HERE IS THE NEW UI FIELD ADDED TO THE GRID --- */}
              <div className="form-group" style={{ gridColumn: 'span 2', padding: '10px 0', borderTop: '1px solid var(--border-color)' }}>
                <label className="label" style={{ color: '#ea580c' }}>Upfront Charges (Admin/Appraisal)</label>
                <div style={{ display: 'flex', gap: 10 }}>
                  <select className="select" value={form.fee_name} style={{ flex: 1 }}
                    onChange={e => setForm({...form, fee_name: e.target.value})}>
                    <option value="Appraisal Fee">Appraisal Fee</option>
                    <option value="Administrative Fee">Administrative Fee</option>
                    <option value="Legal Fee">Legal Fee</option>
                    <option value="Other Charge">Other Charge</option>
                  </select>
                  <input className="input" type="number" placeholder="Fee Amount (0.00)" style={{ flex: 1 }}
                    value={form.fee_amount} onChange={e => setForm({...form, fee_amount: e.target.value})} />
                </div>
              </div>

            </div>

            <div className="form-group" style={{ marginTop: 12 }}>
              <label className="label">Purpose</label>
              <input className="input" value={form.purpose}
                onChange={e => setForm({...form, purpose: e.target.value})}
                placeholder="e.g. Medical emergency, Business loan..." />
            </div>
            <div className="form-group">
              <label className="label">Notes</label>
              <textarea className="input" value={form.notes} rows={2}
                onChange={e => setForm({...form, notes: e.target.value})} />
            </div>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button className="btn btn-secondary" onClick={() => setModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={save} disabled={saving}>
                {saving ? 'Creating...' : 'Create Loan'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
