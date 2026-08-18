from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

BASELINE_WORKFLOW_BLOB = "3df9cd6b4aff8443844052d8c1cd697b34c864e2"
TEST_ANCHOR = "      - name: Run STABLECOIN-LIQUIDITY-0001 data-contract unit tests\n        run: python -m unittest discover -s research/stablecoin_liquidity_0001 -p 'test_*.py'\n"
TEST_INSERTION = "      - name: Run 0072 first-capture wiring unit tests\n        run: python -m unittest discover -s research/brrk_crypto_carry_atlas_0072 -p 'test_capture_wiring.py'\n"
JOB_INSERTION = r'''

  carry-atlas-0072-first-capture-execution:
    name: 0072 guarded first metadata capture
    if: >-
      github.event_name == 'push' &&
      github.ref == 'refs/heads/main' &&
      contains(github.event.head_commit.message, '[0072_FIRST_CAPTURE_EXECUTE_V1]')
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: read
      actions: read
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Preflight frozen wiring and repository-wide duplicate artifact guard
        env:
          GH_TOKEN: ${{ github.token }}
          RAW_ARTIFACT_NAME: 0072-first-capture-raw-BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001
        run: |
          set -euo pipefail
          python - <<'PY'
          from research.brrk_crypto_carry_atlas_0072.capture_wiring import validate
          plan = validate(git=True)
          assert plan['request_count'] == 37
          PY
          COUNT="$(curl -fsSL \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer ${GH_TOKEN}" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "${GITHUB_API_URL}/repos/${GITHUB_REPOSITORY}/actions/artifacts?name=${RAW_ARTIFACT_NAME}&per_page=100" \
            | python -c 'import json,sys; d=json.load(sys.stdin); print(sum(1 for a in d.get("artifacts",[]) if not a.get("expired",False)))')"
          test "${COUNT}" = "0"
      - name: Capture each frozen object at most once without parsing
        id: capture
        env:
          STAGING_ROOT: ${{ runner.temp }}/0072-first-capture
          STAGING_JSON: ${{ runner.temp }}/0072-staging.json
          FAILURE_JSON: ${{ runner.temp }}/0072-failure-receipt.json
        run: |
          set -uo pipefail
          mkdir -p "${STAGING_ROOT}"
          set +e
          python -m research.brrk_crypto_carry_atlas_0072.capture_wiring --storage-root "${STAGING_ROOT}" --capture-only --execute-live-capture --durable-storage-attested > "${STAGING_JSON}"
          RC=$?
          set -e
          if [ "${RC}" -ne 0 ]; then
            python - <<'PY'
          import json, os
          from pathlib import Path
          payload = {'schema_version':1,'research_id':'BRRK-CRYPTO-CARRY-ATLAS-0072','capture_request_id':'BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001','state':'CAPTURE_FAILED_REQUIRES_MANUAL_RECONCILIATION_NO_AUTOMATIC_REFETCH','workflow_run_id':os.environ['GITHUB_RUN_ID'],'workflow_run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'workflow_sha':os.environ['GITHUB_SHA'],'controlled_scientific_history_reads_to_researcher':0,'attempt_consumed':0}
          Path(os.environ['FAILURE_JSON']).write_text(json.dumps(payload, sort_keys=True, separators=(',', ':')) + '\n', encoding='utf-8')
          PY
            echo 'capture_ok=false' >> "${GITHUB_OUTPUT}"
          else
            echo 'capture_ok=true' >> "${GITHUB_OUTPUT}"
          fi
          echo "staging_root=${STAGING_ROOT}" >> "${GITHUB_OUTPUT}"
          echo "staging_json=${STAGING_JSON}" >> "${GITHUB_OUTPUT}"
          echo "failure_json=${FAILURE_JSON}" >> "${GITHUB_OUTPUT}"
      - name: Persist raw or failure state before any parse
        id: raw_archive
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: 0072-first-capture-raw-BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001
          path: |
            ${{ steps.capture.outputs.staging_root }}/**
            ${{ steps.capture.outputs.staging_json }}
            ${{ steps.capture.outputs.failure_json }}
          if-no-files-found: error
          retention-days: 90
          overwrite: false
      - name: Stop permanently after durably recorded capture failure
        if: steps.capture.outputs.capture_ok != 'true'
        run: exit 42
      - name: Create hash-bound durability receipt
        if: steps.capture.outputs.capture_ok == 'true'
        id: receipt
        env:
          STAGING_JSON: ${{ steps.capture.outputs.staging_json }}
          RECEIPT_PATH: ${{ runner.temp }}/0072-durability-receipt.json
          ARTIFACT_ID: ${{ steps.raw_archive.outputs.artifact-id }}
          ARTIFACT_URL: ${{ steps.raw_archive.outputs.artifact-url }}
        run: |
          python - <<'PY'
          import json, os
          from datetime import datetime, timezone
          from pathlib import Path
          from research.brrk_crypto_carry_atlas_0072.capture_wiring import write_receipt
          st=json.loads(Path(os.environ['STAGING_JSON']).read_text(encoding='utf-8'))
          write_receipt(Path(os.environ['RECEIPT_PATH']), st, backend='GITHUB_ACTIONS_ARTIFACT_V4', root_ref=f"{os.environ['ARTIFACT_URL']}#artifact_id={os.environ['ARTIFACT_ID']}", artifact_id=os.environ['ARTIFACT_ID'], artifact_url=os.environ['ARTIFACT_URL'], archived_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
          PY
          echo "receipt_path=${RECEIPT_PATH}" >> "${GITHUB_OUTPUT}"
      - name: Finalize metadata only after raw durability
        if: steps.capture.outputs.capture_ok == 'true'
        id: finalize
        env:
          STAGING_ROOT: ${{ steps.capture.outputs.staging_root }}
          STAGING_JSON: ${{ steps.capture.outputs.staging_json }}
          RECEIPT_PATH: ${{ steps.receipt.outputs.receipt_path }}
          SUMMARY_PATH: ${{ runner.temp }}/0072-metadata-summary.json
        run: |
          python -m research.brrk_crypto_carry_atlas_0072.capture_wiring --storage-root "${STAGING_ROOT}" --finalize --staging-json "${STAGING_JSON}" --receipt "${RECEIPT_PATH}" > "${SUMMARY_PATH}"
          echo "summary_path=${SUMMARY_PATH}" >> "${GITHUB_OUTPUT}"
          echo "support_path=${STAGING_ROOT}/research/brrk_crypto_carry_atlas_0072/captures/BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001/SUPPORT_MANIFEST.json" >> "${GITHUB_OUTPUT}"
          echo "capture_receipt_path=${STAGING_ROOT}/research/brrk_crypto_carry_atlas_0072/captures/BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001/CAPTURE_RECEIPT.json" >> "${GITHUB_OUTPUT}"
      - name: Archive metadata-only support and receipt
        if: steps.capture.outputs.capture_ok == 'true'
        uses: actions/upload-artifact@v4
        with:
          name: 0072-first-capture-metadata-BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001
          path: |
            ${{ steps.finalize.outputs.summary_path }}
            ${{ steps.finalize.outputs.support_path }}
            ${{ steps.finalize.outputs.capture_receipt_path }}
            ${{ steps.receipt.outputs.receipt_path }}
          if-no-files-found: error
          retention-days: 90
          overwrite: false
'''

@dataclass(frozen=True)
class PatchResult:
    original: bytes
    patched: bytes


def patch_bytes(original: bytes) -> PatchResult:
    text = original.decode('utf-8')
    if text.count(TEST_ANCHOR) != 1:
        raise RuntimeError('test anchor count must equal one')
    if TEST_INSERTION in text or 'carry-atlas-0072-first-capture-execution:' in text:
        raise RuntimeError('0072 workflow wiring already present')
    patched = text.replace(TEST_ANCHOR, TEST_ANCHOR + TEST_INSERTION, 1)
    if not patched.endswith('\n'):
        patched += '\n'
    patched += JOB_INSERTION.lstrip('\n')
    restored = patched.replace(TEST_INSERTION, '', 1)
    restored = restored[: restored.index('\n  carry-atlas-0072-first-capture-execution:')] + '\n'
    if restored.encode('utf-8') != original:
        raise RuntimeError('byte-preservation proof failed')
    return PatchResult(original=original, patched=patched.encode('utf-8'))


def patch_file(path: Path) -> None:
    original = path.read_bytes()
    path.write_bytes(patch_bytes(original).patched)
