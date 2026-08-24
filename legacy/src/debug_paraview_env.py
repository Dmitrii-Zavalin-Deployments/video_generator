# src/debug_paraview_env.py

import sys
import os

print("🔍 Starting ParaView environment check...")

try:
    import paraview.simple as ps
except ImportError:
    print("❌ Error: Could not import paraview.simple. Is ParaView set up correctly?")
    sys.exit(1)

print("✅ paraview.simple imported successfully.")
print(f"📦 Module path: {ps.__file__}")

# Try detecting ParaView version if available
try:
    version = ps.ParaViewVersion()
    print(f"📄 ParaView version: {version}")
except AttributeError:
    print("⚠️ ParaViewVersion() not available.")

# Print summary of visible symbols for debug purposes
print("\n🧪 Sample attributes in paraview.simple:")
visible = [attr for attr in dir(ps) if not attr.startswith('_')]
for attr in sorted(visible)[:20]:
    print(f" - {attr}")
print("...")

print("✅ ParaView environment check complete.")



