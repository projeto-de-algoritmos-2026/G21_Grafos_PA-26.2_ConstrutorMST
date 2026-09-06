<h1 align="center">🌐 ConstrutorMST</h1>

<p align="center">
  <b>Planejamento de redes de custo mínimo sobre ruas reais com Kruskal e Prim</b><br>
  Projeto de Algoritmos · Módulo de Grafos · FGA/UnB · 2026.2 · Grupo 21
</p>

<p align="center">
  <img alt="Tamanho do repositório" src="https://img.shields.io/github/repo-size/projeto-de-algoritmos-2026/G21_Grafos_PA-26.2_ConstrutorMST?style=flat-square">
  <img alt="Linguagem principal" src="https://img.shields.io/github/languages/top/projeto-de-algoritmos-2026/G21_Grafos_PA-26.2_ConstrutorMST?style=flat-square">
  <img alt="Quantidade de linguagens" src="https://img.shields.io/github/languages/count/projeto-de-algoritmos-2026/G21_Grafos_PA-26.2_ConstrutorMST?style=flat-square">
  <img alt="Último commit" src="https://img.shields.io/github/last-commit/projeto-de-algoritmos-2026/G21_Grafos_PA-26.2_ConstrutorMST?style=flat-square">
  <img alt="Issues abertas" src="https://img.shields.io/github/issues/projeto-de-algoritmos-2026/G21_Grafos_PA-26.2_ConstrutorMST?style=flat-square">
  <img alt="Observadores" src="https://img.shields.io/github/watchers/projeto-de-algoritmos-2026/G21_Grafos_PA-26.2_ConstrutorMST?style=flat-square">
</p>

<p align="center">
  <img alt="Status" src="https://img.shields.io/badge/status-concluído-success?style=flat-square">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-1.63-FF4B4B?style=flat-square&logo=streamlit&logoColor=white">
  <img alt="OSMnx" src="https://img.shields.io/badge/OSMnx-2.1-7EBC6F?style=flat-square&logo=openstreetmap&logoColor=white">
  <img alt="Testes" src="https://img.shields.io/badge/pytest-116%20testes-0A9EDC?style=flat-square&logo=pytest&logoColor=white">
</p>

---

## 🎯 Objetivos

1. Implementar **do zero** os dois algoritmos clássicos de Árvore Geradora Mínima: **Kruskal** (com Union-Find) e **Prim** (com fila de prioridade baseada em heap binário).
2. Aplicar esses algoritmos a um problema geográfico real: interligar estações com o **menor custo total de cabeamento/via**, usando distâncias medidas sobre as **ruas reais** do OpenStreetMap.
3. Permitir a **comparação experimental** entre os dois algoritmos sobre exatamente o mesmo grafo, evidenciando que o custo ótimo é idêntico e que as arestas podem diferir apenas em caso de empate.
4. Entregar uma ferramenta **visual e demonstrável**, adequada para apresentação em sala.

---

## 📖 Sobre o projeto

O **ConstrutorMST** é uma aplicação web interativa na qual o usuário posiciona estações sobre um mapa (clicando ou informando coordenadas). A partir desses pontos o sistema:

1. Baixa a malha viária real da região no **OpenStreetMap** (via OSMnx).
2. Calcula a distância de **rota** entre cada par de estações percorrendo as ruas (Dijkstra sobre o grafo de ruas).
3. Monta um **grafo ponderado completo** cujos vértices são as estações e cujos pesos são essas distâncias.
4. Executa **Kruskal e Prim** sobre esse grafo e devolve a árvore geradora mínima, o custo total, as métricas de execução e a comparação entre os dois algoritmos.
5. Desenha no mapa as conexões escolhidas, seguindo o traçado real das ruas.

O problema modelado é o clássico *"qual é a rede mais barata que conecta todos os pontos?"* — o mesmo que aparece em projetos de fibra óptica, redes elétricas e linhas de transporte.

