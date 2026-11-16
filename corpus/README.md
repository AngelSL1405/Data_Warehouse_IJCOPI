# Preserved input corpus

This directory preserves the exact input bytes used by this project. The catalogue
covers **65 logical files**: the 62 entries of the extension source manifest, the
two retained CSV inputs of the original study, and the retained ITER extract used
by the per-capita analysis. These are not 65 independent datasets or observations.
The ITER extract is an auxiliary derivative, not a third original-study source or
an additional entry in the 62-source manifest.

`catalogo.json` records each file's size, SHA-256, MD5 when available, publisher,
declared licence, DOI, provenance links and storage parts. `catalogo.csv` is an
exact tabular projection with one row per logical file. The byte-exact scientific
manifest is retained in `manifiestos/fuentes.json`; the source manifest and ETL are
not rewritten by this preservation tool. The catalogue's `summary.complete` and
`missing_ids` are the authority on whether all input bytes are present.

The [human-readable index](INDICE.md) links all 65 inputs, their original files or
ordered parts, download endpoints, publisher-page captures and available archive
pages. Its missing and pending states remain explicit. Rebuild it after updating
the catalogue or web-evidence metadata:

```text
python corpus/scripts/generar_indice.py
```

## Offline copies of source pages

Open [the offline source-copy index](copias_locales/index.html) to access the
original publisher page, its Wayback snapshot and our local visual copy, with
separate dates for original consultation, Wayback capture/consultation and local
image capture. Each local page links the exact preserved input files and retains
publisher attribution and recorded licence terms. No network access is needed to
view its image or open the preserved data files.

The 26 local pages reuse already preserved screenshots covering all 65 logical
inputs. These are **visual copies of the captured area**, not complete scrolling
pages, WARC archives or working clones of interactive applications. The Huerta
page links its complete local PDF as well as the first-page preview; Marco and
DENUE also link existing readable text/document backups. Their unresolved external
map/product-page limitations remain explicit. No new Wayback saves were made.

`copias_locales/registro.json` records the source and archive URLs, dates, copy
type and SHA-256 of each image/page. The global dated CSV/JSON register also links
each local copy. Rebuild these pages using only public preserved evidence:

```text
python corpus/scripts/generar_copias_locales.py
python corpus/scripts/generar_indice.py
python corpus/scripts/verificar_copias_locales.py
```

These copies belong to the Git repository and downloadable corpus. Like the rest
of `corpus/`, they remain excluded from the existing Pages deployment; this does
not alter any URL already cited in the paper. Publication in Git requires a
separately authorised commit/push.

## Verify without unpacking

Python 3.7 or later is sufficient; no external package, database, network request
or ETL execution is required. Run from the repository root:

```text
python corpus/scripts/preparar_corpus.py --verify
```

The verifier checks the manifest, both catalogues, every stored part and the
reconstructed SHA-256/MD5 of every logical file. Reconstruction is streamed into
the digest: it does **not** write a full ZIP or unpack its contents. It rejects
missing, additional or renamed data files under `originales/`, symlinks, unsafe
paths, altered part boundaries, wrong byte counts and wrong digests. Exit status
is `0` for a complete valid corpus, `2` for a valid but explicitly incomplete
corpus, and `1` for an error. Screenshot and archive metadata are separate evidence
and are not certified by this scientific-byte check.

## Storage and reconstruction

Each input has its own directory `originales/{id}/`. Files of at most
**20,000,000 bytes** are stored whole. Larger files are split into contiguous
20,000,000-byte parts named `.001`, `.002`, and so on; only the last part may be
shorter. Concatenating the catalogue's ordered parts reproduces the exact input
file. The existing D15 parts are reused with identical boundaries and hashes.
No compression, line-ending conversion, CSV rewriting or archive repacking is
performed. Thus every stored file remains well below GitHub's individual-file
size limit, while the original logical-file size and hash remain explicit.

To verify and restore the complete files into an **isolated staging directory**:

```text
python corpus/scripts/preparar_corpus.py --restore-to tmp/corpus_restaurado
```

