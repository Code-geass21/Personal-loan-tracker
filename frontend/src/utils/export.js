export const downloadFile = (url, filename) => {
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

export const exportLoansCSV = () =>
  downloadFile('/api/export/loans/csv', 'loans_export.csv')

export const exportLoanStatement = (loanId) =>
  downloadFile(`/api/export/loans/${loanId}/statement`, `statement_${loanId}.txt`)

export const exportPaymentsCSV = (loanId) =>
  downloadFile(`/api/export/loans/${loanId}/payments/csv`, `payments_${loanId}.csv`)

export const fullBackup = () =>
  downloadFile('/api/export/full-backup', 'loan_tracker_backup.json')

// ── Server-side complete backup ───────────────
export const runFullBackup = async () => {
  const response = await fetch('/api/backup/run', { method: 'POST' })
  if (!response.ok) throw new Error('Backup failed')
  return response.json()
}

export const listBackups = async () => {
  const response = await fetch('/api/backup/list')
  if (!response.ok) throw new Error('Failed to list backups')
  return response.json()
}
