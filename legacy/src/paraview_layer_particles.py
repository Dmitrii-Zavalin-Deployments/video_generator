# src/paraview_layer_particles.py

import paraview.simple as pv_s
import sys, os

# --- Parse Arguments ---
PVD_PATH, MODEL_PATH, OUTPUT_VIDEO_PATH = None, None, None
args = sys.argv
for i, arg in enumerate(args):
    if arg == "--pvd-file": PVD_PATH = os.path.abspath(args[i+1])
    elif arg == "--turbine-model": MODEL_PATH = os.path.abspath(args[i+1])
    elif arg == "--output-video": OUTPUT_VIDEO_PATH = os.path.abspath(args[i+1])

if not PVD_PATH or not OUTPUT_VIDEO_PATH:
    print("Usage: pvpython paraview_layer_particles.py --pvd-file path --turbine-model path --output-video path")
    sys.exit(1)

# --- Frame Output Path ---
OUTPUT_DIR = os.path.join(os.path.dirname(OUTPUT_VIDEO_PATH), "particles_layer_frames")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATTERN = os.path.join(OUTPUT_DIR, "frame_%04d.png")

print(f"🎯 Output frames: {OUTPUT_PATTERN}")

# --- Load Data ---
pv_s.ResetSession()
fluid = pv_s.PVDReader(FileName=PVD_PATH)

# --- Stream Tracer ---
bounds = fluid.GetDataInformation().GetBounds()
tracer = pv_s.StreamTracer(Input=fluid, SeedType='Line')
tracer.SeedType.Point1 = [bounds[0], bounds[2], bounds[4]]
tracer.SeedType.Point2 = [bounds[0], bounds[3], bounds[5]]
tracer.SeedType.Resolution = 100
tracer.Vectors = ['POINTS', 'Velocity']
tracer.IntegrationDirection = 'FORWARD'
tracer.MaximumStepLength = 0.01

# --- Glyphs ---
glyph = pv_s.Glyph(Input=tracer, GlyphType='Sphere')
glyph.ScaleArray = ['POINTS', 'Velocity']
glyph.ScaleFactor = 0.2

glyph_display = pv_s.Show(glyph)
glyph_display.Representation = 'Surface'
glyph_display.ColorArrayName = ['POINTS', 'Velocity']
glyph_display.LookupTable = pv_s.GetLookupTableForArray('Velocity', 3)
glyph_display.LookupTable.RescaleTransferFunction(0.0, 5.0)
glyph_display.Opacity = 0.5

# --- Render View ---
view = pv_s.GetActiveViewOrCreate('RenderView')
view.ViewSize = [1920, 1080]
view.BackEnd = 'pathtracer'
view.Shadows = 1

# --- Camera Position ---
cx = (bounds[0] + bounds[1]) / 2
cy = (bounds[2] + bounds[3]) / 2
cz = (bounds[4] + bounds[5]) / 2
d = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]) * 2

view.CameraPosition = [cx + d, cy + d, cz + d]
view.CameraFocalPoint = [cx, cy, cz]
view.CameraViewUp = [0, 0, 1]

# --- Animate + Save ---
scene = pv_s.GetAnimationScene()
scene.PlayMode = 'Snap To TimeSteps'
scene.StartTime = fluid.TimestepValues[0]
scene.EndTime = fluid.TimestepValues[-1]
scene.NumberOfFrames = len(fluid.TimestepValues)

pv_s.Render()
pv_s.SaveAnimation(OUTPUT_PATTERN, view, ImageResolution=[1920, 1080], ImageQuality=90)
pv_s.Disconnect()

print(f"✅ Particle-only pass complete.")
print(f"PNG_OUTPUT_DIR={OUTPUT_DIR}")



