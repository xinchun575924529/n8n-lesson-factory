# -*- coding: utf-8 -*-
# Import + execute all L2-B mock scenarios for 21388, collect Assert outputs.
import json, os, io, sys, subprocess, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

N8N = r"C:\Users\Administrator\AppData\Roaming\npm\n8n.cmd"
DIR = r"C:\Users\Administrator\.easyclaw\workspace\n8n-lesson-crew\workflows\l2-mock-21388"
env = dict(os.environ, NODE_FUNCTION_ALLOW_BUILTIN="crypto,fs,path,querystring",
           N8N_RUNNERS_BROKER_PORT="5691")

summary = []
for sid in ["S1", "S2", "S3", "S4", "S5"]:
    f = os.path.join(DIR, "wf-mock-21388-%s.json" % sid)
    wid = "L2Mock21388%s01" % sid
    r = subprocess.run([N8N, "import:workflow", "--input=" + f], env=env,
                       capture_output=True, text=True, timeout=180)
    if "Successfully imported" not in (r.stdout + r.stderr):
        print(sid, "IMPORT FAIL", r.stdout[-300:], r.stderr[-300:]); continue
    r = subprocess.run([N8N, "execute", "--id", wid], env=env,
                       capture_output=True, text=True, timeout=600)
    out = r.stdout + r.stderr
    # find the Assert JSON output
    found = None
    for m2 in re.finditer(r'"json": (\{\s*"scenario".*?\})\s*,\s*"pairedItem"', out, re.S):
        try:
            found = json.loads(m2.group(1))
        except Exception:
            pass
    if not found:
        print(sid, "NO ASSERT OUTPUT. tail:", out[-2000:])
        summary.append({"scenario": sid, "fail": -1})
        continue
    summary.append(found)
    print(sid, "=> pass %(pass)s/%(total)s fail %(fail)s" % found)
    for it in found["results"]:
        print("   ", "OK " if it["pass"] else "FAIL", it["name"], ("-- " + it.get("detail","")) if not it["pass"] else "")

rep = os.path.join(DIR, "mock-run-summary.json")
json.dump(summary, open(rep, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
tot = sum(s.get("pass", 0) for s in summary); tf = sum(s.get("fail", 0) for s in summary)
print("TOTAL pass=%d fail=%d" % (tot, tf))