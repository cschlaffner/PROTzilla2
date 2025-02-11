import pytest
import plotly.graph_objects as go

from protzilla.constants.colors import PLOT_PRIMARY_COLOR, PLOT_SECONDARY_COLOR
from protzilla.constants.paths import SETTINGS_PATH
from ui.settings.plot_template import (
    determine_font,
    resize_for_display,
    get_scale_factor
)


@pytest.fixture
def sample_params():
    return {
        "section_id": "plots",
        "file_format": "png",
        "width": 85,
        "height": 60,
        "custom_font": "Ubuntu Mono",
        "font": "Arial",
        "heading_size": 11,
        "text_size": 8
    }

def test_determine_font(sample_params):
    assert determine_font(sample_params) == "Arial"
    sample_params["font"] = "Custom"
    assert determine_font(sample_params) == "Ubuntu Mono"

def test_resize_for_display(sample_params):
    result = resize_for_display(sample_params)
    assert result["display_width"] == 600  # SCALED_WIDTH
    assert result["display_heading_size"] == 27

def test_get_scale_factor(sample_params):
    fig = go.Figure()
    fig.update_layout(width=600)
    scale = get_scale_factor(fig, sample_params)
    assert isinstance(scale, float)
    assert round(scale, 3) == 1.673