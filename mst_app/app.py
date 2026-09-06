import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

import ui
from analise import ALGORITMOS, comparar_algoritmos, executar_benchmark
from exemplos import ESTACOES_DEMONSTRACAO, GRAFOS_DIDATICOS, construir_grafo_didatico
from geo import coordenada_valida
from mapa import criar_mapa
from rede import (
    MODO_HAVERSINE,
    MODO_ROTA,
    ErroDeRede,
    Estacao,
    arestas_candidatas,
    criar_estacao,
    montar_rede,
)
from relatorio import (
    exportar_csv,
    exportar_json,
    gerar_relatorio_markdown,
    linhas_das_conexoes,
    linhas_das_estacoes,
)
from rotas import ErroDeRotas, baixar_grafo_area

CENTRO_INICIAL = (-15.7797, -47.9297)
ZOOM_INICIAL = 12
TIPOS_DE_MALHA = {
    "Vias para veiculos": "drive",
    "Vias para pedestres": "walk",
    "Vias para bicicletas": "bike",
}
ROTULO_DOS_MODOS = {
    MODO_ROTA: "Rotas reais (OpenStreetMap)",
    MODO_HAVERSINE: "Linha reta (Haversine)",
}

st.set_page_config(page_title="ConstrutorMST", page_icon="🌐", layout="wide")


@st.cache_resource(show_spinner=False)
def carregar_grafo_ruas(pontos, margem_km, tipo_rede):
    return baixar_grafo_area(list(pontos), margem_km=margem_km, tipo_rede=tipo_rede)


def inicializar_estado():
    padroes = {
        "estacoes": [],
        "rede": None,
        "erro": None,
        "aviso": None,
        "benchmark": None,
        "algoritmo": "Kruskal",
        "modo": MODO_ROTA,
        "malha": "Vias para veiculos",
        "custo_por_km": 1000.0,
        "margem_km": 0.5,
        "mostrar_candidatas": False,
    }
    for chave, valor in padroes.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def invalidar_rede():
    st.session_state.rede = None


def adicionar_estacao(lat, lon, nome=None):
    try:
        estacao = criar_estacao(st.session_state.estacoes, lat, lon, nome)
    except ErroDeRede as erro:
        st.session_state.aviso = str(erro)
        return False
    st.session_state.estacoes.append(estacao)
    st.session_state.aviso = None
    invalidar_rede()
    return True


def carregar_demonstracao():
    st.session_state.estacoes = []
    for ponto in ESTACOES_DEMONSTRACAO:
        adicionar_estacao(ponto["lat"], ponto["lon"], ponto["nome"])
    st.session_state.aviso = None
    st.session_state.erro = None


def limpar_projeto():
    st.session_state.estacoes = []
    st.session_state.rede = None
    st.session_state.erro = None
    st.session_state.aviso = None
    st.session_state.benchmark = None


def mensagem_de_falha(erro):
    if isinstance(erro, ErroDeRotas):
        return (
            f"{erro} Verifique a conexao com a internet ou selecione o modo "
            "'Linha reta (Haversine)' na barra lateral para continuar sem o OpenStreetMap."
        )
    return str(erro)


def construir_rede():
    pontos = tuple(
        (round(estacao.lat, 6), round(estacao.lon, 6)) for estacao in st.session_state.estacoes
    )
    margem = float(st.session_state.margem_km)
    tipo_rede = TIPOS_DE_MALHA[st.session_state.malha]

    def carregador(_pontos):
        return carregar_grafo_ruas(pontos, margem, tipo_rede)

    try:
        with st.spinner("Calculando distancias e construindo a arvore geradora minima..."):
            rede = montar_rede(
                estacoes=st.session_state.estacoes,
                algoritmo=st.session_state.algoritmo,
                modo=st.session_state.modo,
                custo_por_km=float(st.session_state.custo_por_km),
                margem_km=margem,
                tipo_rede=tipo_rede,
                obter_grafo_ruas=carregador if st.session_state.modo == MODO_ROTA else None,
            )
    except (ErroDeRede, ErroDeRotas, ValueError) as erro:
        st.session_state.rede = None
        st.session_state.erro = mensagem_de_falha(erro)
    except Exception as erro:
        st.session_state.rede = None
        st.session_state.erro = f"Falha inesperada ao construir a rede: {erro}"
    else:
        st.session_state.rede = rede
        st.session_state.erro = None
        st.session_state.aviso = None


