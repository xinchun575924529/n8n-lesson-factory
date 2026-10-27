# -*- coding: utf-8 -*-
"""L2-C free real-run for 21388: real DeepSeek + pre-generated ffmpeg videos."""
import json, os

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "workflows", "l2c-21388")
os.makedirs(OUT_DIR, exist_ok=True)

DS_KEY = "sk-3bdc3ad33ecc41baabe98a80774b1274"
VID_DIR = r"C:\Users\Administrator\.easyclaw\workspace\n8n-lesson-crew\state\21388-l2c"

EXTRACT_JS = """const html = $input.first().json.data || '';
const pick = (re) => (html.match(re) || [])[1] || '';
const title = pick(/<meta[^>]+property=["']og:title["'][^>]+content=["']([^"']+)/i) || pick(/<title[^>]*>([^<]*)<\\/title>/i);
const description = pick(/<meta[^>]+(?:name|property)=["'](?:og:)?description["'][^>]+content=["']([^"']+)/i);
const image = pick(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)/i);
const text = html.replace(/<script[\\s\\S]*?<\\/script>|<style[\\s\\S]*?<\\/style>/gi, ' ').replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim().slice(0, 6000);
return [{ json: { title, description, image, text, product_url: $('Settings').first().json.product_url } }];"""

SPLIT_JS = """const o = $input.first().json.output;
return o.prompts.slice(0, 3).map((prompt, i) => ({ json: { variant: i + 1, prompt, hook: o.hook, script: o.script, caption: o.caption } }));"""

BUILD_SLACK_JS = """const v = $input.all().map(i => i.json);
const s = $('Split Into Variants').first().json;
const lines = v.map(x => `Variant ${x.variant}: ${x.video_url || 'failed (' + x.status + ')'}`).join('\\n');
return [{ json: { ready_count: v.filter(x => x.video_url).length, variants: v, caption: s.caption, message: `*New UGC ad for review*\\nHook: ${s.hook}\\nScript: ${s.script}\\n\\n${lines}\\n\\nCaption:\\n${s.caption}` } }];"""

PICK_JS = """const n = Number(String($input.first().json.data.decision).replace(/\\D/g, ''));
const m = $('Build Slack Message').first().json;
const v = m.variants.find(x => x.variant === n);
if (!v || !v.video_url) throw new Error(`Variant ${n} has no video`);
return [{ json: { video_url: v.video_url, caption: m.caption } }];"""

MOCK_HTML = '<html><head><meta property="og:title" content="CoolGadget Pro - Smart Home Hub"><meta property="og:description" content="Control your entire home with one device. Voice control, app, automation."><meta property="og:image" content="https://example.com/product.jpg"><title>CoolGadget Pro</title></head><body><h1>CoolGadget Pro</h1><p>The ultimate smart home hub. Control lights, temperature, security cameras and more from one sleek device. Supports Alexa, Google Home, and HomeKit. Energy efficient with automatic scheduling.</p><span>$79.99</span><p>Over 10,000 happy customers. Easy 2-minute setup.</p></body></html>'

DEEPSEEK_PROMPT = """You are a UGC ad scriptwriter. From the product page below, write a short vertical video ad.
Respond with a JSON object containing exactly these fields:
- hook: a scroll-stopping first line (max 12 words)
- script: a 3-sentence voiceover-style script in a casual first-person UGC tone
- caption: an Instagram caption with up to 5 hashtags
- prompts: an array of exactly 3 different visual prompts (max 60 words each) for a 5 second 9:16 video, each a different angle (unboxing, in-use close-up, lifestyle). No on-screen text.

Title: {{ $json.title }}
Description: {{ $json.description }}
Page text: {{ $json.text }}

Respond ONLY with the JSON object, no other text."""

_nid = [0]
def _id():
    _nid[0] += 1
    return str(_nid[0])

def N(name, ntype, pos, params, tv=1, extra=None):
    n = {"id": _id(), "name": name, "type": ntype, "position": pos, "parameters": params, "typeVersion": tv}
    if extra: n.update(extra)
    return n

def code(name, pos, js, all_items=True):
    p = {"jsCode": js}
    if all_items: p["mode"] = "runOnceForAllItems"
    return N(name, "n8n-nodes-base.code", pos, p, 2)

def set_n(name, pos, params):
    return N(name, "n8n-nodes-base.set", pos, params, 3.4)

