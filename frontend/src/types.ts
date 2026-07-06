export interface AskResult {
  text: string
  link: string | null
}

export interface AskResponse {
  results: AskResult[]
}

export type ChatMessage =
  | { id: string; role: 'user'; question: string }
  | { id: string; role: 'assistant'; status: 'loading' }
  | { id: string; role: 'assistant'; status: 'error' }
  | { id: string; role: 'assistant'; status: 'done'; results: AskResult[] }
