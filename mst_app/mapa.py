import folium

from geo import centro_geografico, limites

CORES_POR_ALGORITMO = {
    "Kruskal": "#1d4ed8",
    "Prim": "#c2410c",
}
COR_ESTACAO = "#0f172a"
COR_CANDIDATA = "#94a3b8"
COR_DESTAQUE = "#059669"


def cor_do_algoritmo(algoritmo):
    return CORES_POR_ALGORITMO.get(algoritmo, "#1d4ed8")


def icone_estacao(rotulo, cor):
    return folium.DivIcon(
        html=(
            f'<div style="display:flex;align-items:center;justify-content:center;'
            f'width:26px;height:26px;border-radius:50%;background:{cor};color:#ffffff;'
            f'font-family:Inter,Segoe UI,sans-serif;font-size:12px;font-weight:600;'
            f'border:2px solid #ffffff;box-shadow:0 1px 4px rgba(15,23,42,.45);">{rotulo}</div>'
        ),
        icon_size=(26, 26),
        icon_anchor=(13, 13),
    )


def legenda_html(algoritmo, modo):
    cor = cor_do_algoritmo(algoritmo)
    origem = "rotas reais (OpenStreetMap)" if modo == "rota" else "linha reta (Haversine)"
    return (
        '<div style="position:fixed;bottom:24px;left:24px;z-index:9999;'
        'background:rgba(255,255,255,.94);padding:10px 14px;border-radius:10px;'
        'border:1px solid #e2e8f0;font-family:Inter,Segoe UI,sans-serif;font-size:12px;'
        'color:#0f172a;box-shadow:0 4px 14px rgba(15,23,42,.12);">'
        f'<div style="font-weight:700;margin-bottom:6px;">MST - {algoritmo}</div>'
        f'<div><span style="display:inline-block;width:18px;height:3px;background:{cor};'
        'vertical-align:middle;margin-right:6px;"></span>Conexao selecionada</div>'
        f'<div><span style="display:inline-block;width:18px;height:3px;background:{COR_CANDIDATA};'
        'vertical-align:middle;margin-right:6px;"></span>Conexao candidata</div>'
        f'<div style="margin-top:6px;color:#475569;">Distancias por {origem}</div>'
        "</div>"
    )


def ajustar_enquadramento(mapa, pontos):
    if len(pontos) == 1:
        mapa.location = list(pontos[0])
        return
    sul, oeste, norte, leste = limites(pontos)
    mapa.fit_bounds([[sul, oeste], [norte, leste]], padding=(40, 40))


def criar_mapa(estacoes, rede=None, candidatas=(), centro_padrao=(-15.7797, -47.9297), zoom=12):
    pontos = [estacao.coordenada for estacao in estacoes]
    centro = centro_geografico(pontos) if pontos else centro_padrao

    mapa = folium.Map(location=centro, zoom_start=zoom, tiles="OpenStreetMap", control_scale=True)

    algoritmo = rede.algoritmo if rede else "Kruskal"
    cor_mst = cor_do_algoritmo(algoritmo)

    if candidatas and estacoes:
        grupo_candidatas = folium.FeatureGroup(name="Conexoes candidatas", show=True)
        for aresta in candidatas:
            origem = estacoes[aresta.origem]
            destino = estacoes[aresta.destino]
            folium.PolyLine(
                locations=[origem.coordenada, destino.coordenada],
                color=COR_CANDIDATA,
                weight=1.5,
                opacity=0.7,
                dash_array="4,6",
                tooltip=f"{origem.nome} - {destino.nome}: {aresta.peso:.2f} km",
            ).add_to(grupo_candidatas)
        grupo_candidatas.add_to(mapa)

    if rede:
        grupo_mst = folium.FeatureGroup(name=f"MST ({algoritmo})", show=True)
        for conexao in rede.conexoes:
            origem = estacoes[conexao.origem]
            destino = estacoes[conexao.destino]
            tipo = "rota real" if conexao.rota_real else "linha reta"
            folium.PolyLine(
                locations=[list(coordenada) for coordenada in conexao.caminho],
                color=cor_mst,
                weight=5,
                opacity=0.85,
                tooltip=(
                    f"{origem.nome} - {destino.nome}: "
                    f"{conexao.distancia_km:.2f} km ({tipo})"
                ),
            ).add_to(grupo_mst)
        grupo_mst.add_to(mapa)

    grupo_estacoes = folium.FeatureGroup(name="Estacoes", show=True)
    for indice, estacao in enumerate(estacoes):
        grau = len(rede.conexoes_por_estacao(indice)) if rede else 0
        popup = folium.Popup(
            (
                f'<div style="font-family:Inter,Segoe UI,sans-serif;font-size:12px;">'
                f"<b>{estacao.nome}</b><br>"
                f"Indice no grafo: {indice}<br>"
                f"Latitude: {estacao.lat:.5f}<br>"
                f"Longitude: {estacao.lon:.5f}<br>"
                f"Conexoes na MST: {grau}"
                "</div>"
            ),
            max_width=240,
        )
        folium.Marker(
            location=estacao.coordenada,
            tooltip=estacao.nome,
            popup=popup,
            icon=icone_estacao(indice, COR_DESTAQUE if grau else COR_ESTACAO),
        ).add_to(grupo_estacoes)
    grupo_estacoes.add_to(mapa)

    folium.LayerControl(collapsed=True).add_to(mapa)

    if rede:
        modo = rede.modo
        mapa.get_root().html.add_child(folium.Element(legenda_html(algoritmo, modo)))

    if pontos:
        ajustar_enquadramento(mapa, pontos)

    return mapa
