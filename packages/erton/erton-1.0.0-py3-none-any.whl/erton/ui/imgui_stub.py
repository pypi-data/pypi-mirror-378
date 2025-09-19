from __future__ import annotations
# Optional: pyimgui minimal stub. Real apps should integrate with a renderer (DX9/GL).
def splash_stub():
    try:
        import imgui
    except Exception as e:
        raise RuntimeError("pyimgui not installed. Install with `pip install '.[gui]'`.") from e
    # Minimal state-only call (no rendering loop here to avoid backend complexity)
    # In real usage, integrate imgui with your chosen renderer and call imgui.new_frame()/render().
    return "imgui_stub_ready"
