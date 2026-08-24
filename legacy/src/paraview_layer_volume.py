# src/paraview_layer_volume.py

import paraview.simple as pv_s
import sys, os

# --- Parse Inputs ---
args = sys.argv
PVD_PATH, OUT_PATH = None, None
for i, arg in enumerate(args):
    if arg == "--pvd-file": PVD_PATH = os.path.abspath(args[i+1])
    elif arg == "--output-video": OUT_PATH = os.path.abspath(args[i+1])

if not PVD_PATH or not OUT_PATH:
    print("Usage: pvpython paraview_layer_volume.py --pvd-file <.pvd> --output-video <.mp4>")
    sys.exit(1)

# --- Frame Output Directory ---
OUT_DIR = os.path.join(os.path.dirname(OUT_PATH), "volume_layer_frames")
os.makedirs(OUT_DIR, exist_ok=True)
FRAME_PATTERN = os.path.join(OUT_DIR, "frame_%04d.png")

print(f"🌫️ Exporting volume frames to: {FRAME_PATTERN}")

# --- Load Data ---
pv_s.ResetSession()
fluid = pv_s.PVDReader(FileName=PVD_PATH)
pv_s.UpdatePipeline()

# --- Compute Velocity Magnitude ---
calc = pv_s.Calculator(Input=fluid)
calc.ResultArrayName = 'VelMag'
calc.Function = 'mag(Velocity)'
pv_s.UpdatePipeline()

# --- View Setup ---
view = pv_s.GetActiveViewOrCreate('RenderView')
pv_s.SetActiveView(view)
view.ViewSize = [1920, 1080]
view.BackEnd = 'pathtracer'
view.Shadows = 1

# --- Volume Rendering ---
volume_display = pv_s.Show(calc, view)
volume_display.Representation = 'Volume'
volume_display.ColorArrayName = ['POINTS', 'VelMag']

lut = pv_s.GetColorTransferFunction('VelMag')
lut.ApplyPreset('Cool to Warm', True)
lut.RescaleTransferFunction(0.0, 10.0)

otf = pv_s.GetOpacityTransferFunction('VelMag')
otf.Points = [
    0.0, 0.0, 0.5, 0.0,
    1.0, 0.05, 0.5, 0.0,
    5.0, 0.3, 0.5, 0.0,
    10.0, 0.8, 0.5, 0.0
]

volume_display.LookupTable = lut
volume_display.OpacityArray = ['POINTS', 'VelMag']
volume_display.ScalarOpacityFunction = otf
volume_display.ScalarOpacityUnitDistance = 1.0

# --- Camera ---
bounds = calc.GetDataInformation().GetBounds()
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
pv_s.SaveAnimation(FRAME_PATTERN, view, ImageResolution=[1920, 1080], ImageQuality=90)
pv_s.Disconnect()

print(f"✅ Volume pass complete.")
print(f"PNG_OUTPUT_DIR={OUT_DIR}")



