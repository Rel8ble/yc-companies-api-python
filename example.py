"""YC batch lead list with the Y Combinator Companies Scraper on Apify.

Pulls every company from one or more YC batches (with founders and social
links), saves companies.csv and founders.csv (one row per founder, with
LinkedIn), and prints per batch: company count, top industries and tags,
median team size, how many are hiring, and the open roles of hiring companies.

Usage:
    pip install -r requirements.txt
    set APIFY_TOKEN=<YOUR_APIFY_TOKEN>      (export on macOS/Linux)
    python example.py W25 S25
"""
import csv
import os
import sys
from collections import Counter, defaultdict
from statistics import median

from apify_client import ApifyClient

ACTOR_ID = "rel8ble/yc-companies-scraper"

token = os.environ.get("APIFY_TOKEN", "<YOUR_APIFY_TOKEN>")
batches = sys.argv[1:] or ["W25"]

client = ApifyClient(token)
run = client.actor(ACTOR_ID).call(run_input={
    "batches": batches,
    "statuses": ["Active"],
    "includeDetails": True,   # founders, LinkedIn/X/GitHub, open job titles
    "maxResults": 0,          # every matching company (~$0.001 each)
})
companies = list(client.dataset(run["defaultDatasetId"]).iterate_items())
print(f"{len(companies)} active companies in {', '.join(batches)}\n")

company_fields = ["name", "website", "oneLiner", "batchShort", "industry", "subindustry",
                  "teamSize", "locations", "country", "yearFounded", "isHiring",
                  "openJobsCount", "linkedinUrl", "twitterUrl", "githubUrl", "ycUrl"]
with open("companies.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=company_fields + ["tags"], extrasaction="ignore")
    w.writeheader()
    for c in companies:
        w.writerow({**c, "tags": "; ".join(c.get("tags") or [])})

with open("founders.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["company", "batch", "website", "founder", "title", "linkedin", "twitter"])
    for c in companies:
        for p in c.get("founders") or []:
            if p.get("isActive", True):
                w.writerow([c["name"], c["batchShort"], c.get("website"), p["name"],
                            p.get("title"), p.get("linkedinUrl"), p.get("twitterUrl")])

by_batch = defaultdict(list)
for c in companies:
    by_batch[c["batchShort"]].append(c)

for batch, rows in by_batch.items():
    industries = Counter(r["industry"] for r in rows if r.get("industry"))
    tags = Counter(t for r in rows for t in r.get("tags") or [])
    sizes = [r["teamSize"] for r in rows if r.get("teamSize")]
    hiring = [r for r in rows if r.get("isHiring")]
    print(f"{batch}: {len(rows)} companies, median team {median(sizes) if sizes else '-'}, "
          f"{len(hiring)} hiring")
    print("  industries: " + ", ".join(f"{k} ({n})" for k, n in industries.most_common(4)))
    print("  tags: " + ", ".join(f"{k} ({n})" for k, n in tags.most_common(5)))
    for r in sorted(hiring, key=lambda r: -(r.get("openJobsCount") or 0))[:10]:
        titles = ", ".join((r.get("openJobTitles") or [])[:3])
        print(f"  hiring: {r['name']} ({r.get('openJobsCount') or 0} roles) {titles}")
    print()

print("Saved companies.csv and founders.csv")
