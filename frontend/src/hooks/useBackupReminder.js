import { useState, useEffect } from 'react'

export function useBackupReminder() {
  const [showReminder, setShowReminder] = useState(false)
  const [lastBackup, setLastBackup] = useState(null)

  useEffect(() => {
    const stored = localStorage.getItem('lastBackupTime')
    if (!stored) {
      setShowReminder(true)
      setLastBackup(null)
      return
    }
    const last = new Date(stored)
    setLastBackup(last)
    const hoursSince = (Date.now() - last.getTime()) / (1000 * 60 * 60)
    if (hoursSince >= 24) setShowReminder(true)
  }, [])

  const markBackupDone = () => {
    const now = new Date().toISOString()
    localStorage.setItem('lastBackupTime', now)
    setLastBackup(new Date())
    setShowReminder(false)
  }

  const dismiss = () => setShowReminder(false)

  return { showReminder, lastBackup, markBackupDone, dismiss }
}