def barra_lateral():
    with st.sidebar:
        st.markdown("### Configuracao da execucao")
        st.radio("Algoritmo de MST", options=list(ALGORITMOS), key="algoritmo")
        st.radio(
            "Origem das distancias",
            options=list(ROTULO_DOS_MODOS),
            format_func=lambda valor: ROTULO_DOS_MODOS[valor],
            key="modo",
            help="O modo Haversine funciona sem internet e e util para demonstracoes rapidas.",
        )
        if st.session_state.modo == MODO_ROTA:
            st.selectbox("Malha viaria", options=list(TIPOS_DE_MALHA), key="malha")
            st.slider("Margem da area baixada (km)", 0.2, 3.0, key="margem_km", step=0.1)
        st.number_input(
            "Custo por km (R$)", min_value=0.0, step=100.0, key="custo_por_km", format="%.2f"
        )
        st.toggle("Mostrar conexoes candidatas no mapa", key="mostrar_candidatas")

        st.divider()
        st.markdown("### Estacoes")
        total = len(st.session_state.estacoes)
        st.caption(f"{total} estacao(oes) cadastradas. Clique no mapa para adicionar novas.")

        with st.expander("Adicionar por coordenada"):
            nome = st.text_input("Nome", key="nome_manual", placeholder="Terminal Norte")
            coluna_lat, coluna_lon = st.columns(2)
            latitude = coluna_lat.number_input(
                "Latitude", value=CENTRO_INICIAL[0], format="%.6f", key="lat_manual"
            )
            longitude = coluna_lon.number_input(
                "Longitude", value=CENTRO_INICIAL[1], format="%.6f", key="lon_manual"
            )
            if st.button("Adicionar estacao", width="stretch"):
                if not coordenada_valida(latitude, longitude):
                    st.session_state.aviso = "Coordenada invalida."
                elif adicionar_estacao(latitude, longitude, nome):
                    st.rerun()

        coluna_desfazer, coluna_limpar = st.columns(2)
        if coluna_desfazer.button("Desfazer", disabled=total == 0, width="stretch"):
            st.session_state.estacoes.pop()
            invalidar_rede()
            st.rerun()
        if coluna_limpar.button("Limpar tudo", disabled=total == 0, width="stretch"):
            limpar_projeto()
            st.rerun()

        if st.button("Carregar exemplo de Brasilia", width="stretch"):
            carregar_demonstracao()
            st.rerun()

        st.divider()
        if st.button("Construir rede", type="primary", disabled=total < 2, width="stretch"):
            construir_rede()
            st.rerun()
        if total < 2:
            st.caption("Adicione pelo menos duas estacoes para construir a rede.")


def metricas_principais(rede):
    if rede is None:
        ui.grade_metricas(
            [
                ("Estacoes", len(st.session_state.estacoes), "vertices do grafo"),
                ("Arestas da MST", "0", "aguardando execucao"),
                ("Distancia total", "0,00 km", "aguardando execucao"),
                ("Custo estimado", "R$ 0,00", "aguardando execucao"),
            ]
        )
        return

    resultado = rede.resultado
    conectividade = "Conexa" if resultado.conexo else f"{resultado.componentes} componentes"
    estilo_conectividade = "destaque" if resultado.conexo else "alerta"
    ui.grade_metricas(
        [
            ("Algoritmo", resultado.algoritmo, ROTULO_DOS_MODOS[rede.modo], "destaque"),
            ("Estacoes", resultado.num_vertices, "vertices do grafo"),
            ("Arestas candidatas", resultado.num_arestas_grafo, "arestas ponderadas"),
            ("Arestas da MST", resultado.num_arestas_mst, "conexoes selecionadas"),
            ("Distancia total", f"{resultado.custo_total:.2f} km", "soma dos pesos"),
            ("Custo estimado", f"R$ {rede.custo_total:,.2f}", "distancia x custo por km"),
            ("Tempo de execucao", f"{resultado.tempo_ms:.3f} ms", "medido com perf_counter"),
            ("Conectividade", conectividade, "componentes do grafo", estilo_conectividade),
        ]
    )