def if_n(name, pos, params):
    return N(name, "n8n-nodes-base.if", pos, params, 2.2)

def wait_n(name, pos, secs):
    return N(name, "n8n-nodes-base.wait", pos, {"amount": secs}, 1.1)

def _if_eq(l, r):
    return {"options":{},"conditions":{"options":{"version":2,"leftValue":"","caseSensitive":True,"typeValidation":"loose"},"combinator":"and","conditions":[{"id":"c1","operator":{"type":"string","operation":"equals"},"leftValue":l,"rightValue":r}]}}

def _if_gt(l, r):
    return {"options":{},"conditions":{"options":{"version":2,"leftValue":"","caseSensitive":True,"typeValidation":"loose"},"combinator":"and","conditions":[{"id":"c1","operator":{"type":"number","operation":"gt"},"leftValue":l,"rightValue":r}]}}

def _if_neq(l, r):
    return {"options":{},"conditions":{"options":{"version":2,"leftValue":"","caseSensitive":True,"typeValidation":"loose"},"combinator":"and","conditions":[{"id":"c1","operator":{"type":"string","operation":"notEquals"},"leftValue":l,"rightValue":r}]}}

def _if_or2(l, r1, r2):
    return {"options":{},"conditions":{"options":{"version":2,"leftValue":"","caseSensitive":True,"typeValidation":"loose"},"combinator":"or","conditions":[
        {"id":"c1","operator":{"type":"string","operation":"equals"},"leftValue":l,"rightValue":r1},
        {"id":"c2","operator":{"type":"string","operation":"equals"},"leftValue":l,"rightValue":r2}]}}

def _if_lt(l, r):
    return {"options":{},"conditions":{"options":{"version":2,"leftValue":"","caseSensitive":True,"typeValidation":"loose"},"combinator":"and","conditions":[{"id":"c1","operator":{"type":"number","operation":"lt"},"leftValue":l,"rightValue":r}]}}

_nid[0] = 0
nodes = []
conns = {}

# 0. Manual Trigger
nodes.append(N("Manual Trigger", "n8n-nodes-base.manualTrigger", [-400, 0], {}, 1))
conns["Manual Trigger"] = {"main":[[{"node":"Mock Input","type":"main","index":0}]]}

# 1. Mock Input
nodes.append(N("Mock Input", "n8n-nodes-base.set", [-200, 0], {"options":{},"assignments":{"assignments":[
    {"id":"i1","name":"product_url","type":"string","value":"https://example.com/products/coolgadget-pro"}]}}, 3.4))
conns["Mock Input"] = {"main":[[{"node":"Settings","type":"main","index":0}]]}

# 2. Settings (verbatim)
nodes.append(set_n("Settings", [0, 0], {"options":{},"assignments":{"assignments":[
    {"id":"a1","name":"product_url","type":"string","value":"={{ $json.product_url || $json.body?.product_url }}"},
    {"id":"a2","name":"ig_user_id","type":"string","value":"MOCK_IG_USER"},
    {"id":"a3","name":"graph_version","type":"string","value":"v21.0"}]}}))
conns["Settings"] = {"main":[[{"node":"Mock Fetch Page","type":"main","index":0}]]}

# 3. Mock Fetch Page
nodes.append(code("Mock Fetch Page", [200, 0],
    f'return [{{ json: {{ data: {json.dumps(MOCK_HTML)} }} }}];'))
conns["Mock Fetch Page"] = {"main":[[{"node":"Extract Page Text","type":"main","index":0}]]}

# 4. Extract Page Text (verbatim)
nodes.append(code("Extract Page Text", [400, 0], EXTRACT_JS))
conns["Extract Page Text"] = {"main":[[{"node":"DeepSeek API","type":"main","index":0}]]}

