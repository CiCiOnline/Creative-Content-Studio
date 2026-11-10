#!/usr/bin/env bash
# One-shot Paper Cut edit:  tools/papercut.sh INPUT.mp4 "WORD1" "WORD2" "WORD 3" [name]
# -> exports/<name>_papercut.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
IN="$1"; T1="$2"; T2="$3"; T3="$4"; NAME="${5:-$(basename "${IN%.*}")}"
P=engine/public/$NAME; mkdir -p "$P"
echo "1/4 cutout";   python3 tools/cutout.py  "$IN" "$P/cut.webm"     2>&1 | grep -E "^cutout" || true
echo "2/4 captions"; python3 tools/captions.py "$IN" "$P/captions.json" 2>&1 | grep -E "^captions"
echo "3/4 levels";   python3 tools/levels.py   "$IN" "$P/levels.json"
python3 - "$NAME" "$T1" "$T2" "$T3" > "$P/props.json" <<'EOF'
import json, sys
n, a, b, c = sys.argv[1:]
cap = json.load(open(f"engine/public/{n}/captions.json"))
print(json.dumps({"video": f"{n}/cut.webm", "title": [a, b, c], "captions": cap,
  "levels": json.load(open(f"engine/public/{n}/levels.json")), "emphasis": [],
  "seconds": cap["words"][-1]["end"] + 0.6 if cap["words"] else 5}))
EOF
echo "4/4 render"
cd engine && npx remotion render PaperCut "../exports/${NAME}_papercut.mp4" --props="public/$NAME/props.json" --concurrency=4 2>&1 | tail -1
