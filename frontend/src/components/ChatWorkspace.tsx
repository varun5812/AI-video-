import React, { useState, useRef, useEffect } from 'react'
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
  Bot
} from 'lucide-react'
import ModeSwitcher from './ModeSwitcher'

interface Message {
  role: 'user' | 'assistant'
  content: string
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

  const handleSend = async (text: string) => {
    if (!text.trim()) return
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
      } else {
        throw new Error('API server returned an error.')
      }
    } catch (err) {
      // Fallback Mock Responses when backend is offline
      setTimeout(() => {
        let mockAnswer = `This is a premium AI response powered by **${activeModelDisplayName}**.<br/><br/>I am running in local workspace mode. When you launch the FastAPI backend server, I will answer your questions in real-time.<br/><br/>**Here is a quick summary of what you asked:**<br/>*${text}*`
        
        if (text.toLowerCase().includes('relativity')) {
          mockAnswer = `### General Relativity Analogy 🌌<br/><br/>Imagine space as a **flexible rubber sheet**. If you place a heavy bowling ball in the center, it creates a deep dip. <br/><br/>If you roll a small marble across the sheet, it curves toward the bowling ball not because of a mysterious pulling force, but because the sheet itself is curved. <br/><br/>* **Mass** (the bowling ball) curves space-time.<br/>* **Space-time curvature** tells mass (the marble) how to move.`
        } else if (text.toLowerCase().includes('python')) {
          mockAnswer = `Here is a clean Python solution using the standard \`urllib.parse\` library:<br/><br/>\`\`\`python\nfrom urllib.parse import urlparse, parse_qs\n\ndef get_query_params(url):\n    parsed_url = urlparse(url)\n    return parse_qs(parsed_url.query)\n\n# Example usage:\nprint(get_query_params("https://example.com?item=chair&qty=4"))\n# Output: {'item': ['chair'], 'qty': ['4']}\n\`\`\``
        }

        const botMsg: Message = {
          role: 'assistant',
          content: mockAnswer,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
        setMessages(prev => [...prev, botMsg])
      }, 800)
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
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
                className={`flex gap-4 max-w-[85%] animate-[fadeUp_0.3s_ease-out] ${
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
                    {/* Rendered HTML/Markdown */}
                    <div 
                      className="prose prose-invert max-w-none text-slate-100"
                      dangerouslySetInnerHTML={{ __html: msg.content }}
                    />
                  </div>

                  {/* Actions (Only for Bot reply) */}
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-3 pl-2 mt-1">
                      <button 
                        onClick={() => copyToClipboard(msg.content.replace(/<[^>]*>/g, ''))}
                        className="p-1 text-slate-500 hover:text-slate-300 transition cursor-pointer"
                        title="Copy text"
                      >
                        <Copy className="w-3.5 h-3.5" />
                      </button>
                      <button className="p-1 text-slate-500 hover:text-slate-300 transition cursor-pointer" title="Regenerate">
                        <RotateCw className="w-3.5 h-3.5" />
                      </button>
                      <button className="p-1 text-slate-500 hover:text-slate-300 transition cursor-pointer" title="Helpful">
                        <ThumbsUp className="w-3.5 h-3.5" />
                      </button>
                      <button className="p-1 text-slate-500 hover:text-slate-300 transition cursor-pointer" title="Not helpful">
                        <ThumbsDown className="w-3.5 h-3.5" />
                      </button>
                      <span className="text-[10px] text-slate-500 font-semibold ml-auto">{msg.timestamp}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Spinner indicator when loading */}
            {isLoading && (
              <div className="flex gap-4 self-start animate-pulse">
                <div className="w-8 h-8 rounded-full bg-white/10 text-indigo-400 border border-white/5 flex items-center justify-center text-sm">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="glass-panel border border-white/5 rounded-2xl rounded-tl-none px-5 py-3.5 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        )}
      </div>

      {/* Floating Chat Input Section (850-950px width, Bottom) */}
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
              if (e.key === 'Enter') handleSend(inputVal)
            }}
            placeholder="Message your AI assistant..."
            className="flex-1 bg-transparent border-none focus:outline-none text-sm text-slate-100 placeholder-slate-500 px-2 py-2"
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
              className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-indigo-600 flex items-center justify-center text-white hover:from-indigo-400 hover:to-indigo-500 shadow-[0_2px_8px_rgba(99,102,241,0.3)] transition-all cursor-pointer"
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