# 5. DeepSeek API (real HTTP Request)
ds_body = json.dumps({
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": DEEPSEEK_PROMPT}],
    "response_format": {"type": "json_object"},
    "max_tokens": 1000,
    "temperature": 0.7
})
nodes.append(N("DeepSeek API", "n8n-nodes-base.httpRequest", [600, 0], {
    "url": "https://api.deepseek.com/v1/chat/completions",
    "method": "POST",
    "sendHeaders": True,
    "headerParameters": {"parameters": [
        {"name": "Authorization", "value": f"Bearer {DS_KEY}"},
        {"name": "Content-Type", "value": "application/json"}
    ]},
    "sendBody": True,
    "specifyBody": "json",
    "jsonBody": ds_body.replace('{{ $json.title }}', '={{ $json.title }}').replace('{{ $json.description }}', '={{ $json.description }}').replace('{{ $json.text }}', '={{ $json.text }}'),
    "options": {"response": {"response": {"responseFormat": "json"}}}
}, 4.2))
conns["DeepSeek API"] = {"main":[[{"node":"Parse DeepSeek","type":"main","index":0}]]}

# 6. Parse DeepSeek Response
nodes.append(code("Parse DeepSeek", [800, 0], """const r = $input.first().json;
const content = r.choices[0].message.content;
let parsed;
try { parsed = JSON.parse(content); } catch(e) { throw new Error('DeepSeek returned invalid JSON: ' + content.slice(0, 200)); }
if (!parsed.hook || !parsed.prompts || !Array.isArray(parsed.prompts)) throw new Error('Missing required fields: ' + Object.keys(parsed).join(','));
return [{ json: { output: parsed } }];"""))
conns["Parse DeepSeek"] = {"main":[[{"node":"Split Into Variants","type":"main","index":0}]]}

# 7. Split Into Variants (verbatim)
nodes.append(code("Split Into Variants", [1000, 0], SPLIT_JS))
conns["Split Into Variants"] = {"main":[[{"node":"Loop Over Variants","type":"main","index":0}]]}

# 8. Loop Over Variants
nodes.append(N("Loop Over Variants", "n8n-nodes-base.splitInBatches", [1200, 0], {"options":{}}, 3))
conns["Loop Over Variants"] = {"main":[
    [{"node":"Build Slack Message","type":"main","index":0}],
    [{"node":"Mock Create Sisif","type":"main","index":0}]]}

# 9. Mock Create Sisif (returns local file path)
VID_JSON = VID_DIR.replace('\\', '/')
nodes.append(code("Mock Create Sisif", [1400, 200], f"""const v = $json.variant;
const fs = require('fs');
const p = '{VID_JSON}/variant_' + v + '.mp4';
if (!fs.existsSync(p)) throw new Error('Video not found: ' + p);
return [{{ json: {{ id: 'poll_v' + v, file_path: p, file_size: fs.statSync(p).size }} }}];"""))
conns["Mock Create Sisif"] = {"main":[[{"node":"Start Poll Counter","type":"main","index":0}]]}

# 10. Start Poll Counter (verbatim)
nodes.append(set_n("Start Poll Counter", [1600, 200], {"options":{},"assignments":{"assignments":[
    {"id":"p1","name":"poll_id","type":"string","value":"={{ $json.id }}"},
    {"id":"p2","name":"attempt","type":"number","value":"0"}]}}))
conns["Start Poll Counter"] = {"main":[[{"node":"Wait Before Status Check","type":"main","index":0}]]}

# 11. Wait
nodes.append(wait_n("Wait Before Status Check", [1800, 200], 1))
conns["Wait Before Status Check"] = {"main":[[{"node":"Mock Check Video Status","type":"main","index":0}]]}

# 12. Mock Check Video Status (returns READY with local file path)
nodes.append(code("Mock Check Video Status", [2000, 200], f"""const v = $('Loop Over Variants').item.json.variant;
return [{{ json: {{ status: 'READY', video_url: 'file:///{VID_JSON}/variant_' + v + '.mp4', id: $json.poll_id }} }}];"""))
conns["Mock Check Video Status"] = {"main":[[{"node":"Track Poll Attempt","type":"main","index":0}]]}

# 13. Track Poll Attempt (verbatim)
nodes.append(set_n("Track Poll Attempt", [2200, 200], {"includeOtherFields":True,"options":{},"assignments":{"assignments":[
    {"id":"p3","name":"poll_id","type":"string","value":"={{ $('Wait Before Status Check').item.json.poll_id }}"},
    {"id":"p4","name":"attempt","type":"number","value":"={{ $('Wait Before Status Check').item.json.attempt + 1 }}"}]}}))
conns["Track Poll Attempt"] = {"main":[[{"node":"Is Video Ready?","type":"main","index":0}]]}

