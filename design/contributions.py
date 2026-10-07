#!/usr/bin/env python3
"""Collect the studio's upstream contributions from the GitHub API and write
data/contributions.toml, which templates/partials/contributions.html renders.

    python3 design/contributions.py            # inside `nix develop`, with `gh` logged in
    GITHUB_TOKEN=... python3 design/contributions.py

Two sources are combined per repository: pull requests authored by the GitHub user (REST search,
for opened / merged counts) and the commits credited to the user on each repository's default
branch (GraphQL contributionsCollection, one query per year). The second catches work that landed
without a merged pull request, e.g. Homebrew's cherry-picked commits. Forks, private repositories
and the studio's own accounts are left out. A repository counts once something landed there.

Landed repositories are sorted into two categories: `major` (most merged pull requests, then
commits) and `popular` (most stars, at least POPULAR_MIN_STARS, not already major). Hand edits on
[[repo]] entries, `hide = true`, `pinned = true` (keeps the `category` set there) and a `summary`
shown instead of the description, are kept by name across runs; entries under [[manual]] are kept
as they are: they record contributions on other forges (Kitware GitLab, gitlab.com, Bitbucket)
that the GitHub API cannot see, each with its own `category`. Output order is deterministic so the diff stays readable.
"""
import datetime, json, os, pathlib, re, subprocess, sys, time, tomllib, urllib.parse, urllib.request

USER = "FlorianFranzen"
OWN = {"florianfranzen", "gliology", "neurosuite"}
MAJOR_MAX = 18            # repositories in each category (the site shows a multiple of three first)
POPULAR_MAX = 36
POPULAR_MIN_STARS = 500
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data/contributions.toml"

def token():
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        sys.exit("needs a GitHub token for the GraphQL API: set GITHUB_TOKEN or log in with `gh auth login`")

TOKEN = token()
PAUSE = 2.5               # seconds between search calls (30 per minute authenticated)

