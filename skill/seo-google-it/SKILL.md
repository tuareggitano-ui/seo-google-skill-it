---
name: seo-google-it
description: Le regole ufficiali di Google Search Central (scansione e indicizzazione, aspetto nei risultati, dati strutturati, e-commerce, IA generativa, spam, cali di traffico) riassunte in italiano per agenti AI e per chi gestisce un sito o un e-commerce. Usare prima di pubblicare o togliere pagine e prodotti, cambiare URL, robots.txt, sitemap, canonical, noindex, redirect, codici HTTP, dati strutturati, e quando Search Console segnala pagine non indicizzate o un calo di traffico.
---

# SEO secondo Google, in italiano (skill per agenti AI)

Riassunto in italiano della documentazione ufficiale Google Search Central (letta per intero a novembre 2026).
Regole complete con numeri e sintassi: `references/regole-google.md`. Qui: le regole d'oro e le liste di controllo.

## Le 20 regole d'oro
1. **Crawl e indicizzazione sono cose diverse.** robots.txt impedisce la scansione, NON l'indicizzazione: una pagina bloccata può comparire senza descrizione. Per tenerla fuori usare `noindex`, e la pagina NON deve essere bloccata in robots.txt, altrimenti Google non legge il noindex.
2. **I link sono il modo principale di scoperta.** Solo `<a href="...">` vero nell'HTML. Niente `onclick`, `<span href>`, `href="javascript:"` o link `#/`. Ogni pagina importante ha almeno un link interno. La sitemap aiuta ma è solo un suggerimento.
3. **Un contenuto = un URL.** Duplicati: 301 (forte) + `rel="canonical"` assoluto e self-referencing nell'`<head>` + solo URL canonici in sitemap. Mai segnali in contrasto. Mai noindex o robots.txt per scegliere il canonico.
4. **Codici HTTP giusti.** 200 pagina valida. **404/410** prodotto tolto per sempre (410 = tolto apposta). **301/308** spostato per sempre, 302/307 temporaneo. **503** per poche ore o giorni (max ~2 giorni, poi gli URL escono). Mai 200 su una pagina di errore o vuota: è un soft 404. Mai 401/403 per rallentare Google. Redirect: al massimo 10 salti, meglio diretto (max 3).
5. **Non mandare molte pagine vecchie alla home**: Google lo tratta come soft 404. Redirect solo verso la pagina equivalente.
6. **Prodotto esaurito: la pagina resta** (200, `availability: OutOfStock` nei dati strutturati e nel feed). Mai Removals tool per gli esauriti.
7. **Sito in pausa: resta online e limita le funzioni** (carrello spento, banner con `data-nosnippet`, dati strutturati aggiornati). Mai 403/404/410/noindex o blocco robots su un sito chiuso temporaneamente, mai 503 sul robots.txt.
8. **robots.txt**: nella root, UTF-8, max **500 KiB**, cache 24 h. Solo `user-agent`, `allow`, `disallow`, `sitemap` (`crawl-delay` ignorato). Vince la regola più lunga; a parità vince `allow`. `User-agent: *` non vale per AdsBot. Non bloccare CSS/JS/immagini che servono a capire la pagina. Se il robots.txt risponde 5xx per oltre 12 ore Google smette di scansionare.
9. **Sitemap**: URL assoluti, UTF-8, max **50.000 URL o 50 MB** per file, `<lastmod>` vero (Google ignora `priority` e `changefreq`), dichiarata in robots.txt (`Sitemap: https://...`). Solo URL canonici che vogliamo nei risultati.
10. **Googlebot legge i primi 2 MB** di ogni HTML, CSS e JS (non compressi) e 64 MB dei PDF; il resto lo ignora. Indicizza la versione **mobile**: stessi contenuti, titoli, dati strutturati e meta della versione desktop.
11. **JavaScript**: titolo, canonical, noindex e contenuto principale devono stare nell'HTML del server, non aggiunti dopo dal JS. Solo le pagine 200 vengono renderizzate. Googlebot non ha cookie né localStorage tra una pagina e l'altra.
12. **`<head>` valido**: solo title, meta, link, script, style, base, noscript, template. Un `<img>` o un `<iframe>` nell'head lo chiude e Google ignora tutto quello che viene dopo (canonical, robots).
13. **Titoli e descrizioni unici per pagina**, chiari e veri. Meta keywords, `rel=next/prev` e l'attributo `lang` sono ignorati. Non esiste un numero minimo di parole. I duplicati non danno penalità, ma copiare contenuti altrui sì. E-E-A-T non è un fattore di ranking.
14. **URL**: parole descrittive in italiano, trattini e non underscore, minuscolo (sono case-sensitive), niente ID di sessione né parametri inutili. I filtri non indicizzabili vanno bloccati in robots.txt; una combinazione senza risultati dà 404.
15. **Tempi**: pagine nuove indicizzate in giorni (3+), effetti valutabili in settimane. La richiesta "Richiedi indicizzazione" ha una quota: solo per le pagine importanti, e ripeterla non accelera.

