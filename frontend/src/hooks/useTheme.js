import { useState, useEffect } from 'react'

export function useTheme() {
  const [theme, setTheme] = useState('light')

  // Load theme from DB on mount
  useEffect(() => {
    fetch('/api/settings/')
      .then(r => r.json())
      .then(data => {
        const t = data.theme || 'light'
        setTheme(t)
        document.documentElement.setAttribute('data-theme', t)
        localStorage.setItem('theme', t)
      })
      .catch(() => {
        // Fallback to localStorage if API fails
        const t = localStorage.getItem('theme') || 'light'
        setTheme(t)
        document.documentElement.setAttribute('data-theme', t)
      })
  }, [])

  // Apply theme change
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggle = async () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    // Save to DB
    try {
      await fetch(`/api/settings/theme`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: newTheme })
      })
    } catch {
      // Silent fail — localStorage still saves it
    }
  }

  return [theme, toggle]
}
