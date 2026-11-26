# Ferry Record

Choose a BC Ferries route and compare its activity with the same quarter a year earlier. Download its reported history or explore the separate 2013 Bowen Island passenger-service appendix.

[Open Ferry Record](https://coolcode.ca/ferryrecord/)

## Try it

<!-- coolcode:guide -->
On Route 08, compare the quarters ending June 2025 and June 2026. The operator recorded 1,386 and 1,384 round trips respectively, while passenger totals rose from 374,200 to 387,857.
<!-- /coolcode:guide -->

[Browse quarterly service figures by ferry route](https://coolcode.ca/ferryrecord/routes/). Each data build publishes the observation history, original source links and a project sitemap from the checked-in edition.

## Sources and interpretation

The operating series starts with the quarter ending June 30, 2024. The first edition includes 25 routes and nine quarters through June 30, 2026. Each row links directly to the round-trip or passenger table in Section 1A. Actual round trips can include a half trip. Automobile equivalents (AEQs) measure vehicle deck space. Route 13 publishes zero vehicle capacity and leaves some vehicle measures empty. The overall utilization figure describes the quarter. It cannot tell a passenger whether an individual sailing was full.

The public report index supplies additional quarters. The importer keeps previously indexed quarters, checks that the passenger and round-trip tables agree on route identifiers, and verifies the historical briefing. The latter’s reported 2013 departure times describe services at the time of the briefing.

[BC Ferries operations reports](https://www.bcferries.com/in-the-community/resources) · [Bowen Island briefing, disclosure page 68](https://docs.openinfo.gov.bc.ca/d32738014a_response_package_tra-2014-00083.pdf#page=17)

## Refresh and verification

Weekly. Install Poppler’s pdftotext program for the quarterly tables. The retrieval date records the last successful source check in UTC. The coverage on the homepage and in the tool describes the underlying records. A changed archive requiring review or a failed download leaves the previous edition available. The scheduled workflow validates the data, runs the tests and publishes the resulting snapshot. For a manual refresh, run `python3 scripts/refresh.py`.

The interface, selections and CSV exports run locally in the browser. Visiting a source or map link opens the publisher’s site. The offline build uses the checked-in edition. To build and preview it, run the following commands.

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

The Pages workflow also exercises the tool in Chromium at its project subpath and checks the mobile layout. Update the source sentence in `tool.json` and the marked guide above when changing coverage or interpretation.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->
