"""
Opções e limites para filtros.
"""

import pandas as pd


def build_filter_options_and_bounds(df: pd.DataFrame):
    clientes = sorted([x for x in df["cliente"].unique() if x])
    os_list = sorted([x for x in df["os_cliente"].unique() if x])
    tag_list = sorted([x for x in df["tag"].unique() if x])
    situacoes = sorted([x for x in df["situacao_desenho"].unique() if x])

    def opt(vals):
        return [{"label": v, "value": v} for v in vals]

    receb_min = pd.to_datetime(df["dt_receb"].min(), errors="coerce")
    receb_max = pd.to_datetime(df["dt_receb"].max(), errors="coerce")
    exp_min = pd.to_datetime(df["dt_exped"].min(), errors="coerce")
    exp_max = pd.to_datetime(df["dt_exped"].max(), errors="coerce")

    receb_min = receb_min.date() if pd.notna(receb_min) else None
    receb_max = receb_max.date() if pd.notna(receb_max) else None
    exp_min = exp_min.date() if pd.notna(exp_min) else None
    exp_max = exp_max.date() if pd.notna(exp_max) else None

    defaults = {"dt_defaults": [None, None, None, None]}

    return (
        opt(clientes),
        opt(os_list),
        opt(tag_list),
        opt(situacoes),
        receb_min,
        receb_max,
        exp_min,
        exp_max,
        defaults,
    )