---

## 🎓 Contexto da disciplina

| Item | Descrição |
| --- | --- |
| Disciplina | Projeto de Algoritmos (FGA/UnB) |
| Semestre | 2026.2 |
| Professor | Maurício Serrano |
| Módulo | Grafos |
| Número da lista | 21 |
| Conteúdo abordado | Árvore Geradora Mínima (Kruskal e Prim), Union-Find, fila de prioridade com heap binário, caminho mínimo (Dijkstra) sobre a malha viária |

A implementação de Prim segue a **versão clássica com heap binário** (`heapq` da biblioteca padrão), e a de Kruskal usa **Union-Find com compressão de caminho e união por rank**. Nenhuma rotina pronta de MST de biblioteca é utilizada.

---

## 🌲 O que é uma Árvore Geradora Mínima

Dado um grafo não direcionado, conexo e ponderado `G = (V, E, w)`, uma **Árvore Geradora Mínima (MST)** é um subconjunto de arestas que:

- conecta **todos** os vértices de `V`;
- não possui ciclos;
- possui exatamente `|V| - 1` arestas;
- tem a **menor soma de pesos possível** entre todas as árvores geradoras.

Ambos os algoritmos exploram a mesma propriedade — a **propriedade do corte**: para qualquer corte do grafo, a aresta de menor peso que atravessa esse corte pertence a alguma MST. Quando os pesos não são todos distintos, o grafo pode ter **várias MSTs diferentes com o mesmo custo ótimo**.

---

## 🔗 Algoritmo de Kruskal

Estratégia **gulosa orientada a arestas**:

1. Ordena todas as arestas por peso crescente.
2. Percorre a lista ordenada e adiciona a aresta à MST **se ela não formar ciclo**.
3. A detecção de ciclo é feita pela estrutura **Union-Find** (`find` com compressão de caminho e `union` por rank).
4. Encerra quando `|V| - 1` arestas foram selecionadas.

```python
for aresta in arestas_ordenadas:
    if len(arestas_mst) == limite:
        break
    if union_find.union(aresta.origem, aresta.destino):
        arestas_mst.append(aresta)
        custo_total += aresta.peso
```

Arquivo: [`mst_app/kruskal.py`](mst_app/kruskal.py) · Estrutura de apoio: `UnionFind` em [`mst_app/grafo.py`](mst_app/grafo.py)

---

## 🌱 Algoritmo de Prim

Estratégia **gulosa orientada a vértices**:

1. Parte de um vértice raiz e mantém um conjunto de vértices já visitados (a árvore em construção).
2. Insere numa **fila de prioridade (heap binário)** todas as arestas que saem da árvore.
3. Remove sempre a aresta de menor peso; se o destino ainda não foi visitado, ela entra na MST.
4. Repete até que todos os vértices alcançáveis tenham sido visitados.
5. Se ainda restarem vértices não visitados (grafo desconexo), **reinicia** a partir de um deles, produzindo uma floresta geradora mínima.

```python
while fila:
    peso, vertice, pai = heappop(fila)
    if visitado[vertice]:
        continue
    visitado[vertice] = True
    if pai != SEM_PAI:
        arestas_mst.append(Aresta(pai, vertice, peso))
        custo_total += peso
    for vizinho, peso_aresta in adjacencia[vertice]:
        if not visitado[vizinho]:
            heappush(fila, (peso_aresta, vizinho, vertice))
```

A implementação usa **remoção preguiçosa** (*lazy deletion*): em vez de atualizar a prioridade de um vértice já presente no heap, insere-se uma nova entrada e descarta-se qualquer remoção referente a um vértice já visitado. É a formulação usual com `heapq`, mantendo a complexidade `O(E log V)`.

O desempate é determinístico: as entradas do heap são a tupla `(peso, vértice, pai)`, então pesos iguais são resolvidos pelo menor índice de vértice, e a mesma entrada sempre produz o mesmo resultado.

