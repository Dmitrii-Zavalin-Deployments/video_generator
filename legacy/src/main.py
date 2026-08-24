import os
import sys
import json
import blender_render  # Importing Blender rendering module

# Retrieve path variables from environment (set by GitHub Actions)
LOCAL_INPUT_FOLDER = os.getenv("INPUT_FOLDER", os.path.join("..", "data", "testing-input-output"))
LOCAL_OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", os.path.join("..", "RenderedOutput"))
LOG_FILE_PATH = os.getenv("LOG_FILE", os.path.join("..", "download_log.txt"))
JSON_FILE = os.path.join(LOCAL_INPUT_FOLDER, "fluid_dynamics_animation.json")
BLENDER_SCENE_FILE = os.getenv("BLEND_FILE", os.path.join(LOCAL_INPUT_FOLDER, "fluid_simulation.blend"))

def prepare_files():
    """Prepares JSON file for rendering and returns simulation parameters."""

    print("🔄 Preparing fluid dynamics simulation input...")

    # ✅ Debugging: Print expected paths
    print(f"🔍 Expected simulation input directory: {LOCAL_INPUT_FOLDER}")
    print(f"🔍 Blender Scene File Path: {BLENDER_SCENE_FILE}")

    # ✅ Ensure the correct directory exists
    if not os.path.exists(LOCAL_INPUT_FOLDER):
        print(f"⚠️ Warning: `{LOCAL_INPUT_FOLDER}` does not exist. Creating directory...")
        os.makedirs(LOCAL_INPUT_FOLDER, exist_ok=True)

    # ✅ Verify the JSON file exists
    if not os.path.exists(JSON_FILE):
        print(f"❌ Error: `fluid_dynamics_animation.json` not found in `{LOCAL_INPUT_FOLDER}`!")
        sys.exit(1)

    print(f"✅ Found simulation input file: {JSON_FILE}. Ready for processing.")

    # ✅ Load fluid dynamics simulation parameters
    try:
        with open(JSON_FILE, "r") as file:
            simulation_data = json.load(file)
    except json.JSONDecodeError:
        print(f"❌ Error: Could not decode JSON from `{JSON_FILE}`!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred during JSON loading: {e}")
        sys.exit(1)

    print("✅ Fluid dynamics simulation data loaded successfully!")

    # ✅ Verify Blender scene file exists BEFORE running rendering
    if not os.path.exists(BLENDER_SCENE_FILE):
        print(f"❌ Error: Blender scene file `{BLENDER_SCENE_FILE}` not found! Rendering aborted.")
        sys.exit(1)

    print(f"✅ Blender scene file `{BLENDER_SCENE_FILE}` found. Proceeding with rendering.")

    # Add the blender_scene_file path to the simulation_data dictionary
    simulation_data["blender_scene_file"] = BLENDER_SCENE_FILE
    return simulation_data  # ✅ Return updated simulation data

if __name__ == "__main__":
    simulation_data = prepare_files()  # ✅ Capture simulation parameters

    # Run Blender rendering with JSON-based simulation input
    blender_render.run_blender_render(simulation_data)

    # ✅ Verify frames were generated before continuing
    frame_check = os.system("ls -lah RenderedOutput/ | grep frame_0000.png")
    if frame_check != 0:
        print("❌ Error: No frames found in RenderedOutput/. Rendering might have failed.")
        sys.exit(1)

    print("✅ Rendering process completed! Frames saved in RenderedOutput.")
    print("📽️ Next step: Convert frames to a video in GitHub Actions.")
