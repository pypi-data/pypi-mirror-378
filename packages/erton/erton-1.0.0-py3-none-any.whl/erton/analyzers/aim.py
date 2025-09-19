from __future__ import annotations
from typing import Dict, Any, List, Tuple
import math
def _norm_angle(a: float) -> float:
    while a > 180: a -= 360
    while a < -180: a += 360
    return a
def features(dt: float, delta_yaw: float, delta_pitch: float, mouse_dx: float, mouse_dy: float, sens: float, fov: float) -> Dict[str,float]:
    if dt <= 0: dt = 1e-3
    yaw = abs(_norm_angle(delta_yaw)); pitch = abs(_norm_angle(delta_pitch))
    ang_vel = math.hypot(yaw, pitch) / dt
    input_mag = math.hypot(mouse_dx, mouse_dy) * max(sens, 1e-3)
    ratio = ang_vel / (input_mag + 1e-3)
    horiz_lock = 1.0 if (yaw > 15 and pitch < 2) else 0.0
    snap = min(1.0, ang_vel / 1500.0)
    decouple = min(1.0, max(0.0, ratio - 2.0) / 8.0)
    return {"snap":snap, "decouple":decouple, "horiz_lock":horiz_lock, "ang_vel":ang_vel, "ratio":ratio}
def score_and_reasons(feats: Dict[str,float]) -> Tuple[float, List[str]]:
    raw = 0.55*feats["snap"] + 0.35*feats["decouple"] + 0.10*feats["horiz_lock"]
    score = 1.0 / (1.0 + math.exp(-6*(raw-0.5)))
    reasons: List[str] = []
    if feats["snap"] > 0.7: reasons.append("High angular snap")
    if feats["decouple"] > 0.5: reasons.append("View movement decoupled from input")
    if feats["horiz_lock"] > 0.0: reasons.append("Horizontal lock pattern")
    return max(0.0, min(1.0, score)), reasons
