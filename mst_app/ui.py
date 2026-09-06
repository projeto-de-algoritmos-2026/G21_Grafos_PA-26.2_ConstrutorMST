import html

import streamlit as st

TEMA = """
<style>
:root {
    --azul: #1d4ed8;
    --laranja: #c2410c;
    --tinta: #0f172a;
    --texto-suave: #475569;
    --borda: #e2e8f0;
    --fundo-suave: #f8fafc;
}
section.main > div.block-container { padding-top: 1.6rem; max-width: 1500px; }
#MainMenu, footer { visibility: hidden; }
.cabecalho {
    border: 1px solid var(--borda);
    border-left: 6px solid var(--azul);
    border-radius: 14px;
    padding: 18px 22px;
    background: linear-gradient(120deg, #ffffff 0%, var(--fundo-suave) 100%);
    margin-bottom: 18px;
}
.cabecalho h1 {
    font-size: 1.65rem;
    margin: 0 0 4px 0;
    color: var(--tinta);
    letter-spacing: -0.02em;
}
.cabecalho p { margin: 0; color: var(--texto-suave); font-size: 0.95rem; }
.etiquetas { margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px; }
.etiqueta {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 999px;
    background: #eef2ff;
    color: var(--azul);
    border: 1px solid #dbeafe;
}
.grade-metricas {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
    gap: 12px;
    margin: 6px 0 18px 0;
}
.cartao {
    border: 1px solid var(--borda);
    border-radius: 12px;
    padding: 14px 16px;
    background: #ffffff;
}
.cartao .rotulo {
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--texto-suave);
    font-weight: 600;
}
.cartao .valor {
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--tinta);
    margin-top: 4px;
    line-height: 1.2;
}
.cartao .detalhe { font-size: 0.78rem; color: var(--texto-suave); margin-top: 2px; }
.cartao.destaque { border-left: 4px solid var(--azul); }
.cartao.alerta { border-left: 4px solid var(--laranja); }
.secao { margin: 6px 0 10px 0; }
.secao h3 { margin: 0; font-size: 1.05rem; color: var(--tinta); }
.secao p { margin: 2px 0 0 0; color: var(--texto-suave); font-size: 0.86rem; }
.vazio {
    border: 1px dashed #cbd5e1;
    border-radius: 14px;
    padding: 28px;
    text-align: center;
    background: var(--fundo-suave);
    color: var(--texto-suave);
}
.vazio h4 { margin: 0 0 6px 0; color: var(--tinta); font-size: 1.05rem; }
.vazio ol { display: inline-block; text-align: left; margin: 12px 0 0 0; }
.rodape {
    margin-top: 24px;
    padding-top: 12px;
    border-top: 1px solid var(--borda);
    color: var(--texto-suave);
    font-size: 0.8rem;
}
div[data-testid="stSidebar"] { border-right: 1px solid var(--borda); }
</style>
"""


def aplicar_tema():
    st.markdown(TEMA, unsafe_allow_html=True)


def escapar(valor):
    return html.escape(str(valor))


def cabecalho(titulo, subtitulo, etiquetas=()):
    marcas = "".join(f'<span class="etiqueta">{escapar(t)}</span>' for t in etiquetas)
    bloco_etiquetas = f'<div class="etiquetas">{marcas}</div>' if marcas else ""
    st.markdown(
        f'<div class="cabecalho"><h1>{escapar(titulo)}</h1>'
        f"<p>{escapar(subtitulo)}</p>{bloco_etiquetas}</div>",
        unsafe_allow_html=True,
    )


def secao(titulo, descricao=""):
    complemento = f"<p>{escapar(descricao)}</p>" if descricao else ""
    st.markdown(
        f'<div class="secao"><h3>{escapar(titulo)}</h3>{complemento}</div>',
        unsafe_allow_html=True,
    )


def grade_metricas(itens):
    cartoes = []
    for item in itens:
        rotulo, valor = item[0], item[1]
        detalhe = item[2] if len(item) > 2 else ""
        estilo = item[3] if len(item) > 3 else ""
        classe = f"cartao {estilo}".strip()
        complemento = f'<div class="detalhe">{escapar(detalhe)}</div>' if detalhe else ""
        cartoes.append(
            f'<div class="{classe}"><div class="rotulo">{escapar(rotulo)}</div>'
            f'<div class="valor">{escapar(valor)}</div>{complemento}</div>'
        )
    st.markdown(f'<div class="grade-metricas">{"".join(cartoes)}</div>', unsafe_allow_html=True)


def estado_vazio(titulo, mensagem, passos=()):
    lista = "".join(f"<li>{escapar(passo)}</li>" for passo in passos)
    bloco = f"<ol>{lista}</ol>" if lista else ""
    st.markdown(
        f'<div class="vazio"><h4>{escapar(titulo)}</h4><div>{escapar(mensagem)}</div>{bloco}</div>',
        unsafe_allow_html=True,
    )


def rodape(texto):
    st.markdown(f'<div class="rodape">{escapar(texto)}</div>', unsafe_allow_html=True)
