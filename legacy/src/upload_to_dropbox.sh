#!/bin/bash

# Dropbox credentials from GitHub Secrets
APP_KEY="${APP_KEY}"
APP_SECRET="${APP_SECRET}"
REFRESH_TOKEN="${REFRESH_TOKEN}"
DROPBOX_BASE_FOLDER="/simulators"

# Path to the zipped archive
ZIP_FILE="$GITHUB_WORKSPACE/data/testing-output-bundle.zip"

# Sanity check
if [ ! -f "$ZIP_FILE" ]; then
    echo "❌ ERROR: Archive not found at $ZIP_FILE"
    exit 1
fi

echo "📤 Uploading archive to Dropbox: $ZIP_FILE"

# Define Dropbox destination path
FILENAME=$(basename "$ZIP_FILE")
DROPBOX_DEST="${DROPBOX_BASE_FOLDER}/${FILENAME}"

# Upload via helper script
python3 src/upload_to_dropbox.py \
    "$ZIP_FILE" \
    "$DROPBOX_DEST" \
    "$REFRESH_TOKEN" \
    "$APP_KEY" \
    "$APP_SECRET"

if [ $? -eq 0 ]; then
    echo "✅ Archive uploaded successfully: $DROPBOX_DEST"
else
    echo "❌ Upload failed"
    exit 1
fi



