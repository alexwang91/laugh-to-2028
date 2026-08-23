#!/usr/bin/env python3
import argparse, concurrent.futures, hashlib, json, os, pathlib, re, sys
import urllib.parse, urllib.request, xml.etree.ElementTree as ET, zipfile

ROOT = pathlib.Path(__file__).resolve().parent
S3 = 'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision'
CDN = 'https://data.binance.vision/'
START, END = '2021-01', '2026-07'
ARTIFACT_NAME = '0075-stage6-authorized-payloads-v1'
STAGE = pathlib.Path('stage')
STABLE_FIAT = {
    'USDT','USDC','BUSD','TUSD','FDUSD','USDP','PAX','DAI','USDS','USDE','USD1',
    'EUR','AEUR','EURI','EURT','GBP','TRY','BRL','AUD','BIDR','IDRT','UAH','RUB',
    'NGN','ZAR','PLN','RON','ARS','JPY'
}
WRAPPED = {'WBTC','WETH','WBETH','WBNB','BETH','STETH','WSTETH'}
LEVERAGED_SUFFIXES = ('UP','DOWN','BULL','BEAR')
NS = {'s3':'http://s3.amazonaws.com/doc/2006-03-01/'}


def s3_page(prefix, delimiter=None, token=None):
    p = {'list-type':'2','prefix':prefix,'max-keys':'1000'}
    if delimiter: p['delimiter'] = delimiter
    if token: p['continuation-token'] = token
    url = S3 + '?' + urllib.parse.urlencode(p)
    with urllib.request.urlopen(url, timeout=30) as r:
        return ET.fromstring(r.read())


def list_common_prefixes(prefix):
    out, token = [], None
    while True:
        root = s3_page(prefix, '/', token)
        out.extend(x.text for x in root.findall('s3:CommonPrefixes/s3:Prefix', NS) if x.text)
        if root.findtext('s3:IsTruncated', 'false', NS).lower() != 'true': break
        token = root.findtext('s3:NextContinuationToken', None, NS)
        if not token: raise RuntimeError('truncated prefix listing without continuation token')
    return out


def list_keys(prefix):
    out, token = [], None
    while True:
        root = s3_page(prefix, None, token)
        out.extend(x.text for x in root.findall('s3:Contents/s3:Key', NS) if x.text)
        if root.findtext('s3:IsTruncated', 'false', NS).lower() != 'true': break
        token = root.findtext('s3:NextContinuationToken', None, NS)
        if not token: raise RuntimeError('truncated key listing without continuation token')
    return out


def identity_reason(symbol):
    base = symbol[:-4]
    if base in STABLE_FIAT: return 'STABLECOIN_OR_FIAT_PROXY_IDENTITY'
    if base in WRAPPED: return 'OBVIOUS_WRAPPED_DUPLICATE_IDENTITY'
    if base.endswith(LEVERAGED_SUFFIXES): return 'LEVERAGED_TOKEN_IDENTITY'
    if base.endswith('OLD'): return 'OBVIOUS_MIGRATION_OLD_IDENTITY'
    return None


def month_keys(prefix, rx):
    rows = []
    for key in list_keys(prefix):
        m = rx.match(key)
        if m and START <= m.group(1) <= END: rows.append((m.group(1), key))
    return rows