Arquivo: [`mst_app/prim.py`](mst_app/prim.py)

---

## ⚖️ Comparação entre Prim e Kruskal

| Critério | Kruskal | Prim (heap binário) |
| --- | --- | --- |
| Estratégia | Gulosa sobre **arestas** | Gulosa sobre **vértices** |
| Estrutura principal | Union-Find (DSU) | Fila de prioridade (heap) |
| Estado intermediário | Floresta de várias árvores | Uma única árvore crescendo |
| Complexidade de tempo | `O(E log E)` = `O(E log V)` | `O(E log V)` |
| Complexidade de espaço | `O(V + E)` | `O(V + E)` |
| Melhor cenário | Grafos **esparsos** | Grafos **densos** |
| Grafo desconexo | Naturalmente gera uma floresta | Precisa reiniciar em cada componente |
| Ordem das arestas na saída | Peso crescente | Ordem de crescimento da árvore |

> **Garantia teórica verificada pelo sistema:** em um mesmo grafo ponderado, Kruskal e Prim sempre produzem MSTs de **mesmo custo total**. O conjunto de arestas pode ser diferente quando existem **pesos empatados**, pois nesse caso o grafo possui mais de uma MST ótima. A aba **Comparação** da aplicação exibe a diferença de custo (esperada: `0`), as arestas em comum e as arestas exclusivas de cada algoritmo.

No caso deste projeto o grafo das estações é **completo** (`E = V(V-1)/2`), portanto denso: é o cenário em que o Prim tende a se comportar melhor. A aba **Benchmark** permite verificar isso experimentalmente.

---

## ✨ Funcionalidades

| Funcionalidade | Justificativa acadêmica |
| --- | --- |
| Adicionar estações clicando no mapa ou por coordenada | Entrada dos vértices do grafo |
| Renomear e remover estações individualmente | Manipulação do conjunto de vértices sem recomeçar |
| Seleção entre **Kruskal** e **Prim** | Requisito central do módulo de Grafos |
| Comparação automática dos dois algoritmos no mesmo grafo | Evidencia a equivalência de custo e o efeito dos empates |
| Distância por **rota real** (OSM) ou **linha reta** (Haversine) | Modo offline para demonstração e comparação entre métricas de peso |
| Painel de métricas (vértices, arestas, custo, tempo, conectividade) | Análise experimental dos algoritmos |
| Contadores de operações | Mostra o comportamento interno de cada estratégia |
| Tabela das arestas selecionadas e grau de cada estação | Leitura direta da MST resultante |
| Exportação em CSV, JSON e relatório Markdown | Registro reproduzível da execução |
| Benchmark com grafos aleatórios conexos | Comparação de tempo em função do tamanho da entrada |
| Modo demonstração com grafos didáticos de custo conhecido | Validação visual dos algoritmos durante a apresentação |
| Tratamento de grafos desconexos (floresta geradora mínima) | Caso limite exigido pela teoria |
| Conexões candidatas exibidas no mapa | Mostra o que foi descartado pelo algoritmo guloso |
| Reset completo do projeto e desfazer | Usabilidade durante a demonstração |

---

## 🏗️ Arquitetura do projeto

A aplicação é organizada em camadas, de modo que **os algoritmos não conhecem nem a interface nem o OpenStreetMap**:

```
Interface (Streamlit)              app.py · ui.py · mapa.py
        │
Camada de serviço                  rede.py · relatorio.py · exemplos.py
        │
Análise e algoritmos               analise.py · kruskal.py · prim.py · mst.py
        │
Estruturas e utilidades            grafo.py · geo.py
        │
Dados externos                     rotas.py  ──►  OpenStreetMap / OSMnx
```

