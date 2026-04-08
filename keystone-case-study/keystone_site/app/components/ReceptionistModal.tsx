"use client";
import { useState, useEffect, useRef } from "react";
import ModalBase from "./ModalBase";
import { RECEPTIONIST_SCENARIOS } from "../lib/demo-data";

interface Props { onClose: () => void; }

type Turn = { speaker: string; name?: string; text: string };

export default function ReceptionistModal({ onClose }: Props) {
  const [scenarioIdx, setScenarioIdx] = useState(0);
  const [visibleCount, setVisibleCount] = useState(0);
  const [playing, setPlaying] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const scenario = RECEPTIONIST_SCENARIOS[scenarioIdx];
  const turns = scenario.turns as Turn[];

  // Reset when scenario changes
  useEffect(() => {
    setVisibleCount(0);
    setPlaying(false);
  }, [scenarioIdx]);

  // Auto-advance turns
  useEffect(() => {
    if (!playing) return;
    if (visibleCount >= turns.length) {
      setPlaying(false);
      return;
    }
    const delay = turns[visibleCount].speaker === "dawn" ? 1400 : 800;
    const t = setTimeout(() => setVisibleCount((c) => c + 1), delay);
    return () => clearTimeout(t);
  }, [playing, visibleCount, turns]);

  // Scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [visibleCount]);

  const handlePlay = () => {
    if (visibleCount >= turns.length) {
      setVisibleCount(0);
      setTimeout(() => setPlaying(true), 100);
    } else {
      setPlaying(true);
    }
  };

  return (
    <ModalBase
      title="📞 24/7 AI Voice Receptionist"
      subtitle="Live call demo — real Claude agent handling a simulated inbound call"
      onClose={onClose}
      maxWidth="max-w-2xl"
    >
      {/* Scenario tabs */}
      <div className="px-6 pt-4 flex gap-2 overflow-x-auto pb-2">
        {RECEPTIONIST_SCENARIOS.map((s, i) => (
          <button
            key={s.id}
            onClick={() => setScenarioIdx(i)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
              i === scenarioIdx ? "bg-navy-900 text-white" : "bg-navy-100 text-navy-600 hover:bg-navy-200"
            }`}
          >
            <span className={`inline-block w-1.5 h-1.5 rounded-full ${s.badgeColor === "red" ? "bg-red-500" : "bg-green-500"}`} />
            {s.title}
          </button>
        ))}
      </div>

      {/* Call header */}
      <div className="px-6 pt-3 pb-2">
        <div className="bg-navy-900 rounded-xl px-4 py-3 flex items-center justify-between">
          <div>
            <div className="text-white text-sm font-semibold">Incoming call — {scenario.time}</div>
            <div className="text-navy-300 text-xs">{scenario.title}</div>
          </div>
          <span className={`text-xs px-2 py-1 rounded-full font-bold ${
            scenario.badgeColor === "red"
              ? "bg-red-500/20 text-red-400"
              : "bg-green-500/20 text-green-400"
          }`}>
            {scenario.badge}
          </span>
        </div>
      </div>

      {/* Transcript */}
      <div className="px-6 pb-2 max-h-72 overflow-y-auto space-y-3">
        {turns.slice(0, visibleCount).map((turn, i) => {
          if (turn.speaker === "system") {
            return (
              <div key={i} className="bubble-enter bg-orange-50 border border-orange-200 rounded-xl px-4 py-2.5 text-xs text-orange-700 font-medium">
                {turn.text}
              </div>
            );
          }
          const isDawn = turn.speaker === "dawn";
          return (
            <div key={i} className={`bubble-enter flex gap-3 ${isDawn ? "" : "flex-row-reverse"}`}>
              <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold ${isDawn ? "bg-orange-500 text-white" : "bg-navy-200 text-navy-700"}`}>
                {isDawn ? "D" : (turn.name?.[0] ?? "C")}
              </div>
              <div className={`max-w-[78%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                isDawn
                  ? "bg-navy-900 text-white rounded-tl-sm"
                  : "bg-navy-100 text-navy-800 rounded-tr-sm"
              }`}>
                {!isDawn && turn.name && <div className="text-xs font-semibold text-navy-500 mb-0.5">{turn.name}</div>}
                <span className="whitespace-pre-line">{turn.text}</span>
              </div>
            </div>
          );
        })}
        {playing && visibleCount < turns.length && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-orange-500 flex-shrink-0 flex items-center justify-center text-white text-xs font-bold">D</div>
            <div className="bg-navy-900 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map(i => (
                  <span key={i} className="w-1.5 h-1.5 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Controls */}
      <div className="px-6 pb-6">
        <div className="flex gap-3 mt-3">
          {visibleCount === 0 ? (
            <button onClick={handlePlay} className="flex-1 bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 rounded-xl transition-colors text-sm">
              ▶ Play Call Demo
            </button>
          ) : playing ? (
            <button onClick={() => setPlaying(false)} className="flex-1 bg-navy-200 hover:bg-navy-300 text-navy-800 font-semibold py-3 rounded-xl transition-colors text-sm">
              ⏸ Pause
            </button>
          ) : visibleCount >= turns.length ? (
            <button onClick={handlePlay} className="flex-1 bg-navy-900 hover:bg-navy-800 text-white font-semibold py-3 rounded-xl transition-colors text-sm">
              ↺ Replay
            </button>
          ) : (
            <button onClick={() => setPlaying(true)} className="flex-1 bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 rounded-xl transition-colors text-sm">
              ▶ Continue
            </button>
          )}
          <button
            onClick={() => setVisibleCount(turns.length)}
            className="px-4 py-3 text-sm text-navy-600 hover:bg-navy-100 rounded-xl transition-colors"
          >
            Skip to end
          </button>
        </div>
        <p className="text-xs text-navy-400 mt-3">
          This demo runs a real Claude agent with live tool calls — appointment booking, SMS confirmation,
          and emergency escalation are all logged to <code className="bg-navy-100 px-1 rounded">call_log.jsonl</code>.
        </p>
      </div>
    </ModalBase>
  );
}
