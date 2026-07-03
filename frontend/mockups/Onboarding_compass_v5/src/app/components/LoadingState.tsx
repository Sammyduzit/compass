import React, { useEffect, useState } from "react";
import { Loader2, Terminal, CheckCircle2 } from "lucide-react";

interface LoadingStateProps {
  onComplete: () => void;
}

const STEPS = [
  "Cloning repository...",
  "Parsing Abstract Syntax Trees (AST)...",
  "Resolving internal dependencies...",
  "Identifying core entities and relationships...",
  "Generating architectural map...",
  "Finalizing workspace..."
];

export function LoadingState({ onComplete }: LoadingStateProps) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    let timeoutId: number;
    
    const advanceStep = (step: number) => {
      if (step >= STEPS.length) {
        timeoutId = setTimeout(() => {
          onComplete();
        }, 1000);
        return;
      }
      
      setCurrentStep(step);
      
      // Random delay between 800ms and 2000ms
      const delay = Math.floor(Math.random() * 1200) + 800;
      timeoutId = setTimeout(() => advanceStep(step + 1), delay);
    };

    advanceStep(0);

    return () => clearTimeout(timeoutId);
  }, [onComplete]);

  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-[#FDFCFB] h-full">
      <div className="max-w-[480px] w-full flex flex-col items-center">
        {/* Animated Icon */}
        <div className="relative mb-10">
          <div className="absolute inset-0 bg-[#4A7862] opacity-20 blur-xl rounded-full animate-pulse"></div>
          <div className="w-[80px] h-[80px] bg-white border border-[rgba(0,0,0,0.07)] shadow-[0_4px_24px_rgba(0,0,0,0.06)] rounded-2xl flex items-center justify-center relative z-10">
            <Loader2 className="w-10 h-10 text-[#4A7862] animate-spin" />
          </div>
        </div>

        <h2 className="font-['Newsreader',_serif] text-[28px] font-semibold tracking-[-0.02em] text-[#1A1C1B] mb-2">
          Analyzing Repository
        </h2>
        <p className="text-[#717975] text-[15px] mb-8">
          This might take a minute depending on the repository size.
        </p>

        {/* Console / Steps UI */}
        <div className="w-full bg-[#1A1C1B] rounded-xl overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.15)] border border-[rgba(0,0,0,0.8)] font-['JetBrains_Mono',_monospace] text-[12px]">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-[rgba(255,255,255,0.1)] bg-[rgba(255,255,255,0.03)] text-[#A0A5A2]">
            <Terminal className="w-4 h-4" />
            <span className="opacity-80">analysis_runner.sh</span>
          </div>
          <div className="p-5 space-y-3">
            {STEPS.map((step, index) => {
              const isActive = index === currentStep;
              const isDone = index < currentStep;
              const isFuture = index > currentStep;
              
              if (isFuture) return null;
              
              return (
                <div 
                  key={index} 
                  className={`flex items-start gap-3 transition-opacity duration-300 ${
                    isActive ? "opacity-100 text-white" : "opacity-60 text-[#A0A5A2]"
                  }`}
                >
                  <div className="mt-[2px] shrink-0">
                    {isDone ? (
                      <CheckCircle2 className="w-[14px] h-[14px] text-[#4A7862]" />
                    ) : (
                      <Loader2 className="w-[14px] h-[14px] animate-spin text-[#A0A5A2]" />
                    )}
                  </div>
                  <span>{step}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