def request(url, body=None):
    req = urllib.request.Request(url, data=body and json.dumps(body).encode(), headers={
        "Accept": "application/vnd.github+json", "User-Agent": "fred.build-contributions",
        "Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def graphql(query, **variables):
    data = request("https://api.github.com/graphql", {"query": query, "variables": variables})
    if data.get("errors"):
        sys.exit(f"GraphQL: {data['errors']}")
    return data["data"]

def search(q):
    items, page = [], 1
    while True:
        data = request(f"https://api.github.com/search/issues?q={urllib.parse.quote(q)}&per_page=100&page={page}")
        items += data["items"]
        if len(items) >= data["total_count"] or not data["items"]:
            return items
        page += 1
        time.sleep(PAUSE)

def own(full):
    return full.split("/")[0].lower() in OWN

def clean(desc, name):
    """The repository description cut to a short line: no emoji, maintainer tags, parenthetical
    asides or self-naming prefix, first sentence only."""
    d = re.sub(r":[a-z0-9_+-]+:", "", desc or "")                                   # emoji shortcodes
    d = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]", "", d)              # emoji
    d = re.sub(r"\s*\[[^]]*\]|\s*\([^)]*\)", "", d)                                    # [maintainer=…], (with 2,500+ …)
    d = re.split(r"(?<=[.!?])\s+(?=[A-Z])", d.strip())[0].rstrip(".").strip()       # first sentence
    repo = name.split("/")[1]
    d = re.sub(rf"^{re.escape(repo)}\s*[:,–-]\s*", "", d, flags=re.I)                # "Rofi: A window …"
    return d[:1].upper() + d[1:] if re.match(r"[a-z]+\b", d) else d   # "a colorscheme …", not "i3-…"

# -- pull requests ----------------------------------------------------------------------------
print("searching pull requests…", file=sys.stderr)
prs = [pr for pr in search(f"author:{USER} type:pr") if not own(pr["repository_url"].split("/repos/")[1])]
time.sleep(PAUSE)
print("counting issues…", file=sys.stderr)
issues = request(f"https://api.github.com/search/issues?q={urllib.parse.quote(f'author:{USER} type:issue')}&per_page=1")["total_count"]

repos = {}
def repo(full):
    return repos.setdefault(full, {"prs": 0, "merged": 0, "commits": 0, "first": None, "last": None})

def seen(r, day):
    r["first"] = min(r["first"] or day, day)
    r["last"] = max(r["last"] or day, day)

for pr in prs:
    r = repo(pr["repository_url"].split("/repos/")[1])
    r["prs"] += 1
    if pr["pull_request"].get("merged_at"):
        r["merged"] += 1
    seen(r, pr["created_at"][:10])

# -- commits on default branches, one year at a time ------------------------------------------
QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      commitContributionsByRepository(maxRepositories: 100) {
        repository {
          nameWithOwner url description stargazerCount isArchived isFork isPrivate
          primaryLanguage { name }
        }
        contributions(first: 100) { totalCount nodes { occurredAt } }
      }
    }
  }
}"""
meta = {}
created = graphql("query($login: String!) { user(login: $login) { createdAt } }", login=USER)["user"]["createdAt"]
for year in range(int(created[:4]), datetime.date.today().year + 1):
    print(f"commits {year}…", file=sys.stderr)
    data = graphql(QUERY, login=USER, **{"from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"})
    for c in data["user"]["contributionsCollection"]["commitContributionsByRepository"]:
        g = c["repository"]
        full = g["nameWithOwner"]
        if g["isPrivate"] or g["isFork"] or own(full):
            continue
        r = repo(full)
        r["commits"] += c["contributions"]["totalCount"]
        for n in c["contributions"]["nodes"]:
            seen(r, n["occurredAt"][:10])
        meta[full] = {"url": g["url"], "description": clean(g["description"], full), "stars": g["stargazerCount"],
                      "language": (g["primaryLanguage"] or {}).get("name", ""), "archived": g["isArchived"]}

landed = {full: r for full, r in repos.items() if r["merged"] or r["commits"]}
for full in sorted(landed.keys() - meta.keys()):      # merged pull requests without credited commits
    m = request(f"https://api.github.com/repos/{full}")
    meta[full] = {"url": m["html_url"], "description": clean(m.get("description"), full), "stars": m.get("stargazers_count", 0),
                  "language": m.get("language") or "", "archived": m.get("archived", False)}
    time.sleep(0.5)

totals = {
    "prs": len(prs),
    "merged": sum(1 for pr in prs if pr["pull_request"].get("merged_at")),
    "open": sum(1 for pr in prs if pr["state"] == "open"),
    "commits": sum(r["commits"] for r in repos.values()),
    "repositories": len(repos),
    "owners": len({f.split("/")[0] for f in repos}),
    "first_year": min(r["first"] for r in repos.values())[:4],
    "last_year": max(r["last"] for r in repos.values())[:4],
    "issues": issues,
}

# -- the previous file: hand edits, manual entries, intro --------------------------------------
manual, intro, edits = [], "", {}
if OUT.exists():
    text = OUT.read_text()
    # the first [[manual]] table header (the file's own header comment mentions the name too),
    # together with the comment lines directly above it
    m = re.search(r"^(?:#.*\n)*\[\[manual\]\]$", text, flags=re.M)
    if m:
        manual_text = text[m.start():]
        manual_text = manual_text.split("\n[[repo]]")[0] if "\n[[repo]]" in manual_text else manual_text
        manual = [manual_text.rstrip("\n"), ""]
    for line in text.splitlines():
        if line.startswith("intro = "):
            intro = line
    for r in tomllib.loads(text).get("repo", []):
        if r.get("hide"):
            edits.setdefault(r["name"], {})["hide"] = True
        if r.get("summary"):
            edits.setdefault(r["name"], {})["summary"] = r["summary"]
        if r.get("pinned"):
            edits.setdefault(r["name"], {})["category"] = r["category"]

# -- categories -------------------------------------------------------------------------------
rows = [{"name": full, **meta[full], **r} for full, r in landed.items()]
by_name = {r["name"]: r for r in rows}
pinned = {n: e["category"] for n, e in edits.items() if "category" in e and n in by_name}
hidden = {n for n, e in edits.items() if e.get("hide")}

def pick(candidates, limit):
    out, shown = [], 0
    for r in candidates:
        if r["name"] in pinned:
            continue
        if r["name"] not in hidden:
            if shown == limit:
                break
            shown += 1
        out.append(r)
    return out

major = pick(sorted(rows, key=lambda r: (-r["merged"], -r["commits"], -r["stars"], r["name"])), MAJOR_MAX)
taken = {r["name"] for r in major}
popular = pick(sorted((r for r in rows if r["stars"] >= POPULAR_MIN_STARS and r["name"] not in taken),
                      key=lambda r: (-r["stars"], r["name"])), POPULAR_MAX)
major += [by_name[n] for n, c in sorted(pinned.items()) if c == "major"]
popular += [by_name[n] for n, c in sorted(pinned.items()) if c == "popular"]
major.sort(key=lambda r: (-r["merged"], -r["commits"], -r["stars"], r["name"]))
popular.sort(key=lambda r: (-r["stars"], r["name"]))

# -- output -----------------------------------------------------------------------------------
def q(s):
    return json.dumps(s, ensure_ascii=False)

lines = [f"# Generated by design/contributions.py on {datetime.date.today()}. Edit [[manual]] entries and, on [[repo]]",
         "# entries, `hide = true`, `pinned = true` (keeps the `category` you set) and `summary` (shown instead",
         "# of the description) by hand; everything else is overwritten on the next run.",
         f"generated = {datetime.date.today()}",
         intro or 'intro = "Most of the studio\'s code lands in other people\'s repositories. The numbers are generated from the public record on GitHub; a few contributions on other forges are listed by hand."',
         "", "[totals]"]
lines += [f"{k} = {v}" for k, v in totals.items()]
lines.append("")
lines += manual if manual else [
    "# Contributions the GitHub API does not see. `note` is shown where the merged count would be;",
    "# `category` is major or popular.",
    "[[manual]]",
    'name = "cmake/cmake"', 'url = "https://gitlab.kitware.com/cmake/cmake/-/merge_requests/5476"',
    'note = "1 merged · Kitware GitLab"', 'description = "FindProtobuf: support files with multiple extensions (2020)."',
    'category = "major"', "",
]
for category, group in (("major", major), ("popular", popular)):
    for r in group:
        lines += ["[[repo]]", f"name = {q(r['name'])}", f"category = {q(category)}", f"url = {q(r['url'])}",
                  f"description = {q(r['description'])}", f"language = {q(r['language'])}", f"stars = {r['stars']}",
                  f"prs = {r['prs']}", f"merged = {r['merged']}", f"commits = {r['commits']}",
                  f"first = {r['first']}", f"last = {r['last']}", f"archived = {str(r['archived']).lower()}"]
        if "summary" in edits.get(r["name"], {}):
            lines.append(f"summary = {q(edits[r['name']]['summary'])}")
        if r["name"] in pinned:
            lines.append("pinned = true")
        if r["name"] in hidden:
            lines.append("hide = true")
        lines.append("")
OUT.write_text("\n".join(lines).rstrip("\n") + "\n")
print(f"{OUT.relative_to(ROOT)}: {totals['prs']} PRs, {totals['merged']} merged, {totals['commits']} commits, "
      f"{totals['repositories']} repositories; {len(major)} major, {len(popular)} popular", file=sys.stderr)
