"""
Gráficos Plotly em KG.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def plot_template(theme: str) -> str:
    return "plotly_dark" if theme == "dark" else "plotly_white"


def fig_empty(template: str, title: str):
    fig = go.Figure()
    fig.update_layout(template=template, title=title, height=360)
    return fig


def build_funnel_fig(df: pd.DataFrame, template: str):
    reached = {
        "Total (escopo)": df["peso_total_kg"].sum(),
        "Preparação atingida": df.loc[df["prep_kg"] > 0, "peso_total_kg"].sum(),
        "Montagem atingida": df.loc[df["mont_kg"] > 0, "peso_total_kg"].sum(),
        "Solda atingida": df.loc[df["sold_kg"] > 0, "peso_total_kg"].sum(),
        "Acabamento atingido": df.loc[df["acab_kg"] > 0, "peso_total_kg"].sum(),
        "Pintura atingida": df.loc[df["pint_kg"] > 0, "peso_total_kg"].sum(),
        "Expedido": df.loc[df["peso_exped_kg"] > 0, "peso_total_kg"].sum(),
    }
    labels = list(reached.keys())
    values = list(reached.values())

    fig = go.Figure(go.Funnel(y=labels, x=values, textinfo="value+percent initial"))
    fig.update_layout(template=template, height=380, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def build_wip_stage_fig(df: pd.DataFrame, template: str):
    wip = df.groupby("etapa_atual", as_index=False)["peso_total_kg"].sum().sort_values("peso_total_kg", ascending=True)
    fig = px.bar(
        wip,
        x="peso_total_kg",
        y="etapa_atual",
        orientation="h",
        labels={"peso_total_kg": "KG", "etapa_atual": "Etapa"},
    )
    fig.update_layout(template=template, height=380, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def build_timeseries_fig(df: pd.DataFrame, template: str):
    tmp = df.copy()
    tmp["receb_sem"] = tmp["dt_receb"].dt.to_period("W").dt.start_time
    tmp["exped_sem"] = tmp["dt_exped"].dt.to_period("W").dt.start_time

    receb = tmp.dropna(subset=["receb_sem"]).groupby("receb_sem", as_index=False)["peso_total_kg"].sum()
    exped = tmp.dropna(subset=["exped_sem"]).groupby("exped_sem", as_index=False)["peso_exped_kg"].sum()

    fig = go.Figure()
    if len(receb):
        fig.add_trace(go.Scatter(x=receb["receb_sem"], y=receb["peso_total_kg"], mode="lines+markers", name="Recebido (kg)"))
    if len(exped):
        fig.add_trace(go.Scatter(x=exped["exped_sem"], y=exped["peso_exped_kg"], mode="lines+markers", name="Expedido (kg)"))

    fig.update_layout(template=template, height=380, margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h"))
    return fig


def build_top_os_fig(df: pd.DataFrame, template: str):
    """
    Top 10 OS por saldo a produzir (kg).
    Substitui o antigo gráfico por cliente.
    """
    by_os = df.groupby("os_cliente", as_index=False).agg(
        saldo_a_produzir_kg=("saldo_a_produzir_kg", "sum"),
        total_kg=("peso_total_kg", "sum"),
    )
    by_os = by_os[by_os["os_cliente"] != ""].sort_values("saldo_a_produzir_kg", ascending=False).head(10)

    fig = px.bar(
        by_os[::-1],
        x="saldo_a_produzir_kg",
        y="os_cliente",
        orientation="h",
        labels={"saldo_a_produzir_kg": "Saldo a Produzir (kg)", "os_cliente": "OS Cliente"},
    )
    fig.update_layout(template=template, height=380, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def build_leadtime_fig(df: pd.DataFrame, template: str):
    lt = df.loc[df["leadtime_dias"].notna() & (df["leadtime_dias"] >= 0) & (df["leadtime_dias"] <= 3650), "leadtime_dias"]
    fig = px.histogram(lt, nbins=30, labels={"value": "Lead time (dias)"})
    fig.update_layout(template=template, height=380, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def build_conversion_fig(df: pd.DataFrame, template: str):
    total_scope = df["peso_total_kg"].sum()
    reached_prep = df.loc[df["prep_kg"] > 0, "peso_total_kg"].sum()
    reached_mont = df.loc[df["mont_kg"] > 0, "peso_total_kg"].sum()
    reached_sold = df.loc[df["sold_kg"] > 0, "peso_total_kg"].sum()
    reached_acab = df.loc[df["acab_kg"] > 0, "peso_total_kg"].sum()
    reached_pint = df.loc[df["pint_kg"] > 0, "peso_total_kg"].sum()
    reached_exped = df.loc[df["peso_exped_kg"] > 0, "peso_total_kg"].sum()

    stages = ["Total→Prep", "Prep→Mont", "Mont→Sold", "Sold→Acab", "Acab→Pint", "Pint→Exped"]
    numer = [reached_prep, reached_mont, reached_sold, reached_acab, reached_pint, reached_exped]
    denom = [total_scope, reached_prep, reached_mont, reached_sold, reached_acab, reached_pint]
    conv = [(n / d) if d > 0 else 0.0 for n, d in zip(numer, denom)]

    fig = px.bar(x=stages, y=[c * 100 for c in conv], labels={"x": "Etapa", "y": "Conversão (%)"})
    fig.update_layout(template=template, height=380, margin=dict(l=10, r=10, t=40, b=10))
    fig.update_yaxes(range=[0, 105])
    return fig

