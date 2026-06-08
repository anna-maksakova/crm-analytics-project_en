"""
Tab «Funnel & Channels».
Charts:
  1. Monthly trend of Leads and Won Confirmed
  2. Funnel by Stage Group (horizontal bars, no connectors)
  3. Conversion Rate by Source
"""
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_loader import load_deals, filter_deals
from theme import (
    CORAL, NAVY, NAVY_SOFT, SAND, STAGE_COLORS, GRAY_BORDER, apply_theme,
)

deals = load_deals()


def layout():
    return html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(id="funnel-trend"), md=12),
        ], style={"marginTop": "20px"}),
        dbc.Row([
            dbc.Col(dcc.Graph(id="funnel-stages"), md=5),
            dbc.Col(dcc.Graph(id="funnel-source-cr"), md=7),
        ]),
    ])


@callback(
    Output("funnel-trend", "figure"),
    Output("funnel-stages", "figure"),
    Output("funnel-source-cr", "figure"),
    Input("filter-date", "start_date"),
    Input("filter-date", "end_date"),
    Input("filter-source", "value"),
    Input("filter-product", "value"),
)
def update_funnel_tab(start_date, end_date, sources, products):
    df = filter_deals(deals, (start_date, end_date), sources, products)

    # --- 1. Monthly trend ---
    df_m = df.assign(month=df["Created Time"].dt.to_period("M").dt.to_timestamp())
    monthly = df_m.groupby("month").agg(
        leads=("Id", "count"),
        won=("is_won_confirmed", "sum"),
    ).reset_index()

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["leads"],
        mode="lines+markers", name="Leads",
        line=dict(color=NAVY_SOFT, width=2.5),
        marker=dict(size=8),
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["won"],
        mode="lines+markers", name="Won Confirmed",
        line=dict(color=CORAL, width=2.5),
        marker=dict(size=8),
        yaxis="y2",
    ))
    fig_trend.update_layout(
        title="Monthly trend: Leads and Won Confirmed",
        yaxis=dict(title="Leads", side="left"),
        yaxis2=dict(title="Won Confirmed", side="right", overlaying="y", showgrid=False),
        hovermode="x unified",
        # Grid for every month
        xaxis=dict(
            dtick="M1",
            tickformat="%b %Y",
            ticklabelmode="period",
            gridcolor=GRAY_BORDER,
        ),
    )
    apply_theme(fig_trend)

    # --- 2. Funnel by Stage Group — horizontal bars, no connectors ---
    stage_counts = (
        df["Stage_Group"]
        .value_counts()
        .reindex(["Lost", "In Progress", "Won"], fill_value=0)
    )
    total = stage_counts.sum()
    labels = [
        f"{stage}<br>{count:,} ({count/total*100:.1f}%)".replace(",", " ")
        for stage, count in stage_counts.items()
    ]

    fig_stages = go.Figure(go.Bar(
        y=stage_counts.index,
        x=stage_counts.values,
        orientation="h",
        marker=dict(color=[STAGE_COLORS[s] for s in stage_counts.index]),
        text=[f"{v:,}".replace(",", " ") + f" ({v/total*100:.1f}%)" for v in stage_counts.values],
        textposition="outside",
        textfont=dict(size=14, color=NAVY),
    ))
    fig_stages.update_layout(
        title="Funnel by Stage Group",
        xaxis=dict(title="Deals", showgrid=True),
        yaxis=dict(title="", categoryorder="array", categoryarray=["Won", "In Progress", "Lost"]),
        showlegend=False,
        bargap=0.4,
    )
    apply_theme(fig_stages)

    # --- 3. Conversion Rate by Source ---
    by_source = df.groupby("Source").agg(
        leads=("Id", "count"),
        won=("is_won_confirmed", "sum"),
    ).reset_index()
    by_source["cr"] = by_source["won"] / by_source["leads"] * 100
    by_source = by_source[by_source["leads"] >= 10].sort_values("cr", ascending=True)

    fig_source = px.bar(
        by_source, x="cr", y="Source", orientation="h",
        text=by_source["cr"].round(1).astype(str) + "%",
        labels={"cr": "Conversion Rate, %", "Source": ""},
        title="Conversion Rate by Source",
    )
    fig_source.update_traces(
        marker_color=CORAL,
        textposition="outside",
        textfont=dict(size=13, color=NAVY),
    )
    apply_theme(fig_source)

    return fig_trend, fig_stages, fig_source
