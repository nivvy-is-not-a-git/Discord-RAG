import { useState } from 'react'
import type { KeyboardEvent } from 'react'

export default function Composer({
  onSubmit,
  disabled,
}: {
  onSubmit: (question: string) => void
  disabled: boolean
}) {
  const [value, setValue] = useState('')

  function submit() {
    const question = value.trim()
    if (!question || disabled) return
    onSubmit(question)
    setValue('')
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="border-t border-discord-darkest bg-discord-bg px-4 py-4 sm:px-8">
      <div className="flex items-end gap-3 rounded-xl bg-discord-darkest px-4 py-3">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
          placeholder="Ask a question about this server's history..."
          className="max-h-32 flex-1 resize-none bg-transparent text-discord-text placeholder-discord-muted outline-none disabled:opacity-50"
        />
        <button
          type="button"
          onClick={submit}
          disabled={disabled || !value.trim()}
          className="shrink-0 rounded-lg bg-discord-blurple px-4 py-2 font-medium text-white transition-colors hover:bg-discord-blurple-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          Ask
        </button>
      </div>
    </div>
  )
}
