"""
Tab «Sales Managers».
Charts:
  1. Scatter: Total Leads (X) × Conversion Rate (Y) × Revenue (bubble size)
     — visual exploration of manager performance
  2. Top-15 managers by Revenue (horizontal bar)
"""
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from data_loader import load_deals, filter_deals
from theme import CORAL, NAVY, NAVY_SOFT, GRAY_BORDER, apply_theme

deals = load_deals()

# Minimum number of leads to include manager in analysis
# (filters out managers with single deals and CR=100% noise)
MIN_LEADS = 90


def layout():
    return html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(id="managers-scatter"), md=12),
        ], style={"marginTop": "20px"}),
        dbc.Row([
            dbc.Col(dcc.Graph(id="managers-top-revenue"), md=12),
        ]),
    ])


@callback(
    Output("managers-scatter", "figure"),
    Output("managers-top-revenue", "figure"),
    Input("filter-date", "start_date"),
    Input("filter-date", "end_date"),
    Input("filter-source", "value"),
    Input("filter-product", "value"),
)
def update_managers_tab(start_date, end_date, sources, products):
    df = filter_deals(deals, (start_date, end_date), sources, products)

    # --- Aggregate by manager ---
    by_mgr = df.groupby("Deal Owner Name").agg(
        leads=("Id", "count"),
        won=("is_won_confirmed", "sum"),
        revenue=("revenue_actual", "sum"),
    ).reset_index()
    by_mgr["cr"] = by_mgr["won"] / by_mgr["leads"] * 100
    by_mgr["aov"] = np.where(by_mgr["won"] > 0, by_mgr["revenue"] / by_mgr["won"], 0)
    by_mgr = by_mgr[by_mgr["leads"] >= MIN_LEADS]

    # --- 1. Scatter: Leads × CR × Revenue ---
    # Top performers labeled by name; others left as bubbles
    by_mgr_sorted = by_mgr.sort_values("revenue", ascending=False)
    top_n = 8
    by_mgr["label"] = np.where(
        by_mgr["Deal Owner Name"].isin(by_mgr_sorted.head(top_n)["Deal Owner Name"]),
        by_mgr["Deal Owner Name"],
        "",
    )

    fig_scatter = px.scatter(
        by_mgr,
        x="leads", y="cr", size="revenue",
        text="label",
        hover_data={
            "Deal Owner Name": True,
            "leads": ":,",
            "won": ":,",
            "revenue": ":,.0f",
            "cr": ":.1f",
            "aov": ":,.0f",
            "label": False,
        },
        labels={
            "leads": "Total Leads",
            "cr": "Conversion Rate, %",
            "revenue": "Revenue",
            "Deal Owner Name": "Manager",
            "won": "Won",
            "aov": "AOV",
        },
        title="Sales Managers: Leads × Conversion Rate × Revenue (bubble size)",
        size_max=60,
    )
    fig_scatter.update_traces(
        marker=dict(color=CORAL, opacity=0.65, line=dict(color=NAVY, width=1)),
        textposition="top center",
        textfont=dict(size=12, color=NAVY),
    )
    # Median lines as visual reference
    median_cr = by_mgr["cr"].median()
    median_leads = by_mgr["leads"].median()
    fig_scatter.add_hline(
        y=median_cr, line_dash="dot", line_color=NAVY_SOFT,
        annotation_text=f"median CR {median_cr:.1f}%",
        annotation_position="bottom right",
        annotation_font=dict(color=NAVY_SOFT, size=12),
    )
    fig_scatter.add_vline(
        x=median_leads, line_dash="dot", line_color=NAVY_SOFT,
        annotation_text=f"median leads {median_leads:.0f}",
        annotation_position="top right",
        annotation_font=dict(color=NAVY_SOFT, size=12),
    )
    apply_theme(fig_scatter)
    fig_scatter.update_layout(height=550)

    # --- 2. Top-15 by Revenue ---
    top15 = by_mgr.nlargest(15, "revenue").sort_values("revenue", ascending=True)
    top15["text_label"] = (
        "€" + top15["revenue"].round(0).astype(int).astype(str)
        + "  ·  " + top15["won"].astype(int).astype(str)
        + "/" + top15["leads"].astype(str)
        + " (CR " + top15["cr"].round(1).astype(str) + "%)"
        + "  ·  AOV €" + top15["aov"].round(0).astype(int).astype(str)
    )

    fig_top = go.Figure(go.Bar(
        x=top15["revenue"],
        y=top15["Deal Owner Name"],
        orientation="h",
        marker=dict(color=NAVY),
        text=top15["text_label"],
        textposition="outside",
        textfont=dict(size=12, color=NAVY),
    ))
    fig_top.update_layout(
        title="Top-15 managers by Revenue",
        xaxis=dict(title="Revenue, €"),
        yaxis=dict(title=""),
        showlegend=False,
        height=600,
        margin=dict(r=350),  # extra right margin for long text labels
    )
    apply_theme(fig_top)

    return fig_scatter, fig_top
