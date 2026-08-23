#!/usr/bin/env python3
import hashlib, re, urllib.parse, urllib.request, zipfile
import stage6_manifest_stager as s


def fetch_one_percent_encoded(spec):
    fam, symbol, ym, key, role = spec
    checksum_key = key + '.CHECKSUM'
    safe = key.replace('/', '__')
    payload_path = s.STAGE / 'payloads' / safe
    checksum_path = s.STAGE / 'checksums' / (safe + '.CHECKSUM')

    # Preserve canonical object identity exactly. Percent-encoding is HTTP transport only.
    urls = (
        (s.CDN + urllib.parse.quote(checksum_key, safe='/'), checksum_path),
        (s.CDN + urllib.parse.quote(key, safe='/'), payload_path),
    )
    for url, dest in urls:
        req = urllib.request.Request(url, headers={'User-Agent':'0075-stage6-identity-stager/2'})
        with urllib.request.urlopen(req, timeout=45) as response:
            dest.write_bytes(response.read())

    checksum_text = checksum_path.read_text(errors='strict').strip()
    match = re.search(r'\b([0-9a-fA-F]{64})\b', checksum_text)
    if not match:
        raise RuntimeError(f'malformed checksum: {checksum_key}')
    official = match.group(1).lower()
    actual = hashlib.sha256(payload_path.read_bytes()).hexdigest()
    if official != actual:
        raise RuntimeError(f'sha256 mismatch: {key}')
    with zipfile.ZipFile(payload_path, 'r') as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f'zip CRC failure: {key}:{bad}')

    return {
        'canonical_object_id': f'BINANCE_VISION::{fam}::{symbol}::{ym}',
        'source_family': fam,
        'symbol': symbol,
        'month': ym,
        'archive_path': key,
        'paired_checksum_path': checksum_key,
        'paired_checksum_identity': checksum_text,
        'payload_sha256': actual,
        'frozen_object_role': role,
        'scientific_content_read_budget': 1,
        'staging_status': 'STAGED_HASH_VERIFIED_OFFLINE_READABLE',
        'staged_relative_path': str(payload_path),
        'staged_byte_size': payload_path.stat().st_size,
        'checksum_relative_path': str(checksum_path),
    }


if __name__ == '__main__':
    s.fetch_one = fetch_one_percent_encoded
    s.stage()
