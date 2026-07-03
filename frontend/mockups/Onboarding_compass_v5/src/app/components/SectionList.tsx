import React, { useState } from "react";
import { clsx } from "clsx";
import { FolderGit2 } from "lucide-react";

interface FileCardProps {
  name: string;
  desc: string;
  isActive?: boolean;
}

function FileCard({ name, desc, isActive }: FileCardProps) {
  return (
    <div
      className={clsx(
        "flex flex-col gap-[3px] px-[16px] py-[10px] cursor-pointer border-l-[3px] transition-all",
        isActive
          ? "border-[#4A7862] bg-[#EBF3EE]"
          : "border-transparent hover:bg-[#F8F8F7] hover:border-[rgba(74,120,98,0.2)]"
      )}
    >
      <div
        className={clsx(
          "font-['JetBrains_Mono',_monospace] text-[11.5px] font-medium leading-tight",
          isActive ? "text-[#3A6252]" : "text-[#1A1C1B]"
        )}
      >
        {name}
      </div>
      <div className="text-[11px] text-[#717975] leading-[1.4]">{desc}</div>
    </div>
  );
}

interface SectionHeaderProps {
  label: string;
  isExpanded: boolean;
  onToggle: () => void;
}

function SectionHeader({ label, isExpanded, onToggle }: SectionHeaderProps) {
  return (
    <button
      onClick={onToggle}
      className="w-full px-[16px] py-[10px] text-[9.5px] font-bold tracking-[0.1em] uppercase text-[#A0A8A4] font-['JetBrains_Mono',_monospace] flex items-center justify-between hover:text-[#717975] transition-colors cursor-pointer border-none bg-transparent text-left group"
    >
      <span>{label}</span>
      <svg
        viewBox="0 0 10 10"
        fill="none"
        className={clsx(
          "w-[9px] h-[9px] shrink-0 transition-transform duration-200",
          !isExpanded && "-rotate-90"
        )}
      >
        <path
          d="M2 3.5l3 3 3-3"
          stroke="currentColor"
          strokeWidth="1.3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </button>
  );
}

export function SectionList() {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    "start-here": true,
    "stable": true,
  });

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  return (
    <aside className="hidden md:flex w-[220px] bg-[#FFFFFF] border-r border-[rgba(0,0,0,0.07)] flex-col shrink-0 overflow-y-auto font-['Public_Sans',_sans-serif]">
      {/* Repository Header */}
      <div className="px-[16px] py-[12px] border-b border-[rgba(0,0,0,0.07)] flex items-center gap-[10px]">
        <div className="w-[32px] h-[32px] bg-[#EBF3EE] rounded-[7px] flex items-center justify-center shrink-0">
          <FolderGit2 className="w-[16px] h-[16px] text-[#4A7862]" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-[12.5px] font-semibold text-[#1A1C1B] whitespace-nowrap overflow-hidden text-ellipsis leading-tight">
            Service-Api
          </div>
          <div className="font-['JetBrains_Mono',_monospace] text-[10px] text-[#A0A8A4] whitespace-nowrap overflow-hidden text-ellipsis mt-[2px]">
            /local/path
          </div>
        </div>
      </div>

      <SectionHeader
        label="Start here"
        isExpanded={expandedSections["start-here"]}
        onToggle={() => toggleSection("start-here")}
      />

      {expandedSections["start-here"] && (
        <div className="pb-[8px]">
          <FileCard
            name="make-app.ts"
            desc="Composition root — where everything is wired"
            isActive
          />
          <FileCard
            name="domain/core.ts"
            desc="Pure business logic, no infrastructure"
          />
          <FileCard
            name="infra/adapter.ts"
            desc="Base adapter interface + error contract"
          />
          <FileCard
            name="config/env.ts"
            desc="Environment schema + validation"
          />
        </div>
      )}

      <div className="h-[1px] bg-[rgba(0,0,0,0.06)] mx-[16px]" />

      <SectionHeader
        label="Stable"
        isExpanded={expandedSections["stable"]}
        onToggle={() => toggleSection("stable")}
      />

      {expandedSections["stable"] && (
        <div className="pb-[8px]">
          <FileCard name="domain/types.ts" desc="Core domain types" />
          <FileCard name="lib/result.ts" desc="Result monad — used throughout" />
        </div>
      )}
    </aside>
  );
}
