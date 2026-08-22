import React from 'react'
import { MessageSquare, Video } from 'lucide-react'

interface ModeSwitcherProps {
  activeTab: 'chat' | 'video'
  setActiveTab: (tab: 'chat' | 'video') => void
}

export default function ModeSwitcher({ activeTab, setActiveTab }: ModeSwitcherProps) {
  return (
    <div className="bg-slate-900/60 p-1 rounded-2xl flex border border-white/5 shadow-inner backdrop-blur-md relative select-none">
      {/* Sliding Active Background */}
      <div 
        className={`absolute top-1 bottom-1 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-600 shadow-[0_0_12px_rgba(99,102,241,0.35)] transition-all duration-300 ease-out z-0 ${
          activeTab === 'chat' ? 'left-1 w-[105px]' : 'left-[108px] w-[112px]'
        }`}
      />

      {/* Chat Tab Option */}
      <button
        onClick={() => setActiveTab('chat')}
        className={`relative z-10 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-xl font-bold text-xs cursor-pointer transition-colors duration-200 ${
          activeTab === 'chat' ? 'text-white' : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <MessageSquare className="w-3.5 h-3.5" />
        <span>Chat AI</span>
      </button>

      {/* Video Tab Option */}
      <button
        onClick={() => setActiveTab('video')}
        className={`relative z-10 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-xl font-bold text-xs cursor-pointer transition-colors duration-200 ${
          activeTab === 'video' ? 'text-white' : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <Video className="w-3.5 h-3.5" />
        <span>Video AI</span>
      </button>
    </div>
  )
}
