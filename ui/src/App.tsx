import { useState } from 'react'
import type { SummaryData, RulesData, DeveloperProfile } from './types'
import { mockSummary, mockRules } from './mock/data'
import SummaryPanel from './components/SummaryPanel'
import RulesPanel from './components/RulesPanel'
import ChatPanel from './components/ChatPanel'
import './App.css'

function App() {
  const [summary] = useState<SummaryData>(mockSummary)
  const [rules] = useState<RulesData>(mockRules)
  const [developerProfile, setDeveloperProfile] = useState<DeveloperProfile | null>(null)

  return (
    <div className="app-layout">
      <SummaryPanel summary={summary} developerProfile={developerProfile} />
      <RulesPanel rules={rules} />
      <ChatPanel
        summary={summary}
        rules={rules}
        developerProfile={developerProfile}
        onProfileSet={setDeveloperProfile}
      />
    </div>
  )
}

export default App
