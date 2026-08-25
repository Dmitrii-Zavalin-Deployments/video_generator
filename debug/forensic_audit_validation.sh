#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "🔍 FORENSIC AUDIT: V4L2 Hardware Encoder Failure"
echo "=================================================="

echo -e "\n--- 1. Diagnostics: Grepping for VideoWriter initialization in code ---"
grep -rn "cv2.VideoWriter" src/ || true

echo -e "\n--- 2. Smoking-Gun Source Audit: cat -n for video assembler ---"
TARGET_FILE=$(grep -rl "VideoWriter" src/ || echo "src/video_assembler.py")
if [ -f "$TARGET_FILE" ]; then
    echo "Inspecting $TARGET_FILE:"
    cat -n "$TARGET_FILE"
else
    echo "⚠️ Target source file not found."
fi

echo -e "\n--- 3. Automated Repair: Injecting Fallback Codec Loop ---"
# Patch src/video_assembler.py to cycle through software-safe FourCC codes if hardware/primary fails
python3 -c '
import pathlib, re

for path in pathlib.Path("src").glob("*.py"):
    content = path.read_text()
    if "cv2.VideoWriter(" in content and "fallback" not in content:
        # Replace single VideoWriter initialization with a robust fallback loop
        old_init_pattern = re.search(r"(fourcc\s*=\s*cv2\.VideoWriter_fourcc[^\n]+\n\s*out\s*=\s*cv2\.VideoWriter\([^)]+\))", content, re.DOTALL)
        if old_init_pattern:
            fallback_code = """
        # Robust fallback loop for containerized runners (GitHub Actions)
        out = None
        for candidate_codec in ["avc1", "mp4v", "XVID", "MJPG"]:
            try:
                fourcc = cv2.VideoWriter_fourcc(*candidate_codec)
                temp_out = cv2.VideoWriter(str(state.output_video_path), fourcc, fps, (width, height))
                if temp_out.isOpened():
                    out = temp_out
                    break
            except Exception:
                continue
        if out is None or not out.isOpened():
            raise RuntimeError("Failed to initialize OpenCV VideoWriter with any software-safe codec.")
            """
            updated = content.replace(old_init_pattern.group(1), fallback_code)
            path.write_text(updated)
            print(f"✅ Successfully injected fallback codec loop into {path}")
'

echo -e "\n--- 4. Post-Repair Verification Check ---"
python3 -c '
import cv2, pathlib, tempfile
with tempfile.TemporaryDirectory() as tmpdir:
    out_path = pathlib.Path(tmpdir) / "test.mp4"
    for codec in ["avc1", "mp4v", "XVID"]:
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(str(out_path), fourcc, 30, (640, 480))
        if writer.isOpened():
            print(f"✅ Verified fallback codec works in environment: {codec}")
            writer.release()
            break
'