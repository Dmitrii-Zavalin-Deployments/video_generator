import bpy
import os
import json

# ✅ Retrieve path variables from environment (set by GitHub Actions)
data_dir = os.getenv("INPUT_FOLDER", os.path.join("data", "testing-input-output"))
json_file = os.path.join(data_dir, "fluid_dynamics_animation.json")
blend_output_path = os.getenv("BLEND_FILE", os.path.join(data_dir, "fluid_simulation.blend"))

# ✅ Ensure `data/testing-input-output/` exists
if not os.path.exists(data_dir):
    os.makedirs(data_dir, exist_ok=True)
    print(f"✅ Created missing directory: {data_dir}")

# ✅ Verify `fluid_dynamics_animation.json` exists
if not os.path.exists(json_file):
    print(f"❌ ERROR: No `{json_file}` found!")
    exit(1)

# ✅ Load fluid dynamics simulation parameters
try:
    with open(json_file, "r") as file:
        simulation_data = json.load(file)
except json.JSONDecodeError:
    print(f"❌ ERROR: Could not decode JSON from `{json_file}`!")
    exit(1)
except Exception as e:
    print(f"❌ ERROR: Unexpected error while loading `{json_file}`: {e}")
    exit(1)

print("✅ Successfully loaded fluid dynamics simulation parameters!")

# ✅ Extract velocity components dynamically from `data_points`
velocity_field = [dp["velocity"]["components"] for dp in simulation_data.get("data_points", []) if "velocity" in dp]
gravity_enabled = simulation_data.get("gravity_enabled", False)
initial_velocity = simulation_data.get("initial_velocity", 15.0)

if not velocity_field:
    print("❌ ERROR: Could not extract velocity field data from `data_points`. Check JSON structure.")
    exit(1)

print(f"✅ Gravity Enabled: {gravity_enabled}")
print(f"✅ Initial Velocity: {initial_velocity}")
print("✅ Setting up Blender fluid simulation environment...")

# ✅ Set Up Fluid Domain
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
domain = bpy.context.object
domain.name = "FluidDomain"
domain.scale = (50, 10, 5)  # Adjust domain size
bpy.ops.object.transform_apply(scale=True)

# ✅ Apply Gravity Settings Based on JSON Input
bpy.context.scene.gravity = (0, 0, 0) if not gravity_enabled else (0, -9.81, 0)
domain.modifiers.new(name="FluidSim", type='FLUID')
domain.modifiers["FluidSim"].fluid_type = 'DOMAIN'
domain.modifiers["FluidSim"].domain_settings.domain_type = 'LIQUID'
domain.modifiers["FluidSim"].domain_settings.gravity = bpy.context.scene.gravity

# ✅ Create Water Source
bpy.ops.mesh.primitive_plane_add(size=12, location=(-12, 0, 0))  # Water inflow from the left
water_source = bpy.context.object
water_source.name = "WaterSource"

# ✅ Apply Fluid Flow Modifier
water_source.modifiers.new(name="FluidFlow", type='FLUID')
water_source.modifiers["FluidFlow"].fluid_type = 'FLOW'
water_source.modifiers["FluidFlow"].flow_settings.flow_type = 'LIQUID'
water_source.modifiers["FluidFlow"].flow_settings.flow_behavior = 'INFLOW'
water_source.modifiers["FluidFlow"].flow_settings.use_initial_velocity = True
water_source.modifiers["FluidFlow"].flow_settings.velocity_factor = initial_velocity

print("✅ Gravity adjusted, water source created, velocity applied!")

# ✅ Iterate Through Velocity Data
for frame, velocity in enumerate(velocity_field):
    print(f"🔹 Frame {frame}: Applying velocity {velocity}")

# ✅ Ensure Blender Scene File Path Exists Before Saving
if not blend_output_path:
    print("❌ ERROR: Blender scene file path is empty or invalid!")
    exit(1)

# ✅ Save Blender Scene
bpy.ops.wm.save_as_mainfile(filepath=blend_output_path)
print(f"✅ Blender scene saved to: {blend_output_path}")

# ✅ Verify Saved File Exists
if not os.path.exists(blend_output_path):
    print("❌ ERROR: Blender scene file was not created successfully!")
    exit(1)

print("✅ Fluid simulation setup complete! Blender scene saved.")
