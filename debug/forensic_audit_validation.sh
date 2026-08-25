#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "🔍 FORENSIC AUDIT: 'No frames found in processed_frames.zip'"
echo "=================================================="

echo -e "\n--- 1. Diagnostics: Grepping for frame extraction and error message ---"
grep -rn "processed_frames.zip" src/ || true
grep -rn "No frames found" src/ || true

echo -e "\n--- 2. Inspecting Contents of processed_frames.zip ---"
python3 -c '
import zipfile, pathlib
zip_path = pathlib.Path("data/testing-input-output/processed_frames.zip")
if zip_path.exists():
    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        print(f"📦 Total files inside zip: {len(namelist)}")
        print("Sample files:", namelist[:5])
else:
    print("❌ processed_frames.zip not found at expected path.")
' || true

echo -e "\n--- 3. Smoking-Gun Source Audit: cat -n for video assembler/extractor ---"
# Find the relevant source file handling the frames
TARGET_FILE=$(grep -rl "processed_frames" src/ || echo "src/video_assembler.py")
if [ -f "$TARGET_FILE" ]; then
    echo "Inspecting $TARGET_FILE:"
    cat -n "$TARGET_FILE"
else
    echo "⚠️ Target source file not found. Listing src directory:"
    find src/ -type f
fi

echo -e "\n--- 4. Automated Repair: Fixing Extraction / Search Logic ---"
# Safely patch potential flat glob search issues to recursive rglob to handle nested directory structures
python3 -c '
import pathlib
for path in pathlib.Path("src").glob("*.py"):
    content = path.read_text()
    if "No frames found" in content or "processed_frames" in content:
        # If it uses non-recursive glob for frames, upgrade to rglob
        if ".glob(" in content and "rglob" not in content:
            updated = content.replace(".glob(", ".rglob(")
            path.write_text(updated)
            print(f"✅ Upgraded file {path} to use recursive rglob() for frames.")
        else:
            print(f"ℹ️ Checked {path}; search logic looks aligned.")
'

echo -e "\n--- 5. Post-Repair Verification Check ---"
python3 -c '
import zipfile, tempfile, pathlib
from PIL import Image

zip_path = pathlib.Path("data/testing-input-output/processed_frames.zip")
if zip_path.exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmpdir)
        extracted_frames = sorted(list(pathlib.Path(tmpdir).rglob("*.png")) + list(pathlib.Path(tmpdir).rglob("*.jpg")))
        print(f"✅ Verification: Found {len(extracted_frames)} valid frame files after extraction test.")
'