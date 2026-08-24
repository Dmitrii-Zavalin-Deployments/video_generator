# src/paraview_layer_geometry.py

import paraview.simple as pv_s
import sys, os

# --- Parse Input Arguments ---
args = sys.argv
PVD, MODEL, OUT_VIDEO = None, None, None
for i, arg in enumerate(args):
    if arg == "--pvd-file": PVD = os.path.abspath(args[i+1])
    elif arg == "--turbine-model": MODEL = os.path.abspath(args[i+1])
    elif arg == "--output-video": OUT_VIDEO = os.path.abspath(args[i+1])

if not PVD or not MODEL or not OUT_VIDEO:
    print("Usage: pvpython paraview_layer_geometry.py --pvd-file <.pvd> --turbine-model <.obj/.stl/.vtp> --output-video <.mp4>")
    sys.exit(1)

# --- Output Path Configuration ---
OUT_DIR = os.path.join(os.path.dirname(OUT_VIDEO), "geometry_layer_frames")
os.makedirs(OUT_DIR, exist_ok=True)
FRAME_PATTERN = os.path.join(OUT_DIR, "frame_%04d.png")

print(f"📦 Exporting turbine geometry frames to: {FRAME_PATTERN}")

# --- Load Session & Turbine Model ---
pv_s.ResetSession()
fluid = pv_s.PVDReader(FileName=PVD)

ext = MODEL.lower()
if ext.endswith(".obj"):
    turbine_reader = pv_s.WavefrontOBJReader(FileName=MODEL)
elif ext.endswith(".stl"):
    turbine_reader = pv_s.STLReader(FileName=MODEL)
elif ext.endswith(".vtp"):
    turbine_reader = pv_s.XMLPolyDataReader(FileName=MODEL)
else:
    print("❌ Unsupported geometry format. Use .obj, .stl, or .vtp.")
    sys.exit(1)

# --- Render View Configuration ---
view = pv_s.GetActiveViewOrCreate('RenderView')
pv_s.SetActiveView(view)
view.ViewSize = [1920, 1080]
view.BackEnd = 'pathtracer'
view.Shadows = 1  # AmbientOcclusion is not available in ParaView 5.11.2

# --- Show Turbine Mesh Only ---
turbine_display = pv_s.Show(turbine_reader, view)
turbine_display.Representation = 'Surface'
turbine_display.DiffuseColor = [0.9, 0.9, 0.9]
turbine_display.AmbientColor = [0.3, 0.3, 0.3]
turbine_display.Opacity = 1.0

# --- Camera Setup ---
bounds = turbine_reader.GetDataInformation().GetBounds()
cx = (bounds[0] + bounds[1]) / 2
cy = (bounds[2] + bounds[3]) / 2
cz = (bounds[4] + bounds[5]) / 2
d = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])

view.CameraPosition = [cx + d, cy + d, cz + d]
view.CameraFocalPoint = [cx, cy, cz]
view.CameraViewUp = [0, 0, 1]

# --- Animation Setup ---
scene = pv_s.GetAnimationScene()
scene.PlayMode = 'Snap To TimeSteps'
scene.StartTime = fluid.TimestepValues[0]
scene.EndTime = fluid.TimestepValues[-1]
scene.NumberOfFrames = len(fluid.TimestepValues)

pv_s.Render()
pv_s.SaveAnimation(FRAME_PATTERN, view, ImageResolution=[1920, 1080], ImageQuality=95)
pv_s.Disconnect()

print(f"✅ Turbine geometry pass complete.")
print(f"PNG_OUTPUT_DIR={OUT_DIR}")