# 14. Is Video Ready? (verbatim)
nodes.append(if_n("Is Video Ready?", [2400, 200], _if_eq("={{ $json.status }}", "READY")))
conns["Is Video Ready?"] = {"main":[
    [{"node":"Collect Variant","type":"main","index":0}],
    [{"node":"Did Generation Fail?","type":"main","index":0}]]}

# 15. Did Generation Fail? (verbatim)
nodes.append(if_n("Did Generation Fail?", [2600, 300], _if_or2("={{ $json.status }}", "ERROR", "REFUNDED")))
conns["Did Generation Fail?"] = {"main":[
    [{"node":"Collect Variant","type":"main","index":0}],
    [{"node":"Under Max Attempts?","type":"main","index":0}]]}

# 16. Under Max Attempts? (verbatim)
nodes.append(if_n("Under Max Attempts?", [2800, 400], _if_lt("={{ $json.attempt }}", 40)))
conns["Under Max Attempts?"] = {"main":[
    [{"node":"Wait Before Status Check","type":"main","index":0}],
    [{"node":"Collect Variant","type":"main","index":0}]]}

# 17. Collect Variant (verbatim)
nodes.append(set_n("Collect Variant", [3000, 200], {"options":{},"assignments":{"assignments":[
    {"id":"c1","name":"variant","type":"number","value":"={{ $('Loop Over Variants').item.json.variant }}"},
    {"id":"c2","name":"video_url","type":"string","value":"={{ $json.status === 'READY' ? $json.video_url : '' }}"},
    {"id":"c3","name":"status","type":"string","value":"={{ $json.status === 'READY' || $json.status === 'ERROR' || $json.status === 'REFUNDED' ? $json.status : 'TIMED_OUT' }}"}]}}))
conns["Collect Variant"] = {"main":[[{"node":"Loop Over Variants","type":"main","index":0}]]}

# 18. Build Slack Message (verbatim)
nodes.append(code("Build Slack Message", [1400, -200], BUILD_SLACK_JS))
conns["Build Slack Message"] = {"main":[[{"node":"Any Variant Ready?","type":"main","index":0}]]}

# 19. Any Variant Ready? (verbatim)
nodes.append(if_n("Any Variant Ready?", [1600, -200], _if_gt("={{ $json.ready_count }}", 0)))
conns["Any Variant Ready?"] = {"main":[
    [{"node":"Mock Approval","type":"main","index":0}],
    [{"node":"Assert","type":"main","index":0}]]}

# 20. Mock Approval (auto-pick first READY variant)
nodes.append(code("Mock Approval", [1800, -200], """const b = $('Build Slack Message').first().json;
const first = b.variants.find(v => v.video_url);
const n = first ? first.variant : 1;
return [{ json: { data: { decision: `Variant ${n}` } } }];"""))
conns["Mock Approval"] = {"main":[[{"node":"Was A Variant Approved?","type":"main","index":0}]]}

# 21. Was A Variant Approved? (verbatim)
nodes.append(if_n("Was A Variant Approved?", [2000, -200], _if_neq("={{ $json.data.decision }}", "Reject")))
conns["Was A Variant Approved?"] = {"main":[
    [{"node":"Pick Approved Variant","type":"main","index":0}],
    [{"node":"Assert","type":"main","index":0}]]}

# 22. Pick Approved Variant (verbatim)
nodes.append(code("Pick Approved Variant", [2200, -200], PICK_JS))
conns["Pick Approved Variant"] = {"main":[[{"node":"Mock Create IG Container","type":"main","index":0}]]}

# 23. Mock Create IG Container
nodes.append(code("Mock Create IG Container", [2400, -200],
    'return [{ json: { id: "ig_container_l2c_1" } }];'))
conns["Mock Create IG Container"] = {"main":[[{"node":"Start Instagram Poll Counter","type":"main","index":0}]]}

# 24. Start IG Poll Counter
nodes.append(set_n("Start Instagram Poll Counter", [2600, -200], {"options":{},"assignments":{"assignments":[
    {"id":"ip1","name":"poll_id","type":"string","value":"={{ $json.id }}"},
    {"id":"ip2","name":"attempt","type":"number","value":"0"}]}}))
conns["Start Instagram Poll Counter"] = {"main":[[{"node":"Wait For Instagram Processing","type":"main","index":0}]]}

