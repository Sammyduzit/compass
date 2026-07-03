import React from "react";
import { clsx } from "clsx";

interface StripItemProps {
  label: string;
  icon: React.ReactNode;
  isActive?: boolean;
  isDone?: boolean;
  title: string;
}

function StripItem({ label, icon, isActive, isDone, title }: StripItemProps) {
  return (
    <div className="flex flex-col items-center gap-[4px]">
      <button
        title={title}
        className={clsx(
          "relative w-[36px] h-[36px] rounded-[7px] flex items-center justify-center cursor-pointer transition-all border-none",
          isActive
            ? "text-[#4A7862] bg-[#EBF3EE]"
            : "text-[#A0A8A4] bg-transparent hover:bg-[#F8F8F7] hover:text-[#717975]"
        )}
      >
        {isActive && (
          <div className="absolute -left-[6px] top-[6px] bottom-[6px] w-[3px] bg-[#4A7862] rounded-r-[2px]" />
        )}
        {isDone && (
          <div className="absolute top-[3px] right-[3px] w-[9px] h-[9px] rounded-full bg-[#4A7862] flex items-center justify-center">
            <svg viewBox="0 0 6 6" fill="none" className="w-[6px] h-[6px]">
              <polyline
                points="1,3 2.5,4.5 5,1.5"
                stroke="white"
                strokeWidth="1.1"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        )}
        <div className="w-[17px] h-[17px] flex items-center justify-center">{icon}</div>
      </button>
      <span
        className={clsx(
          "text-[8.5px] font-semibold tracking-[0.04em] uppercase leading-none",
          isActive ? "text-[#4A7862]" : "text-[#A0A8A4]"
        )}
      >
        {label}
      </span>
    </div>
  );
}

export function NavStrip() {
  return (
    <nav className="hidden sm:flex w-[52px] bg-[#FFFFFF] border-r border-[rgba(0,0,0,0.07)] flex-col items-center py-[12px] gap-[4px] shrink-0 font-['Public_Sans',_sans-serif]">
      <StripItem
        title="What it does"
        label="What"
        isDone
        icon={
          <svg viewBox="0 0 17 17" fill="none" className="w-full h-full">
            <circle cx="8.5" cy="8.5" r="6" stroke="currentColor" strokeWidth="1.3" />
            <path
              d="M8.5 7.5v4M8.5 6v.5"
              stroke="currentColor"
              strokeWidth="1.3"
              strokeLinecap="round"
            />
          </svg>
        }
      />
      <StripItem
        title="Start here"
        label="Start"
        isActive
        icon={
          <svg viewBox="0 0 17 17" fill="none" className="w-full h-full">
            <path
              d="M8.5 2L10 6.2L14.5 6.7L11.3 9.7L12.2 14.5L8.5 12.3L4.8 14.5L5.7 9.7L2.5 6.7L7 6.2L8.5 2Z"
              stroke="currentColor"
              strokeWidth="1.3"
              strokeLinejoin="round"
            />
          </svg>
        }
      />
      <StripItem
        title="Stable"
        label="Stable"
        icon={
          <svg viewBox="0 0 17 17" fill="none" className="w-full h-full">
            <path
              d="M8.5 2L13.5 5V12L8.5 15L3.5 12V5L8.5 2Z"
              stroke="currentColor"
              strokeWidth="1.3"
              strokeLinejoin="round"
            />
            <path
              d="M6 8.5L7.5 10L11 7"
              stroke="currentColor"
              strokeWidth="1.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        }
      />
      <StripItem
        title="Hotspots"
        label="Hot"
        icon={
          <svg viewBox="0 0 17 17" fill="none" className="w-full h-full">
            <path
              d="M8.5 14C6 12 4 10.2 4 7.8a4.5 4.5 0 019 0C13 10.2 11 12 8.5 14z"
              stroke="currentColor"
              strokeWidth="1.3"
              strokeLinejoin="round"
            />
            <circle cx="8.5" cy="8" r="1.4" fill="currentColor" />
          </svg>
        }
      />
      <StripItem
        title="Rule clusters"
        label="Rules"
        icon={
          <svg viewBox="0 0 17 17" fill="none" className="w-full h-full">
            <circle cx="8.5" cy="8.5" r="2" stroke="currentColor" strokeWidth="1.2" />
            <circle cx="3.5" cy="4.5" r="1.4" stroke="currentColor" strokeWidth="1.1" />
            <circle cx="13.5" cy="4.5" r="1.4" stroke="currentColor" strokeWidth="1.1" />
            <circle cx="3.5" cy="12.5" r="1.4" stroke="currentColor" strokeWidth="1.1" />
            <circle cx="13.5" cy="12.5" r="1.4" stroke="currentColor" strokeWidth="1.1" />
            <line x1="5.3" y1="6" x2="6.8" y2="7" stroke="currentColor" strokeWidth="1" />
            <line x1="10.2" y1="7" x2="11.7" y2="6" stroke="currentColor" strokeWidth="1" />
            <line x1="5.3" y1="11" x2="6.8" y2="10" stroke="currentColor" strokeWidth="1" />
            <line x1="10.2" y1="10" x2="11.7" y2="11" stroke="currentColor" strokeWidth="1" />
          </svg>
        }
      />

      <div className="flex-1" />

      <div className="w-full h-[1px] bg-[rgba(0,0,0,0.06)] my-[8px]" />

      <StripItem
        title="Settings"
        label="Config"
        icon={
          <svg viewBox="0 0 17 17" fill="none" className="w-full h-full">
            <circle cx="8.5" cy="8.5" r="2.2" stroke="currentColor" strokeWidth="1.2" />
            <path
              d="M8.5 2v1.1M8.5 13.9V15M2 8.5h1.1M13.9 8.5H15M3.9 3.9l.8.8M12.3 12.3l.8.8M13.1 3.9l-.8.8M4.7 12.3l-.8.8"
              stroke="currentColor"
              strokeWidth="1.2"
              strokeLinecap="round"
            />
          </svg>
        }
      />
    </nav>
  );
}
