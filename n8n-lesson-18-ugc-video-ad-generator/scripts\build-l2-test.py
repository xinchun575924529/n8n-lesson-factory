# -*- coding: utf-8 -*-
# build-l2-test-21388.py — L2-A unit test workflow generator for template 21388
# Faithful ports of template nodes:
#   Settings(set) / Extract Page Text(code) / Split Into Variants(code) /
#   Collect Variant(set) / Build Slack Message(code) / Pick Approved Variant(code) /
#   Start&Track Poll Counter(set x2) / Was A Variant Approved?(if) /
#   Is Video Ready?(if) / Did Generation Fail?(if) / Under Max Attempts?(if)
import json, os

OUT = os.path.join(os.path.dirname(__file__), "wf-21388-l2a-test.json")

def node(nid, name, ntype, pos, params, tv=1, extra=None):
    n = {"id": nid, "name": name, "type": ntype, "position": pos, "parameters": params, "typeVersion": tv}
    if extra: n.update(extra)
    return n

def code(nid, name, pos, js, all_items=True, extra=None):
    p = {"jsCode": js}
    if all_items: p["mode"] = "runOnceForAllItems"
    return node(nid, name, "n8n-nodes-base.code", pos, p, 2, extra)

# ---------------- verbatim template logic ----------------

# Extract Page Text — verbatim from template (only first line const html kept identical)
EXTRACT_JS = r"""
const html = $input.first().json.data || '';
const pick = (re) => (html.match(re) || [])[1] || '';
const title = pick(/<meta[^>]+property=["']og:title["'][^>]+content=["']([^"']+)/i) || pick(/<title[^>]*>([^<]*)<\/title>/i);
const description = pick(/<meta[^>]+(?:name|property)=["'](?:og:)?description["'][^>]+content=["']([^"']+)/i);
const image = pick(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)/i);
const text = html.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi, ' ').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 6000);
return [{ json: { title, description, image, text, product_url: $('Settings').first().json.product_url } }];
"""

SPLIT_JS = r"""
const o = $input.first().json.output;
return o.prompts.slice(0, 3).map((prompt, i) => ({ json: { variant: i + 1, prompt, hook: o.hook, script: o.script, caption: o.caption } }));
"""

BUILD_SLACK_JS = r"""
const v = $input.all().map(i => i.json);
const s = $('Split Into Variants').first().json;
const lines = v.map(x => `Variant ${x.variant}: ${x.video_url || 'failed (' + x.status + ')'}`).join('\n');
return [{ json: { ready_count: v.filter(x => x.video_url).length, variants: v, caption: s.caption, message: `*New UGC ad for review*\nHook: ${s.hook}\nScript: ${s.script}\n\n${lines}\n\nCaption:\n${s.caption}` } }];
"""

PICK_JS = r"""
const n = Number(String($input.first().json.data.decision).replace(/\D/g, ''));
const m = $('Build Slack Message').first().json;
const v = m.variants.find(x => x.variant === n);
if (!v || !v.video_url) throw new Error(`Variant ${n} has no video`);
return [{ json: { video_url: v.video_url, caption: m.caption } }];
"""

# Settings set — verbatim assignments
SETTINGS_PARAMS = {"options": {}, "assignments": {"assignments": [
    {"id": "a1", "name": "product_url", "type": "string", "value": "={{ $json.product_url || $json.body?.product_url }}"},
    {"id": "a2", "name": "ig_user_id", "type": "string", "value": "YOUR_IG_USER_ID"},
    {"id": "a3", "name": "graph_version", "type": "string", "value": "v21.0"}]}}

# Collect Variant set — verbatim assignments
COLLECT_PARAMS = {"options": {}, "assignments": {"assignments": [
    {"id": "c1", "name": "variant", "type": "number", "value": "={{ $('Loop Over Variants').item.json.variant }}"},
    {"id": "c2", "name": "video_url", "type": "string", "value": "={{ $json.status === 'READY' ? $json.video_url : '' }}"},
    {"id": "c3", "name": "status", "type": "string", "value": "={{ $json.status === 'READY' || $json.status === 'ERROR' || $json.status === 'REFUNDED' ? $json.status : 'TIMED_OUT' }}"}]}}

# Poll counters — verbatim assignments
START_POLL_PARAMS = {"options": {}, "assignments": {"assignments": [
    {"id": "p1", "name": "poll_id", "type": "string", "value": "={{ $json.id }}"},
    {"id": "p2", "name": "attempt", "type": "number", "value": "0"}]}}
TRACK_POLL_PARAMS = {"includeOtherFields": True, "options": {}, "assignments": {"assignments": [
    {"id": "p3", "name": "poll_id", "type": "string", "value": "={{ $('Wait Before Status Check').item.json.poll_id }}"},
    {"id": "p4", "name": "attempt", "type": "number", "value": "={{ $('Wait Before Status Check').item.json.attempt + 1 }}"}]}}

# If nodes — verbatim conditions
IF_READY = {"options": {}, "conditions": {"options": {"version": 2, "leftValue": "", "caseSensitive": True, "typeValidation": "loose"}, "combinator": "and",
    "conditions": [{"id": "i1", "operator": {"type": "string", "operation": "equals"}, "leftValue": "={{ $json.status }}", "rightValue": "READY"}]}}
IF_FAILED = {"options": {}, "conditions": {"options": {"version": 2, "leftValue": "", "caseSensitive": True, "typeValidation": "loose"}, "combinator": "or",
    "conditions": [
        {"id": "i2", "operator": {"type": "string", "operation": "equals"}, "leftValue": "={{ $json.status }}", "rightValue": "ERROR"},
        {"id": "i3", "operator": {"type": "string", "operation": "equals"}, "leftValue": "={{ $json.status }}", "rightValue": "REFUNDED"}]}}
IF_UNDER40 = {"options": {}, "conditions": {"options": {"version": 2, "leftValue": "", "caseSensitive": True, "typeValidation": "loose"}, "combinator": "and",
    "conditions": [{"id": "i4", "operator": {"type": "number", "operation": "lt"}, "leftValue": "={{ $json.attempt }}", "rightValue": 40}]}}
IF_APPROVED = {"options": {}, "conditions": {"options": {"version": 2, "leftValue": "", "caseSensitive": True, "typeValidation": "loose"}, "combinator": "and",
    "conditions": [{"id": "i5", "operator": {"type": "string", "operation": "notEquals"}, "leftValue": "={{ $json.data.decision }}", "rightValue": "Reject"}]}}

# ---------------- fixtures & asserts ----------------

FEED_SETTINGS_JS = """
return [
  { json: { product_url: 'https://store.example.com/products/mug' } },
  { json: { body: { product_url: 'https://api.example.com/hook-item' } } }
];
"""

ASSERT_SETTINGS_JS = """
const items = $input.all().map(i => i.json);
const checks = [];
checks.push({ name: 'form shape: product_url direct', pass: items[0].product_url === 'https://store.example.com/products/mug' });
checks.push({ name: 'webhook shape: body.product_url fallback', pass: items[1].product_url === 'https://api.example.com/hook-item' });
checks.push({ name: 'ig_user_id placeholder passthrough', pass: items[0].ig_user_id === 'YOUR_IG_USER_ID' });
checks.push({ name: 'graph_version pinned v21.0', pass: items[0].graph_version === 'v21.0' });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'settings', passed, total: checks.length, checks } }];
"""

FAKE_PAGE_FULL_JS = """
const html = [
 '<html><head>',
 '<meta property="og:title" content="Self-Heating Mug Pro">',
 '<meta name="description" content="Keeps coffee at 55C for 8 hours">',
 '<meta property="og:image" content="https://cdn.example.com/mug.jpg">',
 '<title>Fallback Title Should Not Win</title>',
 '<style>body{color:red}.a{display:none}</style>',
 '<script>var tracker = 1; console.log("buy now");</' + 'script>',
 '</head><body>',
 '<h1>Self-Heating Mug Pro</h1>',
 '<p>Our mug keeps your drink warm.   Free shipping   today!</p>',
 '<script>alert("second")</' + 'script>',
 '</body></html>'
].join('');
return [{ json: { data: html } }];
"""

ASSERT_EXTRACT_FULL_JS = """
const r = $input.first().json;
const checks = [];
checks.push({ name: 'og:title wins over <title>', pass: r.title === 'Self-Heating Mug Pro', got: r.title });
checks.push({ name: 'name=description picked', pass: r.description === 'Keeps coffee at 55C for 8 hours', got: r.description });
checks.push({ name: 'og:image picked', pass: r.image === 'https://cdn.example.com/mug.jpg' });
checks.push({ name: 'script removed (no tracker/alert)', pass: !/tracker|alert/.test(r.text) });
checks.push({ name: 'style removed', pass: !/display:none/.test(r.text) });
checks.push({ name: 'whitespace collapsed', pass: r.text.indexOf('   ') === -1 });
checks.push({ name: 'body text kept', pass: /Free shipping today!/.test(r.text) });
checks.push({ name: 'product_url pulled from Settings node', pass: r.product_url === 'https://store.example.com/products/mug', got: r.product_url });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'extract-full', passed, total: checks.length, checks } }];
"""

FAKE_PAGE_BARE_JS = """
const html = '<html><head><title>Bare Product</title></head><body><p>' + 'x'.repeat(9000) + '</p></body></html>';
return [{ json: { data: html } }];
"""

ASSERT_EXTRACT_BARE_JS = """
const r = $input.first().json;
const checks = [];
checks.push({ name: '<title> fallback when no og:title', pass: r.title === 'Bare Product', got: r.title });
checks.push({ name: 'missing description -> empty string', pass: r.description === '' });
checks.push({ name: 'missing og:image -> empty string', pass: r.image === '' });
checks.push({ name: 'text truncated at 6000 chars', pass: r.text.length === 6000, got: r.text.length });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'extract-bare', passed, total: checks.length, checks } }];
"""

FAKE_LLM_JS = """
return [{ json: { output: { hook: 'Cold coffee? Never again', script: 'I found this mug...', caption: 'best mug #coffee #ugc', prompts: ['unboxing shot', 'close-up pouring', 'lifestyle desk'] } } }];
"""

ASSERT_SPLIT_JS = """
const items = $input.all().map(i => i.json);
const checks = [];
checks.push({ name: '3 variants emitted', pass: items.length === 3 });
checks.push({ name: 'variant numbering 1..3', pass: items.map(x => x.variant).join(',') === '1,2,3' });
checks.push({ name: 'prompts mapped in order', pass: items[1].prompt === 'close-up pouring' });
checks.push({ name: 'hook/script/caption fanned out to every variant', pass: items.every(x => x.hook === 'Cold coffee? Never again' && x.script === 'I found this mug...' && x.caption === 'best mug #coffee #ugc') });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'split-3', passed, total: checks.length, checks } }];
"""

FAKE_LLM5_JS = """
return [{ json: { output: { hook: 'h', script: 's', caption: 'c', prompts: ['p1','p2','p3','p4','p5'] } } }];
"""

ASSERT_SPLIT5_JS = """
const items = $input.all().map(i => i.json);
const checks = [];
checks.push({ name: '5 prompts sliced to 3 (slice(0,3))', pass: items.length === 3 && items[2].prompt === 'p3' });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'split-5', passed, total: checks.length, checks } }];
"""

FAKE_LLM2_JS = """
return [{ json: { output: { hook: 'h', script: 's', caption: 'c', prompts: ['only-one', 'only-two'] } } }];
"""

ASSERT_SPLIT2_JS = """
const items = $input.all().map(i => i.json);
const checks = [];
checks.push({ name: 'only 2 prompts -> 2 items, NO guard in template (documented)', pass: items.length === 2 });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'split-2', passed, total: checks.length, checks } }];
"""

LOOP_VARIANTS_JS = """
return [{ json: { variant: 2, prompt: 'close-up pouring', hook: 'h', script: 's', caption: 'c' } }];
"""

FAKE_SISIF_JS = """
return [
  { json: { status: 'READY', video_url: 'https://cdn.sisif/v1.mp4' } },
  { json: { status: 'ERROR' } },
  { json: { status: 'PROCESSING' } }
];
"""

ASSERT_COLLECT_JS = """
const items = $input.all().map(i => i.json);
const checks = [];
const v = (st) => items.find(x => x.status === st || (st === 'TIMED_OUT' && x.status === 'TIMED_OUT'));
const ready = items.find(x => x.status === 'READY');
const err = items.find(x => x.status === 'ERROR');
const to = items.find(x => x.status === 'TIMED_OUT');
checks.push({ name: 'variant pulled from Loop Over Variants item', pass: items.every(x => x.variant === 2) });
checks.push({ name: 'READY keeps video_url', pass: ready && ready.video_url === 'https://cdn.sisif/v1.mp4' });
checks.push({ name: 'ERROR blanks video_url', pass: err && err.video_url === '' });
checks.push({ name: 'ERROR status kept verbatim', pass: !!err });
checks.push({ name: 'unknown status (PROCESSING) mapped to TIMED_OUT', pass: !!to, got: items.map(x => x.status).join(',') });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'collect-variant', passed, total: checks.length, checks } }];
"""

ASSERT_SLACK_JS = """
const r = $input.first().json;
const checks = [];
checks.push({ name: 'ready_count = 1 of 3', pass: r.ready_count === 1, got: r.ready_count });
checks.push({ name: 'variants array carried', pass: r.variants.length === 3 });
checks.push({ name: 'ready variant line has url', pass: r.message.indexOf('Variant 2: https://cdn.sisif/v1.mp4') !== -1, got: r.message });
checks.push({ name: 'failed variant line has status', pass: /failed \(ERROR\)/.test(r.message) && /failed \(TIMED_OUT\)/.test(r.message) });
checks.push({ name: 'hook+script+caption composed from Split Into Variants', pass: /Cold coffee\\? Never again/.test(r.message) && /best mug #coffee/.test(r.message) });
checks.push({ name: 'caption top-level field', pass: r.caption === 'best mug #coffee #ugc' });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'build-slack', passed, total: checks.length, checks } }];
"""

FEED_PICK_OK_JS = """
return [{ json: { data: { decision: 'Variant 2' } } }];
"""

ASSERT_PICK_OK_JS = """
const r = $input.first().json;
const checks = [];
checks.push({ name: 'decision Variant 2 -> ready video_url', pass: r.video_url === 'https://cdn.sisif/v1.mp4', got: JSON.stringify(r) });
checks.push({ name: 'caption carried', pass: r.caption === 'best mug #coffee #ugc' });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'pick-ok', passed, total: checks.length, checks } }];
"""

FEED_PICK_BAD_JS = """
return [{ json: { data: { decision: 'Variant 1' } } }];
"""

ASSERT_PICK_BAD_JS = """
const items = $input.all().map(i => i.json);
const err = items.find(x => x.error);
const checks = [];
checks.push({ name: 'picking failed variant throws "Variant 1 has no video"', pass: !!err && /Variant 1 has no video/.test(err.error.message || err.error), got: JSON.stringify(items) });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'pick-no-video', passed, total: checks.length, checks } }];
"""

FEED_APPROVAL_JS = """
return [
  { json: { data: { decision: 'Reject' } } },
  { json: { data: { decision: 'Variant 3' } } }
];
"""

ASSERT_APPROVED_TRUE_JS = """
const items = $input.all().map(i => i.json);
const checks = [];
checks.push({ name: 'non-Reject goes to true branch', pass: items.length === 1 && items[0].data.decision === 'Variant 3' });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'approved-true', passed, total: checks.length, checks } }];
"""

ASSERT_APPROVED_FALSE_JS = """
const items = $input.all().map(i => i.json);
const checks = [];
checks.push({ name: 'Reject goes to false branch', pass: items.length === 1 && items[0].data.decision === 'Reject' });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'approved-false', passed, total: checks.length, checks } }];
"""

FEED_READY_JS = """
return [
  { json: { status: 'READY' } },
  { json: { status: 'PENDING' } }
];
"""

ASSERT_READY_T = """
const items = $input.all().map(i => i.json);
const checks = [{ name: 'READY -> true branch only', pass: items.length === 1 && items[0].status === 'READY' }];
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'is-ready-true', passed, total: checks.length, checks } }];
"""

ASSERT_READY_F = """
const items = $input.all().map(i => i.json);
const checks = [{ name: 'PENDING -> false branch', pass: items.length === 1 && items[0].status === 'PENDING' }];
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'is-ready-false', passed, total: checks.length, checks } }];
"""

FEED_FAILED_JS = """
return [
  { json: { status: 'ERROR' } },
  { json: { status: 'REFUNDED' } },
  { json: { status: 'PENDING' } }
];
"""

