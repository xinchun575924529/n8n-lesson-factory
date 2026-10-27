# -*- coding: utf-8 -*-
"""L2-B mock full-chain generator for 21388. 5 scenarios S1-S5."""
import json, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "workflows", "l2-mock-21388")
os.makedirs(OUT, exist_ok=True)

# ---- verbatim template logic ----
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

MOCK_HTML = '<html><head><meta property="og:title" content="CoolGadget Pro - Smart Home Hub"><meta property="og:description" content="Control your entire home with one device. Voice control, app, automation."><meta property="og:image" content="https://example.com/product.jpg"><title>CoolGadget Pro</title></head><body><h1>CoolGadget Pro</h1><p>The ultimate smart home hub. Control lights, temperature, security cameras and more from one sleek device.</p><span>$79.99</span></body></html>'

MOCK_LLM = json.dumps({"output":{"hook":"Stop scrolling! This gadget controls your entire home","script":"I was skeptical but this little box changed my life. Lights, thermostat, cameras - all in one app. Setup took literally 2 minutes.","caption":"Game changer for smart homes! #smarthome #tech #gadget #automation #musthave","prompts":["Close-up unboxing of sleek white smart home hub on wooden table, natural morning light, authentic feel","Person tapping smartphone app to control living room lights, cozy evening setting, genuine smile","Wide shot of modern living room with multiple smart devices syncing, lifestyle context, warm tones"]}})

# ---- verbatim node params ----
def _settings():
    return {"options":{},"assignments":{"assignments":[
        {"id":"a1","name":"product_url","type":"string","value":"={{ $json.product_url || $json.body?.product_url }}"},
        {"id":"a2","name":"ig_user_id","type":"string","value":"MOCK_IG_USER"},
        {"id":"a3","name":"graph_version","type":"string","value":"v21.0"}]}}

def _collect():
    return {"options":{},"assignments":{"assignments":[
        {"id":"c1","name":"variant","type":"number","value":"={{ $('Loop Over Variants').item.json.variant }}"},
        {"id":"c2","name":"video_url","type":"string","value":"={{ $json.status === 'READY' ? $json.video_url : '' }}"},
        {"id":"c3","name":"status","type":"string","value":"={{ $json.status === 'READY' || $json.status === 'ERROR' || $json.status === 'REFUNDED' ? $json.status : 'TIMED_OUT' }}"}]}}

def _start_poll():
    return {"options":{},"assignments":{"assignments":[
        {"id":"p1","name":"poll_id","type":"string","value":"={{ $json.id }}"},
        {"id":"p2","name":"attempt","type":"number","value":"0"}]}}

def _track_poll():
    return {"includeOtherFields":True,"options":{},"assignments":{"assignments":[
        {"id":"p3","name":"poll_id","type":"string","value":"={{ $('Wait Before Status Check').item.json.poll_id }}"},
        {"id":"p4","name":"attempt","type":"number","value":"={{ $('Wait Before Status Check').item.json.attempt + 1 }}"}]}}

def _start_ig_poll():
    return {"options":{},"assignments":{"assignments":[
        {"id":"ip1","name":"poll_id","type":"string","value":"={{ $json.id }}"},
        {"id":"ip2","name":"attempt","type":"number","value":"0"}]}}

def _track_ig_poll():
    return {"includeOtherFields":True,"options":{},"assignments":{"assignments":[
        {"id":"ip3","name":"poll_id","type":"string","value":"={{ $('Wait For Instagram Processing').item.json.poll_id }}"},
        {"id":"ip4","name":"attempt","type":"number","value":"={{ $('Wait For Instagram Processing').item.json.attempt + 1 }}"}]}}

def _if_eq(l, r):
    return {"options":{},"conditions":{"options":{"version":2,"leftValue":"","caseSensitive":True,"typeValidation":"loose"},"combinator":"and","conditions":[{"id":"c1","operator":{"type":"string","operation":"equals"},"leftValue":l,"rightValue":r}]}}

def _if_or2(l, r1, r2):
    return {"options":{},"conditions":{"options":{"version":2,"leftValue":"","caseSensitive":True,"typeValidation":"loose"},"combinator":"or","conditions":[
        {"id":"c1","operator":{"type":"string","operation":"equals"},"leftValue":l,"rightValue":r1},
        {"id":"c2","operator":{"type":"string","operation":"equals"},"leftValue":l,"rightValue":r2}]}}

