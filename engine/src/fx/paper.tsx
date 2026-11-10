// Paper-cut / collage primitives: ransom-note letters, torn paper, scribbles,
// hand-drawn marks. Everything "boils" (re-jitters every few frames) for a
// stop-motion, handmade feel.
import React from "react";
import { useCurrentFrame, spring, useVideoConfig, interpolate, random } from "remotion";

export const PALETTE = {
  paper: "#f3efe6", grid: "rgba(60,90,140,0.13)", yellow: "#f2c230", blue: "#1f4fbf",
  red: "#d7262b", black: "#141414", white: "#fbfaf6", pink: "#f4b6c2", sky: "#8fa9d6",
};
const TILE_BG = [PALETTE.yellow, PALETTE.blue, PALETTE.white, PALETTE.black, PALETTE.red, "#d9d3c7"];
const FONTS = ["Abril Fatface", "Archivo Black", "DM Serif Display", "Anton", "Playfair Display", "Bebas Neue"];

/** frame bucket for stop-motion boil (8 fps feel at 30fps) */
export const useBoil = (every = 4) => Math.floor(useCurrentFrame() / every);

export const GridPaper: React.FC = () => (
  <div style={{
    position: "absolute", inset: 0, backgroundColor: PALETTE.paper,
    backgroundImage: `linear-gradient(${PALETTE.grid} 2px, transparent 2px), linear-gradient(90deg, ${PALETTE.grid} 2px, transparent 2px)`,
    backgroundSize: "54px 54px",
  }} />
);

/** Ransom-note word: every letter its own cut-out tile. */
export const Ransom: React.FC<{ text: string; size?: number; delay?: number; seed?: string; stagger?: number }> = ({
  text, size = 140, delay = 0, seed = "r", stagger = 2,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const boil = useBoil();
  return (
    <div style={{ display: "flex", gap: size * 0.04, alignItems: "center" }}>
      {text.split("").map((ch, i) => {
        if (ch === " ") return <div key={i} style={{ width: size * 0.35 }} />;
        const k = `${seed}-${i}`;
        const bg = TILE_BG[Math.floor(random(k + "bg") * TILE_BG.length)];
        const dark = bg === PALETTE.black || bg === PALETTE.blue || bg === PALETTE.red;
        const fg = dark ? (random(k + "fg") > 0.5 ? PALETTE.white : PALETTE.yellow) : (random(k + "fg") > 0.6 ? PALETTE.red : PALETTE.black);
        const s = spring({ frame: frame - delay - i * stagger, fps, config: { damping: 9, mass: 0.6 } });
        const rot = (random(k + "rot") - 0.5) * 12 + (random(`${k}${boil}`) - 0.5) * 2.5;
        const sc = 0.85 + random(k + "sc") * 0.3;
        return (
          <div key={i} style={{
            background: bg, color: fg, fontFamily: FONTS[Math.floor(random(k + "f") * FONTS.length)],
            fontSize: size * sc, lineHeight: 1, padding: `${size * 0.06}px ${size * 0.08}px`,
            transform: `rotate(${rot}deg) scale(${s}) translateY(${(random(k + "y") - 0.5) * size * 0.15}px)`,
            boxShadow: "3px 4px 0 rgba(0,0,0,0.18)", textTransform: random(k + "case") > 0.3 ? "uppercase" : "none",
            clipPath: `polygon(${random(k + "a") * 4}% 0, 100% ${random(k + "b") * 5}%, ${100 - random(k + "c") * 4}% 100%, 0 ${100 - random(k + "d") * 5}%)`,
          }}>{ch}</div>
        );
      })}
    </div>
  );
};

/** jagged torn-paper block */
export const TornPaper: React.FC<{ x: number; y: number; w: number; h: number; color: string; seed: string; rotate?: number; children?: React.ReactNode }> = ({
  x, y, w, h, color, seed, rotate = 0, children,
}) => {
  const pts: string[] = [];
  const teeth = 28;
  for (let i = 0; i <= teeth; i++) pts.push(`${(i / teeth) * 100}% ${random(seed + "t" + i) * 4}%`);
  for (let i = 0; i <= teeth; i++) pts.push(`${100 - random(seed + "r" + i) * 2}% ${(i / teeth) * 100}%`);
  for (let i = teeth; i >= 0; i--) pts.push(`${(i / teeth) * 100}% ${100 - random(seed + "b" + i) * 4}%`);
  for (let i = teeth; i >= 0; i--) pts.push(`${random(seed + "l" + i) * 2}% ${(i / teeth) * 100}%`);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, background: color,
      clipPath: `polygon(${pts.join(",")})`, transform: `rotate(${rotate}deg)`, overflow: "hidden" }}>{children}</div>
  );
};

