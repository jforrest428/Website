"use client";
import { useState } from "react";
import { Star, CheckCircle } from "lucide-react";
import ModalBase from "./ModalBase";
import { REVIEW_SAMPLES } from "../lib/demo-data";

interface Props { onClose: () => void; }

export default function ReviewModal({ onClose }: Props) {
  const [idx, setIdx] = useState(0);
  const [approved, setApproved] = useState<Set<string>>(new Set());
  const review = REVIEW_SAMPLES[idx];

  const isApproved = approved.has(review.id);

  return (
    <ModalBase
      title="⭐ Review Reply Manager"
      subtitle="AI-drafted replies — owner approves with one click"
      onClose={onClose}
      maxWidth="max-w-3xl"
    >
      {/* Tabs */}
      <div className="px-6 pt-4 flex gap-2 overflow-x-auto pb-2">
        {REVIEW_SAMPLES.map((r, i) => (
          <button
            key={r.id}
            onClick={() => setIdx(i)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
              i === idx ? "bg-navy-900 text-white" : "bg-navy-100 text-navy-600 hover:bg-navy-200"
            }`}
          >
            {"★".repeat(r.stars)}{"☆".repeat(5 - r.stars)} {r.platform}
          </button>
        ))}
      </div>

      <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left: Review */}
        <div className="bg-navy-50 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex gap-0.5">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star key={i} className={`w-4 h-4 ${i < review.stars ? "fill-orange-400 text-orange-400" : "fill-navy-200 text-navy-200"}`} />
              ))}
            </div>
            <span className="text-xs text-navy-400">{review.platform} · {review.date}</span>
          </div>
          {review.tech && (
            <div className="text-xs text-orange-600 font-medium mb-2">Tech mentioned: {review.tech}</div>
          )}
          <p className="text-sm text-navy-700 leading-relaxed italic">&ldquo;{review.review}&rdquo;</p>
        </div>

        {/* Right: Drafted reply */}
        <div className="flex flex-col">
          <div className="text-xs font-semibold text-navy-500 uppercase tracking-wide mb-2">AI-Drafted Reply</div>
          <textarea
            className="flex-1 text-sm text-navy-800 bg-white border border-navy-200 rounded-xl p-4 leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-orange-400 min-h-[160px]"
            defaultValue={review.drafted_reply}
          />
          <div className="flex gap-2 mt-3">
            {isApproved ? (
              <div className="flex items-center gap-2 text-green-600 text-sm font-medium">
                <CheckCircle className="w-4 h-4" /> Reply approved!
              </div>
            ) : (
              <>
                <button
                  onClick={() => { const s = new Set(Array.from(approved)); s.add(review.id); setApproved(s); }}
                  className="flex-1 bg-navy-900 hover:bg-navy-800 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors"
                >
                  ✅ Approve &amp; Post
                </button>
                <button
                  onClick={() => setIdx((idx + 1) % REVIEW_SAMPLES.length)}
                  className="px-4 py-2.5 text-sm text-navy-600 hover:bg-navy-100 rounded-lg transition-colors"
                >
                  Skip →
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="px-6 pb-6">
        <div className="bg-navy-50 rounded-xl p-4 text-sm text-navy-600">
          <strong className="text-navy-800">Pattern alert:</strong> David Chen has 3 negative review
          mentions in the last 90 days. The Tech Coaching Report has been flagged for the owner.
        </div>
      </div>
    </ModalBase>
  );
}
