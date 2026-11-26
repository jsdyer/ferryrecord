import {
  byId,
  choices,
  element,
  facts,
  number,
  sourceLink,
  table,
  downloadCsv,
  loadEdition,
  failed,
} from "./ui.mjs";
import { routeHistory, yearEarlier } from "./model.mjs";
const services = [
  [
    "English Bay Launch · Granville Island",
    "Snug Cove and Granville Island",
    "The weekday schedule lists a 6:30 am departure from Snug Cove and 7:15 am and 4:30 pm departures from Granville Island.",
  ],
  [
    "English Bay Launch · Coal Harbour",
    "Snug Cove and Coal Harbour",
    "Monday to Friday, the appendix lists departures from Snug Cove at 8:00 am and 5:15 pm, with a 6:00 pm return from Coal Harbour.",
  ],
  [
    "Cormorant Marine · Horseshoe Bay",
    "Snug Cove and Horseshoe Bay",
    "The appendix lists Snug Cove departures at 11:15 pm Sunday to Thursday and 12:15 am Friday and Saturday. Horseshoe Bay departures follow 15 minutes later.",
  ],
];
try {
  const data = await loadEdition("route-quarter records");
  const routes = new Map();
  for (const q of data.quarters)
    for (const [id, r] of Object.entries(q.routes)) routes.set(id, r.name);
  choices(
    "route",
    [...routes.entries()]
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([id, name]) => [id, id + " · " + name]),
  );
  const requested = new URLSearchParams(location.search).get("route");
  if (routes.has(requested)) byId("route").value = requested;
  else if (routes.has("08")) byId("route").value = "08";
  let rows = [],
    csv = [];
  function render() {
    const selected = rows.find((r) => r.end === byId("quarter").value),
      past = yearEarlier(rows, selected.end);
    facts("facts", [
      ["Actual round trips", number(selected.trips)],
      ["Passengers", number(selected.passengers)],
      [
        "Vehicle deck utilization",
        selected.utilization == null
          ? "Unreported"
          : number(selected.utilization) + "%",
      ],
    ]);
    const route = "Route " + byId("route").value + " (" + selected.name + ")";
    let finding = route + " recorded " + number(selected.passengers) +
      " passengers in the quarter ending " + selected.end;
    if (selected.passengers == null) {
      finding = "Passenger totals were unreported for " + route + " in the quarter ending " + selected.end;
    } else if (past?.passengers != null) {
      finding += ", compared with " + number(past.passengers) + " in the same quarter a year earlier";
    }
    byId("finding").textContent = finding + ".";
    byId("original").replaceChildren(
      sourceLink(
        "Round trips and vehicle equivalents, PDF p. " + selected.tripPage,
        selected.url + "#page=" + selected.tripPage,
      ),
      " · ",
      sourceLink(
        "Passengers, PDF p. " + selected.paxPage,
        selected.url + "#page=" + selected.paxPage,
      ),
    );
    const hs = [
      "Quarter ending",
      "Round trips",
      "Passengers",
      "AEQs carried",
      "AEQ capacity",
      "Utilization",
      "Report",
    ];
    table(
      "history",
      hs,
      [...rows]
        .reverse()
        .map((r) => [
          r.end,
          number(r.trips),
          number(r.passengers),
          number(r.carried),
          number(r.capacity),
          r.utilization == null ? "—" : number(r.utilization) + "%",
          sourceLink("Tables", r.url + "#page=" + r.tripPage),
        ]),
    );
    csv = [
      [
        "route",
        "quarter_end",
        "round_trips",
        "passengers",
        "AEQs_carried",
        "AEQ_capacity",
        "utilization_percent",
        "source_trips",
        "source_passengers",
      ],
      ...rows.map((r) => [
        byId("route").value,
        r.end,
        r.trips,
        r.passengers,
        r.carried,
        r.capacity,
        r.utilization,
        r.url + "#page=" + r.tripPage,
        r.url + "#page=" + r.paxPage,
      ]),
    ];
  }
  function routeChanged() {
    const prev = byId("quarter").value;
    rows = routeHistory(data.quarters, byId("route").value);
    choices(
      "quarter",
      [...rows].reverse().map((r) => [r.end, r.end]),
    );
    if (rows.some((r) => r.end === prev)) byId("quarter").value = prev;
    render();
  }
  choices(
    "service",
    services.map(([label], i) => [i, label]),
  );
  function showService() {
    const [, route, text] = services[+byId("service").value];
    byId("service-detail").replaceChildren(
      element("strong", route),
      element("p", text),
    );
  }
  byId("bowen-source").replaceChildren(
    sourceLink(
      "Open the 2013 briefing appendix, disclosure p. 68",
      data.bowen + "#page=17",
    ),
  );
  byId("route").onchange = routeChanged;
  byId("quarter").onchange = render;
  byId("service").onchange = showService;
  byId("csv").onclick = () =>
    downloadCsv("bc-ferry-route-" + byId("route").value + ".csv", csv);
  routeChanged();
  showService();
  byId("explore").hidden = false;
  byId("bowen").hidden = false;
} catch {
  failed();
}
