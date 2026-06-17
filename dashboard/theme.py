"""
Theme: colors, fonts, shared styles for the dashboard.
"""

# === Color palette — blue gradations, no warm accents ===
# Contrast comes from lightness, not hue.
BLUE_DARK = "#2F5268"     # primary — text, main elements, accent through darkness
BLUE_MID = "#5F8FA8"      # secondary — lines, second data series, emphasis
BLUE_SOFT = "#9FC3D5"     # light — fills, soft elements
BLUE_PALE = "#D9EAF2"     # very light — grid, card background
BLUE_BG = "#F3F7FA"       # background base

GRAY_BORDER = "#E5E5E5"

# aliases for backward compatibility with already-written code
# (so we don't have to change imports in app.py and tabs/*)
NAVY = BLUE_DARK          # everywhere "dark navy" was used → now the darkest blue
NAVY_SOFT = BLUE_MID      # secondary
CORAL = BLUE_DARK         # former accent → also dark blue (chosen: no warm accent)
SAND = BLUE_SOFT          # former warm accent → light blue
TEAL_SOFT = BLUE_PALE     # additional → pale blue

# Palette for categorical data (Source, etc.)
PALETTE = [BLUE_DARK, BLUE_MID, BLUE_SOFT, BLUE_PALE, "#7AA5BC", "#446F87", "#B4D4E2", "#1F3A4A"]

# Funnel colors for Stage Group — gradation dark → light
STAGE_COLORS = {
    "Lost": BLUE_DARK,
    "In Progress": BLUE_MID,
    "Won": BLUE_SOFT,  # Won — lightest
}

# === Fonts and sizes ===
FONT_FAMILY = 'Calibri, Inter, "Segoe UI", Tahoma, sans-serif'

FONT_SIZE_BASE = 14
FONT_SIZE_AXIS = 13
FONT_SIZE_TITLE = 18
FONT_SIZE_KPI_LABEL = 13
FONT_SIZE_KPI_VALUE = 28

PLOTLY_LAYOUT = {
    "font": {"family": FONT_FAMILY, "color": NAVY, "size": FONT_SIZE_BASE},
    "paper_bgcolor": "white",
    "plot_bgcolor": "white",
    "colorway": PALETTE,
    "margin": {"l": 60, "r": 40, "t": 60, "b": 50},
    "xaxis": {
        "gridcolor": GRAY_BORDER,
        "linecolor": GRAY_BORDER,
        "tickcolor": GRAY_BORDER,
        "tickfont": {"size": FONT_SIZE_AXIS},
        "title": {"font": {"size": FONT_SIZE_AXIS}},
    },
    "yaxis": {
        "gridcolor": GRAY_BORDER,
        "linecolor": GRAY_BORDER,
        "tickcolor": GRAY_BORDER,
        "tickfont": {"size": FONT_SIZE_AXIS},
        "title": {"font": {"size": FONT_SIZE_AXIS}},
    },
    "title": {"font": {"size": FONT_SIZE_TITLE, "color": NAVY}, "x": 0.02},
    "legend": {"bgcolor": "rgba(0,0,0,0)", "font": {"size": FONT_SIZE_BASE}},
}


def apply_theme(fig):
    """Apply theme to a plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig
