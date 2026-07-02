import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { getPersons, createPerson, updatePerson, deletePerson } from '../utils/api'
import { formatDate, relationshipLabel } from '../utils/format'
import { Plus, Search, Edit2, Trash2 } from 'lucide-react'

// <--- NEW: Added entity_type to the default state --->
const EMPTY = {
  entity_type: 'individual',
  full_name: '', nickname: '', phone: '', email: '',
  relationship: 'other', address: '', national_id: '', notes: '',
  dob: '', id_expiry: '', trust_score: 50, kyc_status: 'pending', emergency_contact: ''
}

export default function People() {
  const [persons, setPersons]   = useState([])
  const [search, setSearch]     = useState('')
  const [loading, setLoading]   = useState(true)
  const [modal, setModal]       = useState(false)
  const [editing, setEditing]   = useState(null)
  const [form, setForm]         = useState(EMPTY)
  const [saving, setSaving]     = useState(false)

  const load = () => {
    setLoading(true)
    getPersons().then(r => setPersons(r.data)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const openAdd  = () => { setEditing(null); setForm(EMPTY); setModal(true) }

  const openEdit = (p) => {
    setEditing(p.id)
    setForm({
      entity_type: p.entity_type || 'individual', // <--- Load Entity Type
      full_name: p.full_name, nickname: p.nickname || '',
      phone: p.phone || '', email: p.email || '',
      relationship: p.relationship || 'other', address: p.address || '',
      national_id: p.national_id || '', notes: p.notes || '',
      dob: p.dob || '', id_expiry: p.id_expiry || '',
      trust_score: p.trust_score || 50, kyc_status: p.kyc_status || 'pending',
      emergency_contact: p.emergency_contact || ''
    })
    setModal(true)
  }

  const save = async () => {
    if (!form.full_name.trim()) return toast.error('Name is required')
    setSaving(true)

    const payload = { ...form };

    // <--- NEW: SMART DATA CLEANUP FOR INSTITUTIONS --->
    // If it's a bank, we automatically wipe out the irrelevant human data
    // so your database stays perfectly clean!
    if (payload.entity_type === 'institution') {
      payload.nickname = null;
      payload.dob = null;
      payload.id_expiry = null;
      payload.trust_score = 0;
      payload.kyc_status = 'pending';
      payload.emergency_contact = null;
      payload.national_id = null;
      payload.relationship = 'other';
    } else {
      if (payload.dob === '') payload.dob = null;
      if (payload.id_expiry === '') payload.id_expiry = null;
      if (payload.trust_score === '') payload.trust_score = 0;
    }

    if (payload.email === '') payload.email = null;

    try {
      if (editing) {
        await updatePerson(editing, payload)
        toast.success('Contact updated')
      } else {
        await createPerson(payload)
        toast.success('Contact added')
      }
      setModal(false)
      load()
    } catch (err) {
      console.error("Save failed:", err.response?.data || err.message || err);
      toast.error('Failed to save. Check console for details.')
    } finally {
      setSaving(false)
    }
  }

  const remove = async (p) => {
    if (!confirm(`Remove ${p.full_name}?`)) return
    try {
      await deletePerson(p.id)
      toast.success('Contact removed')
      load()
    } catch {
      toast.error('Failed to remove')
    }
  }

  const filtered = persons.filter(p =>
    p.full_name.toLowerCase().includes(search.toLowerCase()) ||
    (p.nickname || '').toLowerCase().includes(search.toLowerCase()) ||
    (p.phone || '').includes(search)
  )

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">Contacts</div>
          <div className="page-sub">{persons.length} entities</div>
        </div>
        <button className="btn btn-primary" onClick={openAdd}>
          <Plus size={15} /> Add Contact
        </button>
      </div>

      <div style={{ position: 'relative', marginBottom: 20 }}>
        <Search size={15} style={{ position: 'absolute', left: 12, top: 10, color: 'var(--text-tertiary)' }} />
        <input
          className="input"
          style={{ paddingLeft: 36 }}
          placeholder="Search by name or phone..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="spinner-wrap"><div className="spinner" /></div>
      ) : filtered.length === 0 ? (
        <div className="empty">
          <div className="empty-icon"></div>
          <div className="empty-text">No contacts yet. Add your first one.</div>
        </div>
      ) : (
        <div className="grid-3" style={{ gap: 14 }}>
          {filtered.map(p => (
            <div key={p.id} className="card" style={{ padding: 16 }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 44, height: 44, borderRadius: '50%',
                    background: p.entity_type === 'institution' ? '#f1f5f9' : '#dbeafe',
                    color: p.entity_type === 'institution' ? '#475569' : 'var(--text-link)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 700, fontSize: 18, flexShrink: 0
                  }}>
                    {/* <--- NEW: Bank Icon vs Initial ---> */}
                    {p.entity_type === 'institution' ? '🏦' : p.full_name[0].toUpperCase()}
                  </div>
                  <div>
                    <Link to={`/people/${p.id}`} style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>
                      {p.full_name}
                    </Link>
                    {p.entity_type === 'institution' ? (
                       <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Institution</div>
                    ) : (
                       p.nickname && <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>"{p.nickname}"</div>
                    )}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 4 }}>
                  <button className="btn btn-secondary btn-sm" onClick={() => openEdit(p)}>
                    <Edit2 size={12} />
                  </button>
                  <button className="btn btn-danger btn-sm" onClick={() => remove(p)}>
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>

              <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 4 }}>
                {p.phone && <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}> {p.phone}</div>}
                {p.email && <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>✉ {p.email}</div>}

                {p.entity_type === 'individual' && (
                  <div style={{ marginTop: 4 }}>
                    <span className="badge badge-blue">{relationshipLabel(p.relationship)}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {modal && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModal(false)}>
          <div className="modal" style={{ maxWidth: 600 }}>
            <div className="modal-title">{editing ? 'Edit Contact' : 'Add Contact'}</div>

            {/* <--- NEW: Entity Type Toggle ---> */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 20, background: 'var(--bg-tertiary)', padding: 6, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <div
                style={{ flex: 1, textAlign: 'center', padding: '8px', cursor: 'pointer', borderRadius: 6, background: form.entity_type === 'individual' ? '#2563eb' : 'transparent', color: form.entity_type === 'individual' ? 'white' : 'var(--text-secondary)', fontWeight: form.entity_type === 'individual' ? 600 : 400 }}
                onClick={(e) => { e.preventDefault(); setForm({...form, entity_type: 'individual'}); }}
              >
                👤 Individual
              </div>
              <div
                style={{ flex: 1, textAlign: 'center', padding: '8px', cursor: 'pointer', borderRadius: 6, background: form.entity_type === 'institution' ? '#2563eb' : 'transparent', color: form.entity_type === 'institution' ? 'white' : 'var(--text-secondary)', fontWeight: form.entity_type === 'institution' ? 600 : 400 }}
                onClick={(e) => { e.preventDefault(); setForm({...form, entity_type: 'institution'}); }}
              >
                🏦 Institution / Bank
              </div>
            </div>

            <div className="grid-2" style={{ gap: 12 }}>
              <div className="form-group" style={{ gridColumn: form.entity_type === 'institution' ? 'span 2' : 'span 1' }}>
                <label className="label">{form.entity_type === 'institution' ? 'Institution Name *' : 'Full Name *'}</label>
                <input className="input" value={form.full_name} onChange={e => setForm({...form, full_name: e.target.value})} placeholder={form.entity_type === 'institution' ? 'e.g. HDFC Bank' : 'e.g. John Doe'} />
              </div>

              {/* Only show Nickname for Individuals */}
              {form.entity_type === 'individual' && (
                <div className="form-group">
                  <label className="label">Nickname</label>
                  <input className="input" value={form.nickname} onChange={e => setForm({...form, nickname: e.target.value})} />
                </div>
              )}

              <div className="form-group">
                <label className="label">{form.entity_type === 'institution' ? 'Support Phone' : 'Phone'}</label>
                <input className="input" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} />
              </div>
              <div className="form-group">
                <label className="label">{form.entity_type === 'institution' ? 'Support Email' : 'Email'}</label>
                <input className="input" type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
              </div>

              {/* <--- INDIVIDUAL ONLY FIELDS ---> */}
              {form.entity_type === 'individual' && (
                <>
                  <div className="form-group">
                    <label className="label">Date of Birth</label>
                    <input className="input" type="date" value={form.dob} onChange={e => setForm({...form, dob: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label className="label">ID Expiry Date</label>
                    <input className="input" type="date" value={form.id_expiry} onChange={e => setForm({...form, id_expiry: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label className="label">Relationship</label>
                    <select className="select" value={form.relationship} onChange={e => setForm({...form, relationship: e.target.value})}>
                      <option value="friend">Friend</option>
                      <option value="family">Family</option>
                      <option value="colleague">Colleague</option>
                      <option value="acquaintance">Acquaintance</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="label">KYC Status</label>
                    <select className="select" value={form.kyc_status} onChange={e => setForm({...form, kyc_status: e.target.value})}>
                      <option value="pending">Pending</option>
                      <option value="verified">Verified</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="label">National ID</label>
                    <input className="input" value={form.national_id} onChange={e => setForm({...form, national_id: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label className="label">Trust Score (0-100)</label>
                    <input className="input" type="number" min="0" max="100" value={form.trust_score} onChange={e => setForm({...form, trust_score: parseInt(e.target.value) || 0})} />
                  </div>
                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label className="label">Emergency Contact</label>
                    <input className="input" value={form.emergency_contact} onChange={e => setForm({...form, emergency_contact: e.target.value})} />
                  </div>
                </>
              )}

              {/* <--- SHARED FIELDS ---> */}
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label className="label">{form.entity_type === 'institution' ? 'Branch Address' : 'Address'}</label>
                <textarea className="input" value={form.address} onChange={e => setForm({...form, address: e.target.value})} rows={2} />
              </div>
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label className="label">Notes / Account Details</label>
                <textarea className="input" value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} rows={2} />
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 16 }}>
              <button className="btn btn-secondary" onClick={() => setModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={save} disabled={saving}>
                {saving ? 'Saving...' : editing ? 'Update Contact' : 'Add Contact'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
