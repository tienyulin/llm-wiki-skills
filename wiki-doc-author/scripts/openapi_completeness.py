#!/usr/bin/env python3
"""OpenAPI completeness gate — stdlib only.

Reports endpoints/parameters/responses that are missing the descriptions and
examples that make API docs useful to AI agents (error schemas + examples are the
highest-value content). Same gap definition the wiki-doc-author skill uses to
help you fill them.

Usage:
  python openapi_completeness.py [openapi.json] [--fail]
  --fail : exit non-zero on any gap (use as a pre-commit gate). Default: warn (exit 0).

Fix gaps in CODE (route summary=/description=, Pydantic Field(description=...)),
then regenerate — openapi.json is generated, not hand-edited.
"""

import argparse
import json
import sys


def find_gaps(spec):
    """Return a list of human-readable completeness gaps in an OpenAPI spec."""
    gaps = []
    for path, item in (spec.get("paths") or {}).items():
        for method, op in (item or {}).items():
            if method.lower() not in ("get", "post", "put", "delete", "patch"):
                continue
            tag = f"{method.upper()} {path}"
            if not op.get("summary") and not op.get("description"):
                gaps.append(f"{tag}: 缺 summary/description")
            for p in op.get("parameters", []) or []:
                if not p.get("description"):
                    gaps.append(f"{tag}: parameter '{p.get('name', '?')}' 缺 description")
            responses = op.get("responses") or {}
            if not any(str(c).startswith(("4", "5")) for c in responses):
                gaps.append(f"{tag}: 缺 error response（4xx/5xx）")
            # request/response example present anywhere?
            has_example = json.dumps(op, ensure_ascii=False).find('"example') != -1
            if not has_example:
                gaps.append(f"{tag}: 缺 request/response 範例")
    return gaps


def _self_test():
    """Assert the gap rules on hand-built specs (stdlib, no deps)."""
    complete = {
        "paths": {
            "/c": {
                "post": {
                    "summary": "扣款",
                    "parameters": [{"name": "id", "description": "帳號"}],
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {"application/json": {"example": {"ok": 1}}},
                        },
                        "400": {"description": "bad"},
                    },
                }
            }
        }
    }
    assert not find_gaps(complete), find_gaps(complete)
    assert not find_gaps({})
    assert not find_gaps({"paths": {}})
    # non-HTTP keys at the path-item level are ignored
    assert not find_gaps({"paths": {"/c": {"parameters": []}}})

    bare = {"paths": {"/c": {"post": {"parameters": [{"name": "id"}], "responses": {"200": {}}}}}}
    gaps = find_gaps(bare)
    assert any("summary" in g for g in gaps), gaps
    assert any("parameter 'id'" in g for g in gaps), gaps
    assert any("4xx" in g for g in gaps), gaps
    assert any("範例" in g for g in gaps), gaps

    # an example reachable only through a $ref (not inline in the operation) is
    # still a gap — the gate wants the example inline where agents can read it.
    ref_only = {
        "paths": {
            "/c": {
                "post": {
                    "summary": "x",
                    "responses": {"200": {"$ref": "#/components/x"}, "400": {"description": "e"}},
                }
            }
        }
    }
    assert any("範例" in g for g in find_gaps(ref_only)), find_gaps(ref_only)
    print("openapi_completeness self-test: OK")


def main():
    """Load the spec, report gaps, and return a process exit code."""
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?", default="openapi.json")
    ap.add_argument("--fail", action="store_true", help="exit non-zero on any gap")
    ap.add_argument("--self-test", action="store_true", help="run offline self-checks and exit")
    args = ap.parse_args()
    if args.self_test:
        _self_test()
        return 0
    try:
        with open(args.spec, encoding="utf-8") as f:
            spec = json.load(f)
    except FileNotFoundError:
        print(f"[completeness] 找不到 {args.spec} → 跳過（非 OpenAPI app）")
        return 0

    gaps = find_gaps(spec)
    if not gaps:
        print("[completeness] OK — 無缺漏")
        return 0
    print(f"[completeness] {len(gaps)} 處缺漏：")
    for g in gaps:
        print(f"    - {g}")
    print("補在程式碼（summary=/description=/Pydantic Field），或跑 `wiki-doc-author` skill 輔助。")
    return 1 if args.fail else 0


if __name__ == "__main__":
    sys.exit(main())
