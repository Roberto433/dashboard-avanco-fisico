"""
KPIs, insights automáticos e tabela (kg sem casas decimais).
"""

import pandas as pd
from dash import html


def fmt_kg(x):
    """
    Formata kg como inteiro (pt-BR) + 'kg'
    """
    if x is None or pd.isna(x):
        return "-"
    x_int = int(round(float(x)))
    return f"{x_int:,} kg".replace(",", ".")


def make_kpi_card(title, value, subtitle=None):
    return html.Div(
        className="kpi-card",
        children=[
            html.Div(title, className="kpi-title"),
            html.Div(value, className="kpi-value"),
            html.Div(subtitle or "", className="kpi-subtitle"),
        ],
    )


def compute_kpis(df: pd.DataFrame | None):
    if df is None or len(df) == 0:
        return [
            make_kpi_card("Peso Total", "-", "∑ Peso total do escopo (kg)"),
            make_kpi_card("Peso Produzido", "-", "∑ Última etapa atingida (kg)"),
            make_kpi_card("Peso Expedido", "-", "∑ Expedição (kg)"),
            make_kpi_card("Saldo a Produzir", "-", "Total − Produzido (kg)"),
            make_kpi_card("Saldo a Expedir (WIP)", "-", "Produzido − Expedido (kg)"),
            make_kpi_card("% Avanço Físico", "-", "Produzido ÷ Total"),
            make_kpi_card("% Expedição", "-", "Expedido ÷ Total"),
            make_kpi_card("Lead Time Médio", "-", "Expedição − Recebimento (dias)"),
        ]

    total = df["peso_total_kg"].sum()
    produzido = df["produzido_kg"].sum()
    exped = df["peso_exped_kg"].sum()

    saldo_prod = max(0.0, total - produzido)
    saldo_exped = max(0.0, produzido - exped)

    pct_avanco = (produzido / total) if total > 0 else 0.0
    pct_exped = (exped / total) if total > 0 else 0.0

    lt = df.loc[df["leadtime_dias"].notna() & (df["leadtime_dias"] >= 0), "leadtime_dias"]
    lt_mean = float(lt.mean()) if len(lt) else None

    pct_avanco_s = f"{pct_avanco*100:,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    pct_exped_s = f"{pct_exped*100:,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    lt_s = f"{lt_mean:,.1f} dias".replace(",", "X").replace(".", ",").replace("X", ".") if lt_mean is not None else "-"

    return [
        make_kpi_card("Peso Total", fmt_kg(total), "∑ Peso total do escopo (kg)"),
        make_kpi_card("Peso Produzido", fmt_kg(produzido), "∑ Última etapa atingida (kg)"),
        make_kpi_card("Peso Expedido", fmt_kg(exped), "∑ Expedição (kg)"),
        make_kpi_card("Saldo a Produzir", fmt_kg(saldo_prod), "Total − Produzido (kg)"),
        make_kpi_card("Saldo a Expedir (WIP)", fmt_kg(saldo_exped), "Produzido − Expedido (kg)"),
        make_kpi_card("% Avanço Físico", pct_avanco_s, "Produzido ÷ Total"),
        make_kpi_card("% Expedição", pct_exped_s, "Expedido ÷ Total"),
        make_kpi_card("Lead Time Médio", lt_s, "Expedição − Recebimento (dias)"),
    ]


def build_insights(df: pd.DataFrame):
    if df is None or len(df) == 0:
        return "Sem dados suficientes."

    total = df["peso_total_kg"].sum()
    produzido = df["produzido_kg"].sum()
    exped = df["peso_exped_kg"].sum()
    wip = max(0.0, produzido - exped)
    backlog = max(0.0, total - produzido)

    atraso = df.loc[df["atrasado"], "peso_total_kg"].sum()

    wip_only = df[df["etapa_atual"].isin(["Preparação", "Montagem", "Solda", "Acabamento", "Pintura (pronto p/ expedir)", "Não iniciado"])]
    bottleneck = wip_only.groupby("etapa_atual")["peso_total_kg"].sum().sort_values(ascending=False)
    bottleneck_stage = bottleneck.index[0] if len(bottleneck) else "-"
    bottleneck_kg = float(bottleneck.iloc[0]) if len(bottleneck) else 0.0

    os_wip = df.groupby("os_cliente")["saldo_a_expedir_kg"].sum().sort_values(ascending=False)
    os_wip_name = os_wip.index[0] if len(os_wip) else "-"
    os_wip_kg = float(os_wip.iloc[0]) if len(os_wip) else 0.0

    return html.Ul([
        html.Li([html.B("Gargalo atual: "), f"{bottleneck_stage} ({fmt_kg(bottleneck_kg)})"]),
        html.Li([html.B("WIP total: "), fmt_kg(wip)]),
        html.Li([html.B("Backlog de produção: "), fmt_kg(backlog)]),
        html.Li([html.B("Peso em atraso (pela data de entrega): "), fmt_kg(atraso)]),
        html.Li([html.B("OS com maior WIP: "), f"{os_wip_name} ({fmt_kg(os_wip_kg)})"]),
    ])


def build_table_payload(df: pd.DataFrame):
    cols = [
        "cliente", "os_cliente", "tag", "situacao_desenho",
        "desenho_pai",
        "peso_total_kg", "produzido_kg", "peso_exped_kg",
        "saldo_a_produzir_kg", "saldo_a_expedir_kg",
        "etapa_atual",
        "dt_receb", "dt_entrega", "dt_exped",
        "leadtime_dias", "atrasado"
    ]

    tmp = df.copy()
    for c in cols:
        if c not in tmp.columns:
            tmp[c] = pd.NA

    out = tmp[cols].copy()

    # Formata pesos como inteiro sem decimais
    for c in ["peso_total_kg", "produzido_kg", "peso_exped_kg", "saldo_a_produzir_kg", "saldo_a_expedir_kg"]:
        out[c] = out[c].map(lambda v: str(int(round(float(v)))) if pd.notna(v) else "")

    for c in ["dt_receb", "dt_entrega", "dt_exped"]:
        out[c] = pd.to_datetime(out[c], errors="coerce").dt.strftime("%Y-%m-%d")

    data = out.head(300).to_dict("records")
    columns = [{"name": c, "id": c} for c in out.columns]
    return data, columns
