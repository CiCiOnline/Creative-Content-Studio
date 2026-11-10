import { Config } from "@remotion/cli/config";
Config.setEntryPoint("./src/index.ts");
Config.setBrowserExecutable(process.env.REMOTION_CHROME ?? "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell");
Config.setChromiumOpenGlRenderer("swangle");