This recreates the paths recorded by the existing ETL: retained original CSVs in
`warehouse/data/`, pinned snapshots in `warehouse_ampliado/snapshots/`, and other
extension inputs in `warehouse_ampliado/datos_crudos/{id}/`. It refuses restoration
to the current project or corpus directory and refuses to replace an existing file
with different bytes. Restoration does not execute or change the ETL. Keep the
staging directory outside a published checkout, or use an ignored local directory.

## Rebuild the preservation copy

Preparation is a local maintenance operation. It consumes a **private** inventory
containing already verified input paths. That inventory must not be published.
The preparer hashes those paths again before copying and fails before copying if
any expected input is absent. A public catalogue never includes those local paths.

```text
python corpus/scripts/preparar_corpus.py --inventory PRIVATE_INVENTORY.json --pages PRIVATE_PAGES.json
```

`--pages` is optional; it imports only public provenance URLs and their documented
or unverified status. `--allow-missing` permits a provisional partial copy, marks
the missing IDs explicitly and returns exit status `2`. Rerunning with a complete
inventory fills the gaps. Existing copies with the wrong bytes are rejected rather
than overwritten. The command does not download files or change the scientific
source manifest, original input files, or Git state. `--report PATH` writes a
machine-readable verification result to a chosen local path.

## Provenance, archives and attribution

Download URLs, publisher landing pages and DOI resolvers have separate fields.
An upstream download for the ITER ZIP describes the origin of the retained extract;
it is not asserted to be a direct download of the extract. The exact original
Open-Meteo request URL is not recorded, so it is not invented or regenerated.
An inferred landing page remains labelled unverified until separately checked.

`procedencia_web.json` links source IDs to publisher-page captures under
`capturas/`. `wayback.json` records the earlier public Availability API checks.
Both can be updated independently of the pinned scientific bytes. A live
page screenshot or an archive request is not proof of historical retrieval, and
a failed or pending archive request is not a successful capture.

The [browser-attempt history](wayback_intentos_browser.json) preserves the original
failed attempts and the subsequent serial Save Page Now outcomes. The
[new-capture report](wayback_capturas_nuevas.json) records 18 snapshots reported as
captured after 26 canonical source URLs were submitted one at a time on
13–14 November 2026. Eight pages returned HTTP 503 to Wayback: the two SACMEX
pages and six INEGI pages. The new snapshots cover the source pages associated
with 40 of the 65 logical inputs; this is not preservation of their download bytes.

Every submission selected **Save also in my web archive**, with outlink capture
and error-page capture disabled. Nevertheless, no new corpus link was visible
in the account's Web Archives at the final check on 14 November 2026, 16:13 UTC.
Wayback reported delayed registration. Account visibility remains unconfirmed;
17 exact November page replays were opened successfully. Capture, account visibility
and replay verification are independent observations. The [index](INDICE.md)
links the new snapshots alongside, without replacing, the earlier Availability
results. The [earlier retry list](wayback_pendientes.csv) remains a historical
Availability result, not the outcome of this serial batch.

The [dated consultation register (CSV)](consultas_fuentes_y_snapshots.csv) and
[JSON register](consultas_fuentes_y_snapshots.json) contain the original URL and
its actual consultation timestamp, the snapshot URL and capture timestamp, and
the snapshot consultation timestamp. Dates are recorded in UTC and
America/Mexico_City. Missing consultation dates remain empty; Availability API
checks do not count as opening a snapshot. Earlier observed source-page dates
are retained rather than represented as fresh visits.

The [read-only review of the eight older snapshots](wayback_verificacion_anteriores.json)
records six source pages with visible presentations: SACMEX consumption and
reports, CPV 2020, CE 2019, and CNGMD 2019/2021. The DENUE snapshot displays
controls but its map remains blank. The Marco Geoestadistico fiche redirects to
the generic publications catalogue, so the specific fiche is not confirmed.
The dated register retains the requested link and records the final served URL
separately. No pages were saved again for this review; linked data downloads and
interactive result tabs were not verified.

