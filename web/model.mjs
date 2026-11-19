export function routeHistory(quarters, route) {
  return quarters
    .filter((q) => Object.hasOwn(q.routes, route))
    .map((q) => ({
      ...q.routes[route],
      end: q.end,
      url: q.url,
      tripPage: q.tripPage,
      paxPage: q.paxPage,
    }));
}
export function yearEarlier(rows, day) {
  const prior = String(Number(day.slice(0, 4)) - 1) + day.slice(4);
  return rows.find((r) => r.end === prior);
}
