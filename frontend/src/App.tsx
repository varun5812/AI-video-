import React, { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import ChatWorkspace from './components/ChatWorkspace'
import VideoWorkspace from './components/VideoWorkspace'
import PlatformModal from './components/PlatformModal'

export default function App() {
  const [collapsed, setCollapsed] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'video'>('chat')
  const [selectedModel, setSelectedModel] = useState('✨ Google — Gemini 3.6 Flash')
  
  // Credentials checking
  const [googleKeyOk, setGoogleKeyOk] = useState(false)
  const [groqKeyOk, setGroqKeyOk] = useState(false)

  // Active platform modal: 'projects' | 'history' | 'favorites' | 'settings' | null
  const [activeModal, setActiveModal] = useState<'projects' | 'history' | 'favorites' | 'settings' | null>(null)

  // Verify status on load
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/status')
        if (response.ok) {
          const data = await response.json()
          setGoogleKeyOk(data.google_ok)
          setGroqKeyOk(data.groq_ok)
        }
      } catch (err) {
        // Fallback for mocked mode
        setGoogleKeyOk(true)
        setGroqKeyOk(true)
      }
    }
    fetchStatus()
  }, [])

  return (
    <div className="flex bg-[#030712] min-h-screen text-slate-100 font-sans antialiased overflow-hidden">
      
      {/* Collapsible Navigation Sidebar */}
      <Sidebar 
        collapsed={collapsed} 
        setCollapsed={setCollapsed} 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onOpenModal={(modal) => setActiveModal(modal)}
      />

      {/* Main Workspace Frame */}
      <div className="flex-1 flex flex-col min-h-screen overflow-hidden">
        
        {/* Persistent Global Header */}
        <Header 
          activeTab={activeTab} 
          googleKeyOk={googleKeyOk} 
          groqKeyOk={groqKeyOk} 
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
        />

        {/* Dynamic Workspace Toggle View */}
        <main className="flex-1 flex flex-col overflow-hidden relative">
          
          {activeTab === 'chat' ? (
            <ChatWorkspace 
              activeTab={activeTab} 
              setActiveTab={setActiveTab} 
              selectedModel={selectedModel}
              activeModelDisplayName={selectedModel}
            />
          ) : (
            <VideoWorkspace 
              activeTab={activeTab} 
              selectedModel={selectedModel}
              activeModelDisplayName={selectedModel}
            />
          )}

        </main>
      </div>

      {/* Functional Platform Modal (Projects, History, Favorites, Settings) */}
      <PlatformModal 
        activeModal={activeModal}
        onClose={() => setActiveModal(null)}
        googleKeyOk={googleKeyOk}
        groqKeyOk={groqKeyOk}
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
      />

    </div>
  )
}
