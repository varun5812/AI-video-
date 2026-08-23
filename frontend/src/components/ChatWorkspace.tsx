import React, { useState, useRef, useEffect } from 'react'
import { marked } from 'marked'
import { 
  Paperclip, 
  Mic, 
  Send, 
  Lightbulb, 
  BarChart4, 
  PenTool, 
  Code, 
  ThumbsUp, 
  ThumbsDown, 
  Copy, 
  RotateCw,
  Sparkles,
  Bot,
  Check
} from 'lucide-react'
import ModeSwitcher from './ModeSwitcher'

// Configure marked renderer
marked.setOptions({ breaks: true, gfm: true })

interface Message {
  role: 'user' | 'assistant'
  content: string  // always plain text / markdown from API
  timestamp: string
}

interface ChatWorkspaceProps {
  activeTab: 'chat' | 'video'
  setActiveTab: (tab: 'chat' | 'video') => void
  selectedModel: string
  activeModelDisplayName: string
}

export default function ChatWorkspace({ activeTab, setActiveTab, selectedModel, activeModelDisplayName }: ChatWorkspaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputVal, setInputVal] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)

  const suggestions = [
    { id: 'explain', title: 'Explain something', desc: 'Break down complex topics into simple terms', icon: Lightbulb, prompt: 'Explain the theory of general relativity in simple terms with an analogy.' },
    { id: 'analyze', title: 'Analyze data', desc: 'Identify patterns, structure data, or summarize statistics', icon: BarChart4, prompt: 'Here is some mock data: [Sales: $10k, Growth: 12%]. Analyze this and list 3 key takeaways.' },
    { id: 'write', title: 'Write something', desc: 'Draft articles, emails, reports or outline stories', icon: PenTool, prompt: 'Write a professional email template to follow up on a project proposal.' },
    { id: 'code', title: 'Generate code', desc: 'Build logic, refactor scripts, or debug syntax errors', icon: Code, prompt: 'Write a clean Python function to parse a URL and return its query parameters.' },
  ]

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Render markdown -> safe HTML string with big-text sanitization
  const renderMarkdown = (text: string): string => {
    try {
      // Remove <think>...</think> reasoning blocks from Qwen/DeepSeek models
      let cleaned = text.replace(/<think>[\s\S]*?<\/think>/gi, '').trim()
      // Demote top-level H1 headers (# Heading) to H3 to prevent big starting text
      cleaned = cleaned.replace(/^#\s+(.+)$/gm, '### $1')
      return marked.parse(cleaned) as string
    } catch {
      return text.replace(/\n/g, '<br/>')
    }
  }

  const handleSend = async (text: string) => {
    if (!text.trim() || isLoading) return

    const userMsg: Message = {
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    setMessages(prev => [...prev, userMsg])
    setInputVal('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text, model: selectedModel })
      })

      if (response.ok) {
        const data = await response.json()
        const botMsg: Message = {
          role: 'assistant',
          content: data.answer,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
        setMessages(prev => [...prev, botMsg])
        setIsLoading(false)
      } else {
        const errData = await response.json().catch(() => ({ detail: 'Server error.' }))
        throw new Error(errData.detail || 'API returned an error.')
      }
    } catch (err: any) {
      // Graceful fallback — show the error reason as bot reply
      const errMsg = err?.message || 'Something went wrong.'
      const botMsg: Message = {
        role: 'assistant',
        content: `⚠️ **Could not connect to AI backend.**\n\n${errMsg}\n\nMake sure the server is running at \`http://localhost:8000\` and your API keys are valid in \`.env\`.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setMessages(prev => [...prev, botMsg])
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text: string, idx: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIdx(idx)
    setTimeout(() => setCopiedIdx(null), 2000)
  }

  return (
    <div className="flex-1 flex flex-col justify-between relative grid-bg min-h-[calc(100vh-64px)] pb-12 overflow-y-auto">
      {/* Background Gradients */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-[10%] left-[20%] w-[350px] h-[350px] ambient-glow-1 rounded-full filter blur-[80px]" />
        <div className="absolute bottom-[20%] right-[15%] w-[400px] h-[400px] ambient-glow-2 rounded-full filter blur-[90px]" />
      </div>

      {/* Main Container */}
      <div className="flex-1 max-w-[850px] mx-auto w-full px-6 pt-8 flex flex-col justify-between z-10">
        
        {/* Empty State */}
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col justify-center items-center py-12">
            {/* Logo/Icon */}
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500 via-indigo-600 to-purple-600 shadow-[0_8px_32px_rgba(99,102,241,0.25)] flex items-center justify-center text-white mb-6">
              <Sparkles className="w-8 h-8 text-white animate-pulse" />
            </div>

            <h2 className="text-3xl font-extrabold text-white tracking-tight text-center mb-2">
              What can I help you with?
            </h2>
            <p className="text-slate-400 text-sm max-w-lg text-center mb-8 leading-relaxed">
              Ask questions, analyze information, write content, or solve problems with AI.
            </p>

            {/* Suggestions Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
              {suggestions.map((card) => {
                const Icon = card.icon
                return (
                  <button
                    key={card.id}
                    onClick={() => handleSend(card.prompt)}
                    className="glass-card glass-card-hover p-4 rounded-2xl text-left cursor-pointer flex gap-4 items-start"
                  >
                    <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-xl flex-shrink-0">
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-bold text-sm text-slate-100 mb-1">{card.title}</h4>
                      <p className="text-xs text-slate-400 leading-normal">{card.desc}</p>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        ) : (
          /* Active Conversational Log */
          <div className="flex-1 flex flex-col gap-6 py-6 overflow-y-auto max-h-[calc(100vh-220px)] pr-2">
            {messages.map((msg, index) => (
              <div 
                key={index}
                className={`flex gap-4 max-w-[85%] ${
                  msg.role === 'user' ? 'self-end flex-row-reverse' : 'self-start'
                }`}
              >
                {/* Avatar Icon */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-bold ${
                  msg.role === 'user' 
                    ? 'bg-gradient-to-tr from-indigo-500 to-indigo-600 text-white text-xs' 
                    : 'bg-white/10 text-indigo-400 border border-white/5 text-sm'
                }`}>
                  {msg.role === 'user' ? 'U' : <Bot className="w-4 h-4" />}
                </div>

                {/* Message Bubble */}
                <div className="flex flex-col gap-1.5">
                  <div 
                    className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-md ${
                      msg.role === 'user'
                        ? 'bg-indigo-600 text-white rounded-tr-none'
                        : 'glass-panel text-slate-200 rounded-tl-none border border-white/5'
                    }`}
                  >
                    {msg.role === 'user' ? (
                      <span>{msg.content}</span>
                    ) : (
                      /* Render AI markdown */
                      <div 
                        className="prose prose-invert prose-sm max-w-none text-slate-100 [&_code]:bg-white/10 [&_code]:px-1 [&_code]:rounded [&_pre]:bg-white/5 [&_pre]:p-3 [&_pre]:rounded-xl [&_pre]:overflow-x-auto [&_ul]:list-disc [&_ul]:pl-4 [&_ol]:list-decimal [&_ol]:pl-4 [&_h1]:text-base [&_h2]:text-sm [&_h3]:text-sm [&_strong]:text-white"
                        dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
                      />
                    )}
                  </div>

                  {/* Actions (Only for Bot reply) */}
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-3 pl-2 mt-1">
                      <button 
                        onClick={() => copyToClipboard(msg.content, index)}
                        className="p-1 text-slate-500 hover:text-slate-300 transition cursor-pointer"
                        title="Copy text"
                      >
                        {copiedIdx === index ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>
                      <button className="p-1 text-slate-500 hover:text-slate-300 transition cursor-pointer" title="Regenerate">
                        <RotateCw className="w-3.5 h-3.5" />
                      </button>
                      <button className="p-1 text-slate-500 hover:text-green-400 transition cursor-pointer" title="Helpful">
                        <ThumbsUp className="w-3.5 h-3.5" />
                      </button>
                      <button className="p-1 text-slate-500 hover:text-rose-400 transition cursor-pointer" title="Not helpful">
                        <ThumbsDown className="w-3.5 h-3.5" />
                      </button>
                      <span className="text-[10px] text-slate-500 font-semibold ml-auto">{msg.timestamp}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {isLoading && (
              <div className="flex gap-4 self-start">
                <div className="w-8 h-8 rounded-full bg-white/10 text-indigo-400 border border-white/5 flex items-center justify-center text-sm">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="glass-panel border border-white/5 rounded-2xl rounded-tl-none px-5 py-4 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.15s]" />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.3s]" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        )}
      </div>

      {/* Floating Chat Input Section */}
      <div className="max-w-[920px] mx-auto w-full px-6 sticky bottom-0 z-20">
        <div className="glass-panel border border-white/10 rounded-[28px] p-2.5 flex items-center gap-3 shadow-2xl shadow-indigo-950/20 backdrop-blur-2xl">
          {/* Mode Switcher */}
          <ModeSwitcher activeTab={activeTab} setActiveTab={setActiveTab} />
          
          <div className="w-[1px] h-6 bg-white/10" />

          {/* Text Input area */}
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !isLoading) handleSend(inputVal)
            }}
            placeholder="Message your AI assistant..."
            className="flex-1 bg-transparent border-none focus:outline-none text-sm text-slate-100 placeholder-slate-500 px-2 py-2"
            disabled={isLoading}
          />

          {/* Right Action Icons */}
          <div className="flex items-center gap-2.5 pr-1">
            <button className="p-2 text-slate-400 hover:text-slate-200 hover:bg-white/5 rounded-xl transition cursor-pointer">
              <Paperclip className="w-4 h-4" />
            </button>
            <button className="p-2 text-slate-400 hover:text-slate-200 hover:bg-white/5 rounded-xl transition cursor-pointer">
              <Mic className="w-4 h-4" />
            </button>
            
            {/* Round Gradient Send Button */}
            <button 
              onClick={() => handleSend(inputVal)}
              disabled={isLoading || !inputVal.trim()}
              className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-indigo-600 flex items-center justify-center text-white hover:from-indigo-400 hover:to-indigo-500 disabled:opacity-40 shadow-[0_2px_8px_rgba(99,102,241,0.3)] transition-all cursor-pointer"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
        <div className="text-[10px] text-slate-500 text-center mt-2.5 font-medium tracking-wide">
          Running on model: <span className="text-indigo-400 font-semibold">{activeModelDisplayName}</span>
        </div>
      </div>
    </div>
  )
}
