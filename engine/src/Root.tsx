import React from "react";
import { Composition, AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import "@fontsource/anton"; import "@fontsource/abril-fatface"; import "@fontsource/archivo-black";
import "@fontsource/dm-serif-display"; import "@fontsource/permanent-marker"; import "@fontsource/caveat";
import "@fontsource/bebas-neue"; import "@fontsource/playfair-display/900.css"; import "@fontsource/space-grotesk";
import "@fontsource/instrument-serif";
import { PaperCut, PaperCutProps } from "./PaperCut";
import { SerifPop, Word } from "./fx/captions";

const FPS = 30;
const lengthFrom = (p: { captions?: { words: Word[] }; seconds?: number }) =>
  Math.ceil(((p.seconds ?? (p.captions?.words.at(-1)?.end ?? 5) + 0.6)) * FPS);

/** Captions-only overlay for any finished talking-head video */
const SerifCaptioned: React.FC<{ video: string; captions: { words: Word[] } }> = ({ video, captions }) => (
  <AbsoluteFill style={{ background: "black" }}>
    <OffthreadVideo src={staticFile(video)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", top: 300 }}><SerifPop words={captions.words} /></AbsoluteFill>
  </AbsoluteFill>
);

export const Root: React.FC = () => (
  <>
    <Composition id="PaperCut" component={PaperCut as any} width={1080} height={1920} fps={FPS} durationInFrames={150}
      defaultProps={{ video: "demo_cut.webm", title: ["VOICE", "BUILT", "FROM NOTHING"], emphasis: ["outfit", "color"],
        captions: require("../public/demo_captions.json"), levels: require("../public/demo_levels.json"), seconds: 5 } as PaperCutProps & { seconds: number }}
      calculateMetadata={({ props }) => ({ durationInFrames: lengthFrom(props as any) })} />
    <Composition id="SerifCaptions" component={SerifCaptioned as any} width={1080} height={1920} fps={FPS} durationInFrames={150}
      defaultProps={{ video: "demo_in.mp4", captions: require("../public/demo_captions.json"), seconds: 5 } as any}
      calculateMetadata={({ props }) => ({ durationInFrames: lengthFrom(props as any) })} />
  </>
);
