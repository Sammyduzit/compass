import React from "react";
import { clsx } from "clsx";

interface TagPillProps {
  label: string;
  variant: "emerald" | "neutral";
}

function TagPill({ label, variant }: TagPillProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center px-[10px] py-[4px] rounded-[4px] text-[10px] font-bold tracking-[0.07em] uppercase font-['JetBrains_Mono',_monospace] cursor-pointer transition-colors border",
        variant === "emerald"
          ? "border-[#4A7862] text-[#4A7862] bg-[#EBF3EE] hover:bg-[rgba(74,120,98,0.18)]"
          : "border-[rgba(0,0,0,0.07)] text-[#717975] bg-[#FFFFFF] hover:bg-[#FDFCFB] hover:border-[#A0A8A4]"
      )}
    >
      {label}
    </span>
  );
}

export function MainDetail() {
  return (
    <main className="flex-1 bg-[#FDFCFB] overflow-y-auto pt-[28px] px-0 pb-[80px] min-w-0 font-['Public_Sans',_sans-serif]">
      {/* 58px each side -> inner calc width */}
      <div className="w-full px-[20px] md:px-0 md:w-[calc(100%-116px)] mx-auto">
        <div className="flex items-center gap-[4px] mb-[14px] flex-wrap">
          <span className="font-['JetBrains_Mono',_monospace] text-[11px] text-[#A0A8A4] cursor-pointer px-[4px] py-[2px] rounded-[3px] transition-colors hover:bg-[rgba(0,0,0,0.05)] hover:text-[#717975]">
            Onboarding
          </span>
          <span className="font-['JetBrains_Mono',_monospace] text-[11px] text-[#A0A8A4] opacity-50">
            ›
          </span>
          <span className="font-['JetBrains_Mono',_monospace] text-[11px] text-[#A0A8A4] cursor-pointer px-[4px] py-[2px] rounded-[3px] transition-colors hover:bg-[rgba(0,0,0,0.05)] hover:text-[#717975]">
            Start here
          </span>
          <span className="font-['JetBrains_Mono',_monospace] text-[11px] text-[#A0A8A4] opacity-50">
            ›
          </span>
          <span className="font-['JetBrains_Mono',_monospace] text-[11px] text-[#3A3D3B] font-medium px-[4px] py-[2px] rounded-[3px]">
            make-app.ts
          </span>
        </div>

        <div className="flex gap-[6px] mb-[20px] flex-wrap">
          <TagPill label="Entry Point" variant="emerald" />
          <TagPill label="Inversion of Control" variant="neutral" />
          <TagPill label="Factory Pattern" variant="neutral" />
        </div>

        <h1 className="font-['Newsreader',_serif] text-[36px] font-semibold leading-[1.18] text-[#1A1C1B] tracking-[-0.02em] mb-[20px]">
          The composition root —<br />
          where <em className="italic font-normal">everything</em> is wired
        </h1>

        <div className="mb-[24px]">
          <p
            className="text-[15px] leading-[1.78] text-[#3A3D3B] mb-[14px] px-[6px] py-[4px] rounded-[4px] border-l-3 border-transparent transition-colors hover:bg-[rgba(255,255,255,0.7)] hover:border-[rgba(74,120,98,0.3)] cursor-default peer"
            data-rule="DI-01"
          >
            Compass identified this as the first file to read. Every dependency
            in this codebase flows through{" "}
            <code className="font-['JetBrains_Mono',_monospace] text-[12.5px] bg-[rgba(0,0,0,0.05)] px-[5px] py-[1px] rounded-[3px] text-[#3A6252]">
              make-app.ts
            </code>{" "}
            — it is the factory that assembles the application without framework
            magic or reflection.
          </p>
          <p
            className="text-[15px] leading-[1.78] text-[#3A3D3B] mb-[14px] px-[6px] py-[4px] rounded-[4px] border-l-3 border-transparent transition-colors hover:bg-[rgba(255,255,255,0.7)] hover:border-[rgba(74,120,98,0.3)] cursor-default peer"
            data-rule="HEX-04"
          >
            Reading this file gives you a complete mental model of how the
            system is composed: what adapters exist, where configuration enters,
            and how the domain is insulated from infrastructure concerns.
          </p>
        </div>

        <div className="bg-[#FFFFFF] border-l-3 border-[#4A7862] rounded-r-[8px] px-[18px] py-[14px] mb-[24px] shadow-[0_2px_12px_rgba(0,0,0,0.04),_0_0_0_1px_rgba(0,0,0,0.05)]">
          <div className="text-[9.5px] font-bold tracking-[0.12em] uppercase text-[#4A7862] font-['JetBrains_Mono',_monospace] mb-[6px]">
            Why this matters
          </div>
          <p className="font-['Newsreader',_serif] italic text-[14.5px] leading-[1.65] text-[#3A3D3B]">
            "By centralising construction here, the codebase avoids 'spooky
            action at a distance' — you always know exactly where a dependency
            comes from, and swapping an adapter requires changing exactly one
            file."
          </p>
        </div>

        <div className="bg-[#1E2329] rounded-[8px] overflow-hidden mb-[24px] shadow-[0_4px_24px_rgba(0,0,0,0.12)]">
          <div className="flex items-center justify-between px-[16px] py-[9px] bg-[#2D3741] border-b border-[rgba(255,255,255,0.06)]">
            <span className="font-['JetBrains_Mono',_monospace] text-[11px] text-[rgba(255,255,255,0.45)]">
              src/make-app.ts
            </span>
            <span className="font-['JetBrains_Mono',_monospace] text-[9.5px] text-[rgba(255,255,255,0.3)] uppercase tracking-[0.08em]">
              TypeScript
            </span>
          </div>
          <div className="p-[18px] font-['JetBrains_Mono',_monospace] text-[12px] leading-[1.7] text-[#CDD5D0] overflow-x-auto">
            <pre className="m-0">
              <span className="text-[#6A8070] italic">
                // Composition root — assemble once, at the edge
              </span>
              {"\n"}
              <span className="text-[#89B4A0]">import</span>{" "}
              <span className="text-[#8DA89B]">{"{"}</span> AppConfig{" "}
              <span className="text-[#8DA89B]">{"}"}</span>{" "}
              <span className="text-[#89B4A0]">from</span>{" "}
              <span className="text-[#C3A67A]">'./config/env'</span>
              {"\n"}
              <span className="text-[#89B4A0]">import</span>{" "}
              <span className="text-[#8DA89B]">{"{"}</span> makePostgresAdapter{" "}
              <span className="text-[#8DA89B]">{"}"}</span>{" "}
              <span className="text-[#89B4A0]">from</span>{" "}
              <span className="text-[#C3A67A]">'./infra/postgres-adapter'</span>
              {"\n"}
              <span className="text-[#89B4A0]">import</span>{" "}
              <span className="text-[#8DA89B]">{"{"}</span> makeRedisAdapter{" "}
              <span className="text-[#8DA89B]">{"}"}</span>{" "}
              <span className="text-[#89B4A0]">from</span>{" "}
              <span className="text-[#C3A67A]">'./infra/redis-adapter'</span>
              {"\n"}
              <span className="text-[#89B4A0]">import</span>{" "}
              <span className="text-[#8DA89B]">{"{"}</span> makeDomainService{" "}
              <span className="text-[#8DA89B]">{"}"}</span>{" "}
              <span className="text-[#89B4A0]">from</span>{" "}
              <span className="text-[#C3A67A]">'./domain/core'</span>
              {"\n\n"}
              <span className="text-[#89B4A0]">export function</span>{" "}
              <span className="text-[#82CFAA]">makeApp</span>
              <span className="text-[#8DA89B]">(</span>config
              <span className="text-[#8DA89B]">:</span>{" "}
              <span className="text-[#9EC6B3]">AppConfig</span>
              <span className="text-[#8DA89B]">) {"{"}</span>
              {"\n  "}
              <span className="text-[#89B4A0]">const</span> db{"      "}
              <span className="text-[#8DA89B]">=</span>{" "}
              <span className="text-[#82CFAA]">makePostgresAdapter</span>
              <span className="text-[#8DA89B]">(</span>config.db
              <span className="text-[#8DA89B]">)</span>
              {"\n  "}
              <span className="text-[#89B4A0]">const</span> cache{"   "}
              <span className="text-[#8DA89B]">=</span>{" "}
              <span className="text-[#82CFAA]">makeRedisAdapter</span>
              <span className="text-[#8DA89B]">(</span>config.redis
              <span className="text-[#8DA89B]">)</span>
              {"\n  "}
              <span className="text-[#89B4A0]">const</span> service{" "}
              <span className="text-[#8DA89B]">=</span>{" "}
              <span className="text-[#82CFAA]">makeDomainService</span>
              <span className="text-[#8DA89B]">({"{ "}</span>db
              <span className="text-[#8DA89B]">,</span> cache{" "}
              <span className="text-[#8DA89B]">{"}"})</span>
              {"\n  "}
              <span className="text-[#89B4A0]">return</span>{" "}
              <span className="text-[#8DA89B]">{"{"}</span>
              {"\n    "}start<span className="text-[#8DA89B]">:</span>{" "}
              <span className="text-[#8DA89B]">()</span>{" "}
              <span className="text-[#8DA89B]">=&gt;</span> service.
              <span className="text-[#82CFAA]">init</span>
              <span className="text-[#8DA89B]">(),</span>
              {"\n    "}stop<span className="text-[#8DA89B]">:</span>{"  "}
              <span className="text-[#8DA89B]">()</span>{" "}
              <span className="text-[#8DA89B]">=&gt;</span> service.
              <span className="text-[#82CFAA]">teardown</span>
              <span className="text-[#8DA89B]">(),</span>
              {"\n  "}
              <span className="text-[#8DA89B]">{"}"}</span>
              {"\n"}
              <span className="text-[#8DA89B]">{"}"}</span>
            </pre>
          </div>
        </div>

        <div className="text-[12px] text-[#4A7862] mb-[36px] font-medium cursor-pointer inline-flex items-center gap-[5px] py-[4px] border-b border-transparent transition-colors hover:border-[#4A7862]">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <rect
              x="1.5"
              y="1.5"
              width="9"
              height="9"
              rx="1.5"
              stroke="currentColor"
              strokeWidth="1.2"
            />
            <path
              d="M4 4.5h4M4 6.5h4M4 8.5h2"
              stroke="currentColor"
              strokeWidth="1.1"
              strokeLinecap="round"
            />
          </svg>
          3 rules reference this file
        </div>

        <div className="flex justify-between pt-[28px] border-t border-[rgba(0,0,0,0.07)]">
          <a className="flex items-center gap-[6px] text-[12.5px] text-[#717975] font-medium transition-colors cursor-pointer hover:text-[#4A7862]">
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <path
                d="M8 2.5L4 6.5l4 4"
                stroke="currentColor"
                strokeWidth="1.3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>{" "}
            What it does
          </a>
          <a className="flex items-center gap-[6px] text-[12.5px] text-[#717975] font-medium transition-colors cursor-pointer hover:text-[#4A7862]">
            Stable environments{" "}
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <path
                d="M5 2.5l4 4-4 4"
                stroke="currentColor"
                strokeWidth="1.3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </a>
        </div>
      </div>
    </main>
  );
}
