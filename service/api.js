import http from "node:http";
import { getSeedState } from "./data.js";
import { csvToEvents, processEvents } from "./core.js";
import { buildDiagnosticReport } from "./report.js";

const PORT = Number(process.env.PORT || 3100);
let state = getSeedState();

function json(res, status, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(status, { "content-type": "application/json; charset=utf-8", "access-control-allow-origin": "*" });
  res.end(body);
}

function html() {
  return `<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>現場データOS</title><style>
  :root{color-scheme:dark;font-family:Inter,system-ui,sans-serif}body{margin:0;background:#0b0d10;color:#f4f7fa}main{max-width:1180px;margin:auto;padding:24px}.grid{display:grid;grid-template-columns:1.35fr .8fr;gap:16px}.card{background:#14181d;border:1px solid #28303a;border-radius:16px;padding:18px;box-shadow:0 8px 24px #0004}.kpi{font-size:38px;font-weight:800}.muted{color:#98a4b3}.tag{display:inline-block;padding:4px 8px;border-radius:999px;background:#1f2933;margin-right:6px;font-size:12px}.danger{color:#ff7b72}.row{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid #242b33}.top{font-size:22px;font-weight:750}.btn{background:#f0f6fc;color:#0b0d10;border:0;border-radius:10px;padding:10px 14px;font-weight:700;cursor:pointer}.mono{font-family:ui-monospace,SFMono-Regular,monospace}.sim{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.sim .card{padding:12px}@media(max-width:800px){.grid{grid-template-columns:1fr}.sim{grid-template-columns:repeat(2,1fr)}}
</style></head><body><main><div style="display:flex;justify-content:space-between;align-items:end;margin-bottom:18px"><div><div class="muted">DECISION INTELLIGENCE</div><h1 style="margin:.2em 0">今日、何を決めるか。</h1><div class="muted">記録は今のまま。判断の優先順位だけ出す。</div></div><div><button class="btn" onclick="downloadReport()">診断レポート</button><button class="btn" onclick="location.reload()" style="margin-left:8px">再計算</button></div></div><div class="grid"><section class="card"><div class="muted">TODAY'S DECISION</div><div id="today" class="top">読み込み中…</div><div id="why" class="muted" style="margin-top:8px"></div><div style="margin-top:18px" id="breakdown"></div></section><section class="card"><div class="muted">CURRENT PRESSURE</div><div id="pressure" class="kpi">—</div><div class="muted">Top Decision Debt pressure</div><div style="margin-top:18px"><span class="tag" id="site"></span><span class="tag" id="blocked"></span></div></section></div><div class="grid" style="margin-top:16px"><section class="card"><div class="muted">DECISION DEBT</div><div id="list"></div></section><section class="card"><div class="muted">30-DAY COUNTERFACTUAL</div><div class="sim" id="sim"></div><div class="muted" style="margin-top:12px">「AIがそう言った」ではなく、同じルールで再現した結果。</div></section></div><div class="card" style="margin-top:16px"><div class="muted">DATA INGEST</div><pre id="ingest" class="mono" style="white-space:pre-wrap">CSV import API: POST /api/import-csv</pre></div></main><script>
let cached;async function load(){cached=await fetch('/api/state?role=supervisor').then(r=>r.json());const d=cached.decision_debts[0];document.querySelector('#today').textContent=d.title;document.querySelector('#why').textContent=d.reason;document.querySelector('#pressure').textContent=d.pressure_total;document.querySelector('#site').textContent=d.site_id;document.querySelector('#blocked').textContent='下流 '+d.downstream_block_count+'件';document.querySelector('#breakdown').innerHTML=Object.entries(d.breakdown).map(([k,v])=>'<div class="row"><span>'+k+'</span><span>'+v.toFixed(1)+'</span></div>').join('');document.querySelector('#list').innerHTML=cached.decision_debts.map(x=>'<div class="row"><div><b>#'+x.rank+' '+x.title+'</b><div class="muted">'+x.delay_days+'日 / 下流'+x.downstream_block_count+'件 / 依存'+x.dependency_depth+'段</div></div><b class="'+(x.pressure_total>=70?'danger':'')+'">'+x.pressure_total+'</b></div>').join('');document.querySelector('#sim').innerHTML=cached.simulation.map(x=>'<div class="card"><b>'+x.label+'</b><div class="kpi" style="font-size:24px">'+x.explosion_events+'</div><div class="muted">爆発イベント</div><div class="muted">残件 '+x.unresolved_count_30d+'</div></div>').join('')}async function downloadReport(){const r=await fetch('/api/report?site=demo-site&customer=demo-customer').then(r=>r.json());const blob=new Blob([JSON.stringify(r,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='decision-debt-diagnostic.json';a.click()}load()</script></body></html>`;
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  if (req.method === "GET" && url.pathname === "/") { res.writeHead(200, { "content-type": "text/html; charset=utf-8" }); return res.end(html()); }
  if (req.method === "GET" && url.pathname === "/api/health") return json(res, 200, { ok: true, service: "genba-data-os", stage: "demo" });
  if (req.method === "GET" && url.pathname === "/api/state") {
    const role = url.searchParams.get("role") || "supervisor";
    if (role === "supervisor" || role === "boss") return json(res, 200, { decision_debts: state.decisionDebts, simulation: state.simulation, events: role === "supervisor" ? state.events : [] });
    if (role === "keiri") return json(res, 200, { billing_summary: { available: true, note: "billing summary placeholder" } });
    if (role === "tanto") return json(res, 200, { work: state.events.filter(e => e.status === "open") });
    return json(res, 403, { error: "forbidden" });
  }
  if (req.method === "GET" && url.pathname === "/api/report") return json(res, 200, buildDiagnosticReport(state, { site: url.searchParams.get("site"), customer: url.searchParams.get("customer") }));
  if (req.method === "POST" && url.pathname === "/api/recalculate") { state = processEvents(state.events); return json(res, 200, state); }
  if (req.method === "POST" && url.pathname === "/api/import-csv") { let body = ""; req.on("data", c => body += c); req.on("end", () => { try { const events = csvToEvents(body); state = processEvents([...state.events, ...events]); json(res, 200, { imported: events.length, ...state }); } catch (e) { json(res, 400, { error: String(e.message || e) }); } }); return; }
  return json(res, 404, { error: "not_found" });
});

server.listen(PORT, () => console.log(`現場データOS: http://localhost:${PORT}`));
