# Y Combinator Companies API in Python: scrape the YC startup directory (batches, founders, hiring)

A Python tutorial for pulling the **Y Combinator company directory** (ycombinator.com/companies) as data: every YC startup with batch, status, industry, tags, team size, location and website, plus founders with LinkedIn/X links and open job titles. There is no official YC API, so this uses the [Y Combinator Companies Scraper](https://apify.com/rel8ble/yc-companies-scraper) on Apify through the `apify-client` package.

> Disclosure: I built this actor; it's a paid tool on Apify ($1.00 per 1,000 companies). Apify's free plan includes $5/month of credit, which covers the whole directory several times over.

## What you can do with it

- **Lead lists**: every active B2B company from the latest batches with 2-50 people, with founder names and LinkedIn URLs.
- **Market maps**: all YC companies tagged "Developer Tools" or in "Fintech" + "Latin America", by batch.
- **Hiring signals**: YC companies that are hiring right now, with their open job titles.
- **Demo Day tracking**: the new batch the day it goes public, or newest launches first on a weekly schedule.

## Install

```bash
pip install apify-client
```

Get an API token at https://console.apify.com/settings/integrations and replace `<YOUR_APIFY_TOKEN>`.

## Quick start (Python)

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")
run = client.actor("rel8ble/yc-companies-scraper").call(run_input={
    "batches": ["W25"],            # or "Winter 2025"; empty = all batches since 2005
    "statuses": ["Active"],
    "industries": ["B2B"],
    "includeDetails": True,        # founders, social links, open jobs
    "maxResults": 50,
})

for c in client.dataset(run["defaultDatasetId"]).iterate_items():
    founders = ", ".join(f["name"] for f in c.get("founders", []))
    print(c["name"], c["batchShort"], c["teamSize"], c["website"], "|", founders)
```

## Quick start (Node.js)

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/yc-companies-scraper').call({
    query: 'AI agents',
    hiringOnly: true,
    maxResults: 100,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
items.forEach((c) => console.log(c.name, c.batchShort, c.oneLiner));
```

## Full example: batch lead list + hiring report

[`example.py`](example.py) pulls every active company from the batches you pass, writes `companies.csv` and `founders.csv` (one row per founder with LinkedIn and X), and prints per batch the top industries and tags, median team size and which companies are hiring for what.

```bash
pip install -r requirements.txt
export APIFY_TOKEN=<YOUR_APIFY_TOKEN>   # Windows: set APIFY_TOKEN=...
python example.py W25 S25
```

## Input

| Field | Default | What it does |
|---|---|---|
| `query` | - | Free-text search like YC's search box: `"AI agents"`, `"fintech Brazil"` |
| `batches` | all | `["W24", "Summer 2024"]` (W = Winter, S = Summer, F = Fall, X = Spring) |
| `statuses` | all | `Active`, `Acquired`, `Public`, `Inactive` |
| `industries` / `regions` / `tags` | all | YC's own labels, e.g. `["Fintech"]`, `["Europe"]`, `["Developer Tools"]` |
| `hiringOnly` / `topCompaniesOnly` / `nonprofitOnly` | false | Directory flags |
| `teamSizeMin` / `teamSizeMax` | - | Self-reported team size range |
| `sortBy` | `default` | `launch_date` = newest launches first |
| `maxResults` | 100 | `0` = every match |
| `includeDetails` | false | Adds founders, LinkedIn/X/GitHub/Crunchbase, year founded, city, country, open job titles |

## Output sample (real run, 8 Oct 2026, `includeDetails: true`, trimmed)

```json
{
  "name": "assistant-ui",
  "ycUrl": "https://www.ycombinator.com/companies/assistant-ui",
  "website": "https://assistant-ui.com",
  "oneLiner": "Open Source React.js Library for AI Chat",
  "batch": "Winter 2025",
  "batchShort": "W25",
  "status": "Active",
  "industry": "B2B",
  "subindustry": "Infrastructure",
  "tags": ["Developer Tools", "Generative AI", "Chat", "Web Development", "AI Assistant"],
  "locations": "San Francisco, CA, USA",
  "teamSize": 3,
  "launchedAt": "2025-02-06T20:25:28.000Z",
  "isHiring": false,
  "yearFounded": 2024,
  "linkedinUrl": "https://linkedin.com/company/assistant-ui",
  "twitterUrl": "https://x.com/assistantui",
  "githubUrl": "https://github.com/assistant-ui",
  "founders": [
    {
      "name": "Simon Farshid",
      "title": "Founder/CEO",
      "linkedinUrl": "https://linkedin.com/in/simon-farshid",
      "twitterUrl": "https://twitter.com/simonfarshid",
      "isActive": true
    }
  ],
  "openJobsCount": 0,
  "launchesCount": 1
}
```

A hiring company from the same run:

```json
{
  "name": "Thirdlayer",
  "website": "https://thirdlayer.inc",
  "oneLiner": "Continual learning for enterprise AI",
  "batchShort": "W25",
  "teamSize": 2,
  "isHiring": true,
  "openJobsCount": 5,
  "openJobTitles": ["Founding Engineer", "AI Engineer Intern", "Full-Stack Engineer Intern",
                    "2026 Summer AI/ML Engineer Intern", "Summer 2026 Full-Stack Engineer Intern"],
  "yearFounded": 2025
}
```

Fill rates on the full directory (6,279 companies, Oct 2026): website 99%, one-liner 97%, team size 98%, location 98%, tags 86%; batch, status, industry and launch date 100%. With details (30-company sample): company LinkedIn 97%, X 70%, GitHub 33%, founders 100%.

## Price and limits

- **$1.00 per 1,000 companies**, with or without details. The whole directory (~6,300 companies) is about $6.30 and downloads in about 10 seconds without details.
- No browser, no login: it reads the same public search index the YC site uses.
- Filters are exact-match on YC's labels (`"Fintech"`, not `"fin tech"`); `query` is fuzzy.
- Founder data is what YC publishes (name, title, LinkedIn/X). No emails or phone numbers.
- Team size and location are self-reported and can be out of date.
- Jobs are titles only (up to 50 per company), not full descriptions.

## Links

- Actor on the Apify Store: https://apify.com/rel8ble/yc-companies-scraper
- Apify Python client docs: https://docs.apify.com/api/client/python

## License

MIT for the code in this repo. The actor itself is a paid service on Apify.
