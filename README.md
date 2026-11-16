# SEO secondo Google, in italiano — skill gratuita per agenti AI

Tutta la documentazione ufficiale **Google Search Central** su scansione, indicizzazione, aspetto nei risultati, dati strutturati, e-commerce, IA generativa, spam e cali di traffico, **letta per intero e riassunta in italiano**, pronta da dare al tuo agente AI (Claude Code, OpenCode, Cursor, Codex, qualsiasi agente che legge skill in Markdown) o da leggere tu.

Più uno **strumento gratuito** che controlla il tuo sito sui punti verificabili da codice.

> Regalo di [Zero Pensieri Siti](https://zeropensierisiti.it). Nessuna registrazione, nessun costo.

## Cosa c'è dentro

| File | Cosa fa |
|---|---|
| `skill/seo-google-it/SKILL.md` | Le 20 regole d'oro e le liste di controllo: pubblicare prodotti, togliere prodotti, cambiare URL, robots.txt e noindex, mettere in pausa un sito, problemi in Search Console |
| `skill/seo-google-it/references/regole-google.md` | Le regole complete, con numeri esatti e sintassi (limiti di robots.txt e sitemap, codici HTTP, meta robots, canonical, dati strutturati Product/Organization/Breadcrumb/Review, hreflang, ...) |
| `strumenti/controllo_seo.py` | Controlla un sito: redirect, robots.txt, sitemap, title e description doppi, canonical, H1, alt delle immagini, `<head>` valido, peso delle pagine, noindex, JSON-LD Product, soft 404 |

## Come si usa

**Con Claude Code**
```bash
git clone https://github.com/tuareggitano-ui/seo-google-skill-it
cp -r seo-google-skill-it/skill/seo-google-it ~/.claude/skills/
```
**Con OpenCode**: copia la stessa cartella in `~/.config/opencode/skills/`.
**Con altri agenti**: dai al tuo agente `SKILL.md` come istruzioni, e `references/regole-google.md` quando serve il dettaglio.

**Controllo del sito** (Python 3.9+, nessuna libreria da installare):
```bash
python3 strumenti/controllo_seo.py https://tuosito.it
python3 strumenti/controllo_seo.py https://tuosito.it --pagine 100
```
Legge soltanto, non modifica niente. Esce con codice 1 se trova errori, quindi lo puoi mettere in un controllo automatico.

## Alcune cose che (quasi) nessuno sa

- **robots.txt non toglie una pagina da Google.** La blocca dalla scansione, ma può comparire lo stesso senza descrizione. Per toglierla serve `noindex` su una pagina *non* bloccata.
- **Un prodotto esaurito non va tolto**: la pagina resta con disponibilità "esaurito".
- **Mandare le pagine vecchie alla home** con un redirect: per Google è come un errore (soft 404).
- **Googlebot legge solo i primi 2 MB** di ogni pagina HTML.
- **FAQPage non dà più risultati arricchiti** da maggio 2026.
- **Per AI Overviews e AI Mode non serve nessun trucco**: basta essere indicizzati e utili.

## Fonti e licenza

Fonte: [Google Search Central](https://developers.google.com/search/docs), documentazione rilasciata da Google con licenza [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); questo è un riassunto e una traduzione indipendenti, non un documento ufficiale Google. Letto a novembre 2026: le regole possono cambiare, in caso di dubbio vale la pagina originale.

Testi: CC BY 4.0. Codice (`strumenti/`): MIT. Usali, modificali, regalali.

---

## English

A free **AI-agent skill** (Markdown, works with Claude Code, OpenCode and any agent that reads skills) containing the **entire official Google Search Central documentation** on crawling, indexing, search appearance, structured data, e-commerce, generative AI, spam policies and traffic drops — read in full and summarized **in Italian** — plus a dependency-free Python checker (`strumenti/controllo_seo.py https://yoursite.com`). Texts CC BY 4.0, code MIT. Not an official Google document.