The [supplementary INEGI preservation package](respaldos_inegi/index.html) adds a
readable local snapshot of the live Marco Geoestadistico 2020 fiche, original
metadata extracted without alteration from the six pinned input ZIPs, and links
to their existing preserved parts. The six originals were rehashed successfully;
they were not replaced or duplicated. Both tested Wayback fiche captures still
redirect to the generic catalogue, so its external replay remains unresolved.

For DENUE, the package links a readable archived source-presentation page dated
21 October 2026 and preserves the publisher's four-page correction note together
with its byte-identical 3 August 2026 snapshot. The complete archived CDMX ZIP of
9 February 2026 was downloaded and CRC-checked: its own metadata identify the
05_2025 edition, whereas the pinned study ZIP is 05_2026. The historical ZIP is
therefore kept in a separately labelled directory, split into contiguous parts
of at most 20,000,000 bytes, and must not replace the study input. These documentary
backups do not restore the DENUE interactive map. See the [supplementary record](respaldos_inegi/registro.json)
for original/archive URLs, actual consultation dates, hashes, roles and limitations.

The subsequent retry of the eight missing pages again returned HTTP 503 for all
eight; its dated outcomes are appended to the browser-attempt history. The
[Huerta PDF verification](verificacion_huerta.json) confirms that the existing
21 February 2026 snapshot contains the complete 38-page article. Its 5,132,456
bytes and SHA-256 match both the pinned corpus input and the publisher PDF
consulted on 14 November 2026. The blank browser viewer was not evidence of a
missing PDF. The November URL redirects to this older capture; the February
verification does not establish an exact November replay. No new capture of
the Huerta article was requested during this verification.

Wayback checks and retry lists are restricted to the source URLs associated with
the 65 corpus input IDs. Bibliography-only URLs and visual-attribution pages are
outside this archive scope. `bibliografia.json` is a separate reference inventory;
it does not request or imply Wayback preservation of the bibliography.

`manifiestos/capturas_sha256.json` records the size, dimensions and SHA-256 of
the 29 evidence images. These checks protect image bytes; they do not certify
the truth of a publisher page or replace a confirmed archive snapshot.

Retain the publishers' licences and attribution conditions recorded in each
catalogue entry and in the source manifest. The repository's software licence does
not replace data licences. An unspecified original-input licence stays unspecified;
no new licence is inferred from a footer or another dataset. The Huerta-Vergara
article retains its stated CC BY-NC-SA terms, and the InSAR data retain their stated
CC0 terms. Publisher and academic author credits must accompany redistribution.

This corpus is a source-preservation package, not part of the interactive Pages
application. Publishing the website should exclude it from the Pages deployment
bundle; source-repository access and website deployment are separate concerns.

The [additional historical INEGI review](wayback_revision_historica_inegi.json)
records four older captures checked sequentially on 14 November 2026, with pauses
and no new saves: Marco (4 February 2021 and 5 July 2023) shows empty product
fields; DENUE (24 May 2025) shows a blank map, and DENUE (14 November 2018)
loads its historical presentation but reports unavailable map imagery. No functional
replacement of the product fiche or interactive map was found in these four checks.
All local scientific inputs and earlier successful documentary backups are retained.

A further read-only retry on 15 November 2026 checked two additional replays:
Marco selected 6 April 2024 redirects to the 7 April generic catalogue, and a UPC
search does not recover its specific fiche. DENUE selected 21 June 2022 serves
11 June 2022, whose map remains blank after 30 seconds. The historical INEGI
report now records six selected replays, with no functional replacement found
and no new Save Page Now requests. Originals and existing backups are unchanged.

Another sequential read-only review on 15 November 2026 checked Marco dated
8 May 2025, which redirects to a generic catalogue dated 24 May, and DENUE
dated 17 March 2020. The latter presents readable historical introductory text,
but its map remains blank after closing the presentation and waiting again.
The report now records eight selected older replays; no functional replacement
was found, no new pages were saved, and scientific inputs were not changed.