/** zig-zag scribble "waveform"; amplitude follows the voice */
export const Scribble: React.FC<{ width: number; height: number; levels?: number[]; color?: string; peaks?: number; strokeWidth?: number; seed?: string }> = ({
  width, height, levels = [], color = PALETTE.sky, peaks = 34, strokeWidth = 14, seed = "s",
}) => {
  const frame = useCurrentFrame();
  const boil = useBoil(3);
  const pts: string[] = [];
  for (let i = 0; i <= peaks * 2; i++) {
    const lv = levels.length ? levels[Math.min(levels.length - 1, Math.max(0, frame - peaks + Math.floor(i / 2)))] ?? 0 : 0.8;
    const amp = 0.25 + 0.75 * lv;
    const up = i % 2 === 0;
    const jitter = (random(`${seed}${i}${boil}`) - 0.5) * 0.12;
    const yy = height / 2 + (up ? -1 : 1) * (height / 2) * Math.min(1, amp + jitter);
    pts.push(`${(i / (peaks * 2)) * width + (random(`${seed}x${i}${boil}`) - 0.5) * 8},${yy}`);
  }
  return (
    <svg width={width} height={height} style={{ overflow: "visible" }}>
      <polyline points={pts.join(" ")} fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinejoin="round" strokeLinecap="round" opacity={0.9} />
    </svg>
  );
};

/** hand-drawn ellipse that draws itself on */
export const HandCircle: React.FC<{ w: number; h: number; start?: number; color?: string }> = ({ w, h, start = 0, color = PALETTE.red }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - start, [0, 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const d = `M ${w * 0.55} ${h * 0.04} C ${w * 1.02} ${h * 0.02}, ${w * 1.04} ${h * 0.95}, ${w * 0.5} ${h * 0.97}
             C ${w * -0.03} ${h * 0.98}, ${w * -0.02} ${h * 0.08}, ${w * 0.45} ${h * 0.05} L ${w * 0.62} ${h * 0.09}`;
  return (
    <svg width={w} height={h} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
      <path d={d} fill="none" stroke={color} strokeWidth={7} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
    </svg>
  );
};

export const HandUnderline: React.FC<{ w: number; start?: number; color?: string }> = ({ w, start = 0, color = PALETTE.red }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - start, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <svg width={w} height={30} style={{ overflow: "visible", display: "block" }}>
      <path d={`M 4 18 Q ${w * 0.3} 8, ${w * 0.6} 14 T ${w - 4} 10`} fill="none" stroke={color} strokeWidth={7} strokeLinecap="round"
        pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
    </svg>
  );
};

export const XMark: React.FC<{ x: number; y: number; size?: number; seed: string }> = ({ x, y, size = 40, seed }) => {
  const boil = useBoil(5);
  const r = (random(seed + boil) - 0.5) * 16;
  return (
    <div style={{ position: "absolute", left: x, top: y, fontFamily: "Permanent Marker", fontSize: size, color: PALETTE.black, transform: `rotate(${r}deg)` }}>×</div>
  );
};

export const Hatch: React.FC<{ x: number; y: number; w: number; h: number; color?: string }> = ({ x, y, w, h, color = PALETTE.red }) => (
  <div style={{ position: "absolute", left: x, top: y, width: w, height: h,
    backgroundImage: `repeating-linear-gradient(100deg, ${color} 0 6px, transparent 6px 22px)` }} />
);
