"use client";
import { useState } from "react";
import ModalBase from "./ModalBase";
import { BRIEFINGS } from "../lib/demo-data";

interface Props { onClose: () => void; }

export default function BriefingModal({ onClose }: Props) {
  const [selected, setSelected] = useState(0);

  return (
    <ModalBase
      title="📱 Owner's Daily Briefing"
      subtitle="AI-generated SMS sent to the owner every morning at 6am"
      onClose={onClose}
      maxWidth="max-w-lg"
    >
      {/* Date selector */}
      <div className="px-6 pt-4 flex gap-2 flex-wrap">
        {BRIEFINGS.map((b, i) => (
          <button
            key={b.date}
            onClick={() => setSelected(i)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              i === selected
                ? "bg-navy-900 text-white"
                : "bg-navy-100 text-navy-600 hover:bg-navy-200"
            }`}
          >
            {b.date}
          </button>
        ))}
      </div>

      {/* Phone frame */}
      <div className="p-6">
        <div className="bg-[#f2f2f7] rounded-[36px] p-6 max-w-sm mx-auto shadow-xl" style={{ fontFamily: "-apple-system, BlinkMacSystemFont, sans-serif" }}>
          <div className="text-center mb-4">
            <div className="text-[13px] font-semibold text-gray-800">AI Ops Assistant</div>
            <div className="text-[11px] text-gray-400">Keystone Plumbing & Drain</div>
          </div>
          <div className="text-[11px] text-gray-400 text-right mb-1.5 pr-1">{BRIEFINGS[selected].date} · 6:00 AM</div>
          <div className="flex justify-end mb-1">
            <div className="bg-[#007aff] text-white rounded-[18px] rounded-br-[4px] px-4 py-3 max-w-[85%] text-[14px] leading-[1.55] whitespace-pre-wrap">
              {BRIEFINGS[selected].text}
            </div>
          </div>
          <div className="text-[11px] text-gray-400 text-right pr-1 mt-1">Delivered</div>
        </div>
      </div>

      {/* Footer note */}
      <div className="px-6 pb-6">
        <div className="bg-navy-50 rounded-xl p-4 text-sm text-navy-600">
          <strong className="text-navy-800">How it works:</strong> Every morning at 6am, Claude reads
          yesterday&apos;s revenue, today&apos;s schedule, overdue invoices, and unresponded reviews from
          Keystone&apos;s live data — then writes this message in plain English. No dashboard. No login.
        </div>
      </div>
    </ModalBase>
  );
}
