#!/usr/bin/env python3
"""
Passo 1 — Coleta as imagens de treino.

Fonte: fotografias feitas e publicadas por órgãos do governo dos EUA
(FEMA, NOAA, USGS, Serviço Florestal, Serviço de Parques, BLM, USDA, FWS),
todas em domínio público. Elas são buscadas pela API do Wikimedia Commons,
que guarda cópia dessas fotos com a licença e o órgão de origem marcados
(modelos "PD-USGov-..."). Usamos a API do Commons porque os acervos originais
(por exemplo photolib.noaa.gov) bloqueiam acesso automatizado.

O rótulo de cada imagem vem do título do arquivo (ex.: "flood", "wildfire"),
com filtros para descartar mapas, gráficos, retratos e cerimônias.

Saídas:
  dataset/<classe>/<id>.jpg    miniaturas (~330 px de largura)
  dataset/fontes.csv           classe, arquivo, título, órgão, licença e link de cada imagem

Uso:  python3 cnn/1_coletar_imagens.py [--max-por-classe 400]
Só usa a biblioteca padrão do Python.
"""
import argparse, csv, json, os, random, re, ssl, subprocess, sys, time
import urllib.parse, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://commons.wikimedia.org/w/api.php"
UA = "BelkaClima/1.0 (projeto academico FIAP Global Solution; coleta de imagens em dominio publico)"

ORGAOS = {
    "PD-USGov-FEMA": "FEMA", "PD-USGov-NOAA": "NOAA", "PD-USGov-USGS": "USGS",
    "PD-USGov-USDA-FS": "US Forest Service", "PD-USGov-NPS": "National Park Service",
    "PD-USGov-BLM": "Bureau of Land Management", "PD-USGov-USDA": "USDA",
    "PD-USGov-FWS": "Fish and Wildlife Service", "PD-USGov-Military": "Forças Armadas dos EUA",
    "PD-USGov": "Governo dos EUA",
}

# classe -> termos procurados no título do arquivo
CLASSES = {
    "enchente":     ["flood", "flooding", "flooded", "floodwaters"],
    "deslizamento": ["landslide", "landslides", "mudslide", "debris flow"],
    "incendio":     ["wildfire", "wildfires", "forest fire", "brush fire"],
    "tempestade":   ["lightning", "thunderstorm"],
    "tornado":      ["tornado", "funnel cloud"],
    "seca":         ["drought", "dry lake", "cracked"],
    "neve":         ["snowstorm", "blizzard", "snow storm", "ice storm"],
}

# títulos que indicam que a imagem não é uma foto do evento
EXCLUIR_GERAL = re.compile(
    r"\bmaps?\b|radar|chart|graph|track|outlook|forecast|satellite|goes|modis|landsat|reflectivity|velocity|"
    r"sounding|plot|diagram|logo|poster|path|aircraft|f-35|p-38|gr4|gr\.4|panavia|squadron|\braf\b|usaf|"
    r"lightning ii|simulat|model|locator|hazard|risk|precip|rainfall|anomal|index|monitor|icon|symbol|sign\b|"
    r"cover|page|report|brochure|figure|fig\.|schematic|illustration|drawing|painting|memorial|ceremony|"
    r"meeting|briefing|conference|portrait|press|speaks|visit|tour|training|exercise|drill|greets|officer|"
    r"coordinating|community relations|teams?\b|workers|specialist|assistance|registration|governor|president|"
    r"secretary|senator|strategy|task force|school|inspect|assess|volunteer|donation|recovery center|shelter|"
    r"interview|\.png", re.I)
EXCLUIR_CLASSE = {
    "tempestade":   re.compile(r"protection|rod|arrester|detector|test|tower|scar|damage|struck tree", re.I),
    "tornado":      re.compile(r"safe room|siren", re.I),
    "seca":         re.compile(r"relief|aid\b|tolerant|resistant|research|seed", re.I),
    "enchente":     re.compile(r"insurance|gauge|gage|control|wall|gate|warning", re.I),
    "incendio":     re.compile(r"prevention|smokey|engine|truck|station|helmet", re.I),
    "deslizamento": re.compile(r"warning", re.I),
    "neve":         re.compile(r"plow|removal", re.I),
}
# "Lightning" e "Tornado" também são nomes de aviões militares
SEM_ORGAO = {"tempestade": {"PD-USGov-Military"}, "tornado": {"PD-USGov-Military"}}