ASSERT_FAILED_T = """
const items = $input.all().map(i => i.json);
const checks = [{ name: 'ERROR+REFUNDED both match fail branch (or combinator)', pass: items.length === 2 }];
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'gen-fail-true', passed, total: checks.length, checks } }];
"""

ASSERT_FAILED_F = """
const items = $input.all().map(i => i.json);
const checks = [{ name: 'PENDING not a failure', pass: items.length === 1 && items[0].status === 'PENDING' }];
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'gen-fail-false', passed, total: checks.length, checks } }];
"""

FAKE_SISIF_CREATE_JS = """
return [{ json: { id: 'poll-abc-123', extra: 'kept?' } }];
"""

ASSERT_POLL_JS = """
const r = $input.first().json;
const checks = [];
checks.push({ name: 'poll_id carried from create response id', pass: r.poll_id === 'poll-abc-123', got: r.poll_id });
checks.push({ name: 'attempt incremented 0 -> 1 through Wait node lineage', pass: r.attempt === 1, got: r.attempt });
checks.push({ name: 'Start Poll Counter drops non-assigned fields (no includeOtherFields in template, documented)', pass: r.extra === undefined, got: r.extra });
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'poll-counter', passed, total: checks.length, checks } }];
"""

FEED_UNDER40_JS = """
return [ { json: { attempt: 39 } }, { json: { attempt: 40 } } ];
"""

ASSERT_U40_T = """
const items = $input.all().map(i => i.json);
const checks = [{ name: 'attempt 39 < 40 -> loop continues', pass: items.length === 1 && items[0].attempt === 39 }];
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'under40-true', passed, total: checks.length, checks } }];
"""

ASSERT_U40_F = """
const items = $input.all().map(i => i.json);
const checks = [{ name: 'attempt 40 -> loop exits (Collect Variant)', pass: items.length === 1 && items[0].attempt === 40 }];
const passed = checks.filter(c => c.pass).length;
return [{ json: { suite: 'under40-false', passed, total: checks.length, checks } }];
"""

SUMMARY_JS = """
const suites = $input.all().map(i => i.json);
let passed = 0, total = 0;
for (const s of suites) { passed += s.passed; total += s.total; }
const failed = [];
for (const s of suites) for (const c of (s.checks || [])) if (!c.pass) failed.push(s.suite + ': ' + c.name + ' got=' + JSON.stringify(c.got));
return [{ json: { verdict: passed === total ? 'ALL_PASS' : 'FAIL', passed, total, failed, suites: suites.map(s => ({ suite: s.suite, passed: s.passed, total: s.total })) } }];
"""