| Módulo | Responsabilidade |
| --- | --- |
| `geo.py` | Processamento geográfico puro: Haversine, validação de coordenadas, centro, caixa delimitadora |
| `grafo.py` | Estruturas de dados: `Aresta`, `Grafo` ponderado (lista de adjacência) e `UnionFind` |
| `mst.py` | `ResultadoMST`: formato único de resultado devolvido pelos algoritmos |
| `kruskal.py` | Algoritmo de Kruskal e suas métricas |
| `prim.py` | Algoritmo de Prim e suas métricas |
| `analise.py` | Registro de algoritmos, comparação Kruskal × Prim, geração de grafos aleatórios e benchmark |
| `rotas.py` | Único ponto de contato com OSMnx/OpenStreetMap; matriz de distâncias por rota |
| `rede.py` | Orquestra estações → matriz de distâncias → grafo → MST → traçados |
| `mapa.py` | Construção do mapa Folium (marcadores, camadas, legenda) |
| `relatorio.py` | Exportação em CSV, JSON e Markdown |
| `exemplos.py` | Grafos didáticos com custo ótimo conhecido e estações de demonstração |
| `ui.py` | Tema visual e componentes da interface |
| `app.py` | Estado da aplicação, abas e fluxo de interação |

---

## 📁 Estrutura dos arquivos

```text
G21_Grafos_PA-26.2_ConstrutorMST/
├── mst_app/
│   ├── analise.py
│   ├── app.py
│   ├── exemplos.py
│   ├── geo.py
│   ├── grafo.py
│   ├── kruskal.py
│   ├── mapa.py
│   ├── mst.py
│   ├── prim.py
│   ├── rede.py
│   ├── relatorio.py
│   ├── rotas.py
│   ├── ui.py
│   └── tests/
│       ├── conftest.py
│       ├── test_comparacao.py
│       ├── test_geo.py
│       ├── test_grafo.py
│       ├── test_kruskal.py
│       ├── test_prim.py
│       ├── test_rede.py
│       ├── test_relatorio.py
│       ├── test_rotas.py
│       └── test_rotas_integracao.py
├── COMMITS.md
├── README.md
├── pytest.ini
├── requirements.txt
└── .gitignore
```

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Uso no projeto |
| --- | --- |
| **Python 3.10+** | Linguagem base |
| **Streamlit** | Interface web interativa |
| **Folium** + **streamlit-folium** | Renderização do mapa e das camadas |
| **OSMnx** | Download da malha viária real do OpenStreetMap |
| **NetworkX** | Caminho mínimo **sobre o grafo de ruas** (Dijkstra) — nunca para MST |
| **pandas** | Tabelas e gráficos da interface |
| **pytest** | Suíte de testes automatizados |

> Os algoritmos de MST (Kruskal e Prim) e a estrutura Union-Find são implementação própria. O NetworkX é usado apenas onde já fazia parte da arquitetura original: o grafo de ruas do OpenStreetMap.

---

## ✅ Pré-requisitos

- Python 3.10 ou superior
- `pip`
- Conexão com a internet para o modo de **rotas reais** (o modo Haversine funciona offline)

---

## 📦 Instalação

```bash
git clone https://github.com/projeto-de-algoritmos-2026/G21_Grafos_PA-26.2_ConstrutorMST.git
cd G21_Grafos_PA-26.2_ConstrutorMST

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

---

## ▶️ Execução

```bash
streamlit run mst_app/app.py
```

A aplicação abre em `http://localhost:8501`.

---

## 🕹️ Utilização

1. **Adicione as estações** clicando no mapa, informando coordenadas na barra lateral ou usando o botão *Carregar exemplo de Brasília*.
2. **Escolha o algoritmo** (Kruskal ou Prim) e a **origem das distâncias** (rotas reais ou linha reta).
3. Ajuste o **custo por km** para estimar o investimento da rede.
4. Clique em **Construir rede**.
5. Explore as abas:
   - **Mapa** — estações, conexões da MST traçadas sobre as ruas e conexões candidatas descartadas.
   - **Resultados** — arestas selecionadas, contadores de operações, grau de cada estação e exportações.
   - **Comparação** — Kruskal × Prim sobre o mesmo grafo.
   - **Benchmark** — tempo dos dois algoritmos em grafos aleatórios de tamanho crescente.
   - **Demonstração** — grafos didáticos com custo ótimo conhecido.

