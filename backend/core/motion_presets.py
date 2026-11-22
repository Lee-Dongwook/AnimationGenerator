
import math


def get_motion(preset: str, progress: float) -> dict:
    """
    Returns normalized animation parameters.

    x, y: position offsets
    rotation: rotation in degrees
    scale: character scale
    """

    phase = progress * math.tau

    motions = {
        "bounce": {
            "x": 0,
            "y": -abs(math.sin(phase * 2)) * 45,
            "rotation": 0,
            "scale": 1.0 + abs(math.sin(phase * 2)) * 0.025,
        },

        "wave": {
            "x": math.sin(phase) * 12,
            "y": 0,
            "rotation": math.sin(phase * 2) * 5,
            "scale": 1.0,
        },

        "sway": {
            "x": math.sin(phase) * 30,
            "y": math.sin(phase * 2) * 5,
            "rotation": math.sin(phase) * 8,
            "scale": 1.0,
        },

        "dance": {
            "x": math.sin(phase * 2) * 35,
            "y": -abs(math.sin(phase * 2)) * 35,
            "rotation": math.sin(phase * 2) * 12,
            "scale": 1.0 + abs(math.sin(phase * 2)) * 0.04,
        },
    }

    if preset not in motions:
        raise ValueError(f"Unsupported motion preset: {preset}")

    return motions[preset]