nodes = [
    node("t1", "When Executed by Another Workflow", "n8n-nodes-base.executeWorkflowTrigger", [-1200, 400], {}, 1, {"settings": {}}),
    # Settings suite
    code("f-set", "Feed Settings", [-1000, 100], FEED_SETTINGS_JS),
    node("set", "Settings", "n8n-nodes-base.set", [-800, 100], SETTINGS_PARAMS, 3.4),
    code("a-set", "Assert Settings", [-600, 100], ASSERT_SETTINGS_JS),
    # Extract suite
    code("f-pg1", "Fake Page Full", [-1000, 300], FAKE_PAGE_FULL_JS),
    code("ex1", "Extract Page Text", [-800, 300], EXTRACT_JS, False),
    code("a-ex1", "Assert Extract Full", [-600, 300], ASSERT_EXTRACT_FULL_JS),
    code("f-pg2", "Fake Page Bare", [-1000, 480], FAKE_PAGE_BARE_JS),
    code("ex2", "Extract Page Text 2", [-800, 480], EXTRACT_JS, False),
    code("a-ex2", "Assert Extract Bare", [-600, 480], ASSERT_EXTRACT_BARE_JS),
    # Split suites
    code("f-llm", "Fake LLM Output", [-1000, 640], FAKE_LLM_JS),
    code("sp", "Split Into Variants", [-800, 640], SPLIT_JS, False),
    code("a-sp", "Assert Split", [-600, 640], ASSERT_SPLIT_JS),
    code("f-llm5", "Fake LLM Output 5", [-1000, 800], FAKE_LLM5_JS),
    code("sp5", "Split Into Variants 5", [-800, 800], SPLIT_JS, False),
    code("a-sp5", "Assert Split5", [-600, 800], ASSERT_SPLIT5_JS),
    code("f-llm2", "Fake LLM Output 2", [-1000, 960], FAKE_LLM2_JS),
    code("sp2", "Split Into Variants 2", [-800, 960], SPLIT_JS, False),
    code("a-sp2", "Assert Split2", [-600, 960], ASSERT_SPLIT2_JS),
    # Collect Variant suite
    code("lov", "Loop Over Variants", [-1000, 1140], LOOP_VARIANTS_JS, False),
    code("f-sis", "Fake Sisif Status", [-800, 1140], FAKE_SISIF_JS, False),
    node("cv", "Collect Variant", "n8n-nodes-base.set", [-600, 1140], COLLECT_PARAMS, 3.4),
    code("a-cv", "Assert Collect", [-400, 1140], ASSERT_COLLECT_JS),
    # Build Slack suite
    code("bsm", "Build Slack Message", [-200, 1140], BUILD_SLACK_JS),
    code("a-bsm", "Assert Slack Msg", [0, 1140], ASSERT_SLACK_JS),
    # Pick suites
    code("f-pk", "Feed Pick OK", [-200, 1320], FEED_PICK_OK_JS, False),
    code("pk", "Pick Approved Variant", [0, 1320], PICK_JS, False),
    code("a-pk", "Assert Pick OK", [200, 1320], ASSERT_PICK_OK_JS),
    code("f-pkb", "Feed Pick Bad", [-200, 1480], FEED_PICK_BAD_JS, False),
    code("pkb", "Pick Approved Variant Err", [0, 1480], PICK_JS, False, {"onError": "continueRegularOutput"}),
    code("a-pkb", "Assert Pick Bad", [200, 1480], ASSERT_PICK_BAD_JS),
    # Approval If
    code("f-ap", "Feed Approval", [-200, 1640], FEED_APPROVAL_JS),
    node("if-ap", "Was A Variant Approved?", "n8n-nodes-base.if", [0, 1640], IF_APPROVED, 2.2),
    code("a-apt", "Assert Approved T", [200, 1580], ASSERT_APPROVED_TRUE_JS),
    code("a-apf", "Assert Approved F", [200, 1700], ASSERT_APPROVED_FALSE_JS),
    # Ready If
    code("f-rd", "Feed Ready", [-200, 1860], FEED_READY_JS),
    node("if-rd", "Is Video Ready?", "n8n-nodes-base.if", [0, 1860], IF_READY, 2.2),
    code("a-rdt", "Assert Ready T", [200, 1800], ASSERT_READY_T),
    code("a-rdf", "Assert Ready F", [200, 1920], ASSERT_READY_F),
    # Fail If
    code("f-fl", "Feed Failed", [-200, 2080], FEED_FAILED_JS),
    node("if-fl", "Did Generation Fail?", "n8n-nodes-base.if", [0, 2080], IF_FAILED, 2.2),
    code("a-flt", "Assert Fail T", [200, 2020], ASSERT_FAILED_T),
    code("a-flf", "Assert Fail F", [200, 2140], ASSERT_FAILED_F),
    # Poll counter chain: fake create -> Start Poll Counter -> (named) Wait Before Status Check -> Track Poll Attempt
    code("f-cr", "Fake Sisif Create", [-200, 2300], FAKE_SISIF_CREATE_JS, False),
    node("spc", "Start Poll Counter", "n8n-nodes-base.set", [0, 2300], START_POLL_PARAMS, 3.4),
    node("wbs", "Wait Before Status Check", "n8n-nodes-base.set", [200, 2300], {"includeOtherFields": True, "options": {}, "assignments": {"assignments": []}}, 3.4),
    node("tpa", "Track Poll Attempt", "n8n-nodes-base.set", [400, 2300], TRACK_POLL_PARAMS, 3.4),
    code("a-poll", "Assert Poll", [600, 2300], ASSERT_POLL_JS),
    # Under 40 If
    code("f-u40", "Feed Under40", [-200, 2480], FEED_UNDER40_JS),
    node("if-u40", "Under Max Attempts?", "n8n-nodes-base.if", [0, 2480], IF_UNDER40, 2.2),
    code("a-u40t", "Assert U40 T", [200, 2420], ASSERT_U40_T),
    code("a-u40f", "Assert U40 F", [200, 2540], ASSERT_U40_F),
    # Summary
    code("sum", "Summary", [900, 1200], SUMMARY_JS),
]

