# Regole complete Google Search Central (crawling e indicizzazione), lette il 16/11/2026

Parafrasi in italiano delle 42 pagine; sintassi e numeri riportati esattamente.

## Codici HTTP (http-network-errors, troubleshoot-crawling-errors)
- 2xx: contenuto considerato per l'indice. 204: nessun contenuto.
- 301/308 permanenti (segnale forte, Google mostra la destinazione). 302/303/307 temporanei (segnale debole, Google mostra la sorgente). 304 = non modificato (senza body). Googlebot segue max 10 redirect; consigliato diretto o max 3, comunque meno di 5.
- 4xx (tranne 429): URL trattato come inesistente; se era indicizzato esce. 401/403 NON rallentano il crawl.
- 429 e 5xx: crawl rallentato; URL tenuti per circa 2 giorni, poi rimossi se persiste.
- Soft 404: pagina di errore o vuota con 200 (ricerca vuota, errore DB, JS mancante) → esclusa. Fix: 404/410 o 301 a equivalente. Pagina 404 personalizzata con stesso layout e link a home e pagine popolari.
- Redirect: server-side > meta refresh 0 s > JavaScript > link "ci siamo spostati". meta refresh > 0 s = temporaneo.
- NGINX: `return 301 https://example.com/nuovo;` (302 temporaneo).

## Crawler (overview-google-crawlers, googlebot)
- Limite file: 15 MB in generale; Googlebot legge i primi 2 MB di ogni HTML/CSS/JS (non compressi) e 64 MB di PDF.
- HTTP/1.1 e HTTP/2; compressione gzip, deflate, br.
- Cache supportata: ETag/If-None-Match, Last-Modified/If-Modified-Since, Cache-Control max-age. Consigliati sia ETag sia Last-Modified.
- Googlebot Smartphone e Desktop hanno lo stesso token in robots.txt (non si bloccano separatamente). Scansiona di solito dagli USA (fuso Pacifico): mai bloccare gli USA.
- Verificare un "Googlebot" con reverse DNS e la lista IP prima di bloccarlo.
- Google-Read-Aloud non è un crawler; opt-out `<meta name="google" content="nopagereadaloud">`.

## robots.txt (intro, create, submit, robots_txt RFC 9309)
- Nome `robots.txt`, nella root dell'host, UTF-8, editor di testo semplice. Vale solo per quel protocollo+host+porta (un sottodominio ha il suo).
- Max 500 KiB (il resto ignorato). Cache fino a 24 h ("Request a recrawl" nel rapporto robots.txt di Search Console).
- Campi: user-agent, allow, disallow, sitemap. crawl-delay NON supportato. Path case-sensitive, inizia con /. `*` = qualsiasi sequenza, `$` = fine URL. `/*.php$` non copre URL con parametri.
- Precedenza: regola più lunga; a parità `allow`. Il gruppo più specifico per user-agent vince; gruppi dello stesso UA si uniscono, `*` non si unisce agli specifici. Una riga sitemap NON separa i gruppi.
- `User-agent: *` non vale per AdsBot (vanno nominati).
- Status: 2xx usato; 3xx max 5 redirect poi come 404; 4xx (tranne 429) = nessuna restrizione; 5xx = blocco totale per le prime 12 h, poi ultima versione valida per 30 giorni.
- Non serve a nascondere pagine (usare noindex o password); non bloccare CSS/JS necessari; risorse bloccate possono far vedere la pagina come soft 404.
- Usi giusti: carrelli, pagine azione ("buy now"), faccette, session ID, spazi infiniti, ricerca interna, ordinamenti.

