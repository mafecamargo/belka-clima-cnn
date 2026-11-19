#!/usr/bin/env python3
"""
Passo 2 — Treina e testa a BelkaNet com as imagens de dataset/<classe>/.

Segue o protocolo do artigo de referência (Xiao et al., 2021):
  - divisão treino/validação/teste em 8:1:1, estratificada e sem sobreposição;
  - aumento de dados: recorte aleatório e espelhamento horizontal;
  - weight decay 5e-4; taxa de aprendizado reduzida à metade quando a perda
    de validação não melhora por 5 épocas;
  - o modelo com maior acurácia de validação é o escolhido para o teste;
  - métricas: acurácia, precisão, recall e F1 por classe e em macro-média.

Saídas:
  cnn/relatorio/metricas.json      números do teste
  cnn/relatorio/modelo_belkanet.npz pesos em NumPy
  dashboard/modelo.js              pesos + métricas, lidos pelo dashboard

Uso:  python3 cnn/2_treinar_cnn.py [--epocas 40] [--max-por-classe 400]
Requisitos: numpy e Pillow.
"""
import argparse, base64, json, os, sys, time
from datetime import datetime, timezone
import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from belkanet import BelkaNet, Adam, perda_e_gradiente, TAM, TAM_BASE, CANAIS  # noqa: E402

EXT = (".jpg", ".jpeg", ".png", ".webp")


def carregar_imagem(caminho):
    """Abre, converte para RGB, reduz o lado menor para 72 px e recorta o centro (72x72)."""
    with Image.open(caminho) as im:
        im = im.convert("RGB")
        w, h = im.size
        s = TAM_BASE / min(w, h)
        im = im.resize((max(TAM_BASE, round(w * s)), max(TAM_BASE, round(h * s))), Image.BILINEAR)
        w, h = im.size
        x0, y0 = (w - TAM_BASE) // 2, (h - TAM_BASE) // 2
        return np.asarray(im.crop((x0, y0, x0 + TAM_BASE, y0 + TAM_BASE)), dtype=np.uint8)


def carregar_dataset(pasta, max_por_classe, rng, minimo=40):
    classes, X, y = [], [], []
    for nome in sorted(os.listdir(pasta)):
        d = os.path.join(pasta, nome)
        if not os.path.isdir(d):
            continue
        arqs = sorted(f for f in os.listdir(d) if f.lower().endswith(EXT))
        if len(arqs) < minimo:
            print(f"  ! classe '{nome}' ignorada: só {len(arqs)} imagens (mínimo {minimo})")
            continue
        if len(arqs) > max_por_classe:
            arqs = sorted(rng.choice(arqs, max_por_classe, replace=False).tolist())
        ok = 0
        for f in arqs:
            try:
                X.append(carregar_imagem(os.path.join(d, f)))
                y.append(len(classes))
                ok += 1
            except Exception as e:  # arquivo corrompido não derruba o treino
                print(f"  ! não consegui ler {nome}/{f}: {e}")
        classes.append(nome)
        print(f"  {nome:<14} {ok} imagens")
    return classes, np.stack(X), np.array(y)


def dividir_8_1_1(y, rng):
    tr, va, te = [], [], []
    for c in np.unique(y):
        idx = rng.permutation(np.where(y == c)[0])
        n = len(idx)
        nv = nt = max(1, round(n * 0.1))
        te += idx[:nt].tolist(); va += idx[nt:nt + nv].tolist(); tr += idx[nt + nv:].tolist()
    return np.array(tr), np.array(va), np.array(te)


def centro(Xu8):
    o = (TAM_BASE - TAM) // 2
    return Xu8[:, o:o + TAM, o:o + TAM, :]


def aumentar(Xu8, rng):
    """Recorte aleatório 72->64 e espelhamento horizontal (como no artigo: crop + flip)."""
    n = len(Xu8)
    out = np.empty((n, TAM, TAM, 3), dtype=np.uint8)
    ox = rng.integers(0, TAM_BASE - TAM + 1, n); oy = rng.integers(0, TAM_BASE - TAM + 1, n)
    flip = rng.random(n) < 0.5
    for i in range(n):
        im = Xu8[i, oy[i]:oy[i] + TAM, ox[i]:ox[i] + TAM, :]
        out[i] = im[:, ::-1, :] if flip[i] else im
    return out


