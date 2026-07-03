import React from "react";
import { Compass, GitBranch, ArrowRight } from "lucide-react";

interface EmptyStateProps {
  onStart: () => void;
}

export function EmptyState({ onStart }: EmptyStateProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-[#FDFCFB] text-[#1A1C1B] h-full">
      <div className="max-w-[480px] w-full flex flex-col items-center text-center px-6">
        <div className="w-[64px] h-[64px] bg-[#EBF3EE] text-[#4A7862] rounded-2xl flex items-center justify-center mb-8 shadow-sm">
          <Compass className="w-8 h-8" />
        </div>
        
        <h1 className="font-['Newsreader',_serif] text-[32px] font-semibold tracking-[-0.02em] mb-4">
          Navigate your codebase
        </h1>
        
        <p className="text-[#717975] text-[15px] leading-relaxed mb-10">
          Compass helps you understand complex repositories, track dependencies, and map out entity relationships instantly. Connect a repository to get started.
        </p>
        
        <button 
          onClick={onStart}
          className="group flex items-center gap-2 bg-[#4A7862] hover:bg-[#3d6351] text-white px-6 py-3 rounded-lg font-medium transition-all shadow-[0_1px_3px_rgba(0,0,0,0.1)] hover:shadow-[0_2px_5px_rgba(0,0,0,0.15)] active:scale-[0.98]"
        >
          <GitBranch className="w-[18px] h-[18px]" />
          Connect Repository
          <ArrowRight className="w-4 h-4 ml-1 opacity-70 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
}
