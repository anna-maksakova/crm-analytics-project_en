"""
Theme: цвета, шрифты, общие стили для дашборда.
"""

# === Цветовая палитра — синяя градация, без тёплых акцентов ===
# Контраст создаётся через светлоту, а не через цвет.
BLUE_DARK = "#2F5268"     # основной — текст, основные элементы, акцент через тёмность
BLUE_MID = "#5F8FA8"      # вторичный — линии, второй ряд данных, выделение
BLUE_SOFT = "#9FC3D5"     # светлый — заливка, мягкие элементы
BLUE_PALE = "#D9EAF2"     # очень светлый — сетка, фон карточек
BLUE_BG = "#F3F7FA"       # фон-подложка

GRAY_BORDER = "#E5E5E5"

# Алиасы для обратной совместимости с уже написанным кодом
# (чтобы не менять impotrs в app.py и tabs/*)
NAVY = BLUE_DARK          # везде где был "тёмный navy" → теперь самый тёмный синий
NAVY_SOFT = BLUE_MID      # вторичный
CORAL = BLUE_DARK         # бывший акцент → тоже тёмный синий (по выбору Анны: без тёплого акцента)
SAND = BLUE_SOFT          # бывший тёплый акцент → светло-голубой
TEAL_SOFT = BLUE_PALE     # дополнительный → бледно-голубой

# Палитра для категориальных данных (Source и т.п.)
PALETTE = [BLUE_DARK, BLUE_MID, BLUE_SOFT, BLUE_PALE, "#7AA5BC", "#446F87", "#B4D4E2", "#1F3A4A"]

# Цвета для воронки Stage Group — градация тёмный → светлый
STAGE_COLORS = {
    "Lost": BLUE_DARK,
    "In Progress": BLUE_MID,
    "Won": BLUE_SOFT,   # Won — самый светлый, привлекает внимание контрастом
}

# === Шрифты и размеры ===
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
    """Применить тему к plotly-фигуре."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig
