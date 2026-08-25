#!/bin/bash
# ==============================================================================
# requirements.sh - Unified Environmental Provisioning
# ==============================================================================
set -e

echo "📦 Provisioning Runtime Core..."
pip install --no-cache-dir -r requirements.txt

echo "✅ Environment Ready."