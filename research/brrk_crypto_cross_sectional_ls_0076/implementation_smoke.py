"""Stage4 nonhistorical implementation smoke test. Not Stage5 qualification evidence."""
from __future__ import annotations
import hashlib, io, zipfile
from datetime import datetime, timezone
from research.brrk_crypto_cross_sectional_ls_0076.engine import (
    ExecutionContext, create_only_result_objects, run_scientific_engine,
)

def _zip(name: str, text: str) -> bytes:
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(name,text)
    return buf.getvalue()

def run_smoke() -> None:
    ts=int(datetime(2026,1,1,tzinfo=timezone.utc).timestamp()*1000)
    kpath='data/futures/um/monthly/klines/AAAUSDT/1d/AAAUSDT-1d-2026-01.zip'
    fpath='data/futures/um/monthly/fundingRate/AAAUSDT/AAAUSDT-fundingRate-2026-01.zip'
    k=_zip('AAAUSDT-1d-2026-01.csv',f'{ts},1,2,0.5,1.5,10,{ts+86399999},2000000,1,1,1,0\n')
    f=_zip('AAAUSDT-fundingRate-2026-01.csv',f'calc_time,funding_interval_hours,last_funding_rate\n{ts},8,0.0001\n')
    payloads={kpath:k,fpath:f}; hashes={p:hashlib.sha256(b).hexdigest() for p,b in payloads.items()}
    ctx=ExecutionContext()
    result=run_scientific_engine(payloads,hashes,context=ctx)
    assert result.classification=='INCONCLUSIVE_INSUFFICIENT_SUPPORT'
    assert result.execution['scientific_engine_calls']==1
    assert result.execution['controlled_object_reads']==2
    assert result.execution['max_reads_per_object']==1
    outputs=create_only_result_objects(result,())
    assert set(outputs)=={'PRIMARY_RESULT.json','EVIDENCE.json','EXECUTION.json'}
    assert all(v.endswith(b'\n') for v in outputs.values())
    badctx=ExecutionContext()
    bad=run_scientific_engine({kpath:k},{kpath:'0'*64},context=badctx)
    assert bad.classification=='INVALID_EXECUTION'
    assert bad.execution['scientific_engine_calls']==1
    assert bad.execution['controlled_object_reads']==1
    try:
        run_scientific_engine({}, {}, context=badctx)
    except Exception:
        pass
    else:
        raise AssertionError('second engine call must be rejected')

if __name__=='__main__':
    run_smoke()
    print('0076_STAGE4_IMPLEMENTATION_SMOKE_PASS')
