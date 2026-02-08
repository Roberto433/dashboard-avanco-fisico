# 📊 Dashboard — Avanço Físico (KG)

Dashboard interativo desenvolvido em **Python + Dash** para acompanhamento de avanço físico de produção (em quilogramas), com filtros dinâmicos, KPIs, gráficos analíticos e tabela detalhada.

🌐 **Acesse o dashboard online:**  
https://dashboard-avanco-fisico.onrender.com

> ⚠️ Observação: No plano gratuito do Render, o serviço pode “dormir” após um período sem acesso. A primeira abertura pode levar alguns segundos.

---

## 🎯 Principais Funcionalidades

### 🔎 Filtros Interativos

- Cliente
- OS Cliente
- TAG
- Situação do Desenho
- Intervalo de Recebimento
- Intervalo de Expedição
- Desenho PAI (busca por texto)

### 📌 Indicadores (KPIs)

- Peso Total (kg)
- Produzido (kg)
- Expedido (kg)
- Saldo a Produzir (kg)
- Saldo a Expedir (kg)

### 📈 Análises Visuais

- Funil de avanço por etapa (kg)
- Gargalo / WIP por etapa
- Série temporal (Recebido vs Expedido)
- Top OS por saldo a produzir
- Distribuição de Lead Time (dias)
- Taxas de conversão entre etapas

### 🧠 Insights Automáticos

Resumo inteligente destacando gargalos, backlog e ordens críticas.

### 🌙 Tema Claro / Escuro

Alternância de visual para melhor leitura.

---

## 🖥️ Como Rodar Localmente

### 1️⃣ Criar ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 📁 Estrutura do Projeto

dashboard-avanco-fisico/
│
├── app.py
├── requirements.txt
├── CONSOLIDADO_Avanco_Fisico_2026.xlsx
│
├── src/
│ ├── data.py
│ ├── filters.py
│ ├── charts.py
│ └── insights.py
│
└── assets/
├── style.css
└── logo.png

---

## 👤 Autor

Roberto Ferreira Costa
Projeto interno para acompanhamento de produção.
