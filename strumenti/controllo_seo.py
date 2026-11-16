#!/usr/bin/env python3
"""Controllo SEO secondo le regole Google Search Central (solo libreria standard Python 3.9+).

Uso:
    python3 controllo_seo.py https://tuosito.it            # home + robots.txt + sitemap + 20 pagine dalla sitemap
    python3 controllo_seo.py https://tuosito.it --pagine 100

Controlla quello che si puo' verificare da fuori, senza accesso al server:
- redirect http -> https e www -> dominio scelto (301/308, niente catene)
- robots.txt: raggiungibile, sotto 500 KiB, riga Sitemap, Googlebot non bloccato
- sitemap: raggiungibile, sotto 50.000 URL e 50 MB, URL assoluti
- per ogni pagina: codice 200, <title> e meta description presenti e unici, un solo canonical
  assoluto, un solo <h1>, alt su tutte le <img>, <head> valido, peso HTML sotto 2 MB,
  noindex non messo per sbaglio, JSON-LD valido (e Product completo se presente)
- una pagina inesistente deve rispondere 404/410 (non 200 = soft 404)
Non modifica niente: legge e basta.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
try:  # parser XML sicuro se disponibile (pip install defusedxml): le sitemap vengono da siti esterni
    import defusedxml.ElementTree as ET
except ImportError:  # expat recente non risolve entita' esterne e limita l'espansione
    import xml.etree.ElementTree as ET

UA = "Mozilla/5.0 (compatible; controllo-seo/1.0; +https://github.com)"
HEAD_VALIDI = {"html", "head", "title", "meta", "link", "script", "style", "base", "noscript", "template"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def get(url: str, seguire=True, limite=60 * 1024 * 1024):
    opener = urllib.request.build_opener() if seguire else urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        r = opener.open(req, timeout=30)
        return r.status, dict(r.headers), r.read(limite)
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), b""
    except Exception as e:  # rete, DNS, certificato
        return 0, {}, str(e).encode()


class Rapporto:
    def __init__(self):
        self.err, self.avv, self.ok = [], [], []

    def e(self, t): self.err.append(t)
    def a(self, t): self.avv.append(t)
    def o(self, t): self.ok.append(t)


def controlla_redirect(base: str, r: Rapporto):
    p = urllib.parse.urlparse(base)
    host = p.netloc
    altro = host[4:] if host.startswith("www.") else "www." + host
    for u in (f"http://{host}/", f"https://{altro}/"):
        s, h, _ = get(u, seguire=False)
        if s in (301, 308):
            loc = h.get("Location") or h.get("location", "")
            s2, _, _ = get(loc, seguire=False) if loc else (0, {}, b"")
            if s2 in (301, 302, 307, 308):
                r.a(f"{u} fa una catena di redirect (meglio un solo salto verso {base})")
            else:
                r.o(f"{u} -> {loc} ({s})")
        elif s in (302, 307):
            r.a(f"{u} usa un redirect temporaneo {s}: per una scelta definitiva serve 301")
        elif s == 0:
            pass  # host alternativo non esistente: va bene
        elif s == 200 and u.startswith("http://"):
            r.e(f"{u} risponde 200 in http: serve un 301 verso https")


def controlla_robots(base: str, r: Rapporto) -> list[str]:
    s, _, b = get(base + "/robots.txt")
    if s != 200:
        r.a(f"robots.txt risponde {s} (4xx = nessuna restrizione; 5xx = Google blocca la scansione)")
        return []
    if len(b) > 500 * 1024:
        r.e("robots.txt oltre 500 KiB: Google ignora il resto")
    testo = b.decode("utf-8", "ignore")
    sitemaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", testo)
    if not sitemaps:
        r.a("robots.txt senza riga 'Sitemap: https://...'")
    if re.search(r"(?im)^\s*crawl-delay", testo):
        r.a("robots.txt usa crawl-delay: Google lo ignora")
    gruppi, ua = collections.defaultdict(list), []
    nuovo = True
    for riga in testo.splitlines():
        riga = riga.split("#")[0].strip()
        if not riga or ":" not in riga:
            continue
        k, v = [x.strip() for x in riga.split(":", 1)]
        k = k.lower()
        if k == "user-agent":
            if nuovo:
                ua = []
            ua.append(v.lower()); nuovo = False
        elif k in ("allow", "disallow"):
            nuovo = True
            for u in ua:
                gruppi[u].append((k, v))
    regole = gruppi.get("googlebot") or gruppi.get("*") or []
    if ("disallow", "/") in regole and not any(k == "allow" and v in ("/", "/*") for k, v in regole):
        r.e("robots.txt blocca TUTTO il sito a Googlebot (Disallow: /)")
    for k, v in regole:
        if k == "disallow" and re.search(r"\.(css|js)\$?$|/(css|js|assets|static)/?$", v):
            r.a(f"robots.txt blocca risorse ({v}): se servono a capire la pagina, Google non la renderizza bene")
    r.o(f"robots.txt ok ({len(b)} byte)")
    return sitemaps


def url_da_sitemap(url: str, r: Rapporto, profondita=0) -> list[str]:
    s, _, b = get(url)
    if s != 200:
        r.e(f"sitemap {url} risponde {s}")
        return []
    if len(b) > 50 * 1024 * 1024:
        r.e(f"sitemap {url} oltre 50 MB: dividerla")
    try:
        root = ET.fromstring(b)
    except Exception as e:  # ParseError o entita' rifiutate da defusedxml
        r.e(f"sitemap {url} non e' XML valido: {e}")
        return []
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    if root.tag.endswith("sitemapindex") and profondita < 2:
        out = []
        for loc in root.iter(ns + "loc"):
            out += url_da_sitemap(loc.text.strip(), r, profondita + 1)
        return out
    locs = [l.text.strip() for l in root.iter(ns + "loc") if l.text]
    if len(locs) > 50000:
        r.e(f"sitemap {url} con {len(locs)} URL: limite 50.000")
    rel = [l for l in locs if not l.startswith("http")]
    if rel:
        r.e(f"sitemap {url}: {len(rel)} URL non assoluti")
    r.o(f"sitemap {url}: {len(locs)} URL")
    return locs


def controlla_pagina(url: str, r: Rapporto, titoli, descrizioni):
    s, h, b = get(url)
    if s != 200:
        r.e(f"{url} risponde {s}")
        return
    if len(b) > 2 * 1024 * 1024:
        r.e(f"{url} pesa {len(b) // 1024} KB: Googlebot legge solo i primi 2 MB")
    html = b.decode("utf-8", "ignore")
    head = html.split("</head>")[0] if "</head>" in html else html[:20000]
    fuori = {t.lower() for t in re.findall(r"<([a-zA-Z][\w-]*)", head)} - HEAD_VALIDI
    if fuori:
        r.e(f"{url}: nel <head> ci sono {sorted(fuori)}: Google chiude l'head li' e ignora il resto (canonical, robots)")
    t = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    if not t or not t.group(1).strip():
        r.e(f"{url}: manca <title>")
    else:
        titoli[t.group(1).strip()].append(url)
    d = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', html, re.I)
    if not d or not d.group(1).strip():
        r.a(f"{url}: manca la meta description")
    else:
        descrizioni[d.group(1).strip()].append(url)
    can = re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]*>', head, re.I)
    if len(can) != 1:
        r.e(f"{url}: {len(can)} tag canonical (deve essere 1)")
    elif not re.search(r'href=["\']https?://', can[0]):
        r.a(f"{url}: canonical relativo (meglio assoluto)")
    if len(re.findall(r"<h1[\s>]", html, re.I)) != 1:
        r.a(f"{url}: {len(re.findall(r'<h1[\\s>]', html, re.I))} titoli <h1> (consigliato 1)")
    corpo = re.sub(r"<script\b.*?</script>", "", html, flags=re.S | re.I)  # <img> dentro il JS: non sono HTML
    senza_alt = [i for i in re.findall(r"<img\b[^>]*>", corpo, re.I) if not re.search(r'alt=["\'][^"\']+', i)]
    if senza_alt:
        r.a(f"{url}: {len(senza_alt)} immagini senza alt descrittivo")
    xr = h.get("X-Robots-Tag", "") or h.get("x-robots-tag", "")
    if re.search(r"noindex", head, re.I) or "noindex" in xr.lower():
        r.a(f"{url}: ha noindex (voluto?)")
    for blocco in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S | re.I):
        try:
            dati = json.loads(blocco)
        except ValueError:
            r.e(f"{url}: JSON-LD non valido")
            continue
        nodi = dati if isinstance(dati, list) else dati.get("@graph", [dati])
        for n in nodi:
            if not isinstance(n, dict):
                continue
            tipo = n.get("@type")
            if tipo == "FAQPage":
                r.a(f"{url}: FAQPage non da' piu' rich result in Google (dal 7/05/2026)")
            if tipo == "Product":
                for k in ("name", "image", "offers"):
                    if not n.get(k):
                        r.e(f"{url}: Product senza '{k}' (obbligatorio)")
                o = n.get("offers") or {}
                o = o[0] if isinstance(o, list) and o else o
                if isinstance(o, dict):
                    if o.get("@type") == "AggregateOffer":
                        r.a(f"{url}: AggregateOffer su pagina prodotto: per il merchant listing serve Offer")
                    try:
                        if float(str(o.get("price", "0")).replace(",", ".")) <= 0:
                            r.e(f"{url}: price mancante o zero")
                    except ValueError:
                        r.e(f"{url}: price non numerico ({o.get('price')})")
                    if not o.get("priceCurrency"):
                        r.e(f"{url}: priceCurrency mancante")
                    for k in ("availability", "shippingDetails", "hasMerchantReturnPolicy"):
                        if not o.get(k):
                            r.a(f"{url}: Offer senza {k} (consigliato)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Controllo SEO secondo Google Search Central")
    ap.add_argument("sito")
    ap.add_argument("--pagine", type=int, default=20)
    a = ap.parse_args()
    base = a.sito.rstrip("/")
    r = Rapporto()
    controlla_redirect(base, r)
    sitemaps = controlla_robots(base, r) or [base + "/sitemap.xml"]
    urls = []
    for sm in sitemaps:
        urls += url_da_sitemap(sm, r)
    pagine = [base + "/"] + [u for u in urls if u.rstrip("/") != base][: a.pagine]
    titoli, descrizioni = collections.defaultdict(list), collections.defaultdict(list)
    for u in pagine:
        controlla_pagina(u, r, titoli, descrizioni)
    for t, us in titoli.items():
        if len(us) > 1:
            r.e(f"title uguale su {len(us)} pagine: '{t[:60]}'")
    for d, us in descrizioni.items():
        if len(us) > 1:
            r.a(f"meta description uguale su {len(us)} pagine")
    s, _, _ = get(base + "/pagina-che-non-esiste-controllo-seo-7f3a")
    if s == 200:
        r.e("una pagina inesistente risponde 200: soft 404 (deve rispondere 404 o 410)")
    print(f"\nControllo SEO di {base}: {len(pagine)} pagine\n")
    for titolo, lista, segno in (("ERRORI", r.err, "X"), ("AVVISI", r.avv, "!"), ("OK", r.ok, "v")):
        print(f"{titolo} ({len(lista)})")
        for x in lista:
            print(f"  {segno} {x}")
        print()
    return 1 if r.err else 0


if __name__ == "__main__":
    sys.exit(main())