def _if_lt(l, r):
    return {"options":{},"conditions":{"options":{"version":2,"leftValue":"","caseSensitive":True,"typeValidation":"loose"},"combinator":"and","conditions":[{"id":"c1","operator":{"type":"number","operation":"lt"},"leftValue":l,"rightValue":r}]}}

def _if_gt(l, r):
    return {"options":{},"conditions":{"options":{"version":2,"leftValue":"","caseSensitive":True,"typeValidation":"loose"},"combinator":"and","conditions":[{"id":"c1","operator":{"type":"number","operation":"gt"},"leftValue":l,"rightValue":r}]}}

def _if_neq(l, r):
    return {"options":{},"conditions":{"options":{"version":2,"leftValue":"","caseSensitive":True,"typeValidation":"loose"},"combinator":"and","conditions":[{"id":"c1","operator":{"type":"string","operation":"notEquals"},"leftValue":l,"rightValue":r}]}}

# ---- node builders ----
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

def sib(name, pos):
    return N(name, "n8n-nodes-base.splitInBatches", pos, {"options": {}}, 3)

# ---- scenario configs ----
# sisif_js: mock Check Video Status code. Uses variant from Loop, attempt from $json.attempt
# approval: decision string for mock Slack approval
# ig_status: status_code for mock IG container check
# assert_fn: JS that returns assertion results

SCENARIOS = {}

# S1: Full success — all 3 READY first try, approve V2, IG FINISHED
SCENARIOS["S1"] = dict(
    sisif_js="""const v = $('Loop Over Variants').item.json.variant;
return [{ json: { status: 'READY', video_url: `https://mock.sisif.ai/video_v${v}.mp4`, id: $json.poll_id } }];""",
    approval="Variant 2",
    ig_status_js="""return [{ json: { status_code: 'FINISHED' } }];""",
    assert_js="""const results = [];
function A(n,p,d){results.push({name:n,pass:p,detail:d||''})}
const b=$('Build Slack Message').first().json;
const pk=$('Pick Approved Variant').first().json;
const pub=$('Mock Publish IG').first().json;
A('ready_count=3', b.ready_count===3, 'got '+b.ready_count);
A('3 variants', b.variants.length===3);
A('all READY', b.variants.every(v=>v.status==='READY'));
A('picked V2', pk.video_url.includes('v2'), pk.video_url);
A('caption present', pk.caption.length>0);
A('published', pub.success===true);
A('publish id', !!pub.id);
return [{json:{scenario:'S1',total:results.length,pass:results.filter(r=>r.pass).length,fail:results.filter(r=>!r.pass).length,results}}];""",
    end="publish")

# S2: Partial 2/3 — V1=READY, V2=ERROR, V3=PROCESSING×2 then READY
SCENARIOS["S2"] = dict(
    sisif_js="""const v = $('Loop Over Variants').item.json.variant;
const a = $json.attempt;
let status, video_url = '';
if (v === 1) { status = 'READY'; video_url = 'https://mock.sisif.ai/v1.mp4'; }
else if (v === 2) { status = 'ERROR'; }
else { if (a < 2) { status = 'PROCESSING'; } else { status = 'READY'; video_url = 'https://mock.sisif.ai/v3.mp4'; } }
return [{ json: { status, video_url, id: $json.poll_id } }];""",
    approval="Variant 1",
    ig_status_js="""return [{ json: { status_code: 'FINISHED' } }];""",
    assert_js="""const results = [];
function A(n,p,d){results.push({name:n,pass:p,detail:d||''})}
const b=$('Build Slack Message').first().json;
const pk=$('Pick Approved Variant').first().json;
const pub=$('Mock Publish IG').first().json;
A('ready_count=2', b.ready_count===2, 'got '+b.ready_count);
A('V1 READY', b.variants.find(v=>v.variant===1).status==='READY');
A('V2 ERROR', b.variants.find(v=>v.variant===2).status==='ERROR');
A('V3 READY', b.variants.find(v=>v.variant===3).status==='READY');
A('V2 no video', b.variants.find(v=>v.variant===2).video_url==='');
A('picked V1', pk.video_url.includes('v1'), pk.video_url);
A('published', pub.success===true);
return [{json:{scenario:'S2',total:results.length,pass:results.filter(r=>r.pass).length,fail:results.filter(r=>!r.pass).length,results}}];""",
    end="publish")

