#!/bin/bash

echo "📽️ Starting video creation with FFmpeg..."

# Define paths
OUTPUT_FOLDER="./RenderedOutput"
VIDEO_FILE="${OUTPUT_FOLDER}/video.mp4"

# Ensure FFmpeg is installed (skipping sudo for CI/CD environments)
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ Error: FFmpeg is not installed! Installing..."
    apt update && apt install -y ffmpeg
fi

# Check if rendered frames exist
if ls ${OUTPUT_FOLDER}/frame_*.png 1> /dev/null 2>&1; then
    echo "✅ Frames detected, proceeding with video creation..."
else
    echo "❌ Error: No frames found in ${OUTPUT_FOLDER}/. Video creation aborted."
    exit 1
fi

# Create video from rendered frames
ffmpeg -framerate 24 -i "${OUTPUT_FOLDER}/frame_%04d.png" -c:v libx264 -pix_fmt yuv420p "${VIDEO_FILE}"

# Verify video creation
if [[ -f "${VIDEO_FILE}" ]]; then
    echo "✅ Video creation completed! Video saved at ${VIDEO_FILE}"
else
    echo "❌ Error: Video file was not created!"
    exit 1
fi



