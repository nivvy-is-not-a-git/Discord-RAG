import type { ChatMessage } from '../types'

function ThinkingDots() {
  return (
    <span className="inline-flex gap-1">
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-discord-muted [animation-delay:-0.3s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-discord-muted [animation-delay:-0.15s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-discord-muted" />
    </span>
  )
}

export default function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%] rounded-2xl rounded-br-sm bg-discord-blurple px-4 py-2.5 text-white">
          {message.question}
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[75%] rounded-2xl rounded-bl-sm bg-discord-sidebar px-4 py-2.5 text-discord-text">
        {message.status === 'loading' && <ThinkingDots />}

        {message.status === 'error' && (
          <p className="text-discord-red">
            Something went wrong reaching the bot. Is the API server running?
          </p>
        )}

        {message.status === 'done' && message.results.length === 0 && (
          <p className="text-discord-muted">I couldn't find anything relevant.</p>
        )}

        {message.status === 'done' && message.results.length > 0 && (
          <div className="flex flex-col gap-3">
            {message.results.map((result, i) => (
              <div
                key={i}
                className={
                  i > 0 ? 'border-t border-discord-darkest pt-3' : undefined
                }
              >
                <p className="whitespace-pre-wrap">{result.text}</p>
                {result.link && (
                  <a
                    href={result.link}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-1 inline-block text-discord-blurple hover:underline"
                  >
                    🔗 Jump to message
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