---

## 🖥️ Explicação da interface

| Região | Conteúdo |
| --- | --- |
| Cabeçalho | Identificação do projeto e da disciplina |
| Barra lateral | Algoritmo, origem das distâncias, malha viária, margem da área baixada, custo por km, gerenciamento de estações e botão *Construir rede* |
| Cartões de métrica | Algoritmo em uso, número de estações, arestas candidatas, arestas da MST, distância total, custo estimado, tempo de execução e conectividade |
| Mapa | Marcadores numerados pelo índice do vértice, linhas grossas para a MST, linhas tracejadas para as conexões candidatas, legenda e controle de camadas |
| Tabela de estações | Edição do nome e remoção individual |
| Estados vazios | Instruções objetivas quando ainda não há estações ou resultados |
| Mensagens | Erros de download do OSM, pares sem rota, divergência de custo e confirmações de sucesso |

---

## 📊 Explicação das métricas

### Métricas estruturais

| Métrica | Significado |
| --- | --- |
| Vértices | Número de estações (`|V|`) |
| Arestas candidatas | Arestas do grafo de entrada (`|E|`) |
| Arestas da MST | Arestas selecionadas (`|V| - 1` se o grafo for conexo) |
| Distância total | Soma dos pesos das arestas selecionadas, em km |
| Custo estimado | Distância total × custo por km |
| Componentes | Número de componentes conexas encontradas |
| Conectividade | Indica se o resultado é uma árvore geradora ou uma floresta |
| Tempo de execução | Medido com `time.perf_counter()`, isolando apenas o algoritmo (sem download nem renderização) |

### Contadores de operações

Os contadores abaixo são incrementados **dentro** dos algoritmos e refletem exatamente o trabalho realizado. Eles não são estimativas.

**Kruskal**

| Contador | O que conta |
| --- | --- |
| `arestas_ordenadas` | Tamanho da lista ordenada de arestas |
| `arestas_avaliadas` | Arestas efetivamente examinadas antes da parada antecipada |
| `chamadas_find` | Chamadas à operação `find` do Union-Find |
| `passos_find` | Saltos percorridos até a raiz — mede o efeito da compressão de caminho |
| `unioes_efetivadas` | Uniões que realmente fundiram dois conjuntos (igual ao número de arestas da MST) |

**Prim**

| Contador | O que conta |
| --- | --- |
| `insercoes_heap` | Inserções na fila de prioridade |
| `remocoes_heap` | Remoções da fila (inclui as descartadas pela remoção preguiçosa) |
| `arestas_relaxadas` | Arestas examinadas ao expandir a vizinhança de um vértice (`2|E|` em um grafo conexo) |
| `vertices_visitados` | Vértices incorporados à árvore |
| `reinicios_por_componente` | Quantas vezes o algoritmo precisou reiniciar — igual ao número de componentes |

> Comparar `arestas_avaliadas` (Kruskal) com `arestas_relaxadas` (Prim) mostra de forma concreta a diferença entre uma estratégia orientada a arestas e outra orientada a vértices.

---

## 🧪 Testes

A suíte tem **116 testes** e roda em menos de um segundo, porque os testes unitários **não acessam a internet**: o grafo de ruas é simulado por *fixtures* e a função `nearest_nodes` do OSMnx é substituída por um *mock*.

```bash
pytest                    # 116 testes unitários (rápidos, offline)
pytest -m integracao      # testes que baixam dados reais do OpenStreetMap
pytest -v                 # saída detalhada
```