# S3: All fail — all ERROR → stopAndError path
SCENARIOS["S3"] = dict(
    sisif_js="""const v = $('Loop Over Variants').item.json.variant;
return [{ json: { status: 'ERROR', video_url: '', id: $json.poll_id } }];""",
    approval=None,
    ig_status_js=None,
    assert_js="""const results = [];
function A(n,p,d){results.push({name:n,pass:p,detail:d||''})}
const b=$('Build Slack Message').first().json;
const err=$('Mock All Failed').first().json;
A('ready_count=0', b.ready_count===0, 'got '+b.ready_count);
A('all ERROR', b.variants.every(v=>v.status==='ERROR'));
A('error message', err.error.includes('None of the 3'), err.error);
A('lists variants', err.error.includes('Variant 1') && err.error.includes('Variant 3'));
return [{json:{scenario:'S3',total:results.length,pass:results.filter(r=>r.pass).length,fail:results.filter(r=>!r.pass).length,results}}];""",
    end="all_fail")

# S4: Human reject — 2 READY, reject
SCENARIOS["S4"] = dict(
    sisif_js="""const v = $('Loop Over Variants').item.json.variant;
if (v <= 2) return [{ json: { status: 'READY', video_url: `https://mock.sisif.ai/v${v}.mp4`, id: $json.poll_id } }];
return [{ json: { status: 'ERROR', video_url: '', id: $json.poll_id } }];""",
    approval="Reject",
    ig_status_js=None,
    assert_js="""const results = [];
function A(n,p,d){results.push({name:n,pass:p,detail:d||''})}
const b=$('Build Slack Message').first().json;
const rj=$('Mock Reject End').first().json;
A('ready_count=2', b.ready_count===2, 'got '+b.ready_count);
A('decision=Reject', rj.decision==='Reject');
A('no IG publish', rj.rejected===true);
return [{json:{scenario:'S4',total:results.length,pass:results.filter(r=>r.pass).length,fail:results.filter(r=>!r.pass).length,results}}];""",
    end="reject")

# S5: IG timeout — 2 READY, approve V1, IG never finishes
SCENARIOS["S5"] = dict(
    sisif_js="""const v = $('Loop Over Variants').item.json.variant;
if (v <= 2) return [{ json: { status: 'READY', video_url: `https://mock.sisif.ai/v${v}.mp4`, id: $json.poll_id } }];
return [{ json: { status: 'ERROR', video_url: '', id: $json.poll_id } }];""",
    approval="Variant 1",
    ig_status_js="""return [{ json: { status_code: 'IN_PROGRESS' } }];""",
    assert_js="""const results = [];
function A(n,p,d){results.push({name:n,pass:p,detail:d||''})}
const b=$('Build Slack Message').first().json;
const pk=$('Pick Approved Variant').first().json;
const to=$('Mock IG Timeout').first().json;
A('ready_count=2', b.ready_count===2, 'got '+b.ready_count);
A('picked V1', pk.video_url.includes('v1'));
A('IG timeout error', to.error.includes('did not finish'), to.error);
A('40 attempts', to.error.includes('40'));
return [{json:{scenario:'S5',total:results.length,pass:results.filter(r=>r.pass).length,fail:results.filter(r=>!r.pass).length,results}}];""",
    end="ig_timeout")

