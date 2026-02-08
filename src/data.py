"""
Leitura e preparação dos dados:
- Lê Excel local
- Padroniza colunas
- Converte datas/números
- Calcula métricas em KG (sem casas decimais)
- Aplica filtros (OS, TAG, Situação, datas, desenho contém)
"""

import io
import re
from datetime import date

import pandas as pd


def normalize_col(c: str) -> str:
    c = str(c).strip().replace("\n", " ")
    c = re.sub(r"\s+", " ", c)
    return c


def safe_to_datetime(s):
    return pd.to_datetime(s, errors="coerce")


def safe_to_numeric(s):
    return pd.to_numeric(s, errors="coerce")


def load_excel_local(path: str) -> pd.DataFrame:
    """
    Lê Excel do disco.
    Tenta aba CONSOLIDADO; se não existir, usa a primeira aba.
    """
    xls = pd.ExcelFile(path)
    sheet = "CONSOLIDADO" if "CONSOLIDADO" in xls.sheet_names else xls.sheet_names[0]
    df = pd.read_excel(path, sheet_name=sheet)
    df.columns = [normalize_col(c) for c in df.columns]
    return df


def prepare_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara a base para o dashboard.
    Tudo em KG (inteiro no display; internamente float ok).
    """
    df = df_raw.copy()

    col_map = {
        "DATA RECEBIMENTO DA GUIA": "dt_receb",
        "DATA DE ENTREGA": "dt_entrega",
        "DATA EXPEDIÇÃO": "dt_exped",

        "PESO TOTAL ( KG)": "peso_total_kg",
        "PESO TOTAL ( KG )": "peso_total_kg",
        "PESO TOTAL (KG)": "peso_total_kg",
        "PESO EXPEDIDO (KG)": "peso_exped_kg",

        "CLIENTE": "cliente",
        "OS_CLIENTE": "os_cliente",
        "TAG": "tag",
        "SITUAÇÃO DO DESENHO": "situacao_desenho",
        "N° DESENHO PAI": "desenho_pai",
        "DESCRIÇÃO DO DESENHO": "descricao",  # pode existir, mas não filtraremos por ela

        # Etapas (kg)
        "DESENHOS PREPARADOS (KG)": "prep_kg",
        "DESENHOS MONTADOS (KG)": "mont_kg",
        "DESENHOS SOLDADOS (KG)": "sold_kg",
        "DESENHOS ACABADOS (KG)": "acab_kg",
        "DESENHOS PITADOS (KG)": "pint_kg",
        "DESENHOS PINTADOS (KG)": "pint_kg",
    }

    rename = {c: col_map[c] for c in df.columns if c in col_map}
    df = df.rename(columns=rename)

    required = [
        "dt_receb", "dt_entrega", "dt_exped",
        "peso_total_kg", "peso_exped_kg",
        "prep_kg", "mont_kg", "sold_kg", "acab_kg", "pint_kg","cliente",
        "os_cliente", "tag", "situacao_desenho",
        "desenho_pai", "descricao",
    ]
    for r in required:
        if r not in df.columns:
            df[r] = pd.NA

    # Types
    df["dt_receb"] = safe_to_datetime(df["dt_receb"])
    df["dt_entrega"] = safe_to_datetime(df["dt_entrega"])
    df["dt_exped"] = safe_to_datetime(df["dt_exped"])

    for c in ["peso_total_kg", "peso_exped_kg", "prep_kg", "mont_kg", "sold_kg", "acab_kg", "pint_kg"]:
        df[c] = safe_to_numeric(df[c]).fillna(0.0)

    # Produzido (kg): última etapa atingida
    df["produzido_kg"] = df[["pint_kg", "acab_kg", "sold_kg", "mont_kg", "prep_kg"]].max(axis=1)

    # Etapa atual (gargalo)
    def stage_of_row(r):
        if r["peso_exped_kg"] > 0:
            return "Expedido"
        if r["pint_kg"] > 0:
            return "Pintura (pronto p/ expedir)"
        if r["acab_kg"] > 0:
            return "Acabamento"
        if r["sold_kg"] > 0:
            return "Solda"
        if r["mont_kg"] > 0:
            return "Montagem"
        if r["prep_kg"] > 0:
            return "Preparação"
        return "Não iniciado"

    df["etapa_atual"] = df.apply(stage_of_row, axis=1)

    # Saldos
    df["saldo_a_produzir_kg"] = (df["peso_total_kg"] - df["produzido_kg"]).clip(lower=0.0)
    df["saldo_a_expedir_kg"] = (df["produzido_kg"] - df["peso_exped_kg"]).clip(lower=0.0)

    # Lead time
    df["leadtime_dias"] = (df["dt_exped"] - df["dt_receb"]).dt.days

    # Atraso
    today = pd.Timestamp(date.today())
    df["atrasado"] = (df["dt_entrega"].notna()) & (df["dt_entrega"] < today) & (df["peso_exped_kg"] <= 0)

    # Text columns
    for c in ["os_cliente", "tag", "situacao_desenho", "desenho_pai", "descricao"]:
        df[c] = df[c].astype("string").fillna("")

    return df


def df_to_store(df: pd.DataFrame) -> str:
    """
    Serializa DF para Store (JSON split). Datas em ISO.
    """
    return df.to_json(orient="split", date_format="iso")


def df_from_store(data: str) -> pd.DataFrame:
    """
    Deserializa DF do Store e garante tipos corretos.
    """
    df = pd.read_json(io.StringIO(data), orient="split")

    # Datas
    for c in ["dt_receb", "dt_entrega", "dt_exped"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    # Numéricas importantes
    num_cols = [
        "peso_total_kg", "peso_exped_kg",
        "prep_kg", "mont_kg", "sold_kg", "acab_kg", "pint_kg",
        "produzido_kg", "saldo_a_produzir_kg", "saldo_a_expedir_kg",
        "leadtime_dias"
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Texto
    for c in ["cliente","os_cliente", "tag", "situacao_desenho", "desenho_pai", "descricao", "etapa_atual"]:
        if c in df.columns:
            df[c] = df[c].astype("string").fillna("")

    return df


def apply_filters(        
    df: pd.DataFrame,    
    clientes, 
    os_values,
    tag_values,
    situacoes,
    dt_receb_range,
    dt_exped_range,
    desenho_text,
):
    """
    Filtros ativos:
    - OS Cliente (dropdown multi)
    - TAG (dropdown multi)
    - Situação do desenho (dropdown multi)
    - intervalo de dt_receb
    - intervalo de dt_exped
    - desenho_pai contém (texto)
    """
    out = df.copy()
    if clientes:
        out = out[out["cliente"].isin(clientes)]

    if os_values:
        out = out[out["os_cliente"].isin(os_values)]
    if tag_values:
        out = out[out["tag"].isin(tag_values)]
    if situacoes:
        out = out[out["situacao_desenho"].isin(situacoes)]

    # Datas
    if dt_receb_range and len(dt_receb_range) == 2:
        s, e = dt_receb_range
        if s:
            out = out[out["dt_receb"] >= pd.to_datetime(s)]
        if e:
            out = out[out["dt_receb"] <= pd.to_datetime(e)]

    if dt_exped_range and len(dt_exped_range) == 2:
        s, e = dt_exped_range
        if s:
            out = out[out["dt_exped"] >= pd.to_datetime(s)]
        if e:
            out = out[out["dt_exped"] <= pd.to_datetime(e)]

    # desenho contém
    if desenho_text:
        t = str(desenho_text).strip().lower()
        out = out[out["desenho_pai"].str.lower().str.contains(re.escape(t), na=False)]

    return out


