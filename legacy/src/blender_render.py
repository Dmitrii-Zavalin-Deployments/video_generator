import os
import json
import sys

# ✅ Retrieve path variables from environment (set by GitHub Actions)
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "./RenderedOutput")

def run_blender_render(simulation_data):
    """Executes Blender rendering in CLI mode with optimized settings based on simulation data.

    Args:
        simulation_data (dict): A dictionary containing the simulation parameters.
    """
    print("🔄 Starting rendering process with enhanced settings...")
    print(f"⚙️ Received simulation data for rendering: {json.dumps(simulation_data, indent=2)}")

    # ✅ Ensure output folder exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # ✅ Retrieve Blender scene file path from simulation data
    blend_file_path = simulation_data.get("blender_scene_file")

    # ✅ Verify Blender scene file exists BEFORE rendering
    if not blend_file_path or not os.path.exists(blend_file_path):
        print(f"❌ Error: Blender scene file '{blend_file_path}' not found! Rendering aborted.")
        sys.exit(1)

    print(f"✅ Blender scene file '{blend_file_path}' found. Proceeding with rendering.")

    # ✅ Extract relevant parameters with defaults
    scale_factor = simulation_data.get("scale_factor", 1.5)
    rotation_z = simulation_data.get("rotation_z", 45.0)
    num_frames = simulation_data.get("num_frames", 10)
    light_location_x = simulation_data.get("light_location_x", 5)
    light_location_y = simulation_data.get("light_location_y", -5)
    light_location_z = simulation_data.get("light_location_z", 5)
    cycles_samples = simulation_data.get("cycles_samples", 128)

    # ✅ Generate and execute Blender rendering command
    render_command = f"""blender -b "{blend_file_path}" --python-expr "
import bpy
import math

try:
    # Load Blender scene
    bpy.ops.wm.open_mainfile(filepath='{blend_file_path}')
except Exception as e:
    print(f'❌ Error opening Blender file: {{e}}')
    exit()

# ✅ Find the imported model 'MyImportedModel'
obj = bpy.data.objects.get('MyImportedModel')

if obj:
    obj.scale *= {scale_factor}
    obj.rotation_euler.z += math.radians({rotation_z})

    # ✅ Improve Lighting
    if not bpy.data.objects.get('AutoSunLight'):
        light_data = bpy.data.lights.new(name='AutoSunLight', type='SUN')
        light_object = bpy.data.objects.new(name='AutoSunLight', object_data=light_data)
        bpy.context.collection.objects.link(light_object)
        light_object.location = ({light_location_x}, {light_location_y}, {light_location_z})

    # ✅ Enhance render settings
    bpy.context.scene.cycles.samples = {cycles_samples}

    # ✅ Render frames dynamically
    for frame in range(1, {num_frames + 1}):
        bpy.context.scene.frame_set(frame)
        bpy.context.scene.render.filepath = '{OUTPUT_FOLDER}/frame_' + str(frame).zfill(4)
        bpy.ops.render.render(write_still=True)

else:
    print('❌ Object "MyImportedModel" not found in the Blender scene! Skipping rendering.')
    exit()
" """

    os.system(render_command)

    # ✅ Verify rendering success
    frame_check = any(os.path.exists(f"{OUTPUT_FOLDER}/frame_{str(i).zfill(4)}.png") for i in range(1, num_frames + 1))

    if not frame_check:
        print("❌ Error: No frames found in RenderedOutput/. Rendering might have failed.")
        sys.exit(1)

    print(f"✅ Rendering process completed! Frames successfully saved in {OUTPUT_FOLDER}")

if __name__ == "__main__":
    # ✅ Example usage for testing
    fake_simulation_data = {
        "blender_scene_file": os.getenv("BLEND_FILE", "example.blend"),
        "scale_factor": 2.0,
        "rotation_z": 90.0,
        "num_frames": 20,
        "light_location_x": -10,
        "light_location_y": 10,
        "light_location_z": 10,
        "cycles_samples": 256
    }

    # ✅ Create a dummy example.blend file for local testing
    if not os.path.exists(fake_simulation_data["blender_scene_file"]):
        with open(fake_simulation_data["blender_scene_file"], "w") as f:
            f.write("# Dummy Blender file")

    run_blender_render(fake_simulation_data)
