"""Build one quarterly service record per BC Ferries route from the operator's reports."""
from html import escape
import json
from urllib.parse import urlencode
from result_pages import link, publish, table


def number(value):
    if value is None:
        return "Unreported"
    return f"{value:,.1f}".removesuffix(".0")


def publish_profiles(stage, tool):
    data = json.loads((stage / "data/edition.json").read_text())
    histories = {}
    for quarter in sorted(data["quarters"], key=lambda q: q["end"], reverse=True):
        for code, observation in quarter["routes"].items():
            histories.setdefault(code, []).append((quarter, observation))
    records = []
    for code, history in histories.items():
        q, latest = history[0]
        name = latest["name"]
        title = f"{name} ferry passenger counts and round trips"
        intro = f"BC Ferries Route {code} served {name} in the quarter ending {q['end']}."
        if latest["passengers"] is not None:
            intro += f" The operator recorded {number(latest['passengers'])} passengers."
        rows = [(report["end"], number(row["passengers"]), number(row["trips"]),
                 number(row["capacity"]), number(row["carried"]), number(row["utilization"]))
                for report, row in history]
        body = table("Reported service by quarter", ["Quarter ending", "Passengers", "Actual round trips",
                     "Vehicle capacity (AEQ)", "Vehicles carried (AEQ)", "Deck utilization (%)"], rows)
        body += ('<p>AEQ means automobile equivalents. A larger vehicle uses more deck space than one car. '
                 'Reported utilization describes the quarter as a whole. A trip count can include half a round trip.</p>')
        body += '<p>' + link(tool["url"] + "?" + urlencode({"route": code}), "Compare quarters for this route") + '</p>'
        body += (f'<h2>Source reports</h2><p>Snapshot retrieved {escape(data["retrieved"])}. '
                 'Open the round-trip and passenger tables for the latest reporting quarter.</p><p>'
                 + link(q["url"] + "#page=" + str(q["tripPage"]), "BC Ferries round trips and vehicle equivalents")
                 + ' · ' + link(q["url"] + "#page=" + str(q["paxPage"]), "BC Ferries passenger counts") + '</p>')
        if code == '08':
            body += '<p>' + link(tool["url"] + "#bowen", "Read the historical Bowen Island passenger-only service records") + '</p>'
        body += '<p>' + link('/ferrycountss/', 'Explore Halifax harbour ferry and Vancouver SeaBus boarding counts') + '</p>'
        records.append((code, f"Route {code} · {name}", title, intro, body))
    publish(stage, tool, "routes", "BC Ferries passenger counts and round trips by route",
            "Choose a route for the operator’s quarterly passenger counts, round trips and vehicle capacity figures.", records)