## noindex e meta robots (robots-meta-tag, block-indexing, special-tags, valid-page-metadata)
- `<meta name="robots" content="noindex">` oppure header `X-Robots-Tag: noindex` (anche per PDF e immagini). Solo Google: `name="googlebot"`.
- La pagina deve essere crawlabile (non in disallow), altrimenti il noindex non si legge. noindex in robots.txt NON supportato.
- Regole: all, noindex, nofollow, none (= noindex,nofollow), nosnippet (anche per AI Overviews/AI Mode), indexifembedded, max-snippet:N (0 = nosnippet, -1 = libero), max-image-preview:none|standard|large, max-video-preview:N, notranslate, noimageindex, unavailable_after:[data ISO 8601]. Obsoleti: noarchive, nocache, nositelinkssearchbox.
- In conflitto vince la più restrittiva. Non aggiungere o togliere noindex via JS.
- `data-nosnippet` solo su span, div, section, con tag chiusi.
- Ignorati: meta keywords, attributo lang, rel=next/prev.
- `<head>` valido solo con: title, meta, link, script, style, base, noscript, template. Un img o iframe nell'head lo chiude: tutto il resto è ignorato.
- `<meta charset="utf-8">`, `<meta name="viewport">` = mobile-friendly. meta refresh sconsigliato (usare 301).
- Rimozione dopo noindex: serve un recrawl, anche mesi per pagine poco importanti; per urgenza usare Removals tool (circa 6 mesi, rimozione in meno di un giorno; coprire tutte le varianti dell'URL).

## Canonical e duplicati (consolidate-duplicate-urls, canonicalization, troubleshooting)
- Forza: redirect 301 (forte) = rel=canonical (forte) > sitemap (debole). Si sommano.
- `<link rel="canonical" href="https://...">` assoluto nell'`<head>`, self-referencing anche sulla canonica. Per PDF: header `Link: <url>; rel="canonical"`. Un solo canonical per pagina (non HTML + header diversi).
- Link interni sempre all'URL canonico; in sitemap solo canonici.
- Mai: robots.txt, Removals tool, noindex o frammento # per canonicalizzare; mai canonical in contrasto con sitemap; canonical con hreflang/lang/media/type viene ignorato.
- HTTPS preferito: redirect http→https, canonical https, certificato valido per tutti gli host, niente http in sitemap.
- Parametri di tracciamento (gclid, utm): canonical all'URL pulito.
- Controllo: Ispezione URL in Search Console mostra il canonico scelto da Google; un cluster si riconsidera in circa 2 settimane.

## URL e faccette (url-structure, faceted-navigation, crawl-budget)
- URL descrittivi, nella lingua del pubblico, trattini, minuscolo, parametri `?a=b&c=d` (più valori con virgola: color=rosso,blu). Niente #/ per il contenuto (usare History API), niente session ID, link root-relative.
- Filtri non da indicizzare: robots.txt `disallow: /*?*color=` ecc., lasciando crawlabili prodotti e lista senza filtri. Filtri indicizzabili: ordine fisso, niente duplicati, 404 per combinazioni vuote, canonical alla versione non filtrata. nofollow sui link ai filtri vale solo se è su TUTTI.
- Crawl budget conta solo per siti enormi (1M+ pagine o 10.000+ che cambiano ogni giorno). Noi: sitemap aggiornata, 404/410 per i tolti, niente soft 404, niente catene di redirect, 304 supportato. noindex e robots.txt non spostano il budget.

## Sitemap (overview, build, image, video, news)
- Sito piccolo (fino a circa 500 pagine) e ben linkato: sitemap non obbligatoria ma utile; noi la abbiamo.
- Max 50.000 URL o 50 MB non compressi per file; oltre: sitemap index. UTF-8, URL assoluti, valori XML escapati, `<lastmod>` vero (cambio significativo), priority e changefreq ignorati.
- Nella root vale per tutto il sito. Dichiarata in robots.txt con `Sitemap: https://...` (più righe ok).
- Non inviare la stessa sitemap più volte al giorno; è un suggerimento.
- Immagini: `xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"`, `<image:image><image:loc>`, max 1.000 immagini per URL; deprecati caption, geo_location, title, license.
- Video: `xmlns:video=...sitemap-video/1.1`, obbligatori thumbnail_loc, title, description (max 2048), content_loc o player_loc; duration 1-28800 s; max 32 tag. Solo video del contenuto principale.
- News: solo articoli degli ultimi 2 giorni, max 1.000 news:news (non ci serve per i cataloghi).

## JavaScript (javascript-seo-basics, fix-search-javascript)
- Meglio server-side rendering o pre-rendering. Solo pagine 200 vengono renderizzate.
- Title, canonical, noindex nell'HTML originale; non cambiarli via JS. Contenuto nel DOM renderizzato (web component con `<slot>`).
- Niente viste con # (schema AJAX deprecato dal 2015). Niente dipendenza da localStorage, sessionStorage, cookie, permessi utente, WebGL, WebSocket senza fallback HTTP.
- SPA: errore → redirect a URL che risponde 404 o noindex via JS (non 200).
- Nomi file con impronta per la cache (main.2bb85551.js): WRS può usare JS/CSS vecchi.
- Controllo: Rich Results Test e Ispezione URL (HTML renderizzato, console).

## Link (links-crawlable, qualify-outbound-links)
- Crawlabili: `<a href="...">` (anche con onclick o inseriti da JS con lo stesso markup). Non crawlabili: span href, a senza href, routerLink, href="javascript:".
- Anchor descrittivo e conciso; niente "clicca qui"; niente keyword stuffing. Link immagine: conta l'alt.
- Ogni pagina importante con almeno un link interno.
- rel="sponsored" (pagati), "ugc" (utenti), "nofollow" (non fidati); per non far scansionare link interni usare robots.txt, non nofollow.

## Mobile e AMP
- Mobile-first: stessi contenuti principali, title, description, heading, dati strutturati (Breadcrumb, Product, VideoObject), meta robots, immagini (stessi URL e alt) su mobile e desktop. Niente contenuto principale che compare solo dopo un'interazione.
- AMP non obbligatorio.

## Immagini e informazioni da non mostrare
- Bloccare immagini: robots.txt `User-agent: Googlebot-Image / Disallow: /percorso` oppure `X-Robots-Tag: noindex` sull'immagine (non entrambi). noimageindex vale solo per quella pagina.
- Formati indicizzabili: BMP, GIF, JPEG, PNG, WebP, SVG, AVIF. Il Content-Type HTTP deve essere giusto.
- Redazione: ritagliare davvero, togliere metadati, esportare PNG/WebP piatti, mai testo coperto o dello stesso colore dello sfondo.

## Traslochi, test, pause
- Trasloco con cambio URL: un cambiamento alla volta, mappa vecchio→nuovo completa, 301 server-side 1:1, canonical self-referencing, sitemap nuova, Change of Address in Search Console se cambia dominio, redirect almeno 1 anno, aggiornare link e profili.
- Test A/B: 302 verso la variante, canonical all'originale, niente cloaking, chiudere presto.
- Pausa: sito online con funzioni limitate; 503 + Retry-After solo per 1-2 giorni; mai 503 sul robots.txt; mai 403/404/410/noindex o blocco robots; mai Removals tool per una chiusura; prodotti esauriti restano online.
- SafeSearch: contenuti per adulti marcati `<meta name="rating" content="adult">` (per noi non rilevante).

# Parte 2 (16/11/2026 sera): aspetto nei risultati, dati strutturati, e-commerce, IA, spam, cali di traffico

## Titoli (title-link) e snippet
- Ogni pagina con `<title>` unico, descrittivo, conciso; nome sito all'inizio o alla fine con un separatore (– : |). Coerente con il primo `<h1>` visibile.
- Google prende il titolo da: title, h1, og:title, testo in evidenza, anchor dei link, WebSite. Lo sostituisce se è generico, ripetuto su molte pagine, pieno di parole chiave, solo "| Nome sito" o con date vecchie.
- Nessun limite ufficiale di caratteri: troncamento in base alla larghezza dello schermo.
- Meta description: unica per pagina; per i prodotti dati chiave chiari (prezzo, formato, materiale, marca); generazione automatica ammessa se leggibile e variata; mai liste di parole chiave o testi brevissimi. Google la usa solo se descrive meglio del testo.
- Controlli: nosnippet, max-snippet:N, data-nosnippet. "Leggi di più" funziona solo con contenuto visibile (non in tab chiuse).

## Immagini, video, favicon, nome del sito
- Immagini: `<img src>` con alt descrittivo (no CSS background, no alt riempiti di parole chiave), nome file descrittivo con trattini, vicino al testo, stesso URL ovunque, `srcset`/`<picture>` sempre con `<img src>`. Immagine preferita: og:image o primaryImageOfPage; in Product la proprietà image è obbligatoria.
- Video: `<video>`, `<iframe>`, `<embed>` o `<object>` nell'HTML renderizzato; miniatura a URL stabile (min 60×30 px); VideoObject con name, description, thumbnailUrl, contentUrl o embedUrl; niente caricamento solo dopo un clic.
- Favicon: `<link rel="icon">` in home, quadrata, minimo 8×8 (meglio oltre 48×48), formati BMP GIF ICO PNG JPEG (SVG non in lista), URL stabile, non bloccata.
- Nome sito: dati WebSite SOLO in home con `name`, `url` e `alternateName` (es. dominio), coerenti con og:site_name e titolo della home. Un nome per dominio o sottodominio, non per sottocartelle.

## Dati strutturati (policy, Product/merchant listing, Breadcrumb, Organization, Review, FAQ)
- JSON-LD nell'HTML iniziale (quello generato via JS rende meno affidabili i controlli Shopping). Solo su contenuto visibile; mai pagine create solo per il markup.
- Pagina dove si compra = **merchant listing**: Product richiede `name`, `image`, `offers`; Offer richiede `price` (> 0, punto decimale, senza simbolo) e `priceCurrency` (EUR). Consigliati: brand.name, gtin13, sku, description, color, material, size, availability (`https://schema.org/InStock`), itemCondition, url, shippingDetails, hasMerchantReturnPolicy, priceValidUntil (mai nel passato).
- Prezzo barrato: priceSpecification con `priceType: https://schema.org/StrikethroughPrice` (mai priceType sul prezzo attuale; non usare price e priceSpecification insieme per lo stesso prezzo).
- **Prezzo unitario (profumi, UE):** UnitPriceSpecification con referenceQuantity (es. value 100 unitCode ML per mostrare il prezzo ogni 100 ml).
- Spedizione: OfferShippingDetails con shippingRate (valuta = quella dell'offerta), shippingDestination (DefinedRegion addressCountry "IT"), deliveryTime (handlingTime e transitTime, minValue e maxValue interi, unitCode DAY).
- Resi: MerchantReturnPolicy (applicableCountry, returnPolicyCategory, merchantReturnDays, returnFees). Meglio a livello Organization, override sul prodotto solo per eccezioni.
- Varianti: un URL e una Offer per variante (ProductGroup + isVariantOf), mai AggregateOffer per le varianti; niente markup prodotto sulle pagine categoria.
- Organization: in home o "chi siamo", tipo **OnlineStore**: name, url, logo (min 112×112), sameAs (social), address, contactPoint, email, telephone (+39), vatID (segnale di fiducia), hasMerchantReturnPolicy, hasShippingService.
- BreadcrumbList: almeno 2 ListItem, position da 1, item con URL assoluto (ultimo facoltativo), breadcrumb visibile.
- Recensioni: solo reali e visibili, autore persona reale (mai nomi promozionali), punto decimale, aggregateRating con ratingCount o reviewCount; vietate recensioni false o incentivate non dichiarate; niente stelle auto-raccolte su Organization/OnlineStore.
- **FAQPage: rich result dismesso** (non compare dal 7/05/2026): non investirci.
- Violazioni = azione manuale: si perdono i rich result (non il ranking). Controllo: Rich Results Test, rapporto Merchant listings, Ispezione URL.

## E-commerce (sezione specialty/ecommerce)
- Dati prodotto su Google: markup Product su ogni pagina + feed Merchant Center (obbligatorio per la scheda Shopping); attivare l'aggiornamento automatico dal sito per allineare prezzo e stock.
- Struttura: menu → categoria → prodotto con `<a href>`; prodotti importanti linkati dalla home; Google capisce la struttura dai link, non dall'URL; la ricerca interna non basta (Googlebot non compila form).
- URL: parole descrittive, `?chiave=valore`, un valore per parametro separato da virgola, URL stabili; varianti con URL propri, mai `#`; categoria vuota → noindex o 404.
- Paginazione: `?page=n` con `<a href>` alla pagina successiva e alla prima, canonical di ogni pagina su se stessa (non sulla prima); niente rel next/prev; filtri e ordinamenti fuori dall'indice.
- Lancio: non spegnere il carrello per bloccare gli acquisti (Google lo usa per verificare prezzo, tasse e spedizione).
- Internazionale: URL distinti per lingua (es. /en/), mai redirect automatici per IP o lingua (Googlebot viene dagli USA senza Accept-Language), hreflang bidirezionale con x-default, codici it-IT/en (GB non UK).

## IA generativa, contenuti utili, spam
- AI Overviews e AI Mode: nessun markup speciale né file "IA"; basta essere indicizzati e idonei allo snippet. Contenuto importante in testo, dati strutturati coerenti, Merchant Center aggiornato. Traffico IA nel rapporto Prestazioni (tipo "Web"). Google-Extended controlla addestramento e grounding Gemini: noi lo consentiamo.
- Contenuti utili: originali, con valore oltre le fonti, scritti per chi arriva sul sito; descrizioni prodotto generiche o generate in massa = poco sforzo; non cambiare le date per sembrare freschi; nessun numero di parole preferito.
- Contenuti IA: ammessi se utili e verificati a mano (anche title, description, alt, dati strutturati). Pagine in massa senza valore = scaled content abuse. **Merchant Center: immagini generate con IA con metadato IPTC DigitalSourceType = TrainedAlgorithmicMedia; titoli e descrizioni generati con IA vanno indicati separatamente come tali.**
- Spam: niente cloaking, doorway (pagine per città uguali), testo nascosto, keyword stuffing, link comprati o scambiati, scraping o feed altrui senza valore, redirect ingannevoli. Link a pagamento con rel="sponsored".

## Cali di traffico e misurazione
- Prima controllare le anomalie dei dati in Search Console, poi Prestazioni (ultimi 16 mesi, confronto con il periodo precedente o l'anno prima) per query, pagine, paese, dispositivo.
- Impressioni stabili e clic in calo = migliorare titoli e snippet. Calo piccolo (es. posizione 2 → 4): non toccare niente. Calo grande: autovalutazione di tutto il sito, attendere settimane.
- Tecnico: rapporti Statistiche di scansione, Indicizzazione pagine, Problemi di sicurezza, Azioni manuali. Stagionalità: Google Trends.
- Search Console (clic) e Analytics (sessioni) non coincidono: consenso cookie, fuso orario (Search Console usa l'ora del Pacifico), canonical, bot. Il Referer di Google contiene solo il dominio, mai la query.
