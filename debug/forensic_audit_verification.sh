#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "=== [DIAGNOSTIC] Grep diagnostics for logging configuration ==="
echo "=================================================="
grep -n -C 5 "logging.basicConfig" src/main.py || true

echo ""
echo "=================================================="
echo "=== [AUDIT] Smoking-gun source audit (cat -n) ==="
echo "=================================================="
cat -n src/main.py

echo ""
echo "=================================================="
echo "=== [REPAIR] Applying fix for logging.basicConfig force=True ==="
echo "=================================================="
python3 - << 'EOF'
path = "src/main.py"
with open(path, "r") as f:
    content = f.read()

old_config = '''    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )'''

new_config = '''    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True
    )'''

if old_config in content:
    content = content.replace(old_config, new_config)
    with open(path, "w") as f:
        f.write(content)
    print("Successfully updated logging.basicConfig with force=True.")
else:
    import re
    content, count = re.subn(
        r'(logging\.basicConfig\([^)]+)(\))',
        r'\1, force=True\2',
        content,
        flags=re.DOTALL
    )
    if count > 0:
        with open(path, "w") as f:
            f.write(content)
        print(f"Successfully updated logging.basicConfig via regex (count: {count}).")
    else:
        raise RuntimeError("Could not locate logging.basicConfig target block in src/main.py.")
EOF