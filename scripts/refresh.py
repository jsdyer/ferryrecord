"""Read route-level quarterly operating tables and retain dated source pages."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from html.parser import HTMLParser
import json
import re
import subprocess
from urllib.parse import urljoin, urlsplit
from source_io import ROOT, archives, archived, fetch, publish

INDEX = "https://www.bcferries.com/in-the-community/resources"
TITLE = re.compile(r"Q[1-4]\s+Operations Report\s*[-–—]\s*Ended\s+([A-Za-z]+ \d{1,2}, \d{4})",re.I)
ROW = re.compile(r"^\s*(\d{2}) (.+?)\s{2,}([\d,]+(?:\.\d+)?)\s+([\d,]+)\s+([\d,]+)\s+([\d.]+)%")
PASSENGERS = re.compile(r"^\s*(\d{2}) (.+?)\s{2,}([\d,]+)(?=\s)")
class ReportIndex(HTMLParser):
    def __init__(self):
        super().__init__(); self.href=None; self.label=[]; self.reports={}
    def handle_starttag(self,tag,attrs):
        if tag == "a":
            self.href=dict(attrs).get("href"); self.label=[]
    def handle_data(self,data):
        if self.href: self.label.append(data)
    def handle_endtag(self,tag):
        if tag != "a" or not self.href: return
        match=TITLE.search(" ".join(" ".join(self.label).split()))
        url=urljoin(INDEX,self.href)
        if match and urlsplit(url).netloc=="www.bcferries.com" and urlsplit(url).path.endswith(".pdf"):
            day=datetime.strptime(match[1],"%B %d, %Y").date().isoformat()
            if day >= "2024-06-30": self.reports[day]=url
        self.href=None

def extract(pdf,day,url):
    pages=subprocess.run(["pdftotext","-layout","-","-"],input=pdf,stdout=subprocess.PIPE,check=True).stdout.decode().split("\f")
    def page_for(symbol):
        candidates=[(i,p) for i,p in enumerate(pages,1) if p.lstrip().startswith("Section 1A") and symbol in p
                    and re.search(r"^\s*08 Horseshoe Bay - Snug Cove",p,re.M)]
        if len(candidates)!=1: raise ValueError(f"Review {symbol} table in {url}")
        return candidates[0]
    trip_page,trips=page_for("Actual Round")
    pax_page,pax=page_for("Passenger Tariff")
    if datetime.strptime(day,"%Y-%m-%d").strftime("%B %d, %Y") not in trips.splitlines()[0]:
        raise ValueError("Document quarter differs from index")
    passengers={}
    for line in pax.splitlines():
        m=PASSENGERS.match(line)
        if m:
            if m[1] in passengers: raise ValueError("Duplicate passenger row")
            passengers[m[1]]=int(m[3].replace(",",""))
    rows={}
    for line in trips.splitlines():
        match=ROW.match(line)
        if match:
            key,name,actual,capacity,carried,pct=match.groups()
        else:
            # Route 13's row gives round trips and zero vehicle capacity, leaving both vehicle measures empty.
            foot=re.match(r"^\s*(13) (.+?)\s{2,}([\d,.]+)\s+(0)(?:\s+[$(]|\s*$)",line)
            if not foot: continue
            key,name,actual,capacity=foot.groups()
            carried=pct=None
        if key in rows or key not in passengers: raise ValueError("Route table mismatch")
        rows[key]=dict(name=name.strip(),trips=float(actual.replace(",","")),capacity=int(capacity.replace(",","")),
                       carried=int(carried.replace(",","")) if carried is not None else None,utilization=float(pct) if pct is not None else None,passengers=passengers[key])
    if set(rows)!=set(passengers) or len(rows)<22:
        raise ValueError(f"Incomplete route tables for {day}: {set(passengers)^set(rows)}")
    return dict(end=day,url=url,tripPage=trip_page,paxPage=pax_page,routes=rows)

def refresh():
    archive=archives()[0]
    archived(archive)
    index=ReportIndex();index.feed(fetch(INDEX).decode())
    if len(index.reports)<1: raise ValueError("No published quarterly reports")
    previous=ROOT/"web/data/edition.json"
    history={q["end"]:q["url"] for q in json.loads(previous.read_text())["quarters"]} if previous.exists() else {}
    history.update(index.reports)
    def one(item):
        day,url=item
        return extract(fetch(url),day,url)
    with ThreadPoolExecutor(max_workers=3) as pool:
        quarters=list(pool.map(one,sorted(history.items())))
    if len(quarters)<9: raise ValueError("Expected at least nine report quarters")
    return make_edition(quarters,archive["url"])

def make_edition(quarters,url):
    return dict(start=quarters[0]["end"],end=quarters[-1]["end"],
                coverage=f'Quarters ending {quarters[0]["end"]} to {quarters[-1]["end"]}',
                count=sum(len(q["routes"]) for q in quarters), quarters=quarters, bowen=url)

if __name__=="__main__":
    publish(refresh())
