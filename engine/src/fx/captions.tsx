// Caption styles driven by word-level Whisper timestamps (tools/captions.py).
import React from "react";
import { useCurrentFrame, useVideoConfig, spring, random } from "remotion";
import { Ransom, PALETTE } from "./paper";

export type Word = { text: string; start: number; end: number };

/** group words into short punchy chunks (max n words, break on pauses/punctuation) */
export const chunk = (words: Word[], n = 3): Word[][] => {
  const out: Word[][] = [];
  let cur: Word[] = [];
  words.forEach((w, i) => {
    cur.push(w);
    const gap = words[i + 1] ? words[i + 1].start - w.end : 1;
    if (cur.length >= n || gap > 0.35 || /[.,!?]$/.test(w.text)) { out.push(cur); cur = []; }
  });
  if (cur.length) out.push(cur);
  return out;
};

const useActive = (words: Word[], n: number) => {
  const t = useCurrentFrame() / useVideoConfig().fps;
  const groups = chunk(words, n);
  const g = groups.find((gr) => t >= gr[0].start - 0.05 && t <= gr[gr.length - 1].end + 0.15);
  return { t, g };
};

/** Ransom-note captions: the hot word is cut out of magazine letters */
export const RansomCaptions: React.FC<{ words: Word[]; emphasis?: string[] }> = ({ words, emphasis = [] }) => {
  const { t, g } = useActive(words, 3);
  const { fps } = useVideoConfig();
  if (!g) return null;
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 18, justifyContent: "center", alignItems: "center", maxWidth: 980 }}>
      {g.map((w, i) => {
        const clean = w.text.replace(/[^\w']/g, "");
        const hot = emphasis.includes(clean.toLowerCase()) || clean.length >= 6;
        const on = t >= w.start;
        if (!on) return null;
        return hot
          ? <Ransom key={i} text={clean} size={92} delay={Math.round(w.start * fps)} seed={clean + i} stagger={1} />
          : <span key={i} style={{ fontFamily: "Archivo Black", fontSize: 76, color: PALETTE.black, background: PALETTE.white,
              padding: "4px 14px", transform: `rotate(${(random(clean) - 0.5) * 6}deg)`, boxShadow: "3px 4px 0 rgba(0,0,0,.2)" }}>{clean}</span>;
      })}
    </div>
  );
};

/** Big elegant single-word serif pops (the 'clone yourself' reel look) */
export const SerifPop: React.FC<{ words: Word[] }> = ({ words }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const w = words.find((x) => t >= x.start && t <= x.end + 0.1);
  if (!w) return null;
  const s = spring({ frame: frame - Math.round(w.start * fps), fps, config: { damping: 12, mass: 0.5 } });
  return (
    <div style={{ fontFamily: "Instrument Serif", fontSize: 150, color: "white", transform: `scale(${0.7 + 0.3 * s})`,
      textShadow: "0 6px 30px rgba(0,0,0,.45)", letterSpacing: -2 }}>{w.text.replace(/[^\w'’]/g, "").toLowerCase()}</div>
  );
};
