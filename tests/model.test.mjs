import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const edition = JSON.parse(
  readFileSync(new URL("../web/data/edition.json", import.meta.url), "utf8"),
);
import { routeHistory, yearEarlier } from "../web/model.mjs";
test("a route uses the same calendar quarter for its year-on-year comparison", () => {
  const rows = routeHistory(edition.quarters, "08");
  const june = rows.find((row) => row.end === "2026-06-30");
  assert.equal(june.trips, 1384);
  assert.equal(june.passengers, 387857);
  assert.equal(yearEarlier(rows, june.end).passengers, 374200);
  assert.equal(yearEarlier(rows, "2024-06-30"), undefined);
  assert.ok(june.tripPage > 0 && june.paxPage > 0);
});
test("passenger-only zero capacity and unpublished vehicle measures stay distinct", () => {
  const row = routeHistory(edition.quarters, "13").find(
    (row) => row.end === "2026-06-30",
  );
  assert.equal(row.capacity, 0);
  assert.equal(row.carried, null);
  assert.equal(row.utilization, null);
  assert.deepEqual(routeHistory(edition.quarters, "unknown"), []);
});
