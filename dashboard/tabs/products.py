"""
Tab «Products & Payments».
Charts:
  1. Heatmap Product × Education Type with metric switcher
     (Won count / Conversion Rate / Revenue)
  2. Payment Type distribution (donut, Won only)
  3. AOV per month by Product (bar)
"""
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_loader import load_deals, filter_deals
from theme import CORAL, NAVY, NAVY_SOFT, SAND, TEAL_SOFT, GRAY_BORDER, apply_theme

deals = load_deals()


def layout():
    return html.Div([
        html.Div([
            html.Label("Heatmap metric:", style={"color": NAVY, "fontWeight": 600, "marginRight": "15px"}),
            dcc.RadioItems(
                id="heatmap-metric",
                options=[
                    {"label": "  Won count", "value": "won"},
                    {"label": "  Conversion Rate", "value": "cr"},
                    {"label": "  Revenue", "value": "revenue"},
                ],
                value="won",
                inline=True,
                labelStyle={"marginRight": "20px", "color": NAVY},
            ),
        ], style={"marginTop": "20px", "marginBottom": "10px"}),

        dbc.Row([
            dbc.Col(dcc.Graph(id="products-heatmap"), md=12),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="products-payment-pie"), md=5),
            dbc.Col(dcc.Graph(id="products-aov-bar"), md=7),
        ]),
    ])


@callback(
    Output("products-heatmap", "figure"),
    Output("products-payment-pie", "figure"),
    Output("products-aov-bar", "figure"),
    Input("filter-date", "start_date"),
    Input("filter-date", "end_date"),
    Input("filter-source", "value"),
    Input("filter-product", "value"),
    Input("heatmap-metric", "value"),
)
def update_products_tab(start_date, end_date, sources, products, metric):
    df = filter_deals(deals, (start_date, end_date), sources, products)

    # --- 1. Heatmap Product × Education Type ---
    # Только основные продукты (DM, UX/UI, WD), как в анализе
    main_mask = df["is_main_product"] if "is_main_product" in df.columns else df["Product"].isin(
        ["Digital Marketing", "UX/UI Design", "Web Developer"]
    )
    df_main = df[main_mask & df["Education Type"].notna()]

    grouped = df_main.groupby(["Product", "Education Type"]).agg(
        leads=("Id", "count"),
        won=("is_won_confirmed", "sum"),
        revenue=("revenue_actual", "sum"),
    ).reset_index()
    grouped["cr"] = grouped["won"] / grouped["leads"] * 100

    metric_config = {
        "won": ("won", "Won count", ",.0f"),
        "cr": ("cr", "Conversion Rate (%)", ".1f"),
        "revenue": ("revenue", "Revenue (€)", ",.0f"),
    }
    col, title_metric, fmt = metric_config[metric]

    pivot = grouped.pivot(index="Product", columns="Education Type", values=col).fillna(0)
    # Стабильный порядок
    desired_products = [p for p in ["Digital Marketing", "UX/UI Design", "Web Developer"] if p in pivot.index]
    pivot = pivot.loc[desired_products]

    text_template = pivot.map(lambda v: f"{v:{fmt}}".replace(",", " "))

    # Цветовая шкала: очень светлый голубой → тёмно-синий
    heatmap_colorscale = [
        [0, "#F3F7FA"],
        [0.5, "#9FC3D5"],
        [1, "#2F5268"],
    ]

    # Цвет текста: белый на тёмных ячейках, тёмно-синий на светлых
    # Порог — 60% от максимума (выше — тёмная ячейка, нужен белый текст)
    vmax = pivot.values.max() if pivot.values.size > 0 else 1
    threshold = vmax * 0.6
    text_colors = [
        ["white" if v > threshold else "#2F5268" for v in row]
        for row in pivot.values
    ]

    fig_heat = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=heatmap_colorscale,
        text=text_template.values,
        texttemplate="%{text}",
        textfont=dict(size=15),
        showscale=True,
        colorbar=dict(title=title_metric, tickfont=dict(size=12)),
    ))

    # Plotly Heatmap не поддерживает per-cell цвет текста напрямую через textfont.
    # Используем go.Heatmap.update_traces + аннотации поверх для тёмных ячеек.
    # Проще: проходим аннотациями, перекрывая текст с правильным цветом.
    fig_heat.update_traces(textfont=dict(size=15, color="#2F5268"))  # базовый цвет

    # Аннотации с белым текстом для тёмных ячеек
    for i, product in enumerate(pivot.index):
        for j, edu in enumerate(pivot.columns):
            if pivot.values[i, j] > threshold:
                fig_heat.add_annotation(
                    x=edu, y=product,
                    text=text_template.iloc[i, j],
                    showarrow=False,
                    font=dict(size=15, color="white"),
                )
    fig_heat.update_layout(
        title=f"Product × Education Type — {title_metric}",
        xaxis=dict(title="Education Type", side="bottom"),
        yaxis=dict(title=""),
        height=350,
    )
    apply_theme(fig_heat)

    # --- 2. Payment Type — donut chart (Won only) ---
    won_df = df[df["is_won_confirmed"]]
    payment_counts = won_df["Payment Type"].value_counts()

        # Явные цвета по типу платежа (а не по позиции в палитре)
    payment_color_map = {
        "Recurring Payments": "#9FC3D5",   # светло-голубой
        "One Payment": "#2F5268",          # тёмный
        "Reservation": "#5F8FA8",          # средний
        "Free Education": "#D9EAF2",       # самый светлый
    }
    pie_colors = [payment_color_map.get(label, "#5F8FA8") for label in payment_counts.index]

    fig_pie = go.Figure(go.Pie(
        labels=payment_counts.index,
        values=payment_counts.values,
        hole=0.5,
        marker=dict(colors=pie_colors),
        textinfo="label+percent",
        textfont=dict(size=13, color="white"),
    ))
    fig_pie.update_layout(
        title="Payment Type (Won deals)",
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5),
    )
    apply_theme(fig_pie)

    # --- 3. AOV per month by Product ---
    aov_by_product = (
        won_df[won_df["Product"].isin(desired_products)]
        .groupby("Product")["aov_i"]
        .mean()
        .reindex(desired_products)
    )

    fig_aov = go.Figure(go.Bar(
        x=aov_by_product.index,
        y=aov_by_product.values,
        marker=dict(color=CORAL),
        text=[f"€{v:,.0f}".replace(",", " ") for v in aov_by_product.values],
        textposition="outside",
        textfont=dict(size=14, color=NAVY),
    ))
    fig_aov.update_layout(
        title="AOV per month by Product",
        xaxis=dict(title=""),
        yaxis=dict(title="AOV, € per month"),
        showlegend=False,
    )
    apply_theme(fig_aov)

    return fig_heat, fig_pie, fig_aov
