from __future__ import annotations

from collections.abc import Callable

from .base import BaseVisual
from .lissajous import LissajousVisual
from .matrix_rain import MatrixRainVisual
from .particle_flow import ParticleFlowVisual
from .plasma import PlasmaVisual
from .starfield import StarfieldVisual

RendererFactory = Callable[[], BaseVisual]

VISUALS: dict[str, RendererFactory] = {
    StarfieldVisual.name: StarfieldVisual,
    ParticleFlowVisual.name: ParticleFlowVisual,
    PlasmaVisual.name: PlasmaVisual,
    MatrixRainVisual.name: MatrixRainVisual,
    LissajousVisual.name: LissajousVisual,
}


def visual_names() -> list[str]:
    return list(VISUALS.keys())


def create_visual(name: str) -> BaseVisual:
    factory = VISUALS.get(name)
    if factory is None:
        factory = VISUALS["particle_flow"]
    return factory()
