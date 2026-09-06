import math


def haversine(lat1, lon1, lat2, lon2):
    raio_terra_km = 6371.0

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return raio_terra_km * c


class UnionFind:
    def __init__(self, n):
        self.pai = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.pai[x] != x:
            self.pai[x] = self.find(self.pai[x])
        return self.pai[x]

    def union(self, x, y):
        raiz_x, raiz_y = self.find(x), self.find(y)
        if raiz_x == raiz_y:
            return False

        if self.rank[raiz_x] < self.rank[raiz_y]:
            raiz_x, raiz_y = raiz_y, raiz_x
        self.pai[raiz_y] = raiz_x
        if self.rank[raiz_x] == self.rank[raiz_y]:
            self.rank[raiz_x] += 1

        return True