16. **Dati strutturati**: pagina dove si compra = merchant listing (Product name, image, offers con price > 0 e priceCurrency EUR; consigliati gtin13, brand, availability, shippingDetails, hasMerchantReturnPolicy). JSON-LD nell'HTML iniziale. Prezzo barrato con StrikethroughPrice. Profumi: prezzo ogni 100 ml con UnitPriceSpecification. **FAQPage non dà più rich result** (dal 7/05/2026).
17. **Organization in home come OnlineStore** con logo, contatti, vatID, politica resi e spedizione; **WebSite** solo in home con name e alternateName.
18. **Merchant Center e IA**: immagini generate con IA vanno marcate (IPTC TrainedAlgorithmicMedia); titoli e descrizioni generati con IA vanno indicati come tali. Contenuti IA solo se verificati a mano.
19. **AI Overviews/AI Mode**: nessun trucco speciale, basta essere indicizzati e utili. Google-Extended consentito = idonei al grounding Gemini.
20. **Cali di traffico**: prima Search Console (anomalie, Prestazioni 16 mesi, Indicizzazione, Azioni manuali), mai modifiche radicali per un calo piccolo.

## Liste di controllo

### Pubblicare prodotti o pagine
- [ ] Pagina 200, URL descrittivo, canonical assoluto su se stessa, un solo H1, title e meta description unici.
- [ ] Linkata con `<a href>` vero da almeno una pagina (categoria, indice, home). La sitemap non basta.
- [ ] Nessun doppione dello stesso prodotto con URL o codice diverso (altrimenti 301 verso quello tenuto).
- [ ] Immagini con alt descrittivo, vicine al testo, URL stabili, formato WebP/JPEG/PNG/AVIF.
- [ ] Dati strutturati Product (merchant listing) con prezzo e disponibilità veri, nell'HTML iniziale.
- [ ] Sitemap e feed Merchant Center aggiornati.

### Togliere prodotti
- Tolto per sempre: 410 (o 404), oppure 301 verso il prodotto equivalente. **Mai verso la home.**
- Esaurito: la pagina resta (200) con disponibilità OutOfStock. Mai lo strumento Rimozioni.
- Toglierlo da sitemap e feed.

### Cambiare URL
- 301 diretto vecchio → nuovo, niente catene, mantenuto almeno 1 anno. Aggiornare link interni, canonical, sitemap.

### robots.txt e noindex
- Per non far scansionare: `disallow`. Per non indicizzare: `noindex` su pagina scansionabile. Non entrambi sulla stessa pagina.
- Non bloccare CSS, JS e immagini che servono a capire la pagina.

### Mettere in pausa o chiudere un sito
- Pausa: sito online, carrello spento, banner con `data-nosnippet`; 503 + Retry-After solo per 1-2 giorni; mai 503 sul robots.txt.
- Trasloco: 301 pagina per pagina, Change of Address in Search Console se cambia dominio.

### Search Console segnala problemi
- Soft 404: dare il codice giusto o contenuto vero.
- Scansionata/Rilevata ma non indicizzata: qualità o link interni deboli.
- Canonico diverso scelto da Google: allineare canonical, link interni e sitemap.
- Bloccata da robots.txt ma indicizzata: togliere il blocco e usare noindex.
- Calo di traffico: anomalie dei dati → Prestazioni ultimi 16 mesi → Indicizzazione → Azioni manuali; niente modifiche radicali per un calo piccolo.

## Strumento
`strumenti/controllo_seo.py https://tuosito.it` controlla in un minuto i punti verificabili da codice (vedi README).
