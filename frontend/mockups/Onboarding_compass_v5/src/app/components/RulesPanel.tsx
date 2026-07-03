import React from "react";

export function RulesPanel() {
  return (
    <aside className="hidden lg:flex w-[280px] bg-[#FFFFFF] border-l border-[rgba(0,0,0,0.07)] flex-col shrink-0 overflow-y-auto font-['Public_Sans',_sans-serif]">
      <div className="px-[14px] pt-[14px] pb-[8px] text-[9.5px] font-bold tracking-[0.12em] uppercase text-[#A0A8A4] font-['JetBrains_Mono',_monospace] border-b border-[rgba(0,0,0,0.07)]">
        Associated Rules
      </div>
      
      <div className="px-[14px] pt-[10px] pb-[6px] text-[9.5px] font-semibold tracking-[0.08em] uppercase text-[#4A7862] font-['JetBrains_Mono',_monospace] flex items-center gap-[5px]">
        <span className="w-[5px] h-[5px] rounded-full bg-[#4A7862]" />
        Golden file · 3 rules
      </div>

      <div className="mx-[10px] mb-[8px] bg-[#FFFFFF] border border-[rgba(0,0,0,0.07)] rounded-[6px] px-[12px] py-[11px] cursor-pointer transition-all hover:border-[rgba(74,120,98,0.4)] hover:shadow-[0_2px_8px_rgba(74,120,98,0.08)] rule-card" data-rule="DI-01">
        <div className="flex items-center justify-between mb-[5px]">
          <span className="font-['JetBrains_Mono',_monospace] text-[9.5px] font-semibold text-[#4A7862] bg-[#EBF3EE] border border-[rgba(74,120,98,0.2)] rounded-[3px] px-[6px] py-[1px] tracking-[0.04em]">
            DI-01
          </span>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" className="text-[#A0A8A4]">
            <path d="M3 4.5l3 3 3-3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div className="text-[12px] font-semibold text-[#1A1C1B] mb-[3px] leading-[1.35]">
          Use factory functions
        </div>
        <div className="text-[11px] text-[#717975] leading-[1.45]">
          Avoid <code className="font-['JetBrains_Mono',_monospace] text-[10px] bg-[rgba(0,0,0,0.05)] px-[3px] rounded-[2px]">new</code> outside factories. Always wrap construction in a named factory for testability and traceability.
        </div>
      </div>

      <div className="mx-[10px] mb-[8px] bg-[#FFFFFF] border border-[rgba(0,0,0,0.07)] rounded-[6px] px-[12px] py-[11px] cursor-pointer transition-all hover:border-[rgba(74,120,98,0.4)] hover:shadow-[0_2px_8px_rgba(74,120,98,0.08)] rule-card" data-rule="HEX-04">
        <div className="flex items-center justify-between mb-[5px]">
          <span className="font-['JetBrains_Mono',_monospace] text-[9.5px] font-semibold text-[#4A7862] bg-[#EBF3EE] border border-[rgba(74,120,98,0.2)] rounded-[3px] px-[6px] py-[1px] tracking-[0.04em]">
            HEX-04
          </span>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" className="text-[#A0A8A4]">
            <path d="M3 4.5l3 3 3-3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div className="text-[12px] font-semibold text-[#1A1C1B] mb-[3px] leading-[1.35]">
          No infrastructure in root
        </div>
        <div className="text-[11px] text-[#717975] leading-[1.45]">
          Adapters passed as interfaces. The domain must not know about Postgres, Redis, or connection strings.
        </div>
      </div>

      <div className="mx-[10px] mb-[8px] bg-[#FFFFFF] border border-[rgba(0,0,0,0.07)] rounded-[6px] px-[12px] py-[11px] cursor-pointer transition-all hover:border-[rgba(74,120,98,0.4)] hover:shadow-[0_2px_8px_rgba(74,120,98,0.08)] rule-card" data-rule="COMP-02">
        <div className="flex items-center justify-between mb-[5px]">
          <span className="font-['JetBrains_Mono',_monospace] text-[9.5px] font-semibold text-[#4A7862] bg-[#EBF3EE] border border-[rgba(74,120,98,0.2)] rounded-[3px] px-[6px] py-[1px] tracking-[0.04em]">
            COMP-02
          </span>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" className="text-[#A0A8A4]">
            <path d="M3 4.5l3 3 3-3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div className="text-[12px] font-semibold text-[#1A1C1B] mb-[3px] leading-[1.35]">
          Single composition point
        </div>
        <div className="text-[11px] text-[#717975] leading-[1.45]">
          Wiring happens in exactly one place. Multiple composition roots signal architectural drift.
        </div>
      </div>

      <div className="px-[14px] py-[10px] text-[11.5px] text-[#4A7862] font-medium cursor-pointer border-t border-[rgba(0,0,0,0.07)] mt-auto flex items-center gap-[4px] hover:underline">
        View all 12 rules
        <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
          <path d="M4 2l3.5 3.5L4 9" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
    </aside>
  );
}
