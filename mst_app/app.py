import folium
import streamlit as st
from streamlit_folium import st_folium

from kruskal import kruskal
from rotas import baixar_grafo_area, caminho_rota, distancia_rota_km

CENTRO_INICIAL = (-15.7797, -47.9297)
ZOOM_INICIAL = 13

ALGORITMOS = {
    "Kruskal": kruskal,
}

st.set_page_config(page_title="Construtor de Rede MST", layout="wide")


def inicializar_estado():
    if "estacoes" not in st.session_state:
        st.session_state.estacoes = []
    if "rede" not in st.session_state:
        st.session_state.rede = None


def adicionar_estacao(lat, lon):
    novo_id = len(st.session_state.estacoes)
    st.session_state.estacoes.append({"id": novo_id, "lat": lat, "lon": lon})


def ja_existe_estacao(lat, lon, tolerancia=1e-6):
    return any(
        abs(e["lat"] - lat) < tolerancia and abs(e["lon"] - lon) < tolerancia
        for e in st.session_state.estacoes
    )


def gerar_arestas(estacoes, grafo_ruas):
    arestas = []
    for i in range(len(estacoes)):
        for j in range(i + 1, len(estacoes)):
            origem = (estacoes[i]["lat"], estacoes[i]["lon"])
            destino = (estacoes[j]["lat"], estacoes[j]["lon"])
            peso = distancia_rota_km(grafo_ruas, origem, destino)
            arestas.append((i, j, peso))
    return arestas


def gerar_caminhos(estacoes, grafo_ruas, mst):
    caminhos = []
    for u, v, _ in mst:
        origem = (estacoes[u]["lat"], estacoes[u]["lon"])
        destino = (estacoes[v]["lat"], estacoes[v]["lon"])
        caminhos.append(caminho_rota(grafo_ruas, origem, destino))
    return caminhos


def construir_rede():
    algoritmo = ALGORITMOS[st.session_state.algoritmo_escolhido]
    pontos = [(e["lat"], e["lon"]) for e in st.session_state.estacoes]
    with st.spinner("Baixando ruas reais da região..."):
        grafo_ruas = baixar_grafo_area(pontos)
    arestas = gerar_arestas(st.session_state.estacoes, grafo_ruas)
    mst, km_total = algoritmo(len(st.session_state.estacoes), arestas)
    caminhos = gerar_caminhos(st.session_state.estacoes, grafo_ruas, mst)
    st.session_state.rede = {"mst": mst, "km_total": km_total, "caminhos": caminhos}


def desenhar_mapa():
    mapa = folium.Map(location=CENTRO_INICIAL, zoom_start=ZOOM_INICIAL)

    if st.session_state.rede:
        for caminho in st.session_state.rede["caminhos"]:
            folium.PolyLine(locations=caminho, color="#2b6cb0", weight=3).add_to(mapa)

    for estacao in st.session_state.estacoes:
        folium.Marker(
            location=(estacao["lat"], estacao["lon"]),
            tooltip=f"Estação {estacao['id']}",
            icon=folium.DivIcon(
                html=f"""<div style="font-size:12pt;color:white;background:#2b6cb0;
                border-radius:50%;width:24px;height:24px;text-align:center;
                line-height:24px;">{estacao['id']}</div>"""
            ),
        ).add_to(mapa)
    return mapa


inicializar_estado()

st.sidebar.header("Controles")
st.sidebar.radio("Algoritmo", options=list(ALGORITMOS.keys()), key="algoritmo_escolhido")
st.sidebar.number_input("Custo por km (R$)", min_value=0.0, value=1000.0, step=100.0, key="custo_por_km")

col_desfazer, col_limpar = st.sidebar.columns(2)
if col_desfazer.button("Desfazer última estação", disabled=len(st.session_state.estacoes) == 0):
    st.session_state.estacoes.pop()
    st.session_state.rede = None
    st.rerun()
if col_limpar.button("Limpar tudo", disabled=len(st.session_state.estacoes) == 0):
    st.session_state.estacoes.clear()
    st.session_state.rede = None
    st.rerun()

if st.sidebar.button("Construir rede", disabled=len(st.session_state.estacoes) < 2):
    construir_rede()
    st.rerun()

st.sidebar.markdown("Clique no mapa para adicionar uma estação.")

st.title("Construtor de Rede MST")

col_mapa, col_metricas = st.columns([3, 1])

with col_mapa:
    mapa = desenhar_mapa()
    resultado_mapa = st_folium(mapa, height=550, width=None, key="mapa_principal")

    if resultado_mapa and resultado_mapa.get("last_clicked"):
        lat = resultado_mapa["last_clicked"]["lat"]
        lon = resultado_mapa["last_clicked"]["lng"]
        if not ja_existe_estacao(lat, lon):
            adicionar_estacao(lat, lon)
            st.rerun()

with col_metricas:
    st.metric("Estações", len(st.session_state.estacoes))
    if st.session_state.rede:
        km_total = st.session_state.rede["km_total"]
        custo_total = km_total * st.session_state.custo_por_km
        st.metric("Arestas", len(st.session_state.rede["mst"]))
        st.metric("Km total", f"{km_total:.2f}")
        st.metric("Custo total (R$)", f"{custo_total:,.2f}")
    else:
        st.metric("Arestas", 0)
        st.metric("Km total", "0.00")
        st.metric("Custo total (R$)", "0.00")
