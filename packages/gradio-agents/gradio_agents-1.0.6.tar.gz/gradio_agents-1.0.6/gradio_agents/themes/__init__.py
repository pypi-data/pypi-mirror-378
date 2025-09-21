from gradio_agents.themes.base import Base, ThemeClass
from gradio_agents.themes.default import Default
from gradio_agents.themes.glass import Glass
from gradio_agents.themes.monochrome import Monochrome
from gradio_agents.themes.soft import Soft
from gradio_agents.themes.utils import colors, sizes
from gradio_agents.themes.utils.colors import Color
from gradio_agents.themes.utils.fonts import Font, GoogleFont
from gradio_agents.themes.utils.sizes import Size

__all__ = [
    "Base",
    "Color",
    "Default",
    "Font",
    "Glass",
    "GoogleFont",
    "Monochrome",
    "Size",
    "Soft",
    "ThemeClass",
    "colors",
    "sizes",
]


def builder(*args, **kwargs):
    from gradio_agents.themes.builder_app import demo

    return demo.launch(*args, **kwargs)
