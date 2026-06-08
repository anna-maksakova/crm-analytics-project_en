"""
CRM Analytics Dashboard.
Структура: глобальные фильтры → KPI-карточки → 3 таба.

Запуск локально:
    python app.py

Деплой на Render: см. README.md
"""
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd

from data_loader import load_deals, filter_deals
from theme import CORAL, NAVY, NAVY_SOFT, FONT_FAMILY, FONT_SIZE_KPI_LABEL, FONT_SIZE_KPI_VALUE
from tabs import funnel, managers, products

# === Инициализация ===
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        # Inter как fallback к Calibri для не-Windows систем (деплой)
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
    title="CRM Analytics — Online IT School",
    suppress_callback_exceptions=True,
)
server = app.server  # для gunicorn на Render

# Загружаем данные один раз при старте
deals = load_deals()

# === Опции для фильтров ===
SOURCE_OPTIONS = [{"label": s, "value": s} for s in sorted(deals["Source"].dropna().unique())]
EXCLUDED_PRODUCTS = ["Data Analytics", "Find yourself in IT"]
PRODUCT_OPTIONS = [
    {"label": p, "value": p}
    for p in sorted(deals["Product"].dropna().unique())
    if p not in EXCLUDED_PRODUCTS
]
MIN_DATE = deals["Created Time"].min().date()
MAX_DATE = deals["Created Time"].max().date()


# === Компоненты ===
def header():
    """Шапка с заголовком."""
    return dbc.Container([
        html.H2(
            "CRM Analytics — Online IT School",
            style={"color": NAVY, "marginTop": "20px", "fontWeight": 600},
        ),
        html.P(
            "Funnel, campaigns, sales managers and product analysis · Jul 2023 – Jun 2024",
            style={"color": NAVY, "opacity": 0.65, "fontSize": "15px"},
        ),
        html.Hr(style={
            "borderColor": CORAL, "borderWidth": "2px",
            "width": "60px", "marginLeft": 0, "marginTop": "5px",
        }),
    ], fluid=True)


def filters_panel():
    """Глобальные фильтры: Period (с Reset) → Product → Source."""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # Period + Reset
                dbc.Col([
                    html.Label("Period", style={"fontWeight": 600, "color": NAVY}),
                    html.Div([
                        dcc.DatePickerRange(
                            id="filter-date",
                            min_date_allowed=MIN_DATE,
                            max_date_allowed=MAX_DATE,
                            start_date=MIN_DATE,
                            end_date=MAX_DATE,
                            display_format="DD.MM.YYYY",
                            style={"display": "inline-block"},
                        ),
                        dbc.Button(
                            "Reset",
                            id="btn-reset-date",
                            color="light",
                            size="sm",
                            style={"marginLeft": "8px", "color": NAVY, "borderColor": NAVY_SOFT},
                        ),
                    ]),
                ], md=5),
                # Product
                dbc.Col([
                    html.Label("Product", style={"fontWeight": 600, "color": NAVY}),
                    dcc.Dropdown(
                        id="filter-product",
                        options=PRODUCT_OPTIONS,
                        multi=True,
                        placeholder="All products",
                    ),
                ], md=3),
                # Source
                dbc.Col([
                    html.Label("Source", style={"fontWeight": 600, "color": NAVY}),
                    dcc.Dropdown(
                        id="filter-source",
                        options=SOURCE_OPTIONS,
                        multi=True,
                        placeholder="All sources",
                    ),
                ], md=4),
            ])
        ])
    ], style={"marginBottom": "20px", "border": f"1px solid #E5E5E5"})


def kpi_card(title, value_id, color=NAVY):
    """Одна KPI-карточка."""
    return dbc.Card([
        dbc.CardBody([
            html.P(
                title,
                style={
                    "color": NAVY, "opacity": 0.65,
                    "marginBottom": "8px", "fontSize": f"{FONT_SIZE_KPI_LABEL}px",
                    "letterSpacing": "0.5px",
                },
            ),
            html.H3(
                id=value_id,
                style={
                    "color": color, "marginBottom": 0, "fontWeight": 700,
                    "fontSize": f"{FONT_SIZE_KPI_VALUE}px",
                },
            ),
        ])
    ], style={"textAlign": "center", "border": "1px solid #E5E5E5"})


def kpi_row():
    """Ряд KPI-карточек."""
    return dbc.Row([
        dbc.Col(kpi_card("Total Leads", "kpi-leads"), md=2),
        dbc.Col(kpi_card("Won Confirmed", "kpi-won", CORAL), md=2),
        dbc.Col(kpi_card("Revenue", "kpi-revenue", CORAL), md=3),
        dbc.Col(kpi_card("Conversion Rate", "kpi-cr"), md=2),
        dbc.Col(kpi_card("AOV per month", "kpi-aov"), md=3),
    ], style={"marginBottom": "20px"})


# === Лейаут ===
app.layout = dbc.Container([
    header(),
    filters_panel(),
    kpi_row(),
    dbc.Tabs([
        dbc.Tab(funnel.layout(), label="Funnel & Channels", tab_id="tab-funnel"),
        dbc.Tab(managers.layout(), label="Sales Managers", tab_id="tab-managers"),
        dbc.Tab(products.layout(), label="Products & Payments", tab_id="tab-products"),
    ], id="tabs", active_tab="tab-funnel"),
    html.Div(style={"height": "30px"}),
], style={
    "fontFamily": FONT_FAMILY,
    "backgroundColor": "white",
    "maxWidth": "1280px",
    "margin": "0 auto",
    "padding": "0 30px",
})


# === Колбэк Reset даты ===
@callback(
    Output("filter-date", "start_date"),
    Output("filter-date", "end_date"),
    Input("btn-reset-date", "n_clicks"),
    prevent_initial_call=True,
)
def reset_date(_n):
    return MIN_DATE, MAX_DATE


# === Колбэк KPI — обновляется при изменении фильтров ===
@callback(
    Output("kpi-leads", "children"),
    Output("kpi-won", "children"),
    Output("kpi-revenue", "children"),
    Output("kpi-cr", "children"),
    Output("kpi-aov", "children"),
    Input("filter-date", "start_date"),
    Input("filter-date", "end_date"),
    Input("filter-source", "value"),
    Input("filter-product", "value"),
)
def update_kpi(start_date, end_date, sources, products_filter):
    df = filter_deals(deals, (start_date, end_date), sources, products_filter)

    leads = len(df)
    won = int(df["is_won_confirmed"].sum())
    revenue = df.loc[df["is_won_confirmed"], "revenue_actual"].sum()

    # Conversion Rate = Won / Total Leads (по запросу Анны: проще объяснять)
    cr = won / leads * 100 if leads > 0 else 0

    # AOV (мес.) = средний aov_i по Won
    aov_series = df.loc[df["is_won_confirmed"], "aov_i"]
    aov = aov_series.mean() if len(aov_series) > 0 else 0

    return (
        f"{leads:,}".replace(",", " "),
        f"{won:,}".replace(",", " "),
        f"€{revenue:,.0f}".replace(",", " "),
        f"{cr:.2f}%",
        f"€{aov:,.0f}".replace(",", " "),
    )


if __name__ == "__main__":
    app.run(debug=True, port=8050)
