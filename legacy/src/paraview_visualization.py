# src/paraview_visualization.py

# This script should be run with pvpython (ParaView's Python interpreter)
# Example:
# pvpython paraview_visualization.py --pvd-file /path/to/data.pvd --turbine-model /path/to/geometry.obj --output-video /path/to/video.mp4

import paraview.simple as pv_s
import sys
import os

OUTPUT_FRAMES_SUBDIR = "turbine_animation_frames"
PVD_FILE_PATH = None
TURBINE_MODEL_PATH = None

if __name__ == "__main__":
    args = sys.argv
    base_output_path = None
    for i, arg in enumerate(args):
        if arg == "--pvd-file" and i + 1 < len(args):
            PVD_FILE_PATH = args[i+1]
        elif arg == "--turbine-model" and i + 1 < len(args):
            TURBINE_MODEL_PATH = args[i+1]
        elif arg == "--output-video" and i + 1 < len(args):
            base_output_path = args[i+1]

    if not PVD_FILE_PATH or not TURBINE_MODEL_PATH or not base_output_path:
        print("Usage: pvpython paraview_visualization.py --pvd-file <.pvd> --turbine-model <.obj/.stl/.vtp> --output-video <path>")
        sys.exit(1)

    # Normalize paths
    PVD_FILE_PATH = os.path.abspath(PVD_FILE_PATH)
    TURBINE_MODEL_PATH = os.path.abspath(TURBINE_MODEL_PATH)
    actual_output_dir = os.path.join(os.path.dirname(base_output_path), OUTPUT_FRAMES_SUBDIR)
    os.makedirs(actual_output_dir, exist_ok=True)
    PARAVIEW_OUTPUT_PATTERN = os.path.join(actual_output_dir, "frame_%04d.png")

    print(f"✅ Output folder: {actual_output_dir}")
    print(f"ParaView: Reading PVD: {PVD_FILE_PATH}")
    print(f"ParaView: Turbine Geometry: {TURBINE_MODEL_PATH}")

    # --- Load CFD Data ---
    pv_s.ResetSession()
    fluid_reader = pv_s.PVDReader(FileName=PVD_FILE_PATH)

    # --- Load Turbine Geometry ---
    ext = TURBINE_MODEL_PATH.lower()
    if ext.endswith(".obj"):
        turbine_reader = pv_s.WavefrontOBJReader(FileName=TURBINE_MODEL_PATH)
    elif ext.endswith(".stl"):
        turbine_reader = pv_s.STLReader(FileName=TURBINE_MODEL_PATH)
    elif ext.endswith(".vtp"):
        turbine_reader = pv_s.XMLPolyDataReader(FileName=TURBINE_MODEL_PATH)
    else:
        raise ValueError("Unsupported model format. Use .obj, .stl, or .vtp.")

    # --- View & Renderer Setup ---
    render_view = pv_s.GetActiveViewOrCreate('RenderView')
    pv_s.SetActiveView(render_view)
    render_view.OSPRayMaterialLibrary = pv_s.GetMaterialLibrary()
    render_view.Shadows = 1
    render_view.BackEnd = 'pathtracer'

    # --- Place Lights ---
    render_view.KeyLightWarmth = 0.6
    render_view.FillLightWarmth = 0.3
    render_view.HeadLightWarmth = 0.5
    render_view.KeyLightIntensity = 0.7
    render_view.FillLightKFRatio = 3.0

    # --- Stream Tracer for Particles ---
    bounds = fluid_reader.GetDataInformation().GetBounds()
    tracer = pv_s.StreamTracer(Input=fluid_reader, SeedType='Line')
    tracer.SeedType.Point1 = [bounds[0], bounds[2], bounds[4]]
    tracer.SeedType.Point2 = [bounds[0], bounds[3], bounds[5]]
    tracer.SeedType.Resolution = 100
    tracer.Vectors = ['POINTS', 'Velocity']
    tracer.IntegrationDirection = 'FORWARD'
    tracer.MaximumStepLength = 0.01

    glyph = pv_s.Glyph(Input=tracer, GlyphType='Sphere')
    glyph.ScaleArray = ['POINTS', 'Velocity']
    glyph.ScaleFactor = 0.2
    pv_s.UpdatePipeline()

    # --- Display Particles ---
    glyph_display = pv_s.Show(glyph, render_view)
    glyph_display.Representation = 'Surface'
    glyph_display.ColorArrayName = ['POINTS', 'Velocity']
    glyph_display.LookupTable = pv_s.GetLookupTableForArray('Velocity', 3)
    glyph_display.LookupTable.ColorSpace = 'RGB'
    glyph_display.LookupTable.RescaleTransferFunction(0.0, 5.0)
    glyph_display.Opacity = 0.5

    # --- Turbine Display ---
    turbine_display = pv_s.Show(turbine_reader, render_view)
    turbine_display.AmbientColor = [0.7, 0.7, 0.7]
    turbine_display.DiffuseColor = [0.9, 0.9, 0.9]
    turbine_display.Opacity = 1.0
    turbine_display.Representation = 'Surface'

    # --- Camera ---
    cx = (bounds[0] + bounds[1]) / 2
    cy = (bounds[2] + bounds[3]) / 2
    cz = (bounds[4] + bounds[5]) / 2
    dist = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]) * 2

    render_view.CameraPosition = [cx + dist, cy + dist, cz + dist]
    render_view.CameraFocalPoint = [cx, cy, cz]
    render_view.CameraViewUp = [0, 0, 1]
    render_view.ViewSize = [1920, 1080]

    # --- Animate Over Timesteps ---
    animation_scene = pv_s.GetAnimationScene()
    animation_scene.PlayMode = 'Snap To TimeSteps'
    animation_scene.StartTime = fluid_reader.TimestepValues[0]
    animation_scene.EndTime = fluid_reader.TimestepValues[-1]
    animation_scene.NumberOfFrames = len(fluid_reader.TimestepValues)

    pv_s.Render()

    # --- Save Animation ---
    print(f"🎥 Saving frames to {PARAVIEW_OUTPUT_PATTERN} ...")
    pv_s.SaveAnimation(
        PARAVIEW_OUTPUT_PATTERN,
        render_view,
        ImageResolution=[1920, 1080],
        ImageQuality=95
    )

    print(f"✅ Done. Exported PNGs to: {actual_output_dir}")
    pv_s.Disconnect()
    print(f"PNG_OUTPUT_DIR={actual_output_dir}")



