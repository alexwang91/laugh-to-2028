from __future__ import annotations
import argparse,csv,hashlib,io,json,os,subprocess,urllib.error,urllib.request,zipfile
from datetime import datetime,timezone
from pathlib import Path
from typing import Callable

ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
RID="BRRK-CRYPTO-CARRY-ATLAS-0072"; CID="BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001"
PLAN_ID="BRRK-CRYPTO-CARRY-ATLAS-0072-FIRST-CAPTURE-SUPPORT-PLAN-V1"; PARSER="0072_FIRST_CAPTURE_METADATA_V1"
BLOBS={"SOURCE_IDENTITY_CONTRACT.json":"8b933f357a4f4b1299558386e7ad6e91742df939","FIRST_CAPTURE_GATE.json":"e7aa54275d541cefd6f39b6845d619d1b40aafd3","CAPTURE_REQUEST.json":"a0a7d842c2a4d7880580b89504f8c3b16515f76f","CAPTURE_IMPLEMENTATION_CONTRACT.json":"dc1f3416fad6c6934afe890ececbf197bcf8e115"}
ALLOWED={"capture_request_id","source_contract_blob","source_id","canonical_request_id","retrieved_at_utc","raw_sha256","raw_size_bytes","http_status","parser_version","row_count","observed_min_timestamp","observed_max_timestamp","field_names_and_types","missingness_counts","asset","venue","instrument_family","support_status","support_failure_code","raw_object_locator","manifest_locator"}

class CaptureError(RuntimeError): pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise urllib.error.HTTPError(req.full_url,code,"redirect forbidden",headers,fp)

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def sha(b): return hashlib.sha256(b).hexdigest()
def canon(v): return (json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode()
def create(path,b):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o444)
    with os.fdopen(fd,"wb") as f: f.write(b); f.flush(); os.fsync(f.fileno())
def git_blob(name):
    return subprocess.run(["git","rev-parse",f"HEAD:research/brrk_crypto_carry_atlas_0072/{name}"],cwd=ROOT,check=True,text=True,capture_output=True).stdout.strip()
def validate(*,git=True):
    s=load(HERE/"SOURCE_IDENTITY_CONTRACT.json"); g=load(HERE/"FIRST_CAPTURE_GATE.json")
    r=load(HERE/"CAPTURE_REQUEST.json"); i=load(HERE/"CAPTURE_IMPLEMENTATION_CONTRACT.json"); p=load(HERE/"CAPTURE_PLAN.json")
    if (s.get("research_id"),s.get("status"))!=(RID,"FROZEN_NOT_CAPTURED"): raise CaptureError("source drift")
    if (g.get("research_id"),g.get("status"))!=(RID,"FROZEN_NOT_EXECUTED"): raise CaptureError("gate drift")
    if (r.get("capture_request_id"),r.get("status"))!=(CID,"FROZEN_NOT_EXECUTED"): raise CaptureError("request drift")
    if (i.get("status"),i.get("execution_mode"))!=("FROZEN_NOT_EXECUTED","METADATA_ONLY_FIRST_CAPTURE"): raise CaptureError("implementation drift")
    if (p.get("plan_id"),p.get("status"))!=(PLAN_ID,"PROSPECTIVE_SUPPORT_ONLY_NOT_EXECUTED"): raise CaptureError("plan drift")
    if p.get("capture_cutoff_utc")!=r.get("capture_cutoff_utc") or p.get("network_retry_policy")!="ZERO_AUTOMATIC_RETRIES": raise CaptureError("plan semantics drift")
    req=p.get("requests")
    if not isinstance(req,list) or len(req)!=p.get("request_count") or len({x["canonical_request_id"] for x in req})!=len(req): raise CaptureError("request count/id drift")
    hosts=("https://fapi.binance.com/","https://data.binance.vision/","https://api.bybit.com/")
    if any(not x["url"].startswith(hosts) for x in req): raise CaptureError("unapproved host")
    if git:
        for n,e in BLOBS.items():
            if git_blob(n)!=e: raise CaptureError(f"blob drift {n}")
    return p
