import React, { useState } from "react";
import { Topbar } from "./components/Topbar";
import { NavStrip } from "./components/NavStrip";
import { SectionList } from "./components/SectionList";
import { MainDetail } from "./components/MainDetail";
import { RulesPanel } from "./components/RulesPanel";
import { ChatSection } from "./components/ChatSection";
import { EmptyState } from "./components/EmptyState";
import { InputState } from "./components/InputState";
import { LoadingState } from "./components/LoadingState";

type AppState = "empty" | "input" | "loading" | "results";

export default function App() {
  const [appState, setAppState] = useState<AppState>("empty");

  return (
    <div className="h-screen bg-[#F0EFED] text-[#1A1C1B] font-['Public_Sans',_sans-serif] text-[14px] antialiased">
      {/* Outer shell — max-width centred */}
      <div className="max-w-[1440px] mx-auto h-screen flex flex-col bg-[#FDFCFB] shadow-[0_0_0_1px_rgba(0,0,0,0.07),_0_4px_40px_rgba(0,0,0,0.08)] relative overflow-hidden">
        <Topbar />
        
        {/* Workspace */}
        <div className="flex flex-1 overflow-hidden min-h-0">
          {appState === "empty" && <EmptyState onStart={() => setAppState("input")} />}
          {appState === "input" && <InputState onAnalyze={() => setAppState("loading")} onBack={() => setAppState("empty")} />}
          {appState === "loading" && <LoadingState onComplete={() => setAppState("results")} />}
          
          {appState === "results" && (
            <>
              <NavStrip />
              <SectionList />
              <MainDetail />
              <RulesPanel />
            </>
          )}
        </div>

        {/* Chat Section */}
        {appState === "results" && <ChatSection />}
      </div>
    </div>
  );
}
