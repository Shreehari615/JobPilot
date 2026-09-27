"""
JobPilot AI – API Smoke Test
Run: python test_api.py   (backend must be running on port 8000)
"""
import httpx
import json
import sys

BASE = "http://localhost:8000/api/v1"
PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    status = "PASS" if condition else "FAIL"
    icon = "+" if condition else "-"
    print(f"  [{status}] {icon} {name} {detail}")
    if condition:
        PASS += 1
    else:
        FAIL += 1


print("\n" + "="*50)
print("  JobPilot AI – API Smoke Test")
print("="*50 + "\n")

# ── 1. Health ─────────────────────────────────────────
print("[1] Health Check")
try:
    r = httpx.get("http://localhost:8000/health", timeout=10)
    check("Health endpoint", r.status_code == 200)
    check("Status=healthy", r.json().get("status") == "healthy", f"({r.json().get('status')})")
    print(f"      App: {r.json().get('app')} v{r.json().get('version')}")
except Exception as e:
    check("Health endpoint", False, f"(Error: {e})")

# ── 2. Swagger docs ───────────────────────────────────
print("\n[2] Swagger Docs")
r = httpx.get("http://localhost:8000/docs", timeout=10)
check("Swagger UI accessible", r.status_code == 200)

r = httpx.get("http://localhost:8000/openapi.json", timeout=10)
check("OpenAPI schema", r.status_code == 200)
if r.status_code == 200:
    paths = r.json().get("paths", {})
    check("API routes defined", len(paths) > 10, f"({len(paths)} routes)")

# ── 3. Auth ───────────────────────────────────────────
print("\n[3] Authentication")
r = httpx.post(f"{BASE}/auth/register", json={
    "email": "smoketest@jobpilot.ai",
    "password": "SmokeTest123!",
    "full_name": "Smoke Tester"
}, timeout=10)
check("Register user", r.status_code in (200, 201, 400), f"(status {r.status_code})")

r = httpx.post(f"{BASE}/auth/login", json={
    "email": "smoketest@jobpilot.ai",
    "password": "SmokeTest123!"
}, timeout=10)
check("Login user", r.status_code == 200, f"(status {r.status_code})")
token = None
if r.status_code == 200:
    token = r.json().get("access_token")
    check("JWT token issued", bool(token))

headers = {"Authorization": f"Bearer {token}"} if token else {}

r = httpx.get(f"{BASE}/auth/me", headers=headers, timeout=10)
check("Get current user (/me)", r.status_code == 200, f"(status {r.status_code})")
if r.status_code == 200:
    me = r.json()
    check("Email correct", me.get("email") == "smoketest@jobpilot.ai")
    print(f"      Logged in as: {me['email']} | admin={me.get('is_admin')}")

# ── 4. Profile ────────────────────────────────────────
print("\n[4] Profile")
r = httpx.get(f"{BASE}/profile", headers=headers, timeout=10)
check("Get profile", r.status_code == 200, f"(status {r.status_code})")

r = httpx.put(f"{BASE}/profile", headers=headers, json={
    "full_name": "Smoke Tester",
    "location": "Bangalore, India",
    "experience_years": 2.0,
    "experience_level": "junior",
    "bio": "MCA graduate seeking software roles"
}, timeout=10)
check("Update profile", r.status_code == 200, f"(status {r.status_code})")

r = httpx.get(f"{BASE}/profile/preferences", headers=headers, timeout=10)
check("Get preferences", r.status_code == 200, f"(status {r.status_code})")

r = httpx.put(f"{BASE}/profile/preferences", headers=headers, json={
    "remote_preference": "remote",
    "employment_type": "full-time",
    "preferred_roles": ["Software Engineer", "Python Developer"]
}, timeout=10)
check("Update preferences", r.status_code == 200, f"(status {r.status_code})")

# ── 5. Jobs ───────────────────────────────────────────
print("\n[5] Jobs")
r = httpx.get(f"{BASE}/jobs", params={"page": 1, "page_size": 10}, timeout=10)
check("List jobs", r.status_code == 200, f"(status {r.status_code})")
first_job_id = None
if r.status_code == 200:
    data = r.json()
    total = data.get("total", 0)
    items = data.get("items", [])
    check("Jobs in DB (total > 0)", total > 0, f"({total} jobs)")
    check("Items returned in page", len(items) > 0, f"({len(items)} items)")
    if items:
        first_job_id = items[0]["id"]
        print(f"      Sample: [{first_job_id}] {items[0]['title']} @ {items[0].get('company', 'N/A')}")

