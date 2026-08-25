#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "🔍 FORENSIC AUDIT: MISSING MODULE 'cv2'"
echo "=================================================="

echo -e "\n--- 1. Diagnostics: Checking Python Environment & Installed Packages ---"
pip list || true

echo -e "\n--- 2. Smoking-Gun Source Audit: cat -n requirements.txt ---"
if [ -f "requirements.txt" ]; then
    cat -n requirements.txt
else
    echo "⚠️ Warning: requirements.txt does not exist in the root directory."
fi

echo -e "\n--- 3. Automated Repair: Injecting OpenCV Dependency ---"
if [ -f "requirements.txt" ]; then
    if ! grep -qi "opencv-python" requirements.txt; then
        echo "opencv-python-headless" >> requirements.txt
        echo "✅ Added 'opencv-python-headless' to requirements.txt via automated script."
    else
        echo "ℹ️ OpenCV is already listed in requirements.txt."
    fi
else
    echo "opencv-python-headless" > requirements.txt
    echo "✅ Created requirements.txt with 'opencv-python-headless'."
fi

echo -e "\n--- 4. Installing Missing Dependencies ---"
pip install --no-cache-dir -r requirements.txt

echo -e "\n--- 5. Post-Repair Verification ---"
python3 -c "import cv2; print('✅ Verification successful! Imported OpenCV version:', cv2.__version__)"