# ---- build workflow per scenario ----
for sid, cfg in SCENARIOS.items():
    _nid[0] = 0
    nodes = []
    conns = {}

    # 0. Manual Trigger
    nodes.append(N("Manual Trigger", "n8n-nodes-base.manualTrigger", [-200, 0], {}, 1))
    conns["Manual Trigger"] = {"main":[[{"node":"Mock Input","type":"main","index":0}]]}

    # 1. Mock Input
    nodes.append(N("Mock Input", "n8n-nodes-base.set", [0, 0], {"options":{},"assignments":{"assignments":[
        {"id":"i1","name":"product_url","type":"string","value":"https://example.com/products/coolgadget-pro"}]}}, 3.4))
    conns["Mock Input"] = {"main":[[{"node":"Settings","type":"main","index":0}]]}

    # 2. Settings (verbatim)
    nodes.append(set_n("Settings", [200, 0], _settings()))
    conns["Settings"] = {"main":[[{"node":"Mock Fetch Page","type":"main","index":0}]]}

    # 3. Mock Fetch Page (replaces HTTP)
    nodes.append(code("Mock Fetch Page", [400, 0],
        f'return [{{ json: {{ data: {json.dumps(MOCK_HTML)} }} }}];'))
    conns["Mock Fetch Page"] = {"main":[[{"node":"Extract Page Text","type":"main","index":0}]]}

    # 4. Extract Page Text (verbatim)
    nodes.append(code("Extract Page Text", [600, 0], EXTRACT_JS))
    conns["Extract Page Text"] = {"main":[[{"node":"Mock LLM","type":"main","index":0}]]}

    # 5. Mock LLM (replaces chainLlm + outputParser)
    nodes.append(code("Mock LLM", [800, 0],
        f'return [{{ json: {MOCK_LLM} }}];'))
    conns["Mock LLM"] = {"main":[[{"node":"Split Into Variants","type":"main","index":0}]]}

    # 6. Split Into Variants (verbatim)
    nodes.append(code("Split Into Variants", [1000, 0], SPLIT_JS))
    conns["Split Into Variants"] = {"main":[[{"node":"Loop Over Variants","type":"main","index":0}]]}

    # 7. Loop Over Variants (SplitInBatches, verbatim)
    nodes.append(sib("Loop Over Variants", [1200, 0]))
    # output 0 = done → Build Slack Message; output 1 = loop body → Mock Create Sisif
    conns["Loop Over Variants"] = {"main":[
        [{"node":"Build Slack Message","type":"main","index":0}],
        [{"node":"Mock Create Sisif","type":"main","index":0}]]}

    # 8. Mock Create Sisif Video
    nodes.append(code("Mock Create Sisif", [1400, 200],
        "const v = $json.variant;\nreturn [{ json: { id: `poll_v${v}` } }];"))
    conns["Mock Create Sisif"] = {"main":[[{"node":"Start Poll Counter","type":"main","index":0}]]}

    # 9. Start Poll Counter (verbatim)
    nodes.append(set_n("Start Poll Counter", [1600, 200], _start_poll()))
    conns["Start Poll Counter"] = {"main":[[{"node":"Wait Before Status Check","type":"main","index":0}]]}

    # 10. Wait (1s instead of 15s)
    nodes.append(wait_n("Wait Before Status Check", [1800, 200], 1))
    conns["Wait Before Status Check"] = {"main":[[{"node":"Mock Check Video Status","type":"main","index":0}]]}

    # 11. Mock Check Video Status
    nodes.append(code("Mock Check Video Status", [2000, 200], cfg["sisif_js"]))
    conns["Mock Check Video Status"] = {"main":[[{"node":"Track Poll Attempt","type":"main","index":0}]]}

    # 12. Track Poll Attempt (verbatim)
    nodes.append(set_n("Track Poll Attempt", [2200, 200], _track_poll()))
    conns["Track Poll Attempt"] = {"main":[[{"node":"Is Video Ready?","type":"main","index":0}]]}

    # 13. Is Video Ready? (verbatim)
    nodes.append(if_n("Is Video Ready?", [2400, 200], _if_eq("={{ $json.status }}", "READY")))
    conns["Is Video Ready?"] = {"main":[
        [{"node":"Collect Variant","type":"main","index":0}],
        [{"node":"Did Generation Fail?","type":"main","index":0}]]}

    # 14. Did Generation Fail? (verbatim)
    nodes.append(if_n("Did Generation Fail?", [2600, 300], _if_or2("={{ $json.status }}", "ERROR", "REFUNDED")))
    conns["Did Generation Fail?"] = {"main":[
        [{"node":"Collect Variant","type":"main","index":0}],
        [{"node":"Under Max Attempts?","type":"main","index":0}]]}

    # 15. Under Max Attempts? (verbatim)
    nodes.append(if_n("Under Max Attempts?", [2800, 400], _if_lt("={{ $json.attempt }}", 40)))
    conns["Under Max Attempts?"] = {"main":[
        [{"node":"Wait Before Status Check","type":"main","index":0}],
        [{"node":"Collect Variant","type":"main","index":0}]]}

    # 16. Collect Variant (verbatim)
    nodes.append(set_n("Collect Variant", [3000, 200], _collect()))
    conns["Collect Variant"] = {"main":[[{"node":"Loop Over Variants","type":"main","index":0}]]}

    # 17. Build Slack Message (verbatim)
    nodes.append(code("Build Slack Message", [1400, -200], BUILD_SLACK_JS))
    conns["Build Slack Message"] = {"main":[[{"node":"Any Variant Ready?","type":"main","index":0}]]}

    # 18. Any Variant Ready? (verbatim)
    nodes.append(if_n("Any Variant Ready?", [1600, -200], _if_gt("={{ $json.ready_count }}", 0)))

    # ---- scenario-specific endings ----
    if cfg["end"] == "all_fail":
        # S3: Any Variant Ready? false → Mock All Failed → Assert
        conns["Any Variant Ready?"] = {"main":[
            [],  # true → no approval needed
            [{"node":"Mock All Failed","type":"main","index":0}]]}
        # Mock All Failed (replaces stopAndError)
        nodes.append(code("Mock All Failed", [1800, -100],
            """const v = $('Build Slack Message').first().json;
return [{ json: { error: `None of the 3 Sisif variants finished: ${v.variants.map(x=>'Variant '+x.variant+' '+x.status).join(', ')}` } }];"""))
        conns["Mock All Failed"] = {"main":[[{"node":"Assert","type":"main","index":0}]]}

    elif cfg["end"] == "reject":
        # S4: Any Variant Ready? true → Mock Approval(Reject) → Was Approved? false → Mock Reject End → Assert
        conns["Any Variant Ready?"] = {"main":[
            [{"node":"Mock Approval","type":"main","index":0}],
            []]}
        nodes.append(code("Mock Approval", [1800, -200],
            'return [{ json: { data: { decision: "Reject" } } }];'))
        conns["Mock Approval"] = {"main":[[{"node":"Was A Variant Approved?","type":"main","index":0}]]}
        nodes.append(if_n("Was A Variant Approved?", [2000, -200], _if_neq("={{ $json.data.decision }}", "Reject")))
        conns["Was A Variant Approved?"] = {"main":[
            [],  # true → Pick (not reached in reject)
            [{"node":"Mock Reject End","type":"main","index":0}]]}
        nodes.append(code("Mock Reject End", [2200, -100],
            """return [{ json: { decision: 'Reject', rejected: true } }];"""))
        conns["Mock Reject End"] = {"main":[[{"node":"Assert","type":"main","index":0}]]}

    elif cfg["end"] == "ig_timeout":
        # S5: normal flow until IG polling → never finishes → timeout
        conns["Any Variant Ready?"] = {"main":[
            [{"node":"Mock Approval","type":"main","index":0}],
            []]}
        nodes.append(code("Mock Approval", [1800, -200],
            f'return [{{ json: {{ data: {{ decision: "{cfg["approval"]}" }} }} }}];'))
        conns["Mock Approval"] = {"main":[[{"node":"Was A Variant Approved?","type":"main","index":0}]]}
        nodes.append(if_n("Was A Variant Approved?", [2000, -200], _if_neq("={{ $json.data.decision }}", "Reject")))
        conns["Was A Variant Approved?"] = {"main":[
            [{"node":"Pick Approved Variant","type":"main","index":0}],
            []]}
        nodes.append(code("Pick Approved Variant", [2200, -200], PICK_JS))
        conns["Pick Approved Variant"] = {"main":[[{"node":"Mock Create IG Container","type":"main","index":0}]]}
        nodes.append(code("Mock Create IG Container", [2400, -200],
            'return [{ json: { id: "ig_container_mock_1" } }];'))
        conns["Mock Create IG Container"] = {"main":[[{"node":"Start Instagram Poll Counter","type":"main","index":0}]]}
        nodes.append(set_n("Start Instagram Poll Counter", [2600, -200], _start_ig_poll()))
        conns["Start Instagram Poll Counter"] = {"main":[[{"node":"Wait For Instagram Processing","type":"main","index":0}]]}
        nodes.append(wait_n("Wait For Instagram Processing", [2800, -200], 1))
        conns["Wait For Instagram Processing"] = {"main":[[{"node":"Mock Check IG Status","type":"main","index":0}]]}
        nodes.append(code("Mock Check IG Status", [3000, -200], cfg["ig_status_js"]))
        conns["Mock Check IG Status"] = {"main":[[{"node":"Track Instagram Poll Attempt","type":"main","index":0}]]}
        nodes.append(set_n("Track Instagram Poll Attempt", [3200, -200], _track_ig_poll()))
        conns["Track Instagram Poll Attempt"] = {"main":[[{"node":"Is Container Finished?","type":"main","index":0}]]}
        nodes.append(if_n("Is Container Finished?", [3400, -200], _if_eq("={{ $json.status_code }}", "FINISHED")))
        conns["Is Container Finished?"] = {"main":[
            [],  # true → Publish (not reached in timeout)
            [{"node":"Under Instagram Max Attempts?","type":"main","index":0}]]}
        nodes.append(if_n("Under Instagram Max Attempts?", [3600, -100], _if_lt("={{ $json.attempt }}", 40)))
        conns["Under Instagram Max Attempts?"] = {"main":[
            [{"node":"Wait For Instagram Processing","type":"main","index":0}],
            [{"node":"Mock IG Timeout","type":"main","index":0}]]}
        nodes.append(code("Mock IG Timeout", [3800, 0],
            'return [{ json: { error: "Instagram did not finish processing the Reel after 40 status checks" } }];'))
        conns["Mock IG Timeout"] = {"main":[[{"node":"Assert","type":"main","index":0}]]}

    else:  # publish (S1, S2)
        conns["Any Variant Ready?"] = {"main":[
            [{"node":"Mock Approval","type":"main","index":0}],
            []]}
        nodes.append(code("Mock Approval", [1800, -200],
            f'return [{{ json: {{ data: {{ decision: "{cfg["approval"]}" }} }} }}];'))
        conns["Mock Approval"] = {"main":[[{"node":"Was A Variant Approved?","type":"main","index":0}]]}
        nodes.append(if_n("Was A Variant Approved?", [2000, -200], _if_neq("={{ $json.data.decision }}", "Reject")))
        conns["Was A Variant Approved?"] = {"main":[
            [{"node":"Pick Approved Variant","type":"main","index":0}],
            []]}
        nodes.append(code("Pick Approved Variant", [2200, -200], PICK_JS))
        conns["Pick Approved Variant"] = {"main":[[{"node":"Mock Create IG Container","type":"main","index":0}]]}
        nodes.append(code("Mock Create IG Container", [2400, -200],
            'return [{ json: { id: "ig_container_mock_1" } }];'))
        conns["Mock Create IG Container"] = {"main":[[{"node":"Start Instagram Poll Counter","type":"main","index":0}]]}
        nodes.append(set_n("Start Instagram Poll Counter", [2600, -200], _start_ig_poll()))
        conns["Start Instagram Poll Counter"] = {"main":[[{"node":"Wait For Instagram Processing","type":"main","index":0}]]}
        nodes.append(wait_n("Wait For Instagram Processing", [2800, -200], 1))
        conns["Wait For Instagram Processing"] = {"main":[[{"node":"Mock Check IG Status","type":"main","index":0}]]}
        nodes.append(code("Mock Check IG Status", [3000, -200], cfg["ig_status_js"]))
        conns["Mock Check IG Status"] = {"main":[[{"node":"Track Instagram Poll Attempt","type":"main","index":0}]]}
        nodes.append(set_n("Track Instagram Poll Attempt", [3200, -200], _track_ig_poll()))
        conns["Track Instagram Poll Attempt"] = {"main":[[{"node":"Is Container Finished?","type":"main","index":0}]]}
        nodes.append(if_n("Is Container Finished?", [3400, -200], _if_eq("={{ $json.status_code }}", "FINISHED")))
        conns["Is Container Finished?"] = {"main":[
            [{"node":"Mock Publish IG","type":"main","index":0}],
            [{"node":"Under Instagram Max Attempts?","type":"main","index":0}]]}
        nodes.append(if_n("Under Instagram Max Attempts?", [3600, -100], _if_lt("={{ $json.attempt }}", 40)))
        conns["Under Instagram Max Attempts?"] = {"main":[
            [{"node":"Wait For Instagram Processing","type":"main","index":0}],
            []]}  # timeout → not reached in S1/S2
        nodes.append(code("Mock Publish IG", [3600, -300],
            'return [{ json: { id: "ig_published_1", success: true } }];'))
        conns["Mock Publish IG"] = {"main":[[{"node":"Assert","type":"main","index":0}]]}

    # Assert node
    nodes.append(code("Assert", [4000, 0], cfg["assert_js"]))

    wf = {
        "name": f"L2Mock21388{sid}01",
        "nodes": nodes,
        "connections": conns,
        "settings": {"executionOrder": "v1"},
        "active": False,
        "id": f"L2Mock21388{sid}01",
    }
    fp = os.path.join(OUT, f"wf-mock-21388-{sid}.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    print(f"OK {sid} → {len(nodes)} nodes → {os.path.basename(fp)}")

print("DONE")