def baixar(url, binario=False, tentativas=3):
    """GET com urllib; se o Python do Mac reclamar de certificado, usa o curl do sistema."""
    for t in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                dados = r.read()
            return dados if binario else dados.decode("utf-8")
        except ssl.SSLError:
            break
        except Exception as e:
            if "CERTIFICATE" in str(e).upper():
                break
            time.sleep(1.5 * (t + 1))
    try:
        out = subprocess.run(["curl", "-sSL", "--fail", "-m", "40", "-A", UA, url], capture_output=True, check=True).stdout
        return out if binario else out.decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"falha ao baixar {url[:80]}: {e}")


def buscar(consulta, limite):
    """Busca arquivos no Commons e devolve id, título e URL da miniatura."""
    achados, offset = [], 0
    while offset < limite:
        q = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": 50,
             "gsroffset": offset, "gsrsearch": consulta, "prop": "imageinfo", "iiprop": "url|mime|size", "iiurlwidth": 330}
        r = json.loads(baixar(API + "?" + urllib.parse.urlencode(q)))
        for p in (r.get("query", {}).get("pages", {}) or {}).values():
            ii = (p.get("imageinfo") or [None])[0]
            if not ii or ii.get("mime") != "image/jpeg" or min(ii.get("width", 0), ii.get("height", 0)) < 300:
                continue
            achados.append({"id": p["pageid"], "titulo": p["title"], "thumb": ii.get("thumburl"), "pagina": ii.get("descriptionurl")})
        if "continue" not in r:
            break
        offset = r["continue"]["gsroffset"]
        time.sleep(0.2)
    return achados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-por-classe", type=int, default=400)
    ap.add_argument("--saida", default=os.path.join(RAIZ, "dataset"))
    a = ap.parse_args()
    rnd = random.Random(42)
    os.makedirs(a.saida, exist_ok=True)
    linhas = []

    for classe, termos in CLASSES.items():
        print(f"\n== {classe} ==")
        por_orgao, vistos = {}, set()
        for modelo in ORGAOS:
            if modelo in SEM_ORGAO.get(classe, ()):
                continue
            for termo in termos:
                try:
                    res = buscar(f'filetype:bitmap intitle:"{termo}" hastemplate:"{modelo}"', 250)
                except Exception as e:
                    print("  !", e); continue
                for x in res:
                    t = x["titulo"]
                    if x["id"] in vistos or not x["thumb"] or EXCLUIR_GERAL.search(t):
                        continue
                    if classe in EXCLUIR_CLASSE and EXCLUIR_CLASSE[classe].search(t):
                        continue
                    vistos.add(x["id"]); x["modelo"] = modelo
                    por_orgao.setdefault(modelo, []).append(x)
        # escolhe até o limite, revezando entre os órgãos para não depender de um só acervo
        for lst in por_orgao.values():
            rnd.shuffle(lst)
        escolhidos = []
        while len(escolhidos) < a.max_por_classe and any(por_orgao.values()):
            for m in list(por_orgao):
                if por_orgao[m] and len(escolhidos) < a.max_por_classe:
                    escolhidos.append(por_orgao[m].pop())
        print(f"  {len(vistos)} candidatas, baixando {len(escolhidos)}")

        pasta = os.path.join(a.saida, classe)
        os.makedirs(pasta, exist_ok=True)
        ok = 0
        for i, x in enumerate(escolhidos, 1):
            destino = os.path.join(pasta, f"{x['id']}.jpg")
            try:
                if not os.path.exists(destino):
                    dados = baixar(x["thumb"], binario=True)
                    if dados[:2] != b"\xff\xd8":
                        raise RuntimeError("resposta não é JPEG")
                    with open(destino, "wb") as f:
                        f.write(dados)
                    time.sleep(0.08)
                ok += 1
                linhas.append([classe, f"{classe}/{x['id']}.jpg", x["titulo"].replace("File:", ""), ORGAOS[x["modelo"]],
                               x["modelo"] + " (domínio público)", x["pagina"]])
            except Exception as e:
                print("  !", e)
            if i % 50 == 0:
                print(f"  {i}/{len(escolhidos)}")
        print(f"  {ok} imagens em dataset/{classe}/")

    with open(os.path.join(a.saida, "fontes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["classe", "arquivo", "titulo", "orgao", "licenca", "pagina_de_origem"])
        w.writerows(linhas)
    print(f"\nPronto: {len(linhas)} imagens. Fontes listadas em dataset/fontes.csv")
    print("Próximo passo: python3 cnn/2_treinar_cnn.py")


if __name__ == "__main__":
    sys.exit(main())
