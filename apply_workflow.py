import json, urllib.request, urllib.error, sys

API = "http://localhost:5678/api/v1/workflows/eU4PGTpWCBAOOPZp"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxM2YzOTNjYi0yMTMxLTQwN2ItOWNlNS0xMDVkOWI4OTE5MDYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZDllZTgzNjItOTg3MS00NDIyLWEzMTMtMmI5YjA0MWQxY2JkIiwiaWF0IjoxNzc4ODQyMzE3fQ.gdUhqHCEQVlw-gJcNWi8VXmgxpwp3uIwwJUFBbsYhs4"
HEADERS = {"X-N8N-API-KEY": KEY, "Content-Type": "application/json"}

def req(method, url, data=None):
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode()[:300]); sys.exit(1)

# 1. GET current workflow (to reuse its read-only fields)
print("Buscando workflow atual...")
current = req("GET", API)
print(f"  Atual: {current['name']} | {len(current['nodes'])} nodes")

# 2. Load fix file
with open("/tmp/wf_fix.json") as f:
    fix = json.load(f)
print(f"  Fix:   {fix['name']} | {len(fix['nodes'])} nodes")

# 3. Replace only nodes, connections, settings, name
current["name"] = fix["name"]
current["nodes"] = fix["nodes"]
current["connections"] = fix["connections"]
current["settings"] = fix.get("settings", current.get("settings", {}))
if "pinData" in fix:
    current["pinData"] = fix["pinData"]

# 4. Remove known read-only fields before PUT
for k in ["id", "createdAt", "updatedAt", "versionId", "active", "meta", "tags"]:
    current.pop(k, None)

print(f"\nEnviando {len(current['nodes'])} nodes, {len(current['connections'])} connections...")
result = req("PUT", API, current)
print(f"OK: {result['name']} | nodes: {len(result['nodes'])}")