def aba_mapa():
    rede = st.session_state.rede
    metricas_principais(rede)

    if st.session_state.erro:
        st.error(st.session_state.erro)
    if st.session_state.aviso:
        st.warning(st.session_state.aviso)
    if rede and rede.algoritmo != st.session_state.algoritmo:
        st.info(
            f"O mapa mostra a rede construida com {rede.algoritmo}. "
            f"Clique em Construir rede para exibir o resultado de {st.session_state.algoritmo}."
        )
    if rede and rede.pares_sem_conexao:
        st.warning(
            f"{len(rede.pares_sem_conexao)} par(es) de estacoes nao possuem rota entre si "
            "na malha baixada. O grafo foi tratado como possivelmente desconexo."
        )

    coluna_mapa, coluna_lista = st.columns([3, 1.15], gap="medium")

    with coluna_mapa:
        candidatas = (
            arestas_candidatas(rede) if rede and st.session_state.mostrar_candidatas else ()
        )
        mapa = criar_mapa(
            st.session_state.estacoes,
            rede=rede,
            candidatas=candidatas,
            centro_padrao=CENTRO_INICIAL,
            zoom=ZOOM_INICIAL,
        )
        retorno = st_folium(mapa, height=560, use_container_width=True, key="mapa_principal")

        if retorno and retorno.get("last_clicked"):
            latitude = retorno["last_clicked"]["lat"]
            longitude = retorno["last_clicked"]["lng"]
            if adicionar_estacao(latitude, longitude):
                st.rerun()

    with coluna_lista:
        ui.secao("Estacoes cadastradas", "Renomeie ou marque para remover.")
        if not st.session_state.estacoes:
            ui.estado_vazio(
                "Nenhuma estacao ainda",
                "Monte a rede em tres passos:",
                (
                    "Clique no mapa para posicionar as estacoes.",
                    "Escolha o algoritmo na barra lateral.",
                    "Clique em Construir rede.",
                ),
            )
            return

        tabela = pd.DataFrame(
            [
                {
                    "Nome": estacao.nome,
                    "Latitude": estacao.lat,
                    "Longitude": estacao.lon,
                    "Remover": False,
                }
                for estacao in st.session_state.estacoes
            ]
        )
        editado = st.data_editor(
            tabela,
            hide_index=True,
            width="stretch",
            height=360,
            column_config={
                "Nome": st.column_config.TextColumn("Nome", max_chars=40),
                "Latitude": st.column_config.NumberColumn("Lat", format="%.4f", disabled=True),
                "Longitude": st.column_config.NumberColumn("Lon", format="%.4f", disabled=True),
                "Remover": st.column_config.CheckboxColumn("Remover"),
            },
            key="editor_estacoes",
        )

        if st.button("Aplicar alteracoes", width="stretch"):
            mantidas = []
            for estacao, linha in zip(st.session_state.estacoes, editado.to_dict("records")):
                if linha["Remover"]:
                    continue
                nome = str(linha["Nome"]).strip() or estacao.nome
                mantidas.append(Estacao(id=estacao.id, nome=nome, lat=estacao.lat, lon=estacao.lon))
            removeu = len(mantidas) != len(st.session_state.estacoes)
            st.session_state.estacoes = mantidas
            if removeu:
                invalidar_rede()
            st.rerun()