def metricas(y_true, y_pred, classes):
    k = len(classes)
    cm = np.zeros((k, k), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    por_classe = {}
    for i, nome in enumerate(classes):
        tp = cm[i, i]; fp = cm[:, i].sum() - tp; fn = cm[i, :].sum() - tp
        P = tp / (tp + fp) if tp + fp else 0.0
        R = tp / (tp + fn) if tp + fn else 0.0
        F = 2 * P * R / (P + R) if P + R else 0.0
        por_classe[nome] = {"precisao": round(P, 4), "recall": round(R, 4), "f1": round(F, 4), "n": int(cm[i].sum())}
    maP = float(np.mean([v["precisao"] for v in por_classe.values()]))
    maR = float(np.mean([v["recall"] for v in por_classe.values()]))
    maF = 2 * maP * maR / (maP + maR) if maP + maR else 0.0
    return {"acuracia": round(float(np.trace(cm) / cm.sum()), 4), "macro_precisao": round(maP, 4),
            "macro_recall": round(maR, 4), "macro_f1": round(maF, 4),
            "por_classe": por_classe, "matriz_confusao": cm.tolist()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=os.path.join(RAIZ, "dataset"))
    ap.add_argument("--epocas", type=int, default=40)
    ap.add_argument("--lote", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--max-por-classe", type=int, default=400)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    print("1) Lendo imagens de", a.dataset)
    classes, X, y = carregar_dataset(a.dataset, a.max_por_classe, rng)
    if len(classes) < 2:
        sys.exit("Preciso de pelo menos 2 classes com imagens. Rode antes: python3 cnn/1_coletar_imagens.py")

    tr, va, te = dividir_8_1_1(y, rng)
    print(f"2) Divisão 8:1:1 -> treino {len(tr)}, validação {len(va)}, teste {len(te)}")

    # normalização: média e desvio por canal, calculados só no treino
    media = (X[tr].reshape(-1, 3).mean(0) / 255).astype(np.float32)
    desvio = (X[tr].reshape(-1, 3).std(0) / 255).astype(np.float32)
    norm = lambda u8: ((u8.astype(np.float32) / 255) - media) / desvio
    Xva, Xte = norm(centro(X[va])), norm(centro(X[te]))

    cont = np.bincount(y[tr], minlength=len(classes))
    pesos_classe = (cont.sum() / (len(classes) * cont)).astype(np.float32)

    rede = BelkaNet(len(classes), seed=a.seed)
    opt = Adam(rede.parametros(), lr=a.lr, wd=5e-4)
    n_par = sum(getattr(o, n).size for o, n in rede.parametros())
    print(f"3) BelkaNet: {len(CANAIS)} blocos conv {CANAIS} + GAP + softmax, {n_par:,} parâmetros")

    melhor = {"acc": -1, "pesos": None, "epoca": 0}
    hist, melhor_perda, parado = [], 1e9, 0
    t0 = time.time()
    for ep in range(1, a.epocas + 1):
        ordem = rng.permutation(tr)
        soma, acertos = 0.0, 0
        for i in range(0, len(ordem), a.lote):
            idx = ordem[i:i + a.lote]
            xb, yb = norm(aumentar(X[idx], rng)), y[idx]
            logits = rede.forward(xb, treino=True)
            perda, d = perda_e_gradiente(logits, yb, pesos_classe)
            rede.backward(d)
            opt.passo()
            soma += perda * len(idx); acertos += int((logits.argmax(1) == yb).sum())
        lv = np.concatenate([rede.forward(Xva[i:i + 64]) for i in range(0, len(Xva), 64)])
        perda_va, _ = perda_e_gradiente(lv, y[va], pesos_classe)
        acc_va = float((lv.argmax(1) == y[va]).mean())
        hist.append({"epoca": ep, "perda_treino": round(soma / len(tr), 4), "acc_treino": round(acertos / len(tr), 4),
                     "perda_val": round(perda_va, 4), "acc_val": round(acc_va, 4), "lr": opt.lr})
        marca = ""
        if acc_va > melhor["acc"]:
            melhor = {"acc": acc_va, "pesos": rede.pesos(), "epoca": ep}; marca = "  <- melhor"
        if perda_va < melhor_perda - 1e-4:
            melhor_perda, parado = perda_va, 0
        else:
            parado += 1
            if parado >= 5:
                opt.lr *= 0.5; parado = 0
        print(f"   época {ep:>2}/{a.epocas}  perda {soma/len(tr):.3f}  acc treino {acertos/len(tr):.3f}  "
              f"acc val {acc_va:.3f}  lr {opt.lr:.5f}  [{time.time()-t0:.0f}s]{marca}")

    print(f"4) Teste com o modelo da época {melhor['epoca']} (maior acurácia de validação: {melhor['acc']:.3f})")
    rede.carregar_pesos(melhor["pesos"])
    pred = rede.prever_proba(Xte).argmax(1)
    m = metricas(y[te], pred, classes)
    print(f"   acurácia {m['acuracia']:.3f} | macro precisão {m['macro_precisao']:.3f} | "
          f"macro recall {m['macro_recall']:.3f} | macro F1 {m['macro_f1']:.3f}")
    for nome, v in m["por_classe"].items():
        print(f"   {nome:<14} P {v['precisao']:.2f}  R {v['recall']:.2f}  F1 {v['f1']:.2f}  (n={v['n']})")

    # ---- exportação ----------------------------------------------------------
    os.makedirs(os.path.join(AQUI, "relatorio"), exist_ok=True)
    pesos = rede.pesos()
    np.savez_compressed(os.path.join(AQUI, "relatorio", "modelo_belkanet.npz"),
                        classes=np.array(classes), media=media, desvio=desvio, **{f"p{i}": p for i, p in enumerate(pesos)})
    info = {
        "nome": "BelkaNet", "treinado_em": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "classes": classes, "tam": TAM, "tam_base": TAM_BASE, "canais": list(CANAIS),
        "media": media.tolist(), "desvio": desvio.tolist(), "parametros": int(n_par),
        "imagens": {"total": int(len(y)), "treino": int(len(tr)), "validacao": int(len(va)), "teste": int(len(te)),
                    "por_classe": {c: int((y == i).sum()) for i, c in enumerate(classes)}},
        "epocas": a.epocas, "melhor_epoca": melhor["epoca"], "acc_validacao": round(melhor["acc"], 4),
        "teste": m,
    }
    with open(os.path.join(AQUI, "relatorio", "metricas.json"), "w", encoding="utf-8") as f:
        json.dump({**info, "historico": hist}, f, ensure_ascii=False, indent=1)
    blob = {**info, "pesos": [{"forma": list(p.shape), "b64": base64.b64encode(p.astype("<f4").tobytes()).decode()} for p in pesos]}
    destino = os.path.join(RAIZ, "dashboard", "modelo.js")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("// Gerado por cnn/2_treinar_cnn.py — não edite à mão.\nwindow.BELKA_MODELO = ")
        json.dump(blob, f, ensure_ascii=False)
        f.write(";\n")
    print("5) Pronto. Modelo gravado em", destino)


if __name__ == "__main__":
    main()