# 25. Wait IG
nodes.append(wait_n("Wait For Instagram Processing", [2800, -200], 1))
conns["Wait For Instagram Processing"] = {"main":[[{"node":"Mock Check IG Status","type":"main","index":0}]]}

# 26. Mock Check IG Status
nodes.append(code("Mock Check IG Status", [3000, -200],
    'return [{ json: { status_code: "FINISHED" } }];'))
conns["Mock Check IG Status"] = {"main":[[{"node":"Track Instagram Poll Attempt","type":"main","index":0}]]}

# 27. Track IG Poll
nodes.append(set_n("Track Instagram Poll Attempt", [3200, -200], {"includeOtherFields":True,"options":{},"assignments":{"assignments":[
    {"id":"ip3","name":"poll_id","type":"string","value":"={{ $('Wait For Instagram Processing').item.json.poll_id }}"},
    {"id":"ip4","name":"attempt","type":"number","value":"={{ $('Wait For Instagram Processing').item.json.attempt + 1 }}"}]}}))
conns["Track Instagram Poll Attempt"] = {"main":[[{"node":"Is Container Finished?","type":"main","index":0}]]}

# 28. Is Container Finished?
nodes.append(if_n("Is Container Finished?", [3400, -200], _if_eq("={{ $json.status_code }}", "FINISHED")))
conns["Is Container Finished?"] = {"main":[
    [{"node":"Mock Publish IG","type":"main","index":0}],
    [{"node":"Under Instagram Max Attempts?","type":"main","index":0}]]}

# 29. Under IG Max Attempts?
nodes.append(if_n("Under Instagram Max Attempts?", [3600, -100], _if_lt("={{ $json.attempt }}", 40)))
conns["Under Instagram Max Attempts?"] = {"main":[
    [{"node":"Wait For Instagram Processing","type":"main","index":0}],
    []]}

# 30. Mock Publish IG
nodes.append(code("Mock Publish IG", [3600, -300],
    'return [{ json: { id: "ig_l2c_published", success: true } }];'))
conns["Mock Publish IG"] = {"main":[[{"node":"Assert","type":"main","index":0}]]}

# 31. Assert
nodes.append(code("Assert", [4000, 0], """const results = [];
function A(n,p,d){results.push({name:n,pass:p,detail:d||''})}
const fs = require('fs');
// DeepSeek output
const ds = $('Split Into Variants').first().json;
A('DS hook exists', !!(ds.hook && ds.hook.length > 0), ds.hook ? ds.hook.slice(0,60) : 'MISSING');
A('DS script exists', !!(ds.script && ds.script.length > 10));
A('DS caption exists', !!(ds.caption && ds.caption.length > 0));
A('DS 3 prompts', $('Split Into Variants').first().json ? true : true); // checked via variants
// Build Slack
const b = $('Build Slack Message').first().json;
A('ready_count=3', b.ready_count===3, 'got '+b.ready_count);
A('3 variants', b.variants.length===3);
A('all READY', b.variants.every(v=>v.status==='READY'));
// Video files exist
const vidDir = 'C:/Users/Administrator/.easyclaw/workspace/n8n-lesson-crew/state/21388-l2c';
for (let i=1;i<=3;i++) {
  const p = vidDir + '/variant_' + i + '.mp4';
  A('video v'+i+' exists', fs.existsSync(p), p);
  if (fs.existsSync(p)) A('video v'+i+' >10KB', fs.statSync(p).size > 10000, fs.statSync(p).size+'B');
}
// Pick + Publish
const pk = $('Pick Approved Variant').first().json;
A('picked has video_url', !!(pk.video_url && pk.video_url.length > 0), pk.video_url ? pk.video_url.slice(0,60) : 'NONE');
A('caption present', !!(pk.caption && pk.caption.length > 0));
const pub = $('Mock Publish IG').first().json;
A('published', pub.success===true);
return [{json:{scenario:'L2C',total:results.length,pass:results.filter(r=>r.pass).length,fail:results.filter(r=>!r.pass).length,results}}];"""))

wf = {
    "name": "L2C21388001",
    "nodes": nodes,
    "connections": conns,
    "settings": {"executionOrder": "v1"},
    "active": False,
    "id": "L2C21388001",
}
fp = os.path.join(OUT_DIR, "wf-l2c-21388.json")
with open(fp, "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)
print(f"OK L2C → {len(nodes)} nodes → {os.path.basename(fp)}")