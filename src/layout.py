"""
Layout sem upload.
Filtros:
- Cliente (dropdown multi)
- OS Cliente (dropdown multi)
- TAG (dropdown multi)
- Situação do desenho (dropdown multi)
- Datas Recebimento/Expedição (range)
- Desenho PAI contém (texto)
Botão: Limpar filtros
"""

from dash import dcc, html, dash_table


def build_layout():
    return html.Div(
        id="app-root",
        className="theme-light",
        children=[
            dcc.Store(id="store-df"),
            dcc.Store(id="store-theme", data="light"),
            dcc.Store(id="store-filter-defaults"),

            # Disparador de inicialização (1x)
            dcc.Interval(id="page-load", interval=500, n_intervals=0, max_intervals=1),

            html.Div(
                className="topbar",
                children=[
                    html.Div(
                        className="topbar-left",
                        children=[
                            html.Div(
                                className="logo-title",
                                children=[
                                    html.Img(src="/assets/logo.png", className="logo-img"),
                                    html.H2("Dashboard — Avanço Físico (KG)", className="title"),
                        ],
                    ),
                    html.Div(id="load-status", className="subtitle"),
                ],
            ),
                    html.Div(
                        className="topbar-right",
                        children=[
                            html.Div(
                                className="theme-toggle",
                                children=[
                                    html.Span("Claro"),
                                    dcc.Checklist(
                                        id="toggle-theme",
                                        options=[{"label": "", "value": "dark"}],
                                        value=[],
                                        inputStyle={"margin-right": "6px"},
                                    ),
                                    html.Span("Escuro"),
                                ],
                            )
                        ],
                    ),
                ],
            ),

            # Filtros
            html.Div(
                className="filters",
                children=[
                    html.Div(className="filter", children=[
                        html.Label("Cliente"),
                        dcc.Dropdown(id="f-cliente", multi=True, placeholder="Selecione..."),
                    ]),
                    html.Div(className="filter", children=[
                        html.Label("OS Cliente"),
                        dcc.Dropdown(id="f-os", multi=True, placeholder="Selecione..."),
                    ]),
                    html.Div(className="filter", children=[
                        html.Label("TAG"),
                        dcc.Dropdown(id="f-tag", multi=True, placeholder="Selecione..."),
                    ]),
                    html.Div(className="filter", children=[
                        html.Label("Situação do Desenho"),
                        dcc.Dropdown(id="f-situacao", multi=True, placeholder="Selecione..."),
                    ]),
                    html.Div(className="filter", children=[
                        html.Label("Recebimento (intervalo)"),
                        dcc.DatePickerRange(id="f-dt-receb", display_format="YYYY-MM-DD"),
                    ]),
                    html.Div(className="filter", children=[
                        html.Label("Expedição (intervalo)"),
                        dcc.DatePickerRange(id="f-dt-exped", display_format="YYYY-MM-DD"),
                    ]),
                    html.Div(className="filter", children=[
                        html.Label("Desenho PAI contém"),
                        dcc.Input(id="f-desenho", type="text", placeholder="Ex: 71989390", className="text-input"),
                    ]),
                    html.Div(className="filter", children=[
                        html.Label("Ações"),
                        html.Button("Limpar filtros", id="btn-clear", className="btn-clear", n_clicks=0),
                    ]),
                ],
            ),

            # KPIs
            html.Div(id="kpi-grid", className="kpi-grid", children=[]),

            html.Div(
                className="grid-2",
                children=[
                    html.Div(className="panel", children=[
                        html.H3("Funil — Escopo que atingiu cada etapa (kg)"),
                        dcc.Graph(id="g-funnel"),
                    ]),
                    html.Div(className="panel", children=[
                        html.H3("Gargalo/WIP por Etapa Atual (kg)"),
                        dcc.Graph(id="g-wip-stage"),
                    ]),
                ],
            ),

            html.Div(
                className="grid-2",
                children=[
                    html.Div(className="panel", children=[
                        html.H3("Série Temporal — Recebido vs Expedido (kg)"),
                        dcc.Graph(id="g-timeseries"),
                    ]),
                    html.Div(className="panel", children=[
                        html.H3("Top 10 OS — Saldo a Produzir (kg)"),
                        dcc.Graph(id="g-top-os"),
                    ]),
                ],
            ),

            html.Div(
                className="grid-2",
                children=[
                    html.Div(className="panel", children=[
                        html.H3("Lead Time (dias) — Distribuição"),
                        dcc.Graph(id="g-leadtime"),
                    ]),
                    html.Div(className="panel", children=[
                        html.H3("Taxas de Conversão por Etapa"),
                        dcc.Graph(id="g-conv"),
                    ]),
                ],
            ),

            html.Div(
                className="grid-2",
                children=[
                    html.Div(className="panel", children=[
                        html.H3("Insights automáticos"),
                        html.Div(id="insights", className="insights-box"),
                    ]),
                    html.Div(className="panel", children=[
                        html.H3("Tabela — Itens filtrados (amostra)"),
                        dash_table.DataTable(
                            id="tbl",
                            page_size=12,
                            style_table={"overflowX": "auto"},
                            style_cell={"minWidth": "120px", "width": "120px", "maxWidth": "260px", "whiteSpace": "normal"},
                            style_header={"fontWeight": "bold"},
                        )
                    ]),
                ],
            ),
        ],
    )

