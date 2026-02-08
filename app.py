"""
App Dash (sem upload):
- Lê o arquivo CONSOLIDADO_Avanco_Fisico_2026.xlsx na inicialização
- Monta layout
- Popula filtros
- Atualiza KPIs, gráficos, insights e tabela
- Botão "Limpar filtros"
"""

from pathlib import Path

from dash import Dash, Input, Output, State, no_update

from src.data import load_excel_local, prepare_df, df_to_store, df_from_store, apply_filters
from src.layout import build_layout
from src.filters import build_filter_options_and_bounds
from src.charts import (
    plot_template,
    fig_empty,
    build_funnel_fig,
    build_wip_stage_fig,
    build_timeseries_fig,
    build_top_os_fig,
    build_leadtime_fig,
    build_conversion_fig,
)
from src.insights import build_insights, compute_kpis, build_table_payload


APP_FILE = "CONSOLIDADO_Avanco_Fisico_2026.xlsx"

# ✅ Crie o app UMA ÚNICA VEZ
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.layout = build_layout()


def load_initial_store_payload():
    """
    Carrega e prepara o dataframe ao subir o servidor.
    Retorna payload serializado para dcc.Store.
    """
    base_path = Path(__file__).resolve().parent / APP_FILE
    if not base_path.exists():
        # O app sobe, mas mostrará mensagem e gráficos vazios
        return None, f"❌ Arquivo não encontrado: {base_path}"

    raw = load_excel_local(str(base_path))
    df = prepare_df(raw)
    return df_to_store(df), f"✅ Base carregada: {APP_FILE} — {len(df):,} linhas"


# Carrega base ao iniciar (processo do servidor)
INITIAL_STORE_DATA, INITIAL_STATUS = load_initial_store_payload()


@app.callback(
    Output("store-df", "data"),
    Output("load-status", "children"),
    Input("page-load", "n_intervals"),
    prevent_initial_call=False,
)
def init_data(_n):
    """
    Inicializa o store-df na abertura do app.
    Usa Interval para disparar uma vez.
    """
    if INITIAL_STORE_DATA is None:
        return no_update, INITIAL_STATUS
    return INITIAL_STORE_DATA, INITIAL_STATUS


@app.callback(
    Output("store-theme", "data"),
    Output("app-root", "className"),
    Input("toggle-theme", "value"),
)
def set_theme(toggle_value):
    theme = "dark" if (toggle_value and "dark" in toggle_value) else "light"
    return theme, ("theme-dark" if theme == "dark" else "theme-light")


@app.callback(
    Output("f-cliente", "options"),
    Output("f-os", "options"),
    Output("f-tag", "options"),
    Output("f-situacao", "options"),
    Output("f-dt-receb", "min_date_allowed"),
    Output("f-dt-receb", "max_date_allowed"),
    Output("f-dt-exped", "min_date_allowed"),
    Output("f-dt-exped", "max_date_allowed"),
    Output("store-filter-defaults", "data"),
    Input("store-df", "data"),
)
def init_filters(store_data):
    """
    Popula dropdowns e limites de datas.
    Também salva defaults para o botão de limpar filtros.
    """
    if not store_data:
        return [], [], [], [], None, None, None, None, {"dt_defaults": [None, None, None, None]}

    df = df_from_store(store_data)

    (
        opt_cliente,
        opt_os,
        opt_tag,
        opt_situacao,
        receb_min,
        receb_max,
        exp_min,
        exp_max,
        defaults,
    ) = build_filter_options_and_bounds(df)

    return opt_cliente, opt_os, opt_tag, opt_situacao, receb_min, receb_max, exp_min, exp_max, defaults


@app.callback(
    Output("f-cliente", "value"),
    Output("f-os", "value"),
    Output("f-tag", "value"),
    Output("f-situacao", "value"),
    Output("f-dt-receb", "start_date"),
    Output("f-dt-receb", "end_date"),
    Output("f-dt-exped", "start_date"),
    Output("f-dt-exped", "end_date"),
    Output("f-desenho", "value"),
    Input("btn-clear", "n_clicks"),
    State("store-filter-defaults", "data"),
    prevent_initial_call=True,
)
def clear_filters(_n_clicks, defaults):
    """
    Limpa todos os filtros.
    """
    # defaults são opcionais aqui; datas resetam para None mesmo
    return [], [], [], [], None, None, None, None, ""


@app.callback(
    Output("kpi-grid", "children"),
    Output("g-funnel", "figure"),
    Output("g-wip-stage", "figure"),
    Output("g-timeseries", "figure"),
    Output("g-top-os", "figure"),
    Output("g-leadtime", "figure"),
    Output("g-conv", "figure"),
    Output("insights", "children"),
    Output("tbl", "data"),
    Output("tbl", "columns"),
    Input("store-df", "data"),
    Input("store-theme", "data"),
    Input("f-cliente", "value"),
    Input("f-os", "value"),
    Input("f-tag", "value"),
    Input("f-situacao", "value"),
    Input("f-dt-receb", "start_date"),
    Input("f-dt-receb", "end_date"),
    Input("f-dt-exped", "start_date"),
    Input("f-dt-exped", "end_date"),
    Input("f-desenho", "value"),
)
def render(store_data, theme,
           f_cliente, f_os, f_tag, f_situacao,
           receb_s, receb_e, exped_s, exped_e,
           f_desenho):
    """
    Renderiza tudo com base no dataframe e nos filtros.
    """
    template = plot_template(theme)

    if not store_data:
        kpis = compute_kpis(None)
        empty = fig_empty(template, "Base não carregada. Verifique o arquivo Excel na pasta do projeto.")
        return kpis, empty, empty, empty, empty, empty, empty, "Sem dados.", [], []

    df = df_from_store(store_data)

    df_f = apply_filters(
        df,
        clientes=f_cliente or [],
        os_values=f_os or [],
        tag_values=f_tag or [],
        situacoes=f_situacao or [],
        dt_receb_range=[receb_s, receb_e],
        dt_exped_range=[exped_s, exped_e],
        desenho_text=f_desenho,
    )

    kpis = compute_kpis(df_f)

    fig_funnel = build_funnel_fig(df_f, template)
    fig_wip = build_wip_stage_fig(df_f, template)
    fig_ts = build_timeseries_fig(df_f, template)
    fig_top_os = build_top_os_fig(df_f, template)
    fig_lt = build_leadtime_fig(df_f, template)
    fig_conv = build_conversion_fig(df_f, template)

    insights = build_insights(df_f)

    tbl_data, tbl_cols = build_table_payload(df_f)

    return kpis, fig_funnel, fig_wip, fig_ts, fig_top_os, fig_lt, fig_conv, insights, tbl_data, tbl_cols


if __name__ == "__main__":
    # Local: roda com o servidor embutido
    app.run_server(debug=True, port=8050)

