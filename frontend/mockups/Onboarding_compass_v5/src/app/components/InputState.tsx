import React, { useState } from "react";
import { FolderGit2, Play, Folder } from "lucide-react";

interface InputStateProps {
  onAnalyze: () => void;
  onBack: () => void;
}

export function InputState({ onAnalyze, onBack }: InputStateProps) {
  const [localPath, setLocalPath] = useState("");
  const [outputRules, setOutputRules] = useState(true);
  const [outputSummary, setOutputSummary] = useState(true);
  const [aiProvider, setAiProvider] = useState("claude");
  const [language, setLanguage] = useState("auto-detect");
  const [forceRerun, setForceRerun] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (localPath) onAnalyze();
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-[#FDFCFB] h-full overflow-y-auto py-12">
      <div className="w-full max-w-[560px] px-6">
        <div className="mb-8">
          <div className="flex items-center gap-3 text-[#4A7862] mb-3">
            <FolderGit2 className="w-5 h-5" />
            <span className="font-semibold text-[13px] tracking-wide uppercase">New Analysis</span>
          </div>
          <h1 className="font-['Newsreader',_serif] text-[32px] font-semibold tracking-[-0.02em] text-[#1A1C1B]">
            Configure workspace
          </h1>
          <p className="text-[#717975] text-[15px] mt-2">
            Point to a local repository on your machine to analyze its structure.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6 bg-white border border-[rgba(0,0,0,0.07)] rounded-xl p-8 shadow-[0_2px_12px_rgba(0,0,0,0.03)]">
          {/* Local Path Input */}
          <div className="space-y-2">
            <label className="block text-[13px] font-semibold text-[#1A1C1B]">
              Local Repository Path
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#717975]">
                <Folder className="w-[18px] h-[18px]" />
              </div>
              <input
                type="text"
                value={localPath}
                onChange={(e) => setLocalPath(e.target.value)}
                placeholder="/Users/stuart/Projects/my-repo"
                className="w-full pl-10 pr-4 py-[10px] bg-[#FDFCFB] border border-[rgba(0,0,0,0.1)] rounded-lg text-[14px] text-[#1A1C1B] focus:outline-none focus:border-[#4A7862] focus:ring-1 focus:ring-[#4A7862] transition-all placeholder:text-[#A0A5A2]"
                required
              />
            </div>
          </div>

          {/* Output Options */}
          <div className="space-y-3">
            <label className="block text-[13px] font-semibold text-[#1A1C1B]">
              Output
            </label>
            <div className="space-y-2">
              <label className="flex items-center gap-3 cursor-pointer group">
                <div className="relative flex items-center justify-center">
                  <input
                    type="checkbox"
                    checked={outputRules}
                    onChange={(e) => setOutputRules(e.target.checked)}
                    className="peer sr-only"
                  />
                  <div className="w-5 h-5 border border-[rgba(0,0,0,0.2)] rounded-[4px] bg-[#FDFCFB] peer-checked:bg-[#4A7862] peer-checked:border-[#4A7862] transition-colors"></div>
                  <svg className="absolute w-3 h-3 text-white opacity-0 peer-checked:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-[14px] font-medium text-[#1A1C1B]">Rules</span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer group">
                <div className="relative flex items-center justify-center">
                  <input
                    type="checkbox"
                    checked={outputSummary}
                    onChange={(e) => setOutputSummary(e.target.checked)}
                    className="peer sr-only"
                  />
                  <div className="w-5 h-5 border border-[rgba(0,0,0,0.2)] rounded-[4px] bg-[#FDFCFB] peer-checked:bg-[#4A7862] peer-checked:border-[#4A7862] transition-colors"></div>
                  <svg className="absolute w-3 h-3 text-white opacity-0 peer-checked:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-[14px] font-medium text-[#1A1C1B]">Summary</span>
              </label>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="block text-[13px] font-semibold text-[#1A1C1B]">
                AI Provider
              </label>
              <select
                value={aiProvider}
                onChange={(e) => setAiProvider(e.target.value)}
                className="w-full px-4 py-[10px] bg-[#FDFCFB] border border-[rgba(0,0,0,0.1)] rounded-lg text-[14px] text-[#1A1C1B] focus:outline-none focus:border-[#4A7862] focus:ring-1 focus:ring-[#4A7862] transition-all appearance-none"
              >
                <option value="claude">Claude</option>
                <option value="codex">Codex</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="block text-[13px] font-semibold text-[#1A1C1B]">
                Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-4 py-[10px] bg-[#FDFCFB] border border-[rgba(0,0,0,0.1)] rounded-lg text-[14px] text-[#1A1C1B] focus:outline-none focus:border-[#4A7862] focus:ring-1 focus:ring-[#4A7862] transition-all appearance-none"
              >
                <option value="auto-detect">Auto-detect</option>
                <option value="python">Python</option>
                <option value="typescript">TypeScript</option>
              </select>
            </div>
          </div>

          <div className="pt-2">
            <label className="flex items-center gap-3 cursor-pointer group">
              <div className="relative flex items-center justify-center">
                <input
                  type="checkbox"
                  checked={forceRerun}
                  onChange={(e) => setForceRerun(e.target.checked)}
                  className="peer sr-only"
                />
                <div className="w-5 h-5 border border-[rgba(0,0,0,0.2)] rounded-[4px] bg-[#FDFCFB] peer-checked:bg-[#4A7862] peer-checked:border-[#4A7862] transition-colors"></div>
                <svg className="absolute w-3 h-3 text-white opacity-0 peer-checked:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div className="flex flex-col">
                <span className="text-[14px] font-medium text-[#1A1C1B]">Force re-run</span>
                <span className="text-[12px] text-[#717975]">Ignore cached results and analyze from scratch</span>
              </div>
            </label>
          </div>

          <div className="pt-6 mt-6 border-t border-[rgba(0,0,0,0.07)] flex justify-between">
            <button
              type="button"
              onClick={onBack}
              className="flex items-center gap-2 bg-transparent hover:bg-[rgba(0,0,0,0.03)] text-[#1A1C1B] border border-[#1A1C1B] px-6 py-[10px] rounded-lg font-medium text-[14px] transition-all active:scale-[0.98]"
            >
              Back
            </button>
            <button
              type="submit"
              className="flex items-center gap-2 bg-[#1A1C1B] hover:bg-[#3A3D3B] text-white px-6 py-[10px] rounded-lg font-medium text-[14px] transition-all shadow-[0_1px_3px_rgba(0,0,0,0.1)] active:scale-[0.98]"
            >
              Start Analysis
              <Play className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
