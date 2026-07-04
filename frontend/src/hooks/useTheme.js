import { useState, useEffect } from 'react'

export function useTheme() {
  // THE FIX: Check local storage synchronously FIRST, so we never accidentally
  // overwrite the saved theme with a default 'light' on initial load!
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light'
  })

  // Load theme from DB on mount
  useEffect(() => {
    // Set the initial DOM attribute immediately so there is no visual flash
    document.documentElement.setAttribute('data-theme', theme)

    fetch('/api/settings/')
      .then(r => {
        if (!r.ok) throw new Error('API not available');
        return r.json();
      })
      .then(data => {
        const t = data.theme || theme
        setTheme(t)
        document.documentElement.setAttribute('data-theme', t)
        localStorage.setItem('theme', t)
      })
      .catch(() => {
        // Fallback to localStorage if API fails (or if the DB doesn't exist yet)
        const t = localStorage.getItem('theme') || 'light'
        setTheme(t)
        document.documentElement.setAttribute('data-theme', t)
      })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Apply theme change when user clicks toggle
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
      // Silent fail — localStorage still safely saves it!
    }
  }

  return [theme, toggle]
}
