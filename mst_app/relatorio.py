import csv
import io
import json
from datetime import datetime

NOME_DO_PROJETO = "ConstrutorMST"


def linhas_das_conexoes(rede):
    linhas = []
    for ordem, conexao in enumerate(sorted(rede.conexoes, key=lambda c: c.distancia_km), start=1):
        linhas.append(
            {
                "Ordem": ordem,
                "Origem": rede.nome_da_estacao(conexao.origem),
                "Destino": rede.nome_da_estacao(conexao.destino),
                "Distancia (km)": round(conexao.distancia_km, 4),
                "Custo (R$)": round(conexao.distancia_km * rede.custo_por_km, 2),
                "Rota real": "Sim" if conexao.rota_real else "Nao",
            }
        )
    return linhas


def linhas_das_estacoes(rede):
    return [
        {
            "Indice": indice,
            "Nome": estacao.nome,
            "Latitude": round(estacao.lat, 6),
            "Longitude": round(estacao.lon, 6),
            "Conexoes na MST": len(rede.conexoes_por_estacao(indice)),
        }
        for indice, estacao in enumerate(rede.estacoes)
    ]


def exportar_csv(rede):
    linhas = linhas_das_conexoes(rede)
    saida = io.StringIO()
    campos = ["Ordem", "Origem", "Destino", "Distancia (km)", "Custo (R$)", "Rota real"]
    escritor = csv.DictWriter(saida, fieldnames=campos, lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(linhas)
    return saida.getvalue()


def exportar_json(rede):
    resultado = rede.resultado
    dados = {
        "projeto": NOME_DO_PROJETO,
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "algoritmo": resultado.algoritmo,
        "modo_de_distancia": rede.modo,
        "tipo_de_rede": rede.tipo_rede,
        "custo_por_km": rede.custo_por_km,
        "metricas": resultado.resumo(),
        "estacoes": [estacao.como_dict() for estacao in rede.estacoes],
        "conexoes": linhas_das_conexoes(rede),
        "comparacao": {
            nome: valor.resumo() for nome, valor in rede.comparacao.resultados.items()
        },
        "custos_equivalentes": rede.comparacao.custos_equivalentes,
    }
    return json.dumps(dados, ensure_ascii=False, indent=2)


def tabela_markdown(linhas):
    if not linhas:
        return "_Sem dados._"
    cabecalho = list(linhas[0].keys())
    partes = ["| " + " | ".join(cabecalho) + " |", "| " + " | ".join("---" for _ in cabecalho) + " |"]
    for linha in linhas:
        partes.append("| " + " | ".join(str(linha[coluna]) for coluna in cabecalho) + " |")
    return "\n".join(partes)


def gerar_relatorio_markdown(rede):
    resultado = rede.resultado
    comparacao = rede.comparacao
    origem_das_distancias = (
        "rotas reais do OpenStreetMap" if rede.usa_rotas_reais else "distancia em linha reta (Haversine)"
    )

    partes = [
        f"# Relatorio de execucao - {NOME_DO_PROJETO}",
        "",
        f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}.",
        "",
        "## Configuracao",
        "",
        f"- Algoritmo executado: **{resultado.algoritmo}**",
        f"- Origem das distancias: {origem_das_distancias}",
        f"- Tipo de malha viaria: {rede.tipo_rede}",
        f"- Custo por km: R$ {rede.custo_por_km:,.2f}",
        "",
        "## Metricas da MST",
        "",
        f"- Vertices (estacoes): {resultado.num_vertices}",
        f"- Arestas candidatas no grafo: {resultado.num_arestas_grafo}",
        f"- Arestas selecionadas: {resultado.num_arestas_mst}",
        f"- Distancia total: {resultado.custo_total:.3f} km",
        f"- Custo estimado: R$ {rede.custo_total:,.2f}",
        f"- Componentes conexas: {resultado.componentes}",
        f"- Arvore geradora completa: {'sim' if resultado.e_arvore_geradora else 'nao'}",
        f"- Tempo de execucao: {resultado.tempo_ms:.3f} ms",
        "",
        "## Comparacao entre algoritmos",
        "",
        tabela_markdown(comparacao.como_linhas()),
        "",
        f"- Custos equivalentes: {'sim' if comparacao.custos_equivalentes else 'nao'}",
        f"- Diferenca de custo: {comparacao.diferenca_custo:.9f} km",
        f"- Arestas em comum: {len(comparacao.arestas_comuns)}",
        "",
        "## Estacoes",
        "",
        tabela_markdown(linhas_das_estacoes(rede)),
        "",
        "## Conexoes selecionadas",
        "",
        tabela_markdown(linhas_das_conexoes(rede)),
        "",
    ]
    return "\n".join(partes)