def aba_resultados():
    rede = st.session_state.rede
    if rede is None:
        ui.estado_vazio(
            "Nenhum resultado disponivel",
            "Construa a rede para visualizar as arestas selecionadas e as metricas detalhadas.",
        )
        return

    resultado = rede.resultado
    ui.secao(
        f"Arestas selecionadas por {resultado.algoritmo}",
        "Cada linha representa uma conexao da arvore geradora minima.",
    )
    st.dataframe(pd.DataFrame(linhas_das_conexoes(rede)), hide_index=True, width="stretch")

    coluna_esquerda, coluna_direita = st.columns(2, gap="large")

    with coluna_esquerda:
        ui.secao("Contadores de operacoes", "Medidos durante a execucao do algoritmo.")
        st.dataframe(
            pd.DataFrame(
                [{"Operacao": chave, "Quantidade": valor} for chave, valor in resultado.operacoes.items()]
            ),
            hide_index=True,
            width="stretch",
        )

    with coluna_direita:
        ui.secao("Estacoes e grau na MST", "Numero de conexoes de cada estacao.")
        st.dataframe(pd.DataFrame(linhas_das_estacoes(rede)), hide_index=True, width="stretch")

    ui.secao("Exportacao", "Baixe os resultados desta execucao.")
    coluna_csv, coluna_json, coluna_md = st.columns(3)
    coluna_csv.download_button(
        "Arestas (CSV)",
        data=exportar_csv(rede),
        file_name="mst_arestas.csv",
        mime="text/csv",
        width="stretch",
    )
    coluna_json.download_button(
        "Execucao (JSON)",
        data=exportar_json(rede),
        file_name="mst_execucao.json",
        mime="application/json",
        width="stretch",
    )
    coluna_md.download_button(
        "Relatorio (Markdown)",
        data=gerar_relatorio_markdown(rede),
        file_name="mst_relatorio.md",
        mime="text/markdown",
        width="stretch",
    )


def aba_comparacao():
    rede = st.session_state.rede
    if rede is None:
        ui.estado_vazio(
            "Comparacao indisponivel",
            "Construa a rede para executar Kruskal e Prim sobre o mesmo grafo de estacoes.",
        )
        return

    comparacao = rede.comparacao
    ui.secao(
        "Kruskal x Prim sobre o mesmo grafo",
        "Os dois algoritmos recebem exatamente o mesmo conjunto de vertices e arestas.",
    )
    st.dataframe(pd.DataFrame(comparacao.como_linhas()), hide_index=True, width="stretch")

    if comparacao.custos_equivalentes:
        st.success(
            "Os dois algoritmos encontraram MSTs de mesmo custo total "
            f"(diferenca de {comparacao.diferenca_custo:.9f} km), como previsto pela teoria."
        )
    else:
        st.error(
            "Os custos divergiram. Em um mesmo grafo isso indica erro de implementacao "
            "ou pesos nao finitos."
        )

    ui.grade_metricas(
        [
            ("Arestas em comum", len(comparacao.arestas_comuns), "escolhidas pelos dois"),
            (
                "Exclusivas de Kruskal",
                len(comparacao.arestas_exclusivas["Kruskal"]),
                "empates de peso",
            ),
            ("Exclusivas de Prim", len(comparacao.arestas_exclusivas["Prim"]), "empates de peso"),
            ("Mais rapido nesta execucao", comparacao.algoritmo_mais_rapido, "tempo de CPU"),
        ]
    )

    if comparacao.houve_empate_de_arestas:
        st.info(
            "Os algoritmos escolheram arestas diferentes. Isso ocorre quando existem pesos "
            "empatados: varias arvores geradoras minimas distintas possuem o mesmo custo otimo."
        )
    else:
        st.info("Os dois algoritmos selecionaram exatamente o mesmo conjunto de arestas.")

    linhas_exclusivas = []
    for nome, arestas in comparacao.arestas_exclusivas.items():
        for origem, destino, peso in arestas:
            linhas_exclusivas.append(
                {
                    "Algoritmo": nome,
                    "Origem": rede.nome_da_estacao(origem),
                    "Destino": rede.nome_da_estacao(destino),
                    "Peso (km)": round(peso, 4),
                }
            )
    if linhas_exclusivas:
        ui.secao("Arestas escolhidas por apenas um dos algoritmos")
        st.dataframe(pd.DataFrame(linhas_exclusivas), hide_index=True, width="stretch")