| Arquivo | O que valida |
| --- | --- |
| `test_geo.py` | Haversine (simetria, ponto igual, distância conhecida), validação de coordenadas, caixa delimitadora e lado mínimo |
| `test_grafo.py` | Union-Find (união, transitividade, contagem de componentes, cadeia de 20 000 elementos sem estouro de pilha), `Grafo` (adjacência, laços, validações, componentes, densidade, construção por matriz) |
| `test_kruskal.py` | Grafo simples, triângulo, desconexo, vértice único, grafo vazio, arestas paralelas, laços, determinismo com empates e contadores |
| `test_prim.py` | Todos os casos acima mais grafo clássico de 9 vértices (custo 37), independência da raiz, vértices isolados, grafo em estrela, grafo em linha com 500 vértices e ausência de ciclos |
| `test_comparacao.py` | Igualdade de custo entre Prim e Kruskal em 5 sementes aleatórias, exemplos didáticos, arestas comuns e exclusivas, reprodutibilidade dos grafos aleatórios e benchmark |
| `test_rotas.py` | Matriz de distâncias, simetria, pares sem rota (`inf`), erros amigáveis — tudo com grafo de ruas simulado |
| `test_rede.py` | Criação e validação de estações, duplicatas, modo Haversine, modo rota, floresta por estação inalcançável, comparação automática e arestas candidatas |
| `test_relatorio.py` | CSV, JSON válido, tabelas Markdown e seções do relatório |
| `test_rotas_integracao.py` | Download real do OpenStreetMap (marcado com `@pytest.mark.integracao`, desativado por padrão) |

A separação entre lógica pura e acesso externo é o que torna isso possível: `rotas.py` é o único módulo que fala com o OSMnx, e `rede.py` recebe a função de download por injeção de dependência.

---

## ⏱️ Complexidade dos algoritmos

Com `V` = número de estações e `E` = número de arestas candidatas:

| Etapa | Complexidade | Observação |
| --- | --- | --- |
| Ordenação das arestas (Kruskal) | `O(E log E)` | Etapa dominante do Kruskal |
| Union-Find com compressão + rank | `O(α(V))` amortizado | `α` é a inversa de Ackermann, praticamente constante |
| **Kruskal (total)** | **`O(E log E)` = `O(E log V)`** | `log E ≤ 2 log V` |
| Operações de heap (Prim) | `O(log V)` por operação | Heap binário via `heapq` |
| **Prim (total)** | **`O(E log V)`** | Cada aresta gera no máximo uma inserção |
| Espaço | `O(V + E)` | Lista de adjacência + estruturas auxiliares |

Neste projeto o grafo das estações é completo, então `E = V(V-1)/2` e ambos os algoritmos ficam em `O(V² log V)`.

**Custo dominante da aplicação:** a montagem dos pesos, não a MST. Para obter a matriz de distâncias o sistema executa **uma vez o Dijkstra a partir de cada estação** sobre o grafo de ruas (`V` execuções de `O(R log R)`, onde `R` é o número de nós da malha viária baixada) — em vez de uma busca por par, como na versão inicial do projeto, que era `O(V²)` buscas.

---

## 🧩 Tratamento de grafos desconexos

Um grafo de estações pode ficar desconexo quando **não existe rota** entre dois pontos na malha baixada (por exemplo, uma estação posicionada em uma ilha viária ou fora da área coberta). Nesse caso:

- o par sem rota recebe peso infinito e **não vira aresta** do grafo;
- **Kruskal** simplesmente termina com menos de `|V| - 1` arestas — o Union-Find informa quantos conjuntos restaram;
- **Prim** detecta os vértices não visitados e **reinicia** a partir de cada um deles;
- o resultado passa a ser uma **floresta geradora mínima**, e ambos os algoritmos devolvem o mesmo número de componentes e o mesmo custo total;
- a interface exibe um aviso com a quantidade de pares sem rota e o cartão de conectividade muda para `N componentes`.

---

## 🗺️ Integração com o OpenStreetMap

