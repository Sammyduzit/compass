import React from "react";

export function Topbar() {
  return (
    <header className="h-[48px] bg-[#FFFFFF] border-b border-[rgba(0,0,0,0.07)] flex items-center px-4 shrink-0 z-10 gap-0">
      <div className="flex items-center gap-[10px] flex-1 min-w-0">
        <div className="flex items-center gap-[7px] font-['Newsreader',_serif] text-[17px] font-semibold text-[#1A1C1B] tracking-[-0.01em] whitespace-nowrap shrink-0">
          <div className="w-[22px] h-[22px] bg-[#4A7862] rounded-[5px] flex items-center justify-center">
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <circle cx="6.5" cy="6.5" r="4" stroke="white" strokeWidth="1.5" />
              <line
                x1="6.5"
                y1="2"
                x2="6.5"
                y2="0.5"
                stroke="white"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
              <circle cx="6.5" cy="6.5" r="1.2" fill="white" />
            </svg>
          </div>
          Compass
        </div>
      </div>

      <nav className="flex items-center gap-[2px] absolute left-1/2 -translate-x-1/2">
        <button className="px-[14px] py-[5px] rounded-[6px] text-[13px] font-semibold text-[#4A7862] bg-[#EBF3EE] whitespace-nowrap border-none transition-colors">
          Onboarding
        </button>
        <button className="px-[14px] py-[5px] rounded-[6px] text-[13px] font-medium text-[#717975] bg-transparent whitespace-nowrap border-none transition-colors hover:bg-[#FDFCFB] hover:text-[#3A3D3B]">
          Workspace
        </button>
        <button className="px-[14px] py-[5px] rounded-[6px] text-[13px] font-medium text-[#717975] bg-transparent whitespace-nowrap border-none transition-colors hover:bg-[#FDFCFB] hover:text-[#3A3D3B]">
          Community
        </button>
      </nav>

      <div className="flex items-center gap-2 flex-1 justify-end">
        <div className="flex items-center gap-[5px] font-['JetBrains_Mono',_monospace] text-[11px] text-[#717975] bg-[#FDFCFB] border border-[rgba(0,0,0,0.07)] rounded-[20px] px-[9px] py-[3px] whitespace-nowrap">
          <span className="w-[6px] h-[6px] rounded-full bg-[#4A7862] shrink-0"></span>
          Stuart McLean
        </div>
        <div
          className="w-[28px] h-[28px] rounded-full flex items-center justify-center text-[10px] font-bold text-white shrink-0 cursor-pointer font-['Public_Sans',_sans-serif]"
          style={{ background: "linear-gradient(135deg, #6B8F7A, #4A7862)" }}
        >
          SM
        </div>
      </div>
    </header>
  );
}
