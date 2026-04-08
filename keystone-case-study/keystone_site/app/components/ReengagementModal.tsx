"use client";
import { useState } from "react";
import ModalBase from "./ModalBase";
import { REENGAGEMENT_SEGMENTS } from "../lib/demo-data";

interface Props { onClose: () => void; }

export default function ReengagementModal({ onClose }: Props) {
  const [seg, setSeg] = useState(0);
  const segment = REENGAGEMENT_SEGMENTS[seg];
  const totalProjected = REENGAGEMENT_SEGMENTS.reduce((s, r) => s + r.projected_revenue, 0);

  return (
    <ModalBase
      title="💬 Re-Engagement Engine"
      subtitle="Weekly segmentation + AI-written outreach for dormant customers"
      onClose={onClose}
      maxWidth="max-w-3xl"
    >
      {/* Revenue summary */}
      <div className="px-6 pt-5">
        <div className="grid grid-cols-3 gap-3 mb-5">
          <div className="bg-navy-900 text-white rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{REENGAGEMENT_SEGMENTS.reduce((s, r) => s + r.customers, 0)}</div>
            <div className="text-xs text-navy-300 mt-1">Dormant Customers</div>
          </div>
          <div className="bg-orange-500 text-white rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">${totalProjected.toLocaleString()}</div>
            <div className="text-xs text-orange-100 mt-1">Projected Recovery</div>
          </div>
          <div className="bg-navy-50 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-navy-900">12%</div>
            <div className="text-xs text-navy-400 mt-1">Avg Reactivation Rate</div>
          </div>
        </div>

        {/* Segment tabs */}
        <div className="flex gap-2 flex-wrap mb-4">
          {REENGAGEMENT_SEGMENTS.map((s, i) => (
            <button
              key={s.name}
              onClick={() => setSeg(i)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                i === seg ? "bg-navy-900 text-white" : "bg-navy-100 text-navy-600 hover:bg-navy-200"
              }`}
            >
              {s.icon} {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Segment detail */}
      <div className="px-6 pb-6">
        <div className="bg-navy-50 rounded-xl p-4 mb-4">
          <div className="flex items-center justify-between mb-1">
            <span className="font-semibold text-navy-900">{segment.icon} {segment.label}</span>
            <span className="text-xs bg-orange-100 text-orange-700 rounded-full px-2 py-0.5 font-medium">
              ${segment.projected_revenue.toLocaleString()} projected
            </span>
          </div>
          <div className="text-xs text-navy-500">
            {segment.customers} customers · {segment.reactivation_rate}% reactivation · ${segment.avg_job.toLocaleString()} avg job
          </div>
        </div>

        {/* Sample customer */}
        <div className="border border-navy-200 rounded-xl overflow-hidden">
          <div className="bg-navy-100 px-4 py-2 text-xs font-semibold text-navy-600 uppercase tracking-wide">
            Sample: {segment.sample.customer} — last service {segment.sample.last_service} ({segment.sample.months_since} months ago)
          </div>
          <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* SMS */}
            <div>
              <div className="text-xs font-semibold text-navy-500 uppercase tracking-wide mb-2">📱 SMS Draft</div>
              <div className="bg-[#007aff] text-white rounded-2xl rounded-bl-sm px-4 py-3 text-[13px] leading-relaxed">
                {segment.sample.sms}
              </div>
              <div className="text-xs text-navy-400 mt-1">{segment.sample.sms.length}/160 chars</div>
            </div>
            {/* Email */}
            <div>
              <div className="text-xs font-semibold text-navy-500 uppercase tracking-wide mb-2">📧 Email Draft</div>
              <div className="bg-white border border-navy-200 rounded-xl p-3">
                <div className="text-xs font-medium text-navy-700 border-b border-navy-100 pb-2 mb-2">
                  Subject: {segment.sample.email_subject}
                </div>
                <div className="text-xs text-navy-600 leading-relaxed whitespace-pre-line line-clamp-6">
                  {segment.sample.email_body}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ModalBase>
  );
}
