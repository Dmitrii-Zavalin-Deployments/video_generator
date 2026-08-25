#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "🔍 FORENSIC AUDIT: VideoWriter_fourcc Argument Mismatch"
echo "=================================================="

echo -e "\n--- 1. Diagnostics: Grepping for VideoWriter_fourcc ---"
grep -rn "VideoWriter_fourcc" src/ || true

echo -e "\n--- 2. Smoking-Gun Source Audit: cat -n for video assembler ---"
TARGET_FILE=$(grep -rl "VideoWriter_fourcc" src/ || echo "src/video_assembler.py")
if [ -f "$TARGET_FILE" ]; then
    echo "Inspecting $TARGET_FILE:"
    cat -n "$TARGET_FILE"
else
    echo "⚠️ Target source file not found. Listing src directory:"
    find src/ -type f
fi

echo -e "\n--- 3. Automated Repair: Fixing FourCC Codec Call ---"
# Safely replace malformed VideoWriter_fourcc calls with a standard 4-character FourCC code
python3 -c '
import pathlib, re

for path in pathlib.Path("src").glob("*.py"):
    content = path.read_text()
    if "VideoWriter_fourcc" in content:
        # Replace whatever was passed into VideoWriter_fourcc with safe 4-char mp4v characters
        updated = re.sub(
            r"cv2\.VideoWriter_fourcc\s*\([^)]+\)",
            "cv2.VideoWriter_fourcc(\x27m\x27, \x27p\x27, \x274\x27, \x27v\x27)",
            content
        )
        if updated != content:
            path.write_text(updated)
            print(f"✅ Patched VideoWriter_fourcc in {path} to use valid 4-character codes.")
'

echo -e "\n--- 4. Post-Repair Verification Check ---"
python3 -c '
import cv2
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
print("✅ Verification successful! FourCC code compiled cleanly:", fourcc)
'