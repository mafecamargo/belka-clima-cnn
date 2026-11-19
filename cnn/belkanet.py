"""
BelkaNet — CNN pequena escrita só com NumPy.

Inspirada na MeteCNN (Xiao et al., 2021): blocos conv 3x3 + ReLU + max-pooling,
sem camadas totalmente conectadas escondidas; no fim, global average pooling (GAP)
seguido de um classificador softmax.

Entrada: imagens RGB 64x64 (formato NHWC, float32 normalizado).
A mesma rede é reimplementada em JavaScript no dashboard (dashboard/index.html),
então o formato dos pesos aqui é o contrato entre treino e uso.
"""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

TAM = 64            # lado da imagem que entra na rede
TAM_BASE = 72       # lado antes do recorte (aumento de dados: recorte aleatório 72 -> 64)
CANAIS = (16, 32, 64, 96)   # filtros de cada bloco convolucional


class Conv3x3:
    """Convolução 3x3, stride 1, padding 1. Pesos W: (C_in*9, C_out), índice = c*9 + ki*3 + kj."""

    def __init__(self, c_in, c_out, rng):
        self.c_in, self.c_out = c_in, c_out
        self.W = (rng.standard_normal((c_in * 9, c_out)) * np.sqrt(2.0 / (c_in * 9))).astype(np.float32)
        self.b = np.zeros(c_out, dtype=np.float32)

    def forward(self, x, treino=False):
        n, h, w, c = x.shape
        xp = np.pad(x, ((0, 0), (1, 1), (1, 1), (0, 0)))
        cols = sliding_window_view(xp, (3, 3), axis=(1, 2)).reshape(n * h * w, c * 9)
        if treino:
            self._cols, self._shape = cols, x.shape
        return (cols @ self.W + self.b).reshape(n, h, w, self.c_out)

    def backward(self, d):
        n, h, w, c = self._shape
        d2 = d.reshape(-1, self.c_out)
        self.dW = self._cols.T @ d2
        self.db = d2.sum(0)
        dcols = (d2 @ self.W.T).reshape(n, h, w, c, 3, 3)
        dxp = np.zeros((n, h + 2, w + 2, c), dtype=np.float32)
        for i in range(3):
            for j in range(3):
                dxp[:, i:i + h, j:j + w, :] += dcols[:, :, :, :, i, j]
        return dxp[:, 1:-1, 1:-1, :]

    params = property(lambda s: [(s, "W"), (s, "b")])


class ReLU:
    def forward(self, x, treino=False):
        self._m = x > 0
        return x * self._m

    def backward(self, d):
        return d * self._m

    params = []


class MaxPool2:
    def forward(self, x, treino=False):
        n, h, w, c = x.shape
        xr = x.reshape(n, h // 2, 2, w // 2, 2, c)
        out = xr.max(axis=(2, 4))
        if treino:
            self._mask = xr == out[:, :, None, :, None, :]
            self._shape = x.shape
        return out

    def backward(self, d):
        m = self._mask
        g = m * d[:, :, None, :, None, :] / np.maximum(m.sum(axis=(2, 4), keepdims=True), 1)
        return g.reshape(self._shape).astype(np.float32)

    params = []


class GAP:
    """Global average pooling: média de cada mapa de características."""

    def forward(self, x, treino=False):
        self._shape = x.shape
        return x.mean(axis=(1, 2))

    def backward(self, d):
        n, h, w, c = self._shape
        return np.broadcast_to(d[:, None, None, :] / (h * w), self._shape).astype(np.float32)

    params = []


class Dropout:
    def __init__(self, p, rng):
        self.p, self.rng = p, rng

    def forward(self, x, treino=False):
        if not treino:
            return x
        self._m = (self.rng.random(x.shape) >= self.p).astype(np.float32) / (1 - self.p)
        return x * self._m

    def backward(self, d):
        return d * self._m

    params = []


class Dense:
    def __init__(self, n_in, n_out, rng):
        self.W = (rng.standard_normal((n_in, n_out)) * np.sqrt(1.0 / n_in)).astype(np.float32)
        self.b = np.zeros(n_out, dtype=np.float32)

    def forward(self, x, treino=False):
        self._x = x
        return x @ self.W + self.b

    def backward(self, d):
        self.dW = self._x.T @ d
        self.db = d.sum(0)
        return d @ self.W.T

    params = property(lambda s: [(s, "W"), (s, "b")])


class BelkaNet:
    def __init__(self, n_classes, seed=42, dropout=0.3):
        rng = np.random.default_rng(seed)
        self.n_classes = n_classes
        c = (3,) + CANAIS
        self.camadas = []
        for i in range(len(CANAIS)):
            self.camadas += [Conv3x3(c[i], c[i + 1], rng), ReLU()]
            if i < len(CANAIS) - 1:
                self.camadas.append(MaxPool2())
        self.camadas += [GAP(), Dropout(dropout, rng), Dense(CANAIS[-1], n_classes, rng)]

    # ---- inferência / treino -------------------------------------------------
    def forward(self, x, treino=False):
        for cam in self.camadas:
            x = cam.forward(x, treino)
        return x

    def backward(self, d):
        for cam in reversed(self.camadas):
            d = cam.backward(d)

    def parametros(self):
        return [p for cam in self.camadas for p in cam.params]

    def prever_proba(self, x, lote=64):
        saidas = []
        for i in range(0, len(x), lote):
            saidas.append(softmax(self.forward(x[i:i + lote])))
        return np.concatenate(saidas)

    # ---- pesos ---------------------------------------------------------------
    def pesos(self):
        return [getattr(o, n).copy() for o, n in self.parametros()]

    def carregar_pesos(self, lista):
        for (o, n), v in zip(self.parametros(), lista):
            setattr(o, n, v.astype(np.float32).copy())


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def perda_e_gradiente(logits, y, pesos_classe=None):
    """Entropia cruzada (com peso por classe para compensar desbalanceamento)."""
    n = len(y)
    p = softmax(logits)
    w = np.ones(n, dtype=np.float32) if pesos_classe is None else pesos_classe[y]
    perda = float(-(w * np.log(p[np.arange(n), y] + 1e-9)).sum() / w.sum())
    d = p.copy()
    d[np.arange(n), y] -= 1
    d *= (w / w.sum())[:, None]
    return perda, d.astype(np.float32)


class Adam:
    def __init__(self, params, lr=1e-3, wd=5e-4, b1=0.9, b2=0.999):
        self.params, self.lr, self.wd, self.b1, self.b2, self.t = params, lr, wd, b1, b2, 0
        self.m = [np.zeros_like(getattr(o, n)) for o, n in params]
        self.v = [np.zeros_like(getattr(o, n)) for o, n in params]

    def passo(self):
        self.t += 1
        for i, (o, n) in enumerate(self.params):
            p, g = getattr(o, n), getattr(o, "d" + n)
            if n == "W":
                g = g + self.wd * p          # weight decay 5e-4, como no artigo
            self.m[i] = self.b1 * self.m[i] + (1 - self.b1) * g
            self.v[i] = self.b2 * self.v[i] + (1 - self.b2) * g * g
            mh = self.m[i] / (1 - self.b1 ** self.t)
            vh = self.v[i] / (1 - self.b2 ** self.t)
            setattr(o, n, (p - self.lr * mh / (np.sqrt(vh) + 1e-8)).astype(np.float32))