1. A partir das estações é calculada uma **caixa delimitadora** com margem configurável e lado mínimo garantido (evita bounding boxes degeneradas quando os pontos estão muito próximos).
2. `osmnx.graph_from_bbox` baixa a malha viária (`drive`, `walk` ou `bike`).
3. Cada estação é associada ao **nó mais próximo** da malha com `osmnx.nearest_nodes`.
4. A distância entre estações é o **caminho mais curto em metros** sobre as ruas (`length`), obtido com `single_source_dijkstra_path_length`. Como o grafo viário é direcionado, o peso adotado é o **menor** entre ida e volta.
5. O traçado real de cada aresta da MST é recuperado e desenhado no mapa.
6. Todo o download é envolvido em tratamento de erro: falhas de rede ou regiões sem vias mapeadas geram uma mensagem compreensível sugerindo o modo Haversine, e não uma exceção crua.
7. O grafo de ruas é mantido em cache (`st.cache_resource`), evitando baixar a mesma região a cada interação.

---

## 📸 Screenshots

As imagens devem ser salvas em `docs/imagens/` e referenciadas aqui.

| Arquivo esperado | Conteúdo |
| --- | --- |
| `docs/imagens/01-mapa.png` | Aba Mapa com estações e a MST traçada sobre as ruas |
| `docs/imagens/02-resultados.png` | Aba Resultados com a tabela de arestas e os contadores de operações |
| `docs/imagens/03-comparacao.png` | Aba Comparação mostrando Kruskal × Prim com o mesmo custo |
| `docs/imagens/04-benchmark.png` | Aba Benchmark com o gráfico de tempo por número de vértices |
| `docs/imagens/05-demonstracao.png` | Aba Demonstração com um grafo didático |

<!--
Depois de adicionar as imagens, basta remover este bloco de comentário:

![Mapa](docs/imagens/01-mapa.png)
![Resultados](docs/imagens/02-resultados.png)
![Comparação](docs/imagens/03-comparacao.png)
![Benchmark](docs/imagens/04-benchmark.png)
![Demonstração](docs/imagens/05-demonstracao.png)
-->

---

## 🎥 Apresentação

O vídeo de apresentação do projeto será disponibilizado aqui.

| Item | Link |
| --- | --- |
| Vídeo da apresentação | _adicionar a URL após a gravação_ |

Roteiro sugerido para a apresentação:

1. Problema e modelagem em grafos (estações → vértices, distâncias por rota → pesos).
2. Kruskal no código, ao vivo, com o mapa.
3. Prim no código, ao vivo, com o mesmo conjunto de estações.
4. Aba Comparação: mesmo custo, arestas diferentes em caso de empate.
5. Aba Benchmark: comportamento dos tempos conforme `V` cresce.
6. Aba Demonstração: grafo clássico de 9 vértices, custo 37, validando as duas implementações.

---

## 👥 Contribuidores

<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/cwtshh">
        <img src="https://github.com/cwtshh.png" width="120px" alt="Foto de perfil de Gustavo Costa de Jesus"><br>
        <sub><b>Gustavo Costa de Jesus</b></sub>
      </a><br>
      <sub>211061814</sub>
    </td>
    <td align="center">
      <a href="https://github.com/xGabrielCv">
        <img src="https://github.com/xGabrielCv.png" width="120px" alt="Foto de perfil de Jésus Gabriel Carvalho Ventura"><br>
        <sub><b>Jésus Gabriel Carvalho Ventura</b></sub>
      </a><br>
      <sub>211062956</sub>
    </td>
  </tr>
</table>

| Nome | Matrícula | GitHub |
| --- | --- | --- |
| [Gustavo Costa de Jesus](https://github.com/cwtshh) | 211061814 | [@cwtshh](https://github.com/cwtshh) |
| [Jésus Gabriel Carvalho Ventura](https://github.com/xGabrielCv) | 211062956 | [@xGabrielCv](https://github.com/xGabrielCv) |