def enumerate_specs():
    base = 'data/spot/monthly/klines/'
    symbol_prefixes = list_common_prefixes(base)
    symbols = sorted(p[len(base):].strip('/') for p in symbol_prefixes if p.endswith('USDT/'))
    decisions, allowed = [], []
    for s in symbols:
        reason = identity_reason(s)
        decisions.append({'symbol':s,'base_asset':s[:-4],
            'decision':'EXCLUDED_BY_FROZEN_IDENTITY_RULE' if reason else 'AUTHORIZED_CANDIDATE_SYMBOL',
            'reason':reason})
        if not reason: allowed.append(s)
    if len(allowed) < 20: raise RuntimeError(f'candidate symbol universe unexpectedly small: {len(allowed)}')

    spot_rx = lambda s: re.compile(rf'^data/spot/monthly/klines/{re.escape(s)}/1d/{re.escape(s)}-1d-(\d{{4}}-\d{{2}})\.zip$')
    perp_rx = lambda s: re.compile(rf'^data/futures/um/monthly/klines/{re.escape(s)}/1d/{re.escape(s)}-1d-(\d{{4}}-\d{{2}})\.zip$')
    fund_rx = lambda s: re.compile(rf'^data/futures/um/monthly/fundingRate/{re.escape(s)}/{re.escape(s)}-fundingRate-(\d{{4}}-\d{{2}})\.zip$')

    def one_symbol(s):
        spot = month_keys(f'data/spot/monthly/klines/{s}/1d/', spot_rx(s))
        perp = dict(month_keys(f'data/futures/um/monthly/klines/{s}/1d/', perp_rx(s)))
        fund = dict(month_keys(f'data/futures/um/monthly/fundingRate/{s}/', fund_rx(s)))
        specs = [('SPOT_MONTHLY_1D_KLINE',s,ym,key,'SPOT_PRICE_VOLUME_UNIVERSE_INPUT') for ym,key in spot]
        spot_months = {ym for ym,_ in spot}
        for ym in sorted(spot_months):
            if ym in perp: specs.append(('USD_M_MONTHLY_1D_PERPETUAL_KLINE',s,ym,perp[ym],'OPTIONAL_MATCHED_PERPETUAL_FEATURE_INPUT'))
            if ym in fund: specs.append(('USD_M_MONTHLY_FUNDING_RATE',s,ym,fund[ym],'OPTIONAL_MATCHED_FUNDING_FEATURE_INPUT'))
        return s, spot, specs

    specs, first_last = [], {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as ex:
        for s, spot, sp in ex.map(one_symbol, allowed):
            specs.extend(sp)
            if spot: first_last[s] = (min(x[0] for x in spot), max(x[0] for x in spot), len({x[0] for x in spot}))
    for d in decisions:
        if d['symbol'] in first_last:
            a,b,n = first_last[d['symbol']
            ]; d.update(first_archive_month=a,last_archive_month=b,spot_month_count=n)
    ids = [(a,b,c,d) for a,b,c,d,_ in specs]
    if not specs or len(ids) != len(set(ids)): raise RuntimeError('empty or duplicate authorized object enumeration')
    return allowed, decisions, specs


def fetch_one(spec):
    fam,s,ym,key,role = spec
    chk_key = key + '.CHECKSUM'; safe = key.replace('/','__')
    zp = STAGE/'payloads'/safe; cp = STAGE/'checksums'/(safe+'.CHECKSUM')
    for url,dest in ((CDN+chk_key,cp),(CDN+key,zp)):
        req = urllib.request.Request(url, headers={'User-Agent':'0075-stage6-identity-stager/2'})
        with urllib.request.urlopen(req, timeout=45) as r: dest.write_bytes(r.read())
    txt = cp.read_text(errors='strict').strip(); m = re.search(r'\b([0-9a-fA-F]{64})\b', txt)
    if not m: raise RuntimeError(f'malformed checksum: {chk_key}')
    official = m.group(1).lower(); actual = hashlib.sha256(zp.read_bytes()).hexdigest()
    if official != actual: raise RuntimeError(f'sha256 mismatch: {key}')
    with zipfile.ZipFile(zp,'r') as z:
        bad = z.testzip()
        if bad is not None: raise RuntimeError(f'zip CRC failure: {key}:{bad}')
    return {'canonical_object_id':f'BINANCE_VISION::{fam}::{s}::{ym}','source_family':fam,
        'symbol':s,'month':ym,'archive_path':key,'paired_checksum_path':chk_key,
        'paired_checksum_identity':txt,'payload_sha256':actual,'frozen_object_role':role,
        'scientific_content_read_budget':1,'staging_status':'STAGED_HASH_VERIFIED_OFFLINE_READABLE',
        'staged_relative_path':str(zp),'staged_byte_size':zp.stat().st_size,'checksum_relative_path':str(cp)}


def stage():
    contract = json.loads((ROOT/'CONTROLLED_BOUNDARY_CONTRACT.json').read_text())
    assert contract['research_id'] == 'BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-0075'
    assert contract['controlled_attempt']['consumed'] == 0 and contract['controlled_scientific_history_reads'] == 0
    assert contract['scientific_engine_calls']['consumed'] == 0 and contract['scientific_source_network_fetches']['consumed'] == 0
    for p in ('AUTHORIZED_OBJECT_MANIFEST.json','STAGE6_STAGING_EVIDENCE.json','STAGE6_SYMBOL_UNIVERSE.json'):
        if (ROOT/p).exists(): raise RuntimeError(f'create-only output already exists: {p}')
    (STAGE/'payloads').mkdir(parents=True,exist_ok=True); (STAGE/'checksums').mkdir(parents=True,exist_ok=True)
    allowed, decisions, specs = enumerate_specs()
    universe = {'research_id':'BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-0075','stage':6,
        'status':'SYMBOL_UNIVERSE_IDENTITY_FREEZE_COMPLETE','official_host':'https://data.binance.vision',
        'candidate_month_start':START,'candidate_month_end':END,
        'selection_basis':'official S3 object-key identity only; no payload scientific values opened',
        'identity_exclusion_rules':{'stable_or_fiat_bases':sorted(STABLE_FIAT),'wrapped_bases':sorted(WRAPPED),
            'leveraged_suffixes':list(LEVERAGED_SUFFIXES),'migration_suffix':'OLD'},
        'candidate_symbols':allowed,'candidate_symbol_count':len(allowed),'decisions':decisions,
        'scientific_values_exposed':False,'controlled_scientific_history_reads':0,'scientific_engine_calls':0}
    (ROOT/'STAGE6_SYMBOL_UNIVERSE.json').write_text(json.dumps(universe,indent=2,sort_keys=True)+'\n')
    rows, failures = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as ex:
        futs = {ex.submit(fetch_one,x):x for x in specs}
        for fut in concurrent.futures.as_completed(futs):
            x=futs[fut]
            try: rows.append(fut.result())
            except Exception as e: failures.append({'source_family':x[0],'symbol':x[1],'month':x[2],'archive_path':x[3],'error':str(e)})
    rows.sort(key=lambda r:(r['source_family'],r['symbol'],r['month'],r['archive_path']))
    if failures or len(rows)!=len(specs):
        (STAGE/'FAILURES.json').write_text(json.dumps({'expected':len(specs),'captured':len(rows),'failures':failures},indent=2,sort_keys=True)+'\n')
        print(json.dumps({'expected':len(specs),'captured':len(rows),'failure_count':len(failures),'sample_failures':failures[:20]},indent=2)); sys.exit(2)
    if len({r['canonical_object_id'] for r in rows}) != len(rows): raise RuntimeError('duplicate canonical_object_id')
    manifest={'schema_version':1,'research_id':'BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-0075','stage':6,
        'status':'AUTHORIZED_OBJECT_MANIFEST_COMPLETE','official_host':'https://data.binance.vision',
        'candidate_month_start':START,'candidate_month_end':END,'candidate_symbol_count':len(allowed),
        'authorized_payload_objects':len(rows),'counts_by_family':{f:sum(r['source_family']==f for r in rows) for f in sorted({r['source_family'] for r in rows})},
        'failures':[],'scientific_values_exposed':False,'scientific_calculations_performed':False,
        'controlled_scientific_history_reads':0,'scientific_engine_calls':0,'stage8_scientific_source_network_fetches':0,
        'scientific_content_read_budget_each':1,'staging_artifact_name':ARTIFACT_NAME,'objects':rows}
    mp=ROOT/'AUTHORIZED_OBJECT_MANIFEST.json'; mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    (STAGE/'AUTHORIZED_OBJECT_MANIFEST.json').write_text(mp.read_text()); (STAGE/'STAGE6_SYMBOL_UNIVERSE.json').write_text((ROOT/'STAGE6_SYMBOL_UNIVERSE.json').read_text())
    print(json.dumps({'candidate_symbols':len(allowed),'authorized_objects':len(rows),'counts_by_family':manifest['counts_by_family'],'opaque_payload_bytes':sum(r['staged_byte_size'] for r in rows)},indent=2))


def finalize():
    mp=ROOT/'AUTHORIZED_OBJECT_MANIFEST.json'; up=ROOT/'STAGE6_SYMBOL_UNIVERSE.json'; cp=ROOT/'CONTROLLED_BOUNDARY_CONTRACT.json'
    m=json.loads(mp.read_text()); u=json.loads(up.read_text()); c=json.loads(cp.read_text()); n=m['authorized_payload_objects']
    ev={'schema_version':1,'research_id':'BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-0075','stage':6,
        'status':'STAGING_COMPLETE_ZERO_SCIENTIFIC_VALUE_EXPOSURE','artifact_name':ARTIFACT_NAME,
        'artifact_id':os.environ.get('ARTIFACT_ID',''),'artifact_url':os.environ.get('ARTIFACT_URL',''),'artifact_retention_days':90,
        'candidate_symbol_count':u['candidate_symbol_count'],'authorized_payload_objects':n,'hash_verified_objects':n,
        'offline_zip_readability_passed_objects':n,'manifest_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),
        'symbol_universe_sha256':hashlib.sha256(up.read_bytes()).hexdigest(),'controlled_scientific_history_reads':0,
        'scientific_engine_calls':0,'stage8_scientific_source_network_fetches':0,'attempt':'0/1','scientific_values_exposed':False,
        'note':'Stage6 enumerated official object-key identities, fetched paired checksum metadata and opaque authorized ZIP bytes, verified SHA-256 and ZIP structural readability, and never parsed or emitted historical scientific rows.'}
    (ROOT/'STAGE6_STAGING_EVIDENCE.json').write_text(json.dumps(ev,indent=2,sort_keys=True)+'\n')
    c['manifest_completion_rules']['manifest_not_yet_complete']=False; c['offline_staging_rules']['staging_evidence_not_yet_complete']=False
    c['stage6_evidence']={'authorized_object_manifest_sha256':ev['manifest_sha256'],'symbol_universe_sha256':ev['symbol_universe_sha256'],
        'artifact_id':ev['artifact_id'],'artifact_name':ARTIFACT_NAME,'authorized_payload_objects':n,'candidate_symbol_count':ev['candidate_symbol_count'],'scientific_values_exposed':False}
    cp.write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')


if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['stage','finalize']); a=ap.parse_args()
    stage() if a.command=='stage' else finalize()
