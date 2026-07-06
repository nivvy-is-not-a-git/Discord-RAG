import type { AskResponse } from '../types'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${BASE_URL}/api/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
  if (!res.ok) {
    throw new Error(`API error ${res.status}`)
  }
  return res.json()
}