r = httpx.get(f"{BASE}/jobs", params={"query": "python", "page_size": 5}, timeout=10)
check("Search jobs by keyword", r.status_code == 200, f"(results: {r.json().get('total', '?')})")

r = httpx.get(f"{BASE}/jobs", params={"work_mode": "remote", "page_size": 5}, timeout=10)
check("Filter by remote", r.status_code == 200, f"(status {r.status_code})")

r = httpx.get(f"{BASE}/jobs", params={"job_type": "full-time", "page_size": 5}, timeout=10)
check("Filter by job type", r.status_code == 200, f"(status {r.status_code})")

if first_job_id:
    r = httpx.get(f"{BASE}/jobs/{first_job_id}", timeout=10)
    check("Job detail by ID", r.status_code == 200, f"(status {r.status_code})")
    if r.status_code == 200:
        j = r.json()
        check("Job has title", bool(j.get("title")))
        check("Job has original_url", bool(j.get("original_url")))

r = httpx.get(f"{BASE}/jobs/stats/summary", timeout=10)
check("Job stats summary", r.status_code == 200, f"(status {r.status_code})")
if r.status_code == 200:
    s = r.json()
    check("Stats total_jobs > 0", s.get("total_jobs", 0) > 0, f"(total={s.get('total_jobs')})")

# ── 6. Save / Unsave ──────────────────────────────────
print("\n[6] Saved Jobs")
if first_job_id and token:
    r = httpx.post(f"{BASE}/jobs/{first_job_id}/save", headers=headers, json={"status": "saved"}, timeout=10)
    check("Save a job", r.status_code == 200, f"(status {r.status_code})")

    r = httpx.get(f"{BASE}/jobs/saved", headers=headers, timeout=10)
    check("Get saved jobs", r.status_code == 200, f"(status {r.status_code})")
    if r.status_code == 200:
        check("Saved list non-empty", len(r.json()) > 0)

    r = httpx.delete(f"{BASE}/jobs/{first_job_id}/save", headers=headers, timeout=10)
    check("Unsave job", r.status_code == 200, f"(status {r.status_code})")

# ── 7. Interaction tracking ───────────────────────────
print("\n[7] Interaction Tracking")
if first_job_id and token:
    r = httpx.post(f"{BASE}/jobs/{first_job_id}/interact", headers=headers,
                   json={"interaction_type": "clicked_apply"}, timeout=10)
    check("Track job interaction", r.status_code == 200, f"(status {r.status_code})")

# ── 8. Recommendations ────────────────────────────────
print("\n[8] Recommendations")
r = httpx.get(f"{BASE}/recommendations", headers=headers, timeout=30)
check("Get recommendations", r.status_code == 200, f"(status {r.status_code})")
if r.status_code == 200:
    recs = r.json()
    print(f"      Recommendations returned: {len(recs)}")

# ── 9. Skills taxonomy ────────────────────────────────
print("\n[9] Skills Taxonomy")
r = httpx.get(f"{BASE}/skills/categories", timeout=10)
check("Skill categories", r.status_code == 200, f"(status {r.status_code})")
if r.status_code == 200:
    cats = r.json()
    check("Categories non-empty", len(cats) > 0, f"({len(cats)} categories)")

r = httpx.get(f"{BASE}/skills/search", params={"q": "python"}, timeout=10)
check("Skill search (python)", r.status_code == 200, f"(status {r.status_code})")
if r.status_code == 200:
    print(f"      Matched: {r.json()[:5]}")

# ── 10. Admin endpoints ───────────────────────────────
print("\n[10] Admin")
r = httpx.get(f"{BASE}/admin/stats", headers=headers, timeout=10)
check("Admin stats", r.status_code in (200, 403), f"(status {r.status_code})")

r = httpx.get(f"{BASE}/admin/sources", headers=headers, timeout=10)
check("Admin job sources", r.status_code in (200, 403), f"(status {r.status_code})")

# ── Summary ────────────────────────────────────────────
print("\n" + "="*50)
total_tests = PASS + FAIL
pct = int((PASS / total_tests) * 100) if total_tests > 0 else 0
print(f"  Results: {PASS}/{total_tests} passed ({pct}%)")
if FAIL == 0:
    print("  >> ALL TESTS PASSED <<")
else:
    print(f"  !! {FAIL} test(s) FAILED")
print("="*50 + "\n")

sys.exit(0 if FAIL == 0 else 1)
