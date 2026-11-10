// "Paper Cut" talking-head template — collage on grid paper, ransom-note title,
// voice-reactive scribbles, cut-out sticker of the speaker, ransom captions.
import React from "react";
import { AbsoluteFill, OffthreadVideo, Video, staticFile, useCurrentFrame, spring, useVideoConfig, interpolate } from "remotion";
import { GridPaper, Ransom, TornPaper, Scribble, HandCircle, HandUnderline, XMark, Hatch, PALETTE } from "./fx/paper";
import { RansomCaptions, Word } from "./fx/captions";

export type PaperCutProps = {
  video: string;            // cut-out WebM with alpha (tools/cutout.py) in engine/public
  captions?: { words: Word[] };
  levels?: number[];
  title: [string, string, string]; // e.g. ["VOICE", "BUILT", "FROM NOTHING"]
  emphasis?: string[];
};

export const PaperCut: React.FC<PaperCutProps> = ({ video, captions, levels = [], title, emphasis = [] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - 6, fps, config: { damping: 14 } });
  const bob = Math.sin(frame / 18) * 6;
  const isWebm = video.endsWith(".webm");
  return (
    <AbsoluteFill>
      <GridPaper />
      {/* background collage */}
      <TornPaper x={-40} y={1230} w={360} h={330} color={PALETTE.pink} seed="pink" rotate={-3} />
      <TornPaper x={600} y={880} w={520} h={420} color={PALETTE.yellow} seed="yel" rotate={2}>
        <div style={{ position: "absolute", left: 50, top: 40 }}>
          <Scribble width={420} height={330} levels={levels} color={PALETTE.blue} peaks={14} strokeWidth={12} seed="y" />
        </div>
      </TornPaper>
      <Hatch x={720} y={1370} w={400} h={150} />
      <div style={{ position: "absolute", left: 40, top: 560 }}>
        <Scribble width={1000} height={380} levels={levels} peaks={32} seed="main" />
      </div>
      <XMark x={60} y={1240} seed="x1" size={60} /><XMark x={120} y={1290} seed="x2" size={60} /><XMark x={870} y={1260} seed="x3" size={60} />

      {/* title */}
      <div style={{ position: "absolute", left: 80, top: 190 }}>
        <div style={{ position: "relative" }}>
          <Ransom text={title[0]} size={150} delay={0} seed="t0" />
          <div style={{ position: "absolute", left: -50, top: -40, width: 660, height: 260 }}><HandCircle w={660} h={260} start={18} /></div>
        </div>
      </div>
      <div style={{ position: "absolute", right: 40, top: 430 }}><Ransom text={title[1]} size={92} delay={10} seed="t1" /></div>
      <div style={{ position: "absolute", left: 90, top: 640 }}>
        <Ransom text={title[2]} size={84} delay={16} seed="t2" />
        <div style={{ marginTop: 10 }}><HandUnderline w={760} start={34} /></div>
      </div>

      {/* speaker sticker */}
      <div style={{ position: "absolute", left: -20, bottom: 0, width: 920, height: 1100,
        transform: `translateY(${(1 - enter) * 900 + bob}px) rotate(${interpolate(enter, [0, 1], [-8, -1.5])}deg)`,
        filter: "drop-shadow(10px 14px 0 rgba(0,0,0,.18))" }}>
        {isWebm
          ? <Video src={staticFile(video)} transparent style={{ width: "100%", height: "100%", objectFit: "contain", objectPosition: "bottom" }} />
          : <OffthreadVideo src={staticFile(video)} style={{ width: "100%", height: "100%", objectFit: "contain", objectPosition: "bottom" }} />}
      </div>

      {captions && (
        <div style={{ position: "absolute", left: 0, right: 0, top: 1600, display: "flex", justifyContent: "center" }}>
          <RansomCaptions words={captions.words} emphasis={emphasis} />
        </div>
      )}
    </AbsoluteFill>
  );
};