def aba_benchmark():
    ui.secao(
        "Analise experimental",
        "Grafos aleatorios conexos sao gerados com semente fixa e resolvidos pelos dois algoritmos.",
    )

    coluna_a, coluna_b, coluna_c, coluna_d = st.columns(4)
    maximo = coluna_a.number_input("Maior numero de vertices", 20, 600, 200, step=20)
    passos = coluna_b.number_input("Quantidade de tamanhos", 2, 10, 5)
    densidade = coluna_c.slider("Densidade das arestas", 0.1, 1.0, 1.0, step=0.1)
    repeticoes = coluna_d.number_input("Repeticoes por tamanho", 1, 10, 3)

    if st.button("Executar benchmark", type="primary"):
        tamanhos = sorted({max(2, int(maximo * (i + 1) / passos)) for i in range(int(passos))})
        with st.spinner("Executando Kruskal e Prim em grafos aleatorios..."):
            st.session_state.benchmark = executar_benchmark(
                tamanhos, densidade=densidade, repeticoes=int(repeticoes)
            )

    if not st.session_state.benchmark:
        ui.estado_vazio(
            "Nenhum benchmark executado",
            "Defina os parametros acima e execute para comparar o tempo dos dois algoritmos.",
        )
        return

    tabela = pd.DataFrame(st.session_state.benchmark)
    st.dataframe(tabela, hide_index=True, width="stretch")
    st.line_chart(
        tabela.set_index("Vertices")[["Tempo Kruskal (ms)", "Tempo Prim (ms)"]],
        height=320,
    )

    if bool(tabela["Custos iguais"].all()):
        st.success("Em todos os tamanhos testados os dois algoritmos produziram o mesmo custo otimo.")
    else:
        st.error("Houve divergencia de custo em algum tamanho testado.")


def aba_demonstracao():
    ui.secao(
        "Grafos didaticos",
        "Casos pequenos com custo otimo conhecido, uteis para validar os algoritmos na apresentacao.",
    )

    nome = st.selectbox("Exemplo", options=list(GRAFOS_DIDATICOS))
    dados = GRAFOS_DIDATICOS[nome]
    st.caption(dados["descricao"])

    grafo = construir_grafo_didatico(nome)
    comparacao = comparar_algoritmos(grafo)
    rotulos = dados["rotulos"]

    ui.grade_metricas(
        [
            ("Vertices", grafo.num_vertices),
            ("Arestas", grafo.num_arestas),
            ("Custo esperado", f"{dados['custo_esperado']:.2f}"),
            ("Custo Kruskal", f"{comparacao.resultados['Kruskal'].custo_total:.2f}"),
            ("Custo Prim", f"{comparacao.resultados['Prim'].custo_total:.2f}"),
            (
                "Componentes",
                comparacao.resultados["Kruskal"].componentes,
                "1 significa grafo conexo",
            ),
        ]
    )

    linhas = []
    for algoritmo, resultado in comparacao.resultados.items():
        for aresta in resultado.arestas:
            linhas.append(
                {
                    "Algoritmo": algoritmo,
                    "Origem": rotulos[aresta.origem],
                    "Destino": rotulos[aresta.destino],
                    "Peso": aresta.peso,
                }
            )
    if linhas:
        st.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch")
    else:
        st.info("Este exemplo nao possui arestas na arvore geradora minima.")

    esperado = dados["custo_esperado"]
    if all(abs(r.custo_total - esperado) < 1e-9 for r in comparacao.resultados.values()):
        st.success("Kruskal e Prim reproduziram o custo otimo conhecido deste exemplo.")
    else:
        st.error("O custo obtido divergiu do valor otimo conhecido.")


inicializar_estado()
ui.aplicar_tema()
ui.cabecalho(
    "ConstrutorMST",
    "Planejamento de redes de custo minimo sobre ruas reais com Kruskal e Prim.",
    (
        "Projeto de Algoritmos",
        "Grafos",
        "Arvore Geradora Minima",
        "Grupo 21",
    ),
)
barra_lateral()

aba_um, aba_dois, aba_tres, aba_quatro, aba_cinco = st.tabs(
    ["Mapa", "Resultados", "Comparacao", "Benchmark", "Demonstracao"]
)

with aba_um:
    aba_mapa()
with aba_dois:
    aba_resultados()
with aba_tres:
    aba_comparacao()
with aba_quatro:
    aba_benchmark()
with aba_cinco:
    aba_demonstracao()

ui.rodape(
    "ConstrutorMST - Projeto de Algoritmos - Kruskal e Prim implementados do zero, "
    "sem uso de rotinas prontas de arvore geradora minima."
)
