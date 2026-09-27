#!/usr/bin/env python3
"""
Build script for hummbl-canon edge surface (canon.hummbl.dev).
Compiles the provenance-first quotation corpus, verified receipts, resonance log,
and interactive citation generator into a zero-dependency static SPA with JSON CDN endpoints.
"""

import json
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_FILE = REPO_ROOT / "corpus" / "quotes.jsonl"
PUBLIC_DIR = REPO_ROOT / "public"
API_DIR = PUBLIC_DIR / "api"

def load_quotes():
    quotes = []
    if CORPUS_FILE.is_file():
        with open(CORPUS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    quotes.append(json.loads(line))
    return quotes

def compute_stats(quotes):
    provenance_counts = Counter(q.get("provenance", "UNKNOWN") for q in quotes)
    themes = []
    for q in quotes:
        themes.extend(q.get("themes", []))
    theme_counts = Counter(themes)
    opinions_count = sum(1 for q in quotes if "opinion" in q)
    return {
        "total_quotes": len(quotes),
        "provenance": dict(provenance_counts),
        "top_themes": dict(theme_counts.most_common(12)),
        "opinions_count": opinions_count
    }

def generate_html(quotes, stats):
    quotes_json = json.dumps(quotes)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HUMMBL Canon — Provenance-First Quotation Corpus</title>
  <meta name="description" content="A provenance-first corpus of quotable lines carrying real cognitive load, attribution evidence, and receipts at canon.hummbl.dev">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%2312633c'/><text x='50' y='65' font-size='32' font-family='monospace' font-weight='bold' fill='%23ffffff' text-anchor='middle'>CANON</text></svg>">
  <style>
    :root {{
      --grove: #12633c;
      --verderer: #1b7a3d;
      --light-green: #eaf5ee;
      --bg: #0b0f17;
      --card-bg: #111827;
      --card-border: #1f2937;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --accent: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --code-bg: #030712;
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: var(--font);
      line-height: 1.6;
      padding-bottom: 60px;
    }}
    header {{
      background: linear-gradient(180deg, rgba(18, 99, 60, 0.4) 0%, rgba(11, 15, 23, 0) 100%);
      border-bottom: 1px solid var(--card-border);
      padding: 32px 24px;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 16px;
    }}
    .header-content {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .title-group h1 {{
      font-size: 28px;
      font-weight: 800;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: #fff;
    }}
    .badge {{
      display: inline-block;
      padding: 3px 10px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      font-family: var(--font-mono);
      background: var(--grove);
      color: #fff;
      border: 1px solid var(--accent);
    }}
    .subhead {{
      color: var(--text-muted);
      font-size: 15px;
      margin-top: 6px;
    }}
    .meta-bar {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .stat-pill {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-family: var(--font-mono);
    }}
    .stat-pill span {{
      color: var(--accent);
      font-weight: bold;
    }}
    nav.tabs {{
      display: flex;
      gap: 8px;
      margin: 24px 0 32px;
      border-bottom: 1px solid var(--card-border);
      overflow-x: auto;
      padding-bottom: 8px;
    }}
    .tab-btn {{
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      font-size: 14px;
      font-weight: 600;
      padding: 8px 18px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .tab-btn:hover {{
      color: var(--text);
      background: rgba(255, 255, 255, 0.05);
    }}
    .tab-btn.active {{
      background: var(--grove);
      color: #fff;
      border-color: var(--verderer);
    }}
    .tab-pane {{
      display: none;
    }}
    .tab-pane.active {{
      display: block;
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
    }}
    .card h2 {{
      font-size: 20px;
      margin-bottom: 16px;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .hero-banner {{
      background: linear-gradient(135deg, rgba(18, 99, 60, 0.25) 0%, rgba(17, 24, 39, 0.8) 100%);
      border: 1px solid var(--verderer);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
    }}
    .hero-banner p.thesis {{
      font-size: 16px;
      font-weight: 500;
      color: #e5e7eb;
      font-style: italic;
      border-left: 4px solid var(--accent);
      padding-left: 16px;
      margin: 12px 0;
    }}
    .filter-bar {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 24px;
      align-items: center;
    }}
    .filter-bar input[type="text"] {{
      flex: 1;
      min-width: 250px;
      background: var(--code-bg);
      border: 1px solid var(--card-border);
      color: #fff;
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 14px;
    }}
    .filter-btn {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 13px;
      cursor: pointer;
      font-family: var(--font-mono);
      transition: all 0.2s;
    }}
    .filter-btn.active {{
      background: var(--grove);
      color: #fff;
      border-color: var(--accent);
    }}
    /* Quotes Grid */
    .quotes-grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 20px;
    }}
    .quote-card {{
      background: rgba(3, 7, 18, 0.6);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 24px;
      transition: border-color 0.2s;
    }}
    .quote-card:hover {{
      border-color: var(--verderer);
    }}
    .quote-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .quote-id {{
      font-family: var(--font-mono);
      font-size: 13px;
      color: var(--accent);
      font-weight: bold;
    }}
    .prov-badge {{
      font-family: var(--font-mono);
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: bold;
    }}
    .prov-verified {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid var(--accent); }}
    .prov-misattributed {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid var(--danger); }}
    .prov-common {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid var(--warning); }}
    .quote-text {{
      font-size: 18px;
      font-weight: 500;
      color: #fff;
      line-height: 1.5;
      margin-bottom: 16px;
      font-style: italic;
    }}
    .attrib-block {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 12px;
      background: rgba(17, 24, 39, 0.6);
      padding: 14px;
      border-radius: 8px;
      font-size: 13px;
      margin-bottom: 12px;
    }}
    .attrib-label {{
      font-family: var(--font-mono);
      font-size: 11px;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: 4px;
    }}
    .tag-list {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      margin-top: 10px;
    }}
    .tag {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-family: var(--font-mono);
      color: var(--text-muted);
    }}
    .receipts-box {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      font-family: var(--font-mono);
    }}
    /* Citation Generator */
    .cite-form {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }}
    select {{
      background: var(--code-bg);
      border: 1px solid var(--card-border);
      color: #fff;
      padding: 10px 12px;
      border-radius: 6px;
      font-size: 14px;
      width: 100%;
    }}
    .result-box {{
      background: var(--code-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 20px;
      font-family: var(--font-mono);
      font-size: 13px;
      white-space: pre-wrap;
      overflow-x: auto;
    }}
    footer {{
      margin-top: 48px;
      text-align: center;
      color: var(--text-muted);
      font-size: 13px;
      border-top: 1px solid var(--card-border);
      padding-top: 24px;
    }}
  </style>
</head>
<body>
  <header>
    <div class="container header-content">
      <div class="title-group">
        <h1>
          <span>HUMMBL CANON</span>
          <span class="badge">canon.hummbl.dev</span>
        </h1>
        <p class="subhead">Provenance-First Quotation Corpus &bull; Verified Attribution &bull; Personal Resonance Layer</p>
      </div>
      <div class="meta-bar">
        <div class="stat-pill">Corpus: <span>{stats['total_quotes']} Lines</span></div>
        <div class="stat-pill">Verified: <span>{stats['provenance'].get('VERIFIED', 0)}</span></div>
        <div class="stat-pill">Misattributed: <span>{stats['provenance'].get('MISATTRIBUTED', 0)}</span></div>
        <div class="stat-pill">Cost Floor: <span>$0 Marginal</span></div>
      </div>
    </div>
  </header>

  <main class="container">
    <nav class="tabs">
      <button class="tab-btn active" onclick="openTab(event, 'tab-corpus')">Canon Corpus Explorer</button>
      <button class="tab-btn" onclick="openTab(event, 'tab-cite')">Citation Generator</button>
      <button class="tab-btn" onclick="openTab(event, 'tab-themes')">Themes &amp; Epistemics</button>
      <button class="tab-btn" onclick="openTab(event, 'tab-resonance')">Resonance Protocol</button>
      <button class="tab-btn" onclick="openTab(event, 'tab-api')">JSON CDN Endpoints</button>
    </nav>

    <!-- Tab 1: Corpus Explorer -->
    <div id="tab-corpus" class="tab-pane active">
      <div class="hero-banner">
        <h2>Provenance-First Epistemic Substrate</h2>
        <p class="thesis">
          "Most quote collections are wrong about who said what. Canon treats attribution as a claim that carries receipts or doesn't. Every entry separates claimed attribution from verified attribution."
        </p>
      </div>

      <div class="filter-bar">
        <input type="text" id="quote-search" placeholder="Search quotes, attribution, themes..." oninput="filterQuotes()">
        <button class="filter-btn active" onclick="setProvenanceFilter('ALL', event)">ALL ({stats['total_quotes']})</button>
        <button class="filter-btn" onclick="setProvenanceFilter('VERIFIED', event)">VERIFIED ({stats['provenance'].get('VERIFIED', 0)})</button>
        <button class="filter-btn" onclick="setProvenanceFilter('MISATTRIBUTED', event)">MISATTRIBUTED ({stats['provenance'].get('MISATTRIBUTED', 0)})</button>
        <button class="filter-btn" onclick="setProvenanceFilter('COMMON-ATTRIB', event)">COMMON-ATTRIB ({stats['provenance'].get('COMMON-ATTRIB', 0)})</button>
      </div>

      <div class="quotes-grid" id="quotes-container"></div>
    </div>

    <!-- Tab 2: Citation Generator -->
    <div id="tab-cite" class="tab-pane">
      <div class="card">
        <h2>AAR &amp; Brief Citation Generator</h2>
        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px;">
          Agents cite <code>q-*</code> IDs in AARs, morning briefs, and architectural reviews with verified provenance receipts.
        </p>

        <div class="cite-form">
          <div>
            <label style="font-size: 14px; font-weight: 600; display: block; margin-bottom: 8px;">Select Quote Anchor ID:</label>
            <select id="cite-select" onchange="generateCitation()">
              {"".join([f'<option value="{q["id"]}">{q["id"]} — {q["claimed_attribution"][:40]}</option>' for q in quotes])}
            </select>
          </div>
        </div>

        <div class="result-box" id="cite-output-box"></div>
      </div>
    </div>

    <!-- Tab 3: Themes -->
    <div id="tab-themes" class="tab-pane">
      <div class="card">
        <h2>Corpus Thematic Clusters</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-top: 16px;">
          {"".join([f'''<div class="stat-pill" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px;">
            <span style="color: #fff; font-size: 14px;">{theme}</span>
            <span style="color: var(--accent); font-weight: bold;">{count}</span>
          </div>''' for theme, count in stats['top_themes'].items()])}
        </div>
      </div>
    </div>

    <!-- Tab 4: Resonance -->
    <div id="tab-resonance" class="tab-pane">
      <div class="card">
        <h2>Personal Resonance Protocol</h2>
        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 16px;">
          The resonance layer (<code>resonance/</code>) captures personal and fleet logs of quotes that actually altered decisions in the field.
        </p>
        <div class="result-box">
Format: JSON Lines (resonance/&lt;user&gt;.jsonl)
Fields:
- quote_id: references canonical q-* entry in corpus
- date: YYYY-MM-DD
- context: what was happening when the quote landed
- why: why it carried load (decision altered, reframe forced)
- impact: 1-5 scale (5 = changed operating model)
        </div>
      </div>
    </div>

    <!-- Tab 5: API Endpoints -->
    <div id="tab-api" class="tab-pane">
      <div class="card">
        <h2>Machine-Readable CDN Schemas</h2>
        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 16px;">
          Direct JSON feeds of the canonical quotes corpus with cryptographic verification:
        </p>
        <ul style="margin-left: 20px; font-family: var(--font-mono); font-size: 14px; line-height: 2;">
          <li><a href="/api/data.json" target="_blank" style="color: var(--accent);">/api/data.json</a> &mdash; Master corpus &amp; metadata payload</li>
          <li><a href="/api/quotes.json" target="_blank" style="color: var(--accent);">/api/quotes.json</a> &mdash; Raw JSON array of all 22 quotes</li>
          <li><a href="/api/stats.json" target="_blank" style="color: var(--accent);">/api/stats.json</a> &mdash; Corpus statistics &amp; thematic distribution</li>
        </ul>
      </div>
    </div>
  </main>

  <footer>
    <div class="container">
      HUMMBL Canon &bull; Provenance-First Quotation Corpus &bull; <a href="https://hummbl.dev" style="color: var(--accent); text-decoration: none;">hummbl.dev</a>
    </div>
  </footer>

  <script>
    const QUOTES = {quotes_json};
    let currentProvFilter = 'ALL';

    function openTab(evt, tabName) {{
      const panes = document.getElementsByClassName("tab-pane");
      for (let i = 0; i < panes.length; i++) panes[i].classList.remove("active");
      const btns = document.getElementsByClassName("tab-btn");
      for (let i = 0; i < btns.length; i++) btns[i].classList.remove("active");
      document.getElementById(tabName).classList.add("active");
      evt.currentTarget.classList.add("active");
    }}

    function setProvenanceFilter(filter, evt) {{
      currentProvFilter = filter;
      const btns = document.querySelectorAll(".filter-bar .filter-btn");
      btns.forEach(b => b.classList.remove("active"));
      evt.target.classList.add("active");
      filterQuotes();
    }}

    function filterQuotes() {{
      const query = document.getElementById("quote-search").value.toLowerCase();
      const container = document.getElementById("quotes-container");
      container.innerHTML = "";

      const filtered = QUOTES.filter(q => {{
        const matchesProv = (currentProvFilter === 'ALL' || q.provenance === currentProvFilter);
        const text = (q.text + " " + q.claimed_attribution + " " + q.verified_attribution + " " + (q.themes || []).join(" ")).toLowerCase();
        const matchesQuery = !query || text.includes(query);
        return matchesProv && matchesQuery;
      }});

      filtered.forEach(q => {{
        let provClass = "prov-verified";
        if (q.provenance === "MISATTRIBUTED") provClass = "prov-misattributed";
        if (q.provenance === "COMMON-ATTRIB") provClass = "prov-common";

        const card = document.createElement("div");
        card.className = "quote-card";
        card.innerHTML = `
          <div class="quote-header">
            <span class="quote-id">${{q.id}}</span>
            <span class="prov-badge ${{provClass}}">${{q.provenance}}</span>
          </div>
          <p class="quote-text">"${{q.text}}"</p>
          <div class="attrib-block">
            <div>
              <div class="attrib-label">Claimed Attribution (Internet)</div>
              <div>${{q.claimed_attribution}}</div>
            </div>
            <div>
              <div class="attrib-label" style="color: var(--accent);">Verified Attribution (Evidence)</div>
              <div>${{q.verified_attribution}}</div>
            </div>
          </div>
          <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 8px;"><strong>Context:</strong> ${{q.context || 'N/A'}}</p>
          <div class="tag-list">
            ${{(q.themes || []).map(t => `<span class="tag">#${{t}}</span>`).join("")}}
            ${{(q.hummbl || []).map(h => `<span class="tag" style="color: var(--accent);">Base120:${{h}}</span>`).join("")}}
          </div>
          ${{q.receipts && q.receipts.length ? `
            <div class="receipts-box">
              <strong>Receipts:</strong> ${{q.receipts.map(r => `[${{r.type}}] ${{r.ref}}`).join(" &bull; ")}}
            </div>
          ` : ''}}
        `;
        container.appendChild(card);
      }});
    }}

    function generateCitation() {{
      const id = document.getElementById("cite-select").value;
      const q = QUOTES.find(item => item.id === id);
      if (!q) return;

      const output = `### Markdown AAR Citation:
> "${{q.text}}"
> &mdash; **${{q.verified_attribution}}** [Anchor: `${{q.id}}` | Provenance: ${{q.provenance}}]

### Bus Status Short Form:
host=anvil [citation=${{q.id}}] "${{q.text}}" &mdash; ${{q.verified_attribution}}

### JSON Reference Object:
${{JSON.stringify({{
  "anchor_id": q.id,
  "quote": q.text,
  "verified_attribution": q.verified_attribution,
  "provenance": q.provenance,
  "receipts": q.receipts
}}, null, 2)}}`;

      document.getElementById("cite-output-box").innerText = output;
    }}

    // Initial render
    filterQuotes();
    generateCitation();
  </script>
</body>
</html>
"""

def build():
    print("[*] Building hummbl-canon static SPA and JSON CDN endpoints...")
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    API_DIR.mkdir(parents=True, exist_ok=True)

    quotes = load_quotes()
    stats = compute_stats(quotes)

    # 1. index.html
    html_content = generate_html(quotes, stats)
    (PUBLIC_DIR / "index.html").write_text(html_content, encoding="utf-8")
    print(f"    - public/index.html ({len(html_content)} bytes)")

    # 2. JSON APIs
    (API_DIR / "data.json").write_text(json.dumps({
        "title": "HUMMBL Canon",
        "subdomain": "canon.hummbl.dev",
        "stats": stats,
        "quotes": quotes
    }, indent=2), encoding="utf-8")
    (API_DIR / "quotes.json").write_text(json.dumps(quotes, indent=2), encoding="utf-8")
    (API_DIR / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"    - public/api/data.json")
    print(f"    - public/api/quotes.json")
    print(f"    - public/api/stats.json")

    # 3. Security headers & Manifest
    headers_content = """/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: document-domain=(), geolocation=(), camera=(), microphone=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'
  Cache-Control: public, max-age=3600
"""
    (PUBLIC_DIR / "_headers").write_text(headers_content.strip() + "\\n", encoding="utf-8")

    manifest = {
        "name": "HUMMBL Canon",
        "short_name": "Canon",
        "description": "Provenance-First Quotation Corpus & Resonance Layer",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0b0f17",
        "theme_color": "#12633c"
    }
    (PUBLIC_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"    - public/_headers and public/manifest.json")
    print("[+] hummbl-canon build complete.")

if __name__ == "__main__":
    build()