def storage_root(p):
    p=Path(p)
    if not p.is_absolute(): raise CaptureError("storage root must be absolute")
    p=p.resolve(strict=False); repo=ROOT.resolve(strict=False)
    if p==repo or repo in p.parents: raise CaptureError("storage root inside repository")
    return p
def caproot(p): return storage_root(p)/"research"/"brrk_crypto_carry_atlas_0072"/"captures"/CID
def fetch_once(url,timeout=30):
    req=urllib.request.Request(url,headers={"User-Agent":"laugh-to-2028/0072-metadata-capture","Accept":"*/*"})
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=timeout) as resp:
            body=resp.read(); status=int(resp.getcode())
            hdr={k:resp.headers.get(k,"") for k in ("Content-Type","Content-Length","Last-Modified","ETag")}
    except Exception as e: raise CaptureError("network failure: fail closed") from e
    if status!=200: raise CaptureError("HTTP_NON_200")
    return {"body":body,"status":status,"headers":hdr,"retrieved_at_utc":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
def capture(storage,fetcher:Callable[[str],dict]=fetch_once,*,git=True):
    p=validate(git=git); root=caproot(storage)
    if root.exists() and any(x.is_file() for x in root.rglob("*")): raise CaptureError("CAPTURE_ALREADY_EXISTS")
    objs=[]
    for row in p["requests"]:
        x=fetcher(row["url"]); body=x["body"]; rid=row["canonical_request_id"]; safe="".join(c if c.isalnum() or c in "._-" else "_" for c in rid)
        raw=root/"raw"/(safe+".bin"); man=root/"manifests"/(safe+".json"); create(raw,body)
        m={"schema_version":1,"capture_request_id":CID,"source_id":row["source_id"],"canonical_request_id":rid,"retrieved_at_utc":x["retrieved_at_utc"],"raw_sha256":sha(body),"raw_size_bytes":len(body),"http_status":x["status"],"selected_headers":x.get("headers",{}),"asset":row["asset"],"venue":row["venue"],"instrument_family":row["instrument_family"],"kind":row["kind"],"timestamp_rule":row["timestamp_rule"],"support_if_parsed":row["support_if_parsed"],"raw_object_locator":f"raw/{safe}.bin"}
        create(man,canon(m)); objs.append({**m,"manifest_locator":f"manifests/{safe}.json"})
    by={x["canonical_request_id"]:x for x in objs}; pp={x["canonical_request_id"]:x for x in p["requests"]}
    for k,row in pp.items():
        target=row.get("checksum_for_request_id")
        if target:
            txt=(root/by[k]["raw_object_locator"]).read_text(encoding="ascii").strip().split()[0].lower()
            if len(txt)!=64 or txt!=by[target]["raw_sha256"]: raise CaptureError("CHECKSUM_MISMATCH")
    agg=hashlib.sha256()
    for x in objs: agg.update(x["canonical_request_id"].encode()); agg.update(bytes.fromhex(x["raw_sha256"]))
    st={"schema_version":1,"research_id":RID,"capture_request_id":CID,"plan_id":PLAN_ID,"parser_version":PARSER,"source_contract_blob":BLOBS["SOURCE_IDENTITY_CONTRACT.json"],"object_count":len(objs),"aggregate_raw_sha256":agg.hexdigest(),"state":"PERSISTED_VERIFIED_AWAITING_DURABLE_RECEIPT","objects":objs}
    st["manifest_sha256"]=sha(canon(st)); create(root/"STAGING_MANIFEST.json",canon(st)); return st
def write_receipt(path,st,*,backend,root_ref,artifact_id,artifact_url,archived_at):
    vals=(backend,root_ref,artifact_id,artifact_url,archived_at)
    if any(not isinstance(v,str) or not v.strip() for v in vals): raise CaptureError("invalid durability identity")
    r={"schema_version":1,"research_id":RID,"capture_request_id":CID,"plan_id":PLAN_ID,"manifest_sha256":st["manifest_sha256"],"aggregate_raw_sha256":st["aggregate_raw_sha256"],"object_count":st["object_count"],"durable_backend":backend,"durable_root_ref":root_ref,"artifact_id":artifact_id,"artifact_url":artifact_url,"archived_at_utc":archived_at,"write_semantics":"CREATE_ONLY_VERSIONED_COPY"}
    create(path,canon(r)); return r
def bounds(vals):
    if not vals:return None,None
    s=[datetime.fromtimestamp(int(str(v))/1000,tz=timezone.utc).isoformat().replace("+00:00","Z") for v in vals]
    if len(set(s))!=len(s): raise CaptureError("DUPLICATE_OR_NON_MONOTONE_TIMESTAMP")
    return min(s),max(s)
def schema(rows):
    if not rows:return {},{}
    if isinstance(rows[0],dict):
        fs=sorted({str(k) for r in rows for k in r}); typ={f:type(next((r.get(f) for r in rows if r.get(f) is not None),None)).__name__ for f in fs}; miss={f:sum(r.get(f) in (None,"") for r in rows) for f in fs}
    else:
        w=max(len(r) for r in rows); typ={f"col_{j}":type(next((r[j] for r in rows if j<len(r) and r[j] not in (None,"")),None)).__name__ for j in range(w)}; miss={f"col_{j}":sum(j>=len(r) or r[j] in (None,"") for r in rows) for j in range(w)}
    return typ,miss
def parse_meta(raw,row):
    kind=row["kind"]
    if kind=="sha256_checksum": return 1,None,None,{"sha256":"str"},{"sha256":0},"PASS",None
    if kind=="zip_csv_kline":
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as z: names=[n for n in z.namelist() if not n.endswith("/")]; rows=list(csv.reader(io.StringIO(z.read(names[0]).decode()))) if len(names)==1 else []
        except Exception as e: raise CaptureError("SCHEMA_DRIFT") from e
        if not rows or max(len(r) for r in rows)<12: return 0,None,None,{}, {},"FAIL","SCHEMA_DRIFT"
        typ,miss=schema(rows); lo,hi=bounds([r[0] for r in rows]); return len(rows),lo,hi,typ,miss,"PASS",None
    try: payload=json.loads(raw)
    except Exception: return 0,None,None,{}, {},"FAIL","SCHEMA_DRIFT"
    if row["source_id"]=="BYBIT_V5_OFFICIAL_PUBLIC_MARKET_V1":
        if not isinstance(payload,dict) or payload.get("retCode")!=0 or not isinstance(payload.get("result"),dict) or not isinstance(payload["result"].get("list"),list): return 0,None,None,{}, {},"FAIL","SOURCE_UNAVAILABLE"
        rows=payload["result"]["list"]
    elif isinstance(payload,list): rows=payload
    elif isinstance(payload,dict) and isinstance(payload.get("symbols"),list): rows=payload["symbols"]
    else:return 0,None,None,{}, {},"FAIL","SCHEMA_DRIFT"
    if not rows:return 0,None,None,{}, {},"FAIL","INSUFFICIENT_INSTRUMENT_SUPPORT"
    typ,miss=schema(rows); rule=row["timestamp_rule"]; lo=hi=None
    if rule=="array_0_ms":lo,hi=bounds([r[0] for r in rows if isinstance(r,list) and r])
    elif rule in ("fundingTime","fundingRateTimestamp","timestamp"):lo,hi=bounds([r.get(rule) for r in rows if isinstance(r,dict) and r.get(rule) is not None])
    if row["support_if_parsed"]=="HISTORICAL_METADATA_UNPROVABLE":return len(rows),lo,hi,typ,miss,"FAIL","HISTORICAL_METADATA_UNPROVABLE"
    if rule not in ("NONE","NONE_CURRENT_METADATA_NOT_HISTORICAL_EFFECTIVE") and (lo is None or hi is None):return len(rows),lo,hi,typ,miss,"FAIL","POINT_IN_TIME_SEMANTICS_UNPROVABLE"
    return len(rows),lo,hi,typ,miss,"PASS",None
def finalize(storage,st,receipt_path,*,git=False):
    p=validate(git=git); root=caproot(storage); saved=load(root/"STAGING_MANIFEST.json")
    if saved!=st: raise CaptureError("RAW_HASH_MISMATCH")
    unsigned=dict(st); mh=unsigned.pop("manifest_sha256")
    if sha(canon(unsigned))!=mh: raise CaptureError("RAW_HASH_MISMATCH")
    rec=load(receipt_path)
    for k,e in (("research_id",RID),("capture_request_id",CID),("plan_id",PLAN_ID),("manifest_sha256",st["manifest_sha256"]),("aggregate_raw_sha256",st["aggregate_raw_sha256"]),("object_count",st["object_count"]),("write_semantics","CREATE_ONLY_VERSIONED_COPY")):
        if rec.get(k)!=e:raise CaptureError("RAW_HASH_MISMATCH")
    by={x["canonical_request_id"]:x for x in p["requests"]}; out=[]
    for x in st["objects"]:
        raw=(root/x["raw_object_locator"]).read_bytes()
        if sha(raw)!=x["raw_sha256"]:raise CaptureError("RAW_HASH_MISMATCH")
        n,lo,hi,typ,miss,status,fail=parse_meta(raw,by[x["canonical_request_id"]])
        m={"capture_request_id":CID,"source_contract_blob":BLOBS["SOURCE_IDENTITY_CONTRACT.json"],"source_id":x["source_id"],"canonical_request_id":x["canonical_request_id"],"retrieved_at_utc":x["retrieved_at_utc"],"raw_sha256":x["raw_sha256"],"raw_size_bytes":x["raw_size_bytes"],"http_status":x["http_status"],"parser_version":PARSER,"row_count":n,"observed_min_timestamp":lo,"observed_max_timestamp":hi,"field_names_and_types":typ,"missingness_counts":miss,"asset":x["asset"],"venue":x["venue"],"instrument_family":x["instrument_family"],"support_status":status,"support_failure_code":fail,"raw_object_locator":rec["durable_root_ref"]+"#"+x["raw_object_locator"],"manifest_locator":rec["durable_root_ref"]+"#"+x["manifest_locator"]}
        if set(m)!=ALLOWED:raise CaptureError("metadata allowlist drift")
        out.append(m)
    support={"schema_version":1,"research_id":RID,"capture_request_id":CID,"plan_id":PLAN_ID,"parser_version":PARSER,"lifecycle_credit":"NONE_STAGE_3_REMAINS_INCOMPLETE","controlled_scientific_history_reads_to_researcher":0,"attempt_consumed":0,"production_authorized":False,"signature_authorized":False,"order_submission_authorized":False,"object_count":len(out),"objects":out}
    create(root/"SUPPORT_MANIFEST.json",canon(support)); create(root/"CAPTURE_RECEIPT.json",Path(receipt_path).read_bytes()); return support
def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument("--storage-root",type=Path,required=True); g=ap.add_mutually_exclusive_group(required=True); g.add_argument("--capture-only",action="store_true"); g.add_argument("--finalize",action="store_true"); ap.add_argument("--execute-live-capture",action="store_true"); ap.add_argument("--durable-storage-attested",action="store_true"); ap.add_argument("--staging-json",type=Path); ap.add_argument("--receipt",type=Path); a=ap.parse_args(argv)
    if a.capture_only:
        if not a.execute_live_capture or not a.durable_storage_attested:raise CaptureError("explicit live+durable authorization required")
        print(json.dumps(capture(a.storage_root),sort_keys=True,separators=(",",":")));return 0
    if not a.staging_json or not a.receipt:raise CaptureError("finalize requires staging and receipt")
    st=load(a.staging_json); s=finalize(a.storage_root,st,a.receipt); print(json.dumps({"research_id":RID,"capture_request_id":CID,"object_count":s["object_count"],"support_manifest_sha256":sha(canon(s)),"controlled_scientific_history_reads_to_researcher":0,"attempt_consumed":0,"lifecycle_credit":"NONE_STAGE_3_REMAINS_INCOMPLETE"},sort_keys=True,separators=(",",":")));return 0
if __name__=="__main__":raise SystemExit(main())
