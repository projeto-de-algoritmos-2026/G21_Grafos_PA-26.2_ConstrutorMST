from grafo import UnionFind


def kruskal(n, arestas):
    uf = UnionFind(n)
    mst = []
    custo_total = 0.0

    for u, v, peso in sorted(arestas, key=lambda e: e[2]):
        if uf.union(u, v):
            mst.append((u, v, peso))
            custo_total += peso

    return mst, custo_total
