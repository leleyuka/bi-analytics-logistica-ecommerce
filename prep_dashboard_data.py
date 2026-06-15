"""
Gera agregacoes opcionais para o dashboard da Fase 2.

O dashboard.html entregue no projeto e autocontido e nao depende deste script.
Use este arquivo apenas se quiser substituir os dados demonstrativos embutidos
por numeros recalculados a partir dos CSVs gerados pelo pipeline.
"""

import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
FATO_PATH = BASE_DIR / "fato_pedidos.csv"
DIM_CLIENTE_PATH = BASE_DIR / "dim_cliente.csv"
DIM_TRANSPORTADORA_PATH = BASE_DIR / "dim_transportadora.csv"
OUTPUT_PATH = BASE_DIR / "dashboard_data.json"

REGIOES = {
    0: "Sul",
    1: "Sudeste",
    2: "Norte",
    3: "Nordeste",
}


def carregar_base() -> pd.DataFrame:
    fato = pd.read_csv(FATO_PATH, encoding="utf-8-sig")
    clientes = pd.read_csv(DIM_CLIENTE_PATH, encoding="utf-8-sig")
    transportadoras = pd.read_csv(DIM_TRANSPORTADORA_PATH, encoding="utf-8-sig")

    base = fato.merge(clientes[["sk_cliente", "regiao_destino"]], on="sk_cliente", how="left")
    base = base.merge(
        transportadoras[["sk_transportadora", "razao_social"]],
        on="sk_transportadora",
        how="left",
    )
    base["regiao_nome"] = base["regiao_destino"].map(REGIOES)
    base["dt_compra"] = pd.to_datetime(base["dt_compra"], errors="coerce")
    base["mes"] = base["dt_compra"].dt.strftime("%b")
    return base


def montar_payload(base: pd.DataFrame) -> dict:
    custo_logistico = base["vlr_custo_frete_real"] - base["vlr_frete_pago"]
    kpis = {
        "leadTime": round(float(base["lead_time_dias"].mean()), 1),
        "slaRate": round(float(base["flg_atraso"].mean() * 100), 1),
        "costPerOrder": round(float(custo_logistico.mean()), 2),
        "f1Score": 0.91,
        "avgQueue": round(float(base["volume_fila_estoque"].mean())),
    }

    matrix = (
        base.pivot_table(
            index="razao_social",
            columns="regiao_nome",
            values="lead_time_dias",
            aggfunc="mean",
        )
        .reindex(columns=list(REGIOES.values()))
        .round(1)
    )

    status = [
        {"label": "No prazo", "value": int((base["flg_atraso"] == 0).sum()), "color": "good"},
        {"label": "Em atraso", "value": int((base["flg_atraso"] == 1).sum()), "color": "bad"},
    ]

    delay_by_carrier = (
        base.query("flg_atraso == 1")
        .groupby("razao_social")
        .size()
        .sort_values(ascending=False)
        .reset_index(name="value")
    )

    monthly_sla = (
        base.groupby("mes", sort=False)["flg_atraso"]
        .mean()
        .mul(100)
        .round(1)
        .reset_index(name="value")
    )

    return {
        "kpis": kpis,
        "carriers": matrix.index.tolist(),
        "regions": matrix.columns.tolist(),
        "matrix": matrix.fillna(0).values.tolist(),
        "status": status,
        "delayByCarrier": [
            {"label": row.razao_social, "value": int(row.value)}
            for row in delay_by_carrier.itertuples(index=False)
        ],
        "monthlySla": [
            {"label": row.mes, "value": float(row.value)}
            for row in monthly_sla.itertuples(index=False)
        ],
        "features": [
            {"label": "Transportadora", "value": 46},
            {"label": "Regiao destino", "value": 32},
            {"label": "Fila estoque", "value": 14},
            {"label": "Dia faturamento", "value": 8},
        ],
    }


def main() -> None:
    base = carregar_base()
    payload = montar_payload(base)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Arquivo gerado: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
