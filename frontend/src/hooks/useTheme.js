import { useState, useEffect } from 'react'

export function useTheme() {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light')

  useEffect(() => {
    // 1. First, apply whatever we have locally so there's no visual flash
    document.documentElement.setAttribute('data-theme', theme)

    // 2. Then, ask the Database if it has a better answer
    fetch('/api/settings/')
      .then(r => r.json())
      .then(data => {
        if (data.theme) {
          setTheme(data.theme)
          document.documentElement.setAttribute('data-theme', data.theme)
          localStorage.setItem('theme', data.theme)
        }
      })
      .catch(() => console.log("DB unreachable, using local theme"))
  }, [])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggle = async () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)

    try {
      await fetch(`/api/settings/theme`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: newTheme })
      })
    } catch {
      console.log("Could not save theme to DB, relying on local storage")
    }
  }

  return [theme, toggle]
}
