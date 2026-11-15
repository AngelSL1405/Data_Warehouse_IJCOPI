#!/usr/bin/env python3
"""Check offline source-copy coverage, hashes, dates and local links without network access."""
import csv
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.local_paths = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'iframe', 'form', 'object', 'embed') or any(k.lower().startswith('on') for k in attrs):
            raise ValueError('Active content in offline visual copy')
        for key in ('href', 'src'):
            if key not in attrs:
                continue
            url = urlsplit(attrs[key])
            if url.scheme:
                if key != 'href' or url.scheme not in ('https', 'http'):
                    raise ValueError('Unexpected external resource or URL scheme')
            elif url.path:
                self.local_paths.append(unquote(url.path))


def verify():
    load = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
    manifest = load(ROOT/'copias_locales/registro.json')
    register = load(ROOT/'consultas_fuentes_y_snapshots.json')
    catalogue = load(ROOT/'catalogo.json')
    expected = {s['id'] for s in catalogue['sources']}
    actual = {i for r in manifest['copies'] for i in r['source_ids']}
    if expected != actual or len(manifest['copies']) != len(register['rows']):
        raise ValueError('Incomplete source-copy coverage')
    count = 0
    for copy in manifest['copies']:
        row = next(x for x in register['rows'] if x['sequence'] == copy['sequence'])
        if row['local_copy_path'] != copy['path'] or row['local_copy_evidence_captured_at_utc'] != copy['evidence_captured_at_utc']:
            raise ValueError('Local-copy date/path mismatch')
        for key in ('original_url', 'snapshot_url', 'snapshot_captured_at_utc', 'snapshot_consulted_at_utc'):
            if copy[key] != row[key]:
                raise ValueError('Original/archive metadata mismatch')
        for path_key, hash_key in [('path', 'sha256'), ('screenshot', 'screenshot_sha256')]:
            path = ROOT/copy[path_key]
            if hashlib.sha256(path.read_bytes()).hexdigest() != copy[hash_key]:
                raise ValueError('Stored copy/evidence hash mismatch')
    with (ROOT/'consultas_fuentes_y_snapshots.csv').open(encoding='utf-8', newline='') as f:
        csv_rows = list(csv.DictReader(f))
    if csv_rows != [{k:'' if v is None else str(v) for k,v in r.items()} for r in register['rows']]:
        raise ValueError('CSV/JSON projection mismatch')
    for path in (ROOT/'copias_locales').glob('*.html'):
        parser = Page()
        parser.feed(path.read_text(encoding='utf-8'))
        for link in parser.local_paths:
            target = (path.parent/link).resolve()
            if ROOT.resolve() not in target.parents or not target.is_file():
                raise ValueError('Missing/unsafe local reference: ' + str(target))
            count += 1
    return dict(source_pages=len(manifest['copies']), logical_inputs=len(actual),
                local_references_verified=count, offline_html_pages=len(list((ROOT/'copias_locales').glob('*.html'))),
                image_and_page_hashes_verified=2*len(manifest['copies']),
                active_content=False, remote_embedded_resources=False, network_requests=0)


if __name__ == '__main__':
    print(json.dumps(verify()))
