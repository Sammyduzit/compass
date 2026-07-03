import React, { useState } from "react";
import { clsx } from "clsx";

export function ChatSection() {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={clsx(
        "shrink-0 bg-[#FFFFFF] border-t border-[rgba(0,0,0,0.07)] shadow-[0_-2px_12px_rgba(0,0,0,0.03)] flex flex-col overflow-hidden transition-[height] duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] relative left-1/2 right-1/2 -ml-[50vw] -mr-[50vw] w-[100vw] font-['Public_Sans',_sans-serif]",
        expanded ? "h-[52vh]" : "h-[44px]",
      )}
    >
      <div className="h-[44px] min-h-[44px] flex items-center px-[24px] shrink-0 max-w-[1440px] mx-auto w-full">
        <div className="flex-1 flex items-center">
          <span className="font-['JetBrains_Mono',_monospace] text-[10.5px] text-[#A0A8A4] bg-[#FDFCFB] border border-[rgba(0,0,0,0.07)] rounded-[4px] px-[6px] py-[2px]">
            ⌘K
          </span>
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-[8px] px-[14px] py-[6px] rounded-[8px] border border-[rgba(0,0,0,0.07)] bg-[#FDFCFB] cursor-pointer transition-all hover:bg-[#FFFFFF] hover:border-[#4A7862] hover:shadow-[0_0_0_3px_#EBF3EE] w-[216px] shrink-0 group"
        >
          <div className="w-[22px] h-[22px] bg-[#4A7862] rounded-[5px] flex items-center justify-center shrink-0">
            <svg
              width="13"
              height="13"
              viewBox="0 0 13 13"
              fill="none"
            >
              <circle
                cx="6.5"
                cy="6.5"
                r="4"
                stroke="white"
                strokeWidth="1.5"
              />
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
          <span className="text-[13px] text-[#A0A8A4] whitespace-nowrap transition-colors group-hover:text-[#717975]">
            Ask Compass
          </span>
          <svg
            viewBox="0 0 10 10"
            fill="none"
            className={clsx(
              "w-[10px] h-[10px] text-[#A0A8A4] shrink-0 transition-transform duration-250 ml-auto",
              !expanded && "rotate-180",
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

        <div className="flex-1 flex items-center justify-end">
          <button
            className="w-[26px] h-[26px] rounded-[5px] border border-[rgba(0,0,0,0.07)] bg-transparent flex items-center justify-center text-[#A0A8A4] opacity-35 cursor-default"
            disabled
          >
            <svg
              viewBox="0 0 15 15"
              fill="none"
              width="13"
              height="13"
            >
              <path
                d="M7.5 2v11M2 7.5h11"
                stroke="currentColor"
                strokeWidth="1.4"
                strokeLinecap="round"
              />
            </svg>
          </button>
        </div>
      </div>

      <div
        className={clsx(
          "flex-1 min-h-0 grid grid-cols-1 md:grid-cols-2 grid-rows-1 border-t border-[rgba(0,0,0,0.07)] overflow-hidden transition-opacity duration-200 delay-75",
          expanded ? "opacity-100" : "opacity-0",
        )}
      >
        {/* Left: Chat Thread */}
        <div className="flex flex-col min-h-0 overflow-hidden border-r border-[rgba(0,0,0,0.07)]">
          <div className="flex-1 overflow-y-auto px-[20px] py-[14px] flex flex-col gap-[12px]">
            <div className="flex flex-col gap-[3px] max-w-[88%] self-end items-end">
              <span className="text-[9.5px] font-bold tracking-[0.08em] uppercase text-[#4A7862] font-['JetBrains_Mono',_monospace]">
                You
              </span>
              <div className="px-[12px] py-[8px] rounded-[7px] text-[13px] leading-[1.6] bg-[#EBF3EE] border border-[rgba(74,120,98,0.2)] text-[#3A6252]">
                Why factory functions instead of a DI container?
              </div>
            </div>

            <div className="flex flex-col gap-[3px] max-w-[88%] self-start items-start">
              <span className="text-[9.5px] font-bold tracking-[0.08em] uppercase text-[#A0A8A4] font-['JetBrains_Mono',_monospace]">
                Compass
              </span>
              <div className="px-[12px] py-[8px] rounded-[7px] text-[13px] leading-[1.6] bg-[#FDFCFB] border border-[rgba(0,0,0,0.07)] text-[#3A3D3B]">
                This codebase keeps the dependency graph
                explicit by design. With factories, every
                dependency is a function argument — you can
                trace the full wiring by reading{" "}
                <code className="font-['JetBrains_Mono',_monospace] text-[11px] bg-[rgba(0,0,0,0.05)] px-[4px] py-[1px] rounded-[2px] text-[#3A6252]">
                  make-app.ts
                </code>{" "}
                top to bottom. Containers require understanding
                their annotation system before understanding the
                app. Rule <code>DI-01</code> formalises this.
              </div>
            </div>

            <div className="flex flex-col gap-[3px] max-w-[88%] self-end items-end">
              <span className="text-[9.5px] font-bold tracking-[0.08em] uppercase text-[#4A7862] font-['JetBrains_Mono',_monospace]">
                You
              </span>
              <div className="px-[12px] py-[8px] rounded-[7px] text-[13px] leading-[1.6] bg-[#EBF3EE] border border-[rgba(74,120,98,0.2)] text-[#3A6252]">
                Can you show what extracting the Redis wiring
                into its own factory would look like?
              </div>
            </div>

            <div className="flex flex-col gap-[3px] max-w-[88%] self-start items-start">
              <span className="text-[9.5px] font-bold tracking-[0.08em] uppercase text-[#A0A8A4] font-['JetBrains_Mono',_monospace]">
                Compass
              </span>
              <div className="flex gap-[4px] items-center px-[12px] py-[10px] bg-[#FDFCFB] border border-[rgba(0,0,0,0.07)] rounded-[7px] w-fit">
                <div className="w-[5px] h-[5px] rounded-full bg-[#A0A8A4] animate-pulse" />
                <div className="w-[5px] h-[5px] rounded-full bg-[#A0A8A4] animate-pulse delay-200" />
                <div className="w-[5px] h-[5px] rounded-full bg-[#A0A8A4] animate-pulse delay-400" />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-[8px] px-[16px] py-[9px] border-t border-[rgba(0,0,0,0.07)] bg-[#FFFFFF]">
            <input
              type="text"
              placeholder="Ask a follow-up…"
              className="flex-1 text-[13px] font-['Public_Sans',_sans-serif] text-[#1A1C1B] border border-[rgba(0,0,0,0.07)] rounded-[6px] px-[11px] py-[7px] bg-[#FDFCFB] outline-none transition-colors focus:border-[#4A7862] placeholder:text-[#A0A8A4]"
            />
            <button className="w-[30px] h-[30px] bg-[#4A7862] border-none rounded-[6px] flex items-center justify-center cursor-pointer shrink-0 transition-colors hover:bg-[#3A6252]">
              <svg
                viewBox="0 0 13 13"
                fill="none"
                className="w-[13px] h-[13px]"
              >
                <path
                  d="M2 6.5h9M8 3l3.5 3.5L8 10"
                  stroke="white"
                  strokeWidth="1.4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Right: Output Panel */}
        <div className="hidden md:flex flex-col min-h-0 overflow-hidden bg-[#FDFCFB]">
          <div className="flex items-center justify-between px-[16px] py-[9px] border-b border-[rgba(0,0,0,0.07)] bg-[#FFFFFF] shrink-0">
            <span className="text-[9.5px] font-bold tracking-[0.1em] uppercase text-[#A0A8A4] font-['JetBrains_Mono',_monospace]">
              Output
            </span>
            <div className="flex gap-[2px]">
              <button className="text-[11px] font-semibold px-[8px] py-[3px] rounded-[4px] font-['JetBrains_Mono',_monospace] transition-colors border-none bg-[#EBF3EE] text-[#4A7862]">
                Diff
              </button>
              <button className="text-[11px] font-medium px-[8px] py-[3px] rounded-[4px] font-['JetBrains_Mono',_monospace] transition-colors border-none bg-transparent text-[#A0A8A4] hover:bg-[#FDFCFB] hover:text-[#717975]">
                Diagram
              </button>
              <button className="text-[11px] font-medium px-[8px] py-[3px] rounded-[4px] font-['JetBrains_Mono',_monospace] transition-colors border-none bg-transparent text-[#A0A8A4] hover:bg-[#FDFCFB] hover:text-[#717975]">
                Canvas
              </button>
              <div className="w-[1px] h-[12px] bg-[rgba(0,0,0,0.07)] mx-[4px] my-auto" />
              <button
                className="flex items-center justify-center w-[22px] h-[22px] p-0 text-[#A0A8A4] bg-transparent border-none"
                title="Share output"
              >
                <svg
                  viewBox="0 0 12 12"
                  fill="none"
                  width="11"
                  height="11"
                >
                  <circle
                    cx="9.5"
                    cy="2.5"
                    r="1.5"
                    stroke="currentColor"
                    strokeWidth="1.1"
                  />
                  <circle
                    cx="9.5"
                    cy="9.5"
                    r="1.5"
                    stroke="currentColor"
                    strokeWidth="1.1"
                  />
                  <circle
                    cx="2.5"
                    cy="6"
                    r="1.5"
                    stroke="currentColor"
                    strokeWidth="1.1"
                  />
                  <path
                    d="M4 6l4.1-3M4 6l4.1 3.1"
                    stroke="currentColor"
                    strokeWidth="1.1"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </div>
          </div>

          <div className="flex-1 min-h-0 overflow-y-auto p-[12px] flex flex-col">
            <div className="bg-[#1E2329] rounded-[6px] overflow-hidden text-[11.5px] flex-1 flex flex-col">
              <div className="flex items-center justify-between px-[14px] py-[8px] bg-[#2D3741] border-b border-[rgba(255,255,255,0.06)] shrink-0">
                <span className="font-['JetBrains_Mono',_monospace] text-[10px] text-[rgba(255,255,255,0.45)]">
                  src/make-app.ts — suggested refactor
                </span>
                <span className="font-['JetBrains_Mono',_monospace] text-[9px] font-semibold bg-[rgba(74,120,98,0.3)] text-[#82CFAA] rounded-[3px] px-[6px] py-[1px]">
                  +8 / −3
                </span>
              </div>
              <div className="p-[14px] font-['JetBrains_Mono',_monospace] text-[11.5px] leading-[1.65] text-[#CDD5D0] flex-1 overflow-y-auto">
                <pre className="m-0">
                  <span className="text-[#89B4A0]">import</span>{" "}
                  <span className="text-[#8DA89B]">{"{"}</span>{" "}
                  AppConfig{" "}
                  <span className="text-[#8DA89B]">{"}"}</span>{" "}
                  <span className="text-[#89B4A0]">from</span>{" "}
                  <span className="text-[#C3A67A]">
                    './config/env'
                  </span>
                  {"\n"}
                  <span className="text-[#89B4A0]">
                    import
                  </span>{" "}
                  <span className="text-[#8DA89B]">{"{"}</span>{" "}
                  makePostgresAdapter{" "}
                  <span className="text-[#8DA89B]">{"}"}</span>{" "}
                  <span className="text-[#89B4A0]">from</span>{" "}
                  <span className="text-[#C3A67A]">
                    './infra/postgres-adapter'
                  </span>
                  {"\n"}
                  <span className="block mx-[-14px] px-[14px] bg-[rgba(74,120,98,0.15)] text-[#82CFAA]">
                    <span className="text-[#89B4A0]">
                      import
                    </span>{" "}
                    <span className="text-[#8DA89B]">
                      {"{"}
                    </span>{" "}
                    makeRedisAdapter{" "}
                    <span className="text-[#8DA89B]">
                      {"}"}
                    </span>{" "}
                    <span className="text-[#89B4A0]">from</span>{" "}
                    <span className="text-[#C3A67A]">
                      './infra/redis-adapter'
                    </span>
                  </span>
                  <span className="text-[#89B4A0]">import</span>{" "}
                  <span className="text-[#8DA89B]">{"{"}</span>{" "}
                  makeDomainService{" "}
                  <span className="text-[#8DA89B]">{"}"}</span>{" "}
                  <span className="text-[#89B4A0]">from</span>{" "}
                  <span className="text-[#C3A67A]">
                    './domain/core'
                  </span>
                  {"\n\n"}
                  <span className="block mx-[-14px] px-[14px] bg-[rgba(74,120,98,0.15)] text-[#82CFAA]">
                    <span className="text-[#89B4A0]">
                      function
                    </span>{" "}
                    <span className="text-[#82CFAA]">
                      makeInfra
                    </span>
                    <span className="text-[#8DA89B]">(</span>
                    config
                    <span className="text-[#8DA89B]">:</span>{" "}
                    <span className="text-[#9EC6B3]">
                      AppConfig
                    </span>
                    <span className="text-[#8DA89B]">
                      ) {"{"}
                    </span>
                  </span>
                  <span className="block mx-[-14px] px-[14px] bg-[rgba(74,120,98,0.15)] text-[#82CFAA]">
                    {"  "}
                    <span className="text-[#89B4A0]">
                      return
                    </span>{" "}
                    <span className="text-[#8DA89B]">
                      {"{"}
                    </span>{" "}
                    db<span className="text-[#8DA89B]">:</span>{" "}
                    <span className="text-[#82CFAA]">
                      makePostgresAdapter
                    </span>
                    <span className="text-[#8DA89B]">(</span>
                    config.db
                    <span className="text-[#8DA89B]">),</span>{" "}
                    cache
                    <span className="text-[#8DA89B]">:</span>{" "}
                    <span className="text-[#82CFAA]">
                      makeRedisAdapter
                    </span>
                    <span className="text-[#8DA89B]">(</span>
                    config.redis
                    <span className="text-[#8DA89B]">
                      ) {"}"}
                    </span>
                  </span>
                  <span className="block mx-[-14px] px-[14px] bg-[rgba(74,120,98,0.15)] text-[#82CFAA]">
                    <span className="text-[#8DA89B]">
                      {"}"}
                    </span>
                  </span>
                  {"\n"}
                  <span className="text-[#89B4A0]">
                    export function
                  </span>{" "}
                  <span className="text-[#82CFAA]">
                    makeApp
                  </span>
                  <span className="text-[#8DA89B]">(</span>
                  config
                  <span className="text-[#8DA89B]">:</span>{" "}
                  <span className="text-[#9EC6B3]">
                    AppConfig
                  </span>
                  <span className="text-[#8DA89B]">
                    ) {"{"}
                  </span>
                  {"\n"}
                  <span className="block mx-[-14px] px-[14px] bg-[rgba(180,60,60,0.12)] text-[#CF8F8F] line-through opacity-70">
                    {"  "}
                    <span className="text-[#89B4A0]">
                      const
                    </span>{" "}
                    db <span className="text-[#8DA89B]">=</span>{" "}
                    <span className="text-[#82CFAA]">
                      makePostgresAdapter
                    </span>
                    <span className="text-[#8DA89B]">(</span>
                    config.db
                    <span className="text-[#8DA89B]">)</span>
                  </span>
                  <span className="block mx-[-14px] px-[14px] bg-[rgba(180,60,60,0.12)] text-[#CF8F8F] line-through opacity-70">
                    {"  "}
                    <span className="text-[#89B4A0]">
                      const
                    </span>{" "}
                    cache{" "}
                    <span className="text-[#8DA89B]">=</span>{" "}
                    <span className="text-[#82CFAA]">
                      makeRedisAdapter
                    </span>
                    <span className="text-[#8DA89B]">(</span>
                    config.redis
                    <span className="text-[#8DA89B]">)</span>
                  </span>
                  <span className="block mx-[-14px] px-[14px] bg-[rgba(74,120,98,0.15)] text-[#82CFAA]">
                    {"  "}
                    <span className="text-[#89B4A0]">
                      const
                    </span>{" "}
                    infra{" "}
                    <span className="text-[#8DA89B]">=</span>{" "}
                    <span className="text-[#82CFAA]">
                      makeInfra
                    </span>
                    <span className="text-[#8DA89B]">(</span>
                    config
                    <span className="text-[#8DA89B]">)</span>
                  </span>
                  {"  "}
                  <span className="text-[#89B4A0]">
                    const
                  </span>{" "}
                  service{" "}
                  <span className="text-[#8DA89B]">=</span>{" "}
                  <span className="text-[#82CFAA]">
                    makeDomainService
                  </span>
                  <span className="text-[#8DA89B]">(</span>infra
                  <span className="text-[#8DA89B]">)</span>
                  {"\n"}
                  {"  "}
                  <span className="text-[#89B4A0]">
                    return
                  </span>{" "}
                  <span className="text-[#8DA89B]">{"{"}</span>{" "}
                  start<span className="text-[#8DA89B]">:</span>{" "}
                  <span className="text-[#8DA89B]">()</span>{" "}
                  <span className="text-[#8DA89B]">=&gt;</span>{" "}
                  service.
                  <span className="text-[#82CFAA]">init</span>
                  <span className="text-[#8DA89B]">
                    (),
                  </span>{" "}
                  stop<span className="text-[#8DA89B]">:</span>{" "}
                  <span className="text-[#8DA89B]">()</span>{" "}
                  <span className="text-[#8DA89B]">=&gt;</span>{" "}
                  service.
                  <span className="text-[#82CFAA]">
                    teardown
                  </span>
                  <span className="text-[#8DA89B]">
                    () {"}"}
                  </span>
                  {"\n"}
                  <span className="text-[#8DA89B]">{"}"}</span>
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}