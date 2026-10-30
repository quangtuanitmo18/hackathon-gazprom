#!/usr/bin/env python3
"""Isolated localhost-only smoke of pinned Rereflect REST API.

No sensitive data, provider keys, Jira writes, or production URLs are used.
An HTTP-only test, NOT proof of frontend/worker completeness.
"""
from __future__ import annotations
import json, os, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "http://127.0.0.1:8000"
RESULT = Path("docs/spikes/evidence/rereflect-runtime.json")
RESULT.parent.mkdir(parents=True, exist_ok=True)
checks = []

def request(method, path, data=None, token=None):
    payload = None if data is None else json.dumps(data).encode()
    headers = {"Content-Type":"application/json"}
    if token: headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read(2_000_000)
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        # Do not print server responses (might include cookies, user values or secrets)
        return e.code, {}

def check(label, got, wanted, note=None):
    ok = got == wanted
    checks.append({"check": label, "passed": ok, "observed_http": got, "expected_http": wanted, "note":note})
    print(f"{'PASS' if ok else 'FAIL'} {label}: HTTP {got}, expected {wanted}",flush=True)
    if not ok: raise AssertionError(f"{label}: got HTTP {got}, expected {wanted}")

def main():
    status = "failed"
    try:
        deadline = time.monotonic() + 90
        while True:
            try:
                code, health = request("GET", "/health")
                if code == 200: break
            except (urllib.error.URLError,TimeoutError,OSError):
                pass
            if time.monotonic() >= deadline: raise RuntimeError("backend /health not ready")
            time.sleep(3)
        check("GET /health", code, 200)
        a = {"email":"spike-org-a@example.invalid","password":"NotARealPassword-1234!","organization_name":"Spike Organization A"}
        b = {"email":"spike-org-b@example.invalid","password":"NotARealPassword-5678!","organization_name":"Spike Organization B"}
        c1, org1 = request("POST", "/api/v1/auth/signup", a)
        check("POST auth/signup organization A",c1,201)
        token_a=org1.get("access_token")
        if not token_a: raise AssertionError("missing JWT access token")
        c2,org2 = request("POST","/api/v1/auth/signup",b)
        check("POST auth/signup organization B",c2,201)
        token_b=org2.get("access_token")
        if not token_b: raise AssertionError("missing second JWT")
        c3, me=request("GET","/api/v1/auth/me",token=token_a)
        check("GET auth/me",c3,200)
        if me.get("role")!="owner":raise AssertionError("expected owner of new org")
        text="Синтетический тест: при входе в ERP после обновления наблюдается HTTP 403."
        c4,fb=request("POST","/api/v1/feedback/",{"text":text,"source":"manual"},token_a)
        check("POST feedback synthetic Russian",c4,201)
        fid=fb.get("id")
        if not isinstance(fid,int): raise AssertionError("feedback id not integer")
        c5,feedback=request("GET",f"/api/v1/feedback/{fid}",token=token_a)
        check("GET own feedback",c5,200)
        if feedback.get("id")!=fid or feedback.get("text")!=text:
            raise AssertionError("feedback roundtrip failed")
        c6,foreign=request("GET",f"/api/v1/feedback/{fid}",token=token_b)
        check("GET other org feedback (isolation)",c6,404)
        c7, dashboard=request("GET","/api/v1/dashboard/",token=token_a)
        check("GET dashboard",c7,200)
        total=dashboard.get("total_feedback",None)
        if not isinstance(total,int) or total<1:raise AssertionError("dashboard missing created item")
        c8, issue=request("POST",f"/api/v1/feedback/{fid}/issue-draft",{"target":"jira"},token_a)
        check("POST issue-draft with no model configured",c8,409)
        # Note: no real Jira credentials configured, endpoint only returns a draft.
        status="passed"
    except Exception as err:
        print("Smoke failure type:",type(err).__name__,str(err)[:240],flush=True)
    finally:
        result={"status":status,"verified_at_utc":datetime.now(timezone.utc).isoformat(),
                "scope":"pinned Rereflect backend + Postgres + Redis; localhost-only; NO worker/UI/Jira external test",
                "upstream_commit":"987dd9f0611c693524ec0cfba880517fa4d5ec57",
                "checks":checks}
        RESULT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print("Evidence at:",RESULT,flush=True)
    return 0 if status=="passed" else 1

if __name__=="__main__":
    sys.exit(main())
