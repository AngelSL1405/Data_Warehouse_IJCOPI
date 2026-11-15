#!/usr/bin/env python3
"""Build offline visual source copies using already preserved public evidence.

No network access, new archive requests, data rewriting or page execution.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
from html import escape
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
STYLE = '''body{font:17px/1.55 system-ui,sans-serif;max-width:1100px;margin:32px auto;padding:20px;color:#172b3a}a{color:#075b9e;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccd4db;padding:10px;text-align:left;vertical-align:top}aside{background:#fff3cd;padding:16px;border-left:5px solid #9c7100}img{max-width:100%;height:auto;border:1px solid #ccd4db}dt{font-weight:bold}dd{margin-bottom:12px}code{overflow-wrap:anywhere}h1{line-height:1.2}small{color:#435565} @media(max-width:650px){table{font-size:14px}th,td{padding:5px}}'''


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save_json(path, data):
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def external(label, url):
    if not url or not url.startswith(('https://', 'http://')):
        raise ValueError('Invalid public URL')
    return '<a href="{}">{}</a>'.format(escape(url, quote=True), escape(label))


def local(label, path):
    target = (ROOT / path).resolve()
    if ROOT.resolve() not in target.parents or not target.is_file():
        raise ValueError('Missing local evidence: ' + path)
    return '<a href="../{}">{}</a>'.format(quote(path, safe='/._-'), escape(label))


def document(title, body):
    return ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; img-src &#39;self&#39; data:; style-src &#39;unsafe-inline&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;">'
            '<title>' + escape(title) + '</title><style>' + STYLE + '</style></head>'
            '<body>' + body + '</body></html>\n')


def build(root=ROOT):
    global ROOT
    ROOT = root
    out = ROOT / 'copias_locales'
    out.mkdir(exist_ok=True)
    catalogue = read(ROOT / 'catalogo.json')
    register = read(ROOT / 'consultas_fuentes_y_snapshots.json')
    evidence = read(ROOT / 'procedencia_web.json')['captures']
    sources = {s['id']: s for s in catalogue['sources']}
    records = []
    for row in register['rows']:
        ids = row['source_ids'].split(',')
        matches = [p for p in evidence if set(ids) <= set(p['source_ids']) and
                   p['capture_kind'] in ('live_publisher_page', 'rendered_preserved_pdf_first_page')]
        if not matches:
            raise ValueError('No primary public screenshot for source group ' + str(row['sequence']))
        capture = matches[0]
        image = ROOT / capture['screenshot']
        title = capture['title']
        filename = '{:02d}_{}.html'.format(row['sequence'], capture['id'])
        kind = 'local_visual_copy_from_preserved_screenshot'
        body = '<p><a href="index.html">← Índice de copias locales</a></p><h1>' + escape(title) + '</h1>'
        body += ('<aside>Copia visual local de la zona capturada de una fuente pública. '
                 'La imagen se conserva sin cambios; no representa toda la página desplazable '
                 'ni una aplicación interactiva completa. Los títulos y enlaces de esta ficha '
                 'proceden del registro de evidencias. No es una nueva captura de Wayback.</aside>')
        body += '<h2>Original, Wayback y copia local</h2><dl>'
        body += '<dt>Original</dt><dd>' + external(row['original_url'], row['original_url']) + '<br>Consulta registrada: ' + escape(row['original_consulted_at_mexico'] or 'No registrada') + '</dd>'
        body += '<dt>Wayback Machine</dt><dd>' + external('Abrir snapshot registrado', row['snapshot_url'])
        body += '<br>Captura: ' + escape(row['snapshot_captured_at_mexico'] or 'No registrada')
        body += '<br>Consulta: ' + escape(row['snapshot_consulted_at_mexico'] or 'No registrada')
        body += '<br>Estado: <code>' + escape(row['snapshot_status']) + '</code></dd>'
        if row.get('alternative_snapshot_url'):
            body += '<dt>Wayback documental alternativo</dt><dd>' + external('Abrir documentación alternativa', row['alternative_snapshot_url'])
            body += '<br>Consulta UTC: ' + escape(row.get('alternative_snapshot_consulted_at_utc') or 'No registrada') + '</dd>'
        body += '<dt>Copia visual local</dt><dd>Captura de la evidencia: ' + escape(capture['captured_at_utc']) + ' (UTC)'
        body += '<br>Tipo de evidencia: <code>' + escape(capture['capture_kind']) + '</code>'
        body += '<br>URL observada en la captura: ' + external(capture['final_url'], capture['final_url'])
        body += '<br>SHA-256 de la imagen: <code>' + digest(image) + '</code></dd></dl>'
        body += '<p>' + escape(capture.get('note', '')) + '</p>'
        body += '<h2>Imagen conservada</h2><a href="../' + quote(capture['screenshot'], safe='/._-') + '"><img src="../' + quote(capture['screenshot'], safe='/._-') + '" alt="Captura de la fuente: ' + escape(title, quote=True) + '"></a>'
        body += '<h2>Archivos originales conservados</h2><p>Los enlaces siguientes funcionan sin conexión. Si un archivo está dividido, concatenar sus partes en el orden del catálogo para recuperar sus bytes exactos.</p><ul>'
        for identifier in ids:
            source = sources[identifier]
            parts = [local('Parte ' + str(i + 1) if source['storage']['split'] else 'Archivo completo', part['path']) for i,part in enumerate(source['storage']['files'])]
            body += '<li><strong>' + escape(identifier + ': ' + source['name']) + '</strong><br>' + ' · '.join(parts)
            body += '<br>Editor: ' + escape(source['publisher']) + '<br>Licencia declarada: ' + escape(source.get('licence') or 'No especificada; no se infiere una licencia nueva.') + '</li>'
        body += '</ul>'
        supplemental = []
        if set(ids) & {'B3', 'B8', 'B11'}:
            supplemental.append(local('Texto local de la ficha del Marco', 'respaldos_inegi/marco_ficha_original.html'))
        if set(ids) & {'B5', 'B9d1', 'B9d2'}:
            supplemental.extend([local('Texto local de la documentación DENUE', 'respaldos_inegi/denue_documentacion_archivada.html'), local('Nota PDF de DENUE', 'respaldos_inegi/documentos/denue_nota_wayback_20260803.pdf')])
        if supplemental:
            body += '<h2>Copias documentales adicionales</h2><p>' + ' · '.join(supplemental) + '</p>'
        body += '<p><small>Fechas de consulta, captura y generación son distintas. Se conservan las fechas originales de las evidencias; generar esta ficha no implica consultar nuevamente la fuente. Créditos y licencias de los editores conservados. ' + local('Registro global', 'consultas_fuentes_y_snapshots.csv') + '.</small></p>'
        path = out / filename
        path.write_bytes(document(title, body).encode('utf-8'))
        records.append(dict(sequence=row['sequence'], source_ids=ids, path='copias_locales/' + filename,
                            copy_kind=kind, screenshot=capture['screenshot'], screenshot_sha256=digest(image),
                            evidence_captured_at_utc=capture['captured_at_utc'], original_url=row['original_url'],
                            original_consulted_at_utc=row['original_consulted_at_utc'], snapshot_url=row['snapshot_url'],
                            snapshot_captured_at_utc=row['snapshot_captured_at_utc'], snapshot_consulted_at_utc=row['snapshot_consulted_at_utc'],
                            snapshot_status=row['snapshot_status'], bytes=path.stat().st_size, sha256=digest(path)))
    unique = {identifier for r in records for identifier in r['source_ids']}
    if unique != set(sources):
        raise ValueError('Copy index does not cover exactly the corpus')
    body = '<h1>Copias locales de las fuentes del corpus</h1><p>' + str(len(records)) + ' páginas de procedencia para ' + str(len(unique)) + ' insumos. Original, Wayback y copia visual local con sus fechas. <a href="../INDICE.md">Índice general del corpus</a>.</p>'
    body += '<aside>Este archivo funciona sin conexión. Las copias visuales conservan las capturas existentes y enlazan los archivos originales completos. No son clones navegables de los sitios ni restauran mapas externos. Marco y DENUE conservan sus limitaciones documentadas. No se hicieron solicitudes nuevas a Wayback.</aside>'
    body += '<table><thead><tr><th>Fuente / insumos</th><th>Copia local y fecha de captura (UTC)</th><th>Original y consulta</th><th>Wayback y fecha de captura</th></tr></thead><tbody>'
    for r in records:
        row = next(x for x in register['rows'] if x['sequence'] == r['sequence'])
        body += '<tr><td>' + escape(', '.join(r['source_ids'])) + '</td><td><a href="' + quote(Path(r['path']).name) + '">Abrir copia local</a><br>' + escape(r['evidence_captured_at_utc']) + '</td>'
        body += '<td>' + external('Original', r['original_url']) + '<br>' + escape(row['original_consulted_at_mexico'] or 'Sin fecha') + '</td>'
        body += '<td>' + external('Wayback', r['snapshot_url']) + '<br>' + escape(row['snapshot_captured_at_mexico'] or 'Sin fecha') + '<br><code>' + escape(r['snapshot_status']) + '</code></td></tr>'
    body += '</tbody></table><p><a href="registro.json">Registro y hashes de las copias locales</a>. ' + local('Consultas originales y de snapshots con fechas completas', 'consultas_fuentes_y_snapshots.csv') + '.</p>'
    (out/'index.html').write_bytes(document('Copias locales de las fuentes del corpus', body).encode('utf-8'))
    manifest = dict(schema_version=1, generated_at_utc=datetime.now(timezone.utc).isoformat(),
                    generation_date_note='Build time of these local wrappers; source images retain their original capture dates.',
                    method='Offline visual copies from previously preserved public screenshots; no network access or new Wayback saves',
                    limitations='A screenshot preserves the visible captured area, not the complete scrolling page or interactive application. Exact corpus input bytes are linked separately.',
                    summary=dict(source_pages=len(records), logical_inputs=len(unique), missing_ids=sorted(set(sources)-unique)), copies=records)
    save_json(out/'registro.json', manifest)
    for row in register['rows']:
        entry = next(x for x in records if x['sequence'] == row['sequence'])
        row['local_copy_path'] = entry['path']
        row['local_copy_evidence_captured_at_utc'] = entry['evidence_captured_at_utc']
        row['local_copy_kind'] = entry['copy_kind']
    save_json(ROOT/'consultas_fuentes_y_snapshots.json', register)
    with (ROOT/'consultas_fuentes_y_snapshots.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(register['rows'][0]))
        writer.writeheader()
        writer.writerows(register['rows'])
    return manifest['summary']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(build(args.root)))
