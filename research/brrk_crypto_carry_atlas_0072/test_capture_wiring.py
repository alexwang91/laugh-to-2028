import hashlib,json,tempfile,unittest,zipfile,urllib.parse,urllib.request
from io import BytesIO
from pathlib import Path
from unittest import mock
from research.brrk_crypto_carry_atlas_0072 import capture_wiring as c

def z():
    b=BytesIO()
    with zipfile.ZipFile(b,"w") as f:f.writestr("x.csv","1782864000000,1,2,0,1,10,1782950399999,10,1,5,5,0\n1782950400000,1,2,0,1,10,1783036799999,10,1,5,5,0\n")
    return b.getvalue()

class CaptureWiringTests(unittest.TestCase):
    def test_plan(self):
        p=c.validate(git=False);self.assertEqual(p["request_count"],37);self.assertEqual(len(p["requests"]),37);self.assertEqual(len({r["canonical_request_id"] for r in p["requests"]}),37)
    def test_explicit_live_guard(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(c.CaptureError):c.main(["--storage-root",d,"--capture-only"])
    def test_create_only(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x";c.create(p,b"a")
            with self.assertRaises(FileExistsError):c.create(p,b"b")
    def test_values_not_echoed(self):
        r={"kind":"json","source_id":"BINANCE_OFFICIAL_PUBLIC_FUTURES_AND_ARCHIVE_V1","timestamp_rule":"fundingTime","support_if_parsed":"SUPPORTED"}
        out=c.parse_meta(json.dumps([{"fundingTime":1782864000000,"fundingRate":"SECRET"}]).encode(),r)
        self.assertNotIn("SECRET",json.dumps(out));self.assertEqual(out[0],1)
    def test_current_metadata_fail_closed(self):
        r={"kind":"json","source_id":"BYBIT_V5_OFFICIAL_PUBLIC_MARKET_V1","timestamp_rule":"NONE_CURRENT_METADATA_NOT_HISTORICAL_EFFECTIVE","support_if_parsed":"HISTORICAL_METADATA_UNPROVABLE"}
        out=c.parse_meta(json.dumps({"retCode":0,"result":{"list":[{"symbol":"BTCUSDT"}]}}).encode(),r);self.assertEqual(out[-2:],("FAIL","HISTORICAL_METADATA_UNPROVABLE"))
    def test_capture_exactly_once_and_no_second_capture(self):
        zp=z();zs=hashlib.sha256(zp).hexdigest();calls=[]
        def f(url):
            calls.append(url)
            if url.endswith(".zip"):body=zp
            elif url.endswith(".CHECKSUM"):body=(zs+"  x.zip\n").encode()
            elif "api.bybit.com" in url:body=json.dumps({"retCode":0,"result":{"list":[["1782864000000","X"]]}}).encode()
            elif "exchangeInfo" in url:body=json.dumps({"symbols":[{"symbol":"BTCUSDT"}]}).encode()
            elif "fundingRate" in url:body=json.dumps([{"fundingTime":1782864000000,"fundingRate":"X"}]).encode()
            else:body=json.dumps([[1782864000000,"X"]]).encode()
            return {"body":body,"status":200,"headers":{},"retrieved_at_utc":"2026-08-18T20:00:00Z"}
        with tempfile.TemporaryDirectory() as d:
            st=c.capture(Path(d),f,git=False);self.assertEqual(st["object_count"],37);self.assertEqual(len(calls),37)
            with self.assertRaises(c.CaptureError):c.capture(Path(d),f,git=False)
    def test_finalize_allowlist(self):
        one={"requests":[{"canonical_request_id":"ONE","source_id":"BINANCE_OFFICIAL_PUBLIC_FUTURES_AND_ARCHIVE_V1","asset":"BTC","venue":"BINANCE","instrument_family":"PERPETUAL_FUNDING","kind":"json","timestamp_rule":"fundingTime","support_if_parsed":"SUPPORTED","url":"https://fapi.binance.com/fapi/v1/fundingRate"}]}
        def f(url):return {"body":json.dumps([{"fundingTime":1782864000000,"fundingRate":"SECRET"}]).encode(),"status":200,"headers":{},"retrieved_at_utc":"2026-08-18T20:00:00Z"}
        with mock.patch.object(c,"validate",return_value=one):
            with tempfile.TemporaryDirectory() as d:
                d=Path(d);st=c.capture(d,f,git=False);rp=d/"r.json";c.write_receipt(rp,st,backend="GITHUB_ACTIONS_ARTIFACT_V4",root_ref="artifact://1",artifact_id="1",artifact_url="https://x",archived_at="2026-08-18T20:01:00Z");s=c.finalize(d,st,rp);self.assertNotIn("SECRET",json.dumps(s));self.assertEqual(set(s["objects"][0]),c.ALLOWED);self.assertEqual(s["attempt_consumed"],0)
    def test_capture_artifact_status_probe_metadata_only(self):
        names=[
            "0072-first-capture-raw-BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001",
            "0072-first-capture-metadata-BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001",
        ]
        out={}
        for name in names:
            url="https://api.github.com/repos/alexwang91/laugh-to-2028/actions/artifacts?name="+urllib.parse.quote(name)+"&per_page=100"
            req=urllib.request.Request(url,headers={"Accept":"application/vnd.github+json","User-Agent":"0072-metadata-only-status-probe","X-GitHub-Api-Version":"2022-11-28"})
            with urllib.request.urlopen(req,timeout=20) as r:data=json.load(r)
            rows=[]
            for a in data.get("artifacts",[]):
                wr=a.get("workflow_run") or {}
                rows.append({"id":a.get("id"),"name":a.get("name"),"size_in_bytes":a.get("size_in_bytes"),"expired":a.get("expired"),"created_at":a.get("created_at"),"updated_at":a.get("updated_at"),"workflow_run_id":wr.get("id"),"workflow_head_sha":wr.get("head_sha")})
            out[name]=rows
        print("0072_CAPTURE_STATUS_PROBE="+json.dumps(out,sort_keys=True,separators=(",",":")))
        self.assertLessEqual(len(out[names[0]]),1)
        self.assertLessEqual(len(out[names[1]]),1)

if __name__=="__main__":unittest.main()
