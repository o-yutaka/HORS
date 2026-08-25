import { processEvents } from "./core.js";

export const seedEvents = [
  { id: "EV-001", site_id: "SITE-A", date: "2026-08-24", event_type: "delay", status: "open", note: "コンクリート搬入が3日遅延。主要工程への影響を確認中" },
  { id: "EV-002", site_id: "SITE-A", date: "2026-08-23", event_type: "material", status: "open", note: "外装材が未着。代替手段が未決" },
  { id: "EV-003", site_id: "SITE-A", date: "2026-08-22", event_type: "approval", status: "pending", note: "施主承認待ち。契約工程に影響" },
  { id: "EV-004", site_id: "SITE-A", date: "2026-08-22", event_type: "delay", status: "open", note: "電気配線が2日遅延。後続4件をブロック" },
  { id: "EV-005", site_id: "SITE-A", date: "2026-08-21", event_type: "material", status: "open", note: "資材搬入日が不明。確認中" },
  { id: "EV-006", site_id: "SITE-A", date: "2026-08-20", event_type: "hold", status: "open", note: "設備仕様が未決。全体工程に影響" },
  { id: "EV-007", site_id: "SITE-A", date: "2026-08-20", event_type: "delay", status: "open", note: "内装工程が1日遅延" },
  { id: "EV-008", site_id: "SITE-A", date: "2026-08-19", event_type: "approval", status: "pending", note: "図面承認が未決" },
  { id: "EV-009", site_id: "SITE-B", date: "2026-08-19", event_type: "delay", status: "open", note: "配管部材が未着。後続3件をブロック" },
  { id: "EV-010", site_id: "SITE-B", date: "2026-08-18", event_type: "hold", status: "open", note: "施工順序の判断待ち" },
  { id: "EV-011", site_id: "SITE-B", date: "2026-08-18", event_type: "material", status: "open", note: "断熱材不足。代替候補を確認中" },
  { id: "EV-012", site_id: "SITE-B", date: "2026-08-17", event_type: "delay", status: "open", note: "職人手配が2日遅延" }
];

export function getSeedState() {
  return processEvents(seedEvents);
}
