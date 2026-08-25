import http from "node:http";
import { getSeedState } from "./data.js";
import { csvToEvents, processEvents } from "./core.js";
import { buildDiagnosticReport } from "./report.js";

const PORT = Number(process.env.PORT || 3100);
const MAX_BODY_BYTES = 2_000_000;
const VALID_ROLES = new Set(["tanto", "supervisor", "keiri", "boss"]);
let state = getSeedState();

function json(res, status, payload, role = "unknown") {
  const body = JSON.stringify(payload);
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "x-role-scope": role,
    "cache-control": "no-store"
  });
  res.end(body);
}

function resolveDevRole(req) {
  const role = String(req.headers["x-dev-role"] || "supervisor");
  return VALID_ROLES.has(role) ? role : null;
}

function requireRole(req, allowed) {
  const role = resolveDevRole(req);
  return role && allowed.has(role) ? role : null;
}

function html() {
  return `<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>現場データOS</title><style>
  :root{color-scheme:dark;font-family:Inter,system-ui,sans-serif}body{margin:0;background:#0b0d10;color:#f4f7fa}main{max-width:1180px;margin:auto;padding:24px}.grid{display:grid;grid-template-columns:1.35fr .8fr;gap:16px}.card{background:#14181d;border:1px solid #28303a;border-radius:16px;padding:18px;box-shadow:0 8px 24px #0004}.kpi{font-size:38px;font-weight:800}.muted{color:#98a4b3}.tag{display:inline-block;padding:4px 8px;border-radius:999px;background:#1f2933;margin-right:6px;font-size:12px}.danger{color:#ff7b72}.good{color:#7ee787}.row{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid #242b33}.top{font-size:22px;font-weight:750}.btn{background:#f0f6fc;color:#0b0d10;border:0;border-radius:10px;padding:10px 14px;font-weight:700;cursor:pointer}.mono{font-family:ui-monospace,SFMono-Regular,monospace}.sim{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.sim .card{padding:12px}@media(max-width:800px){.grid{grid-template-columns:1fr}.sim{grid-template-columns:repeat(2,1fr)}}
</style></head><body><main><div style="display:flex;justify-content:space-between;align-items:end;margin-bottom:18px"><div><div class="muted">DECISION DEBT ACCOUNTING</div><h1 style="margin:.2em 0">今日、何を決めるか。</h1><div class="muted">記録は今のまま。未決判断だけを負債として計測する。</div></div><div><button class="btn" onclick="downloadReport()">診断レポート</button><button class="btn" onclick="recalculate()" style="margin-left:8px">再計算</button></div></div><div class="grid"><section class="card"><div class="muted">TODAY'S DECISION</div><div id="today" class="top">読み込み中…</div><div id="why" class="muted" style="margin-top:8px"></div><div style="margin-top:18px" id="breakdown"></div></section><section class="card"><div class="muted">CURRENT PRESSURE</div><div id="pressure" class="kpi">—</div><div class="muted">Top Decision Debt pressure</div><div style="margin-top:18px"><span class="tag" id="site"></span><span class="tag" id="blocked"></span><span class="tag" id="debtCount"></span></div></section></div><div class="grid" style="margin-top:16px"><section class="card"><div class="muted">DECISION DEBT</div><div id="list"></div></section><section class="card"><div class="muted">30-DAY COUNTERFACTUAL</div><div class="sim" id="sim"></div><div class="muted" style="margin-top:12px">日次でDelayを進め、放置と処理の差を同じ決定論で再計算。</div></section></div><div class="card" style="margin-top:16px"><div class="muted">DATA INGEST</div><pre id="ingest" class="mono" style="white-space:pre-wrap">CSV: POST /api/import-csv（Supervisor）</pre></div></main><script>
const headers={'x-dev-role':'supervisor'};
async function load(){const r=await fetch('/api/state',{headers});const s=await r.json();if(!r.ok)throw new Error(s.error||'state_error');const d=s.decision_debts[0];document.querySelector('#today').textContent=d?.title||'Decision Debtなし';document.querySelector('#why').textContent=d?.reason||'';document.querySelector('#pressure').textContent=d?.pressure_total??'—';document.querySelector('#site').textContent=d?.site_id||'';document.querySelector('#blocked').textContent=d?('下流 '+d.downstream_block_count+'件'):'';document.querySelector('#debtCount').textContent='残高 '+s.decision_debts.length+'件';document.querySelector('#breakdown').innerHTML=d?Object.entries(d.breakdown).map(([k,v])=>'<div class="row"><span>'+k+'</span><span>'+Number(v).toFixed(1)+'</span></div>').join(''):'<div class="muted">未検出</div>';document.querySelector('#list').innerHTML=s.decision_debts.map(x=>'<div class="row"><div><b>#'+x.rank+' '+x.title+'</b><div class="muted">'+x.delay_days+'日 / 下流'+x.downstream_block_count+'件 / 依存'+x.dependency_depth+'段</div></div><b class="'+(x.pressure_total>=70?'danger':'')+'">'+x.pressure_total+'</b></div>').join('');document.querySelector('#sim').innerHTML=s.simulation.map(x=>'<div class="card"><b>'+x.label+'</b><div class="kpi" style="font-size:24px">'+x.final_high_pressure_count+'</div><div class="muted">30日後High Pressure</div><div class="muted">残件 '+x.unresolved_count_30d+' / 交差 '+x.crossed_high_pressure_count+'</div></div>').join('')}
async function recalculate(){await fetch('/api/recalculate',{method:'POST',headers});location.reload()}
async function downloadReport(){const r=await fetch('/api/report?site=demo-site&customer=demo-customer',{headers});const payload=await r.json();if(!r.ok)throw new Error(payload.error||'report_error');const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='decision-debt-diagnostic.json';a.click()}
load().catch(e=>document.querySelector('#today').textContent='読み込みエラー: '+e.message)</script></body></html>`;
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  if (req.method === "GET" && url.pathname === "/") {
    res.writeHead(200, { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" });
    return res.end(html());
  }
  if (req.method === "GET" && url.pathname === "/api/health") return json(res, 200, { ok: true, service: "genba-data-os", stage: "demo" }, "public");

  if (req.method === "GET" && url.pathname === "/api/state") {
    const role = resolveDevRole(req);
    if (!role) return json(res, 403, { error: "invalid_role" }, "none");
    if (role === "supervisor") return json(res, 200, { decision_debts: state.decisionDebts, simulation: state.simulation, events: state.events }, role);
    if (role === "boss") return json(res, 200, {
      decision_debts: state.decisionDebts.map(({ title, rank, pressure_total, downstream_block_count, dependency_depth }) => ({ title, rank, pressure_total, downstream_block_count, dependency_depth })),
      simulation: state.simulation
    }, role);
    if (role === "keiri") return json(res, 200, { billing_summary: { available: true, note: "billing summary placeholder; real billing connector is not part of v1" } }, role);
    if (role === "tanto") return json(res, 200, { work: state.events.filter((e) => e.status === "open") }, role);
  }

  if (req.method === "GET" && url.pathname === "/api/report") {
    const role = requireRole(req, new Set(["supervisor", "boss"]));
    if (!role) return json(res, 403, { error: "report_requires_supervisor_or_boss" }, "none");
    return json(res, 200, buildDiagnosticReport(state, { site: url.searchParams.get("site"), customer: url.searchParams.get("customer") }), role);
  }

  if (req.method === "POST" && url.pathname === "/api/recalculate") {
    const role = requireRole(req, new Set(["supervisor"]));
    if (!role) return json(res, 403, { error: "recalculate_requires_supervisor" }, "none");
    state = processEvents(state.events);
    return json(res, 200, state, role);
  }

  if (req.method === "POST" && url.pathname === "/api/import-csv") {
    const role = requireRole(req, new Set(["supervisor"]));
    if (!role) return json(res, 403, { error: "import_requires_supervisor" }, "none");
    let body = "";
    let size = 0;
    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) { req.destroy(); return; }
      body += chunk;
    });
    req.on("end", () => {
      if (size > MAX_BODY_BYTES) return json(res, 413, { error: "payload_too_large" }, role);
      try {
        const events = csvToEvents(body);
        state = processEvents([...state.events, ...events]);
        json(res, 200, { imported: events.length, ...state }, role);
      } catch (e) {
        json(res, 400, { error: String(e.message || e) }, role);
      }
    });
    return;
  }

  return json(res, 404, { error: "not_found" }, "none");
});

server.listen(PORT, () => console.log(`現場データOS: http://localhost:${PORT}`));
