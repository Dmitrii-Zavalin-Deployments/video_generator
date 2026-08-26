#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "=== [DIAGNOSTIC] Scanning for exc_info=True usages ==="
echo "=================================================="
grep -n -C 2 "exc_info=True" src/*.py || true

echo ""
echo "=================================================="
echo "=== [AUDIT] Smoking-gun source audit (cat -n) ==="
echo "=================================================="
cat -n src/frames_loader.py
cat -n src/main.py
cat -n src/state.py
cat -n src/video_assembler.py

echo ""
echo "=================================================="
echo "=== [REPAIR] Fixing G201: Using logger.exception ==="
echo "=================================================="

python3 - << 'EOF'
import glob
import re

for filepath in glob.glob("src/*.py"):
    with open(filepath, "r") as f:
        content = f.read()
    
    if "exc_info=True" in content:
        # Match logger.error(args..., exc_info=True) and convert to logger.exception(args...)
        new_content = re.sub(
            r'logger\.error\((.*?),\s*exc_info=True\)',
            r'logger.exception(\1)',
            content
        )
        if new_content != content:
            with open(filepath, "w") as f:
                f.write(new_content)
            print(f"Successfully converted logger.error to logger.exception in: {filepath}")
EOF