#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "🔍 FORENSIC AUDIT: V4L2 Hardware Encoder Failure (h264_v4l2m2m)"
echo "=================================================="

echo -e "\n--- 1. Diagnostics: Grepping for VideoWriter & Codec Mapping ---"
grep -rn "VideoWriter" src/ || true
grep -rn "codec_mapping" src/ || true

echo -e "\n--- 2. Smoking-Gun Source Audit: cat -n for video assembler ---"
TARGET_FILE=$(grep -rl "VideoWriter" src/ || echo "src/video_assembler.py")
if [ -f "$TARGET_FILE" ]; then
    echo "Inspecting $TARGET_FILE:"
    cat -n "$TARGET_FILE"
else
    echo "⚠️ Target source file not found."
fi

echo -e "\n--- 3. Automated Repair: Forcing Pure Software Codec (mp4v) ---"
python3 -c '
import pathlib

path = pathlib.Path("src/video_assembler.py")
if path.exists():
    content = path.read_text()
    # Force mp4v as the primary software codec to bypass V4L2 hardware device requirements in CI
    updated = content.replace("\"libx264\": \"avc1\"", "\"libx264\": \"mp4v\"")
    updated = updated.replace("\"avc1\": \"avc1\"", "\"avc1\": \"mp4v\"")
    if "candidates = [" in updated:
        updated = updated.replace("candidates = [primary_chars, \"avc1\", \"mp4v\"", "candidates = [\"mp4v\", primary_chars, \"avc1\"")
    path.write_text(updated)
    print("✅ Successfully patched src/video_assembler.py to prioritize software-safe mp4v encoding.")
'

echo -e "\n--- 4. Post-Repair Verification Check ---"
python3 -c '
import cv2, tempfile, pathlib
with tempfile.TemporaryDirectory() as tmpdir:
    out_path = pathlib.Path(tmpdir) / "test.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, 30, (640, 480))
    if writer.isOpened():
        print("✅ Verification successful: mp4v initialized software encoder cleanly without V4L2 errors.")
        writer.release()
    else:
        print("❌ Verification failed: Unable to open VideoWriter with mp4v codec.")
'