connections = {}
def add(src, dst, outIdx=0):
    c = connections.setdefault(src, {"main": []})
    while len(c["main"]) <= outIdx: c["main"].append([])
    c["main"][outIdx].append({"node": dst, "type": "main", "index": 0})

add("When Executed by Another Workflow", "Feed Settings")
add("When Executed by Another Workflow", "Fake Page Full")
add("When Executed by Another Workflow", "Fake Page Bare")
add("When Executed by Another Workflow", "Fake LLM Output")
add("When Executed by Another Workflow", "Fake LLM Output 5")
add("When Executed by Another Workflow", "Fake LLM Output 2")
add("When Executed by Another Workflow", "Loop Over Variants")
add("When Executed by Another Workflow", "Feed Approval")
add("When Executed by Another Workflow", "Feed Ready")
add("When Executed by Another Workflow", "Feed Failed")
add("When Executed by Another Workflow", "Fake Sisif Create")
add("When Executed by Another Workflow", "Feed Under40")

add("Feed Settings", "Settings"); add("Settings", "Assert Settings")
add("Fake Page Full", "Extract Page Text"); add("Extract Page Text", "Assert Extract Full")
add("Fake Page Bare", "Extract Page Text 2"); add("Extract Page Text 2", "Assert Extract Bare")
add("Fake LLM Output", "Split Into Variants"); add("Split Into Variants", "Assert Split")
add("Fake LLM Output 5", "Split Into Variants 5"); add("Split Into Variants 5", "Assert Split5")
add("Fake LLM Output 2", "Split Into Variants 2"); add("Split Into Variants 2", "Assert Split2")
add("Loop Over Variants", "Fake Sisif Status"); add("Fake Sisif Status", "Collect Variant")
add("Collect Variant", "Build Slack Message")
add("Collect Variant", "Assert Collect")
add("Build Slack Message", "Assert Slack Msg")
add("Assert Slack Msg", "Feed Pick OK")
add("Feed Pick OK", "Pick Approved Variant"); add("Pick Approved Variant", "Assert Pick OK")
add("Assert Pick OK", "Feed Pick Bad")
add("Feed Pick Bad", "Pick Approved Variant Err"); add("Pick Approved Variant Err", "Assert Pick Bad")
add("Feed Approval", "Was A Variant Approved?")
add("Was A Variant Approved?", "Assert Approved T", 0); add("Was A Variant Approved?", "Assert Approved F", 1)
add("Feed Ready", "Is Video Ready?")
add("Is Video Ready?", "Assert Ready T", 0); add("Is Video Ready?", "Assert Ready F", 1)
add("Feed Failed", "Did Generation Fail?")
add("Did Generation Fail?", "Assert Fail T", 0); add("Did Generation Fail?", "Assert Fail F", 1)
add("Fake Sisif Create", "Start Poll Counter"); add("Start Poll Counter", "Wait Before Status Check")
add("Wait Before Status Check", "Track Poll Attempt"); add("Track Poll Attempt", "Assert Poll")
add("Feed Under40", "Under Max Attempts?")
add("Under Max Attempts?", "Assert U40 T", 0); add("Under Max Attempts?", "Assert U40 F", 1)

for a in ["Assert Settings", "Assert Extract Full", "Assert Extract Bare", "Assert Split", "Assert Split5",
          "Assert Split2", "Assert Collect", "Assert Slack Msg", "Assert Pick OK", "Assert Pick Bad",
          "Assert Approved T", "Assert Approved F", "Assert Ready T", "Assert Ready F",
          "Assert Fail T", "Assert Fail F", "Assert Poll", "Assert U40 T", "Assert U40 F"]:
    add(a, "Summary")

wf = {"id": "L2Test213880001", "name": "L2Test213880001", "nodes": nodes,
      "connections": connections, "settings": {}, "pinData": {}}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=1)
print("written", OUT, len(nodes), "nodes")