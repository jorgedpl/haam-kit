"""Stand-ins for the GitHub CLI and the Linear API, so the setup tool can be tested offline."""

import json
import os
import stat
import textwrap
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

FAKE_GH = textwrap.dedent('''\
    #!/usr/bin/env python3
    import json, os, sys
    a = sys.argv[1:]
    body = sys.stdin.read() if "--input" in a else ""
    with open(os.environ["FAKE_GH_LOG"], "a") as f:
        f.write(json.dumps({"args": a, "body": body}) + "\\n")
    def out(x):
        print(json.dumps(x)); sys.exit(0)
    if a[:2] == ["auth", "status"]: sys.exit(0)
    if a[:2] == ["label", "list"]: out([{"name": "uat-passed"}])
    if a[:2] in (["label", "create"], ["variable", "set"]): sys.exit(0)
    if a[:2] == ["secret", "list"]: out([])
    if a and a[0] == "api":
        method = a[a.index("-X") + 1] if "-X" in a else "GET"
        path = next(x for x in a[1:] if x.startswith(("repos/", "users/")))
        if path.startswith("users/"): print("583231"); sys.exit(0)
        rs = os.environ.get("FAKE_GH_RULESET")
        if path.endswith("/rulesets") and method == "GET": out([{"id": 1, "name": "HAAM main protection"}] if rs else [])
        if path.endswith("/rulesets/1") and method == "GET": out(json.load(open(rs)))
        if path.endswith("environments/production") and method == "GET": sys.exit(1)
        if (path.endswith("environments/production") and method == "PUT" and os.environ.get("FAKE_GH_ENV_422")
                and json.loads(body).get("reviewers")):
            print("gh: Failed to create the environment protection rule (HTTP 422)", file=sys.stderr); sys.exit(1)
        if "collaborators" in path and method == "GET": sys.exit(1)
        if path.count("/") == 2 and method == "GET":
            out({"permissions": {"admin": True}, "private": bool(os.environ.get("FAKE_GH_PRIVATE")), "security_and_analysis": {}})
        out({})
    sys.exit(0)
    ''')


def install_fake_gh(bin_dir: Path):
    bin_dir.mkdir(parents=True, exist_ok=True)
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH)
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    return gh


GOOD_KEY = "lin_api_TEST"


class FakeLinear:
    """Minimal Linear GraphQL stand-in, starting from a team with Linear's default statuses."""

    def __init__(self):
        self.calls = []
        self.state = {
            "team": {"id": "t1", "key": "ACM", "name": "Acme", "triageEnabled": False,
                     "states": {"nodes": [
                         {"id": "s1", "name": "Backlog", "type": "backlog", "position": 0},
                         {"id": "s2", "name": "Todo", "type": "unstarted", "position": 1},
                         {"id": "s3", "name": "In Progress", "type": "started", "position": 2},
                         {"id": "s4", "name": "Done", "type": "completed", "position": 3},
                         {"id": "s5", "name": "Canceled", "type": "canceled", "position": 4},
                         {"id": "s6", "name": "Duplicate", "type": "canceled", "position": 5}]}},
            "labels": [{"id": "l1", "name": "Bug", "team": None}],
        }
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                fake.calls.append({"auth": self.headers.get("Authorization"), **body})
                data, errors = fake.answer(self.headers.get("Authorization"), body["query"], body.get("variables") or {})
                payload = {"data": data}
                if errors:
                    payload["errors"] = errors
                raw = json.dumps(payload).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/graphql"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()

    def answer(self, auth, q, v):
        if auth != GOOD_KEY:
            return None, [{"message": "Authentication required"}]
        t = self.state["team"]
        if "viewer" in q:
            return {"viewer": {"name": "Test Admin", "email": "admin@example.com", "organization": {"name": "Example"}}}, None
        if "teamCreate" in q:
            return {"teamCreate": {"success": True, "team": t}}, None
        if "teams(" in q:
            return {"teams": {"nodes": [t] if v.get("k") == t["key"] else []}}, None
        if "teamUpdate" in q:
            t["triageEnabled"] = True
            t["states"]["nodes"].append({"id": "s7", "name": "Triage", "type": "triage", "position": -1})
            return {"teamUpdate": {"success": True}}, None
        if "team(" in q:
            return {"team": t}, None
        if "workflowStateUpdate" in q:
            for s in t["states"]["nodes"]:
                if s["id"] == v["id"]:
                    s["name"] = v["i"]["name"]
            return {"workflowStateUpdate": {"success": True}}, None
        if "workflowStateCreate" in q:
            i = v["i"]
            t["states"]["nodes"].append({"id": "n" + i["name"], "name": i["name"], "type": i["type"], "position": i["position"]})
            return {"workflowStateCreate": {"success": True}}, None
        if "issueLabels" in q:
            return {"issueLabels": {"nodes": self.state["labels"], "pageInfo": {"hasNextPage": False, "endCursor": None}}}, None
        if "issueLabelCreate" in q:
            self.state["labels"].append({"id": "x" + v["i"]["name"], "name": v["i"]["name"], "team": {"id": v["i"]["teamId"]}})
            return {"issueLabelCreate": {"success": True}}, None
        if "__schema" in q:
            return {"__schema": {"mutationType": {"fields": [{"name": "organizationInviteCreate"}]}}}, None
        if "__type" in q:
            return {"__type": {"inputFields": [{"name": "email"}, {"name": "teamIds"}, {"name": "role"}]}}, None
        if "organizationInviteCreate" in q:
            return {"organizationInviteCreate": {"success": True}}, None
        return None, [{"message": "unknown query in fake"}]

    def mutations(self):
        return [c["query"] for c in self.calls if c["query"].lstrip().startswith("mutation")]


# ----------------------------------------------------------------------------- GitHub Projects stand-in

FAKE_GH_PROJECTS = r'''#!/usr/bin/env python3
"""Stateful stand-in for the gh CLI covering what haam.py uses for GitHub Projects."""
import json, os, subprocess, sys
STATE = os.environ["FAKE_GH_STATE"]
LOG = os.environ.get("FAKE_GH_LOG")
a = sys.argv[1:]
stdin = sys.stdin.read() if ("--input" in a) else ""
if LOG:
    with open(LOG, "a") as f:
        f.write(json.dumps({"args": a, "body": stdin}) + "\n")
st = json.load(open(STATE)) if os.path.exists(STATE) else {
    "me": "tester", "projects": [], "issues": {}, "items": [], "next_issue": 1, "next_id": 1,
    "comments": [], "labels": [], "secrets": [], "prs": {}}
def save():
    json.dump(st, open(STATE, "w"))
def nid(prefix):
    st["next_id"] += 1
    return f"{prefix}_{st['next_id']}"
def out(x):
    save(); print(json.dumps(x)); sys.exit(0)
def opt(a, name, default=None):
    return a[a.index(name) + 1] if name in a else default
def opts(a, name):
    return [a[i + 1] for i, x in enumerate(a) if x == name]
def proj_view(p):
    return {"id": p["id"], "number": p["number"], "url": p["url"], "title": p["title"],
            "items": {"totalCount": len([i for i in st["items"] if i["project"] == p["id"]])},
            "fields": {"nodes": [{"__typename": "ProjectV2SingleSelectField", "id": f["id"], "name": f["name"],
                                  "options": f["options"]} for f in p["fields"]]}}
def values(item):
    out_ = []
    p = next(p for p in st["projects"] if p["id"] == item["project"])
    for f in p["fields"]:
        oid = item["values"].get(f["id"])
        o = next((o for o in f["options"] if o["id"] == oid), None)
        if o:
            out_.append({"name": o["name"], "field": {"name": f["name"]}})
    return out_
def issue_view(n):
    i = st["issues"][str(n)]
    items = [it for it in st["items"] if it["issue"] == n]
    return {"id": i["id"], "number": n, "title": i["title"], "state": i["state"], "url": i["url"], "body": i["body"],
            "createdAt": i["created"],
            "parent": {"number": i["parent"], "repository": {"nameWithOwner": "example-org/example-app"}} if i.get("parent") else None,
            "assignees": {"nodes": [{"login": x} for x in i["assignees"]]},
            "labels": {"nodes": [{"name": x} for x in i["labels"]]},
            "projectItems": {"nodes": [{"id": it["id"], "project": {"id": it["project"], "number": next(
                p["number"] for p in st["projects"] if p["id"] == it["project"])},
                "fieldValues": {"nodes": values(it)}} for it in items]}}

if a[:2] == ["auth", "status"]:
    print("Token scopes: 'gist', 'project', 'repo'"); sys.exit(0)
if a[:2] == ["label", "list"]:
    out([{"name": x} for x in st["labels"]])
if a[:2] == ["label", "create"]:
    st["labels"].append(a[2]); save(); sys.exit(0)
if a[:2] == ["secret", "list"]:
    out([{"name": x} for x in st["secrets"]])
if a[:2] == ["issue", "create"]:
    n = st["next_issue"]; st["next_issue"] += 1
    st["issues"][str(n)] = {"id": nid("I"), "title": opt(a, "--title"), "body": opt(a, "--body", ""), "state": "OPEN",
                            "url": f"https://github.com/example-org/example-app/issues/{n}", "labels": opts(a, "--label"),
                            "assignees": [], "created": f"2026-01-01T00:00:{n:02d}Z"}
    save(); print(f"https://github.com/example-org/example-app/issues/{n}"); sys.exit(0)
if a[:2] == ["issue", "edit"]:
    i = st["issues"][a[2]]
    if "--title" in a:
        i["title"] = opt(a, "--title")
    if "--body" in a:
        i["body"] = opt(a, "--body")
    for x in opts(a, "--add-assignee"):
        i["assignees"].append(st["me"] if x == "@me" else x)
    for x in opts(a, "--add-label"):
        i["labels"].append(x)
    for x in opts(a, "--remove-label"):
        i["labels"] = [l for l in i["labels"] if l != x]
    save(); sys.exit(0)
if a[:2] == ["issue", "view"]:
    out({"comments": [{"body": c["body"]} for c in st["comments"] if c["issue"] == int(a[2])]})
if a[:2] == ["issue", "comment"]:
    st["comments"].append({"issue": int(a[2]), "body": opt(a, "--body")}); save(); sys.exit(0)
if a[:2] == ["issue", "close"]:
    st["issues"][a[2]]["state"] = "CLOSED"; save(); sys.exit(0)
def origin_head(branch):
    o = os.environ.get("FAKE_GH_ORIGIN")
    if not o or not branch:
        return None
    r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", branch], cwd=o, capture_output=True, text=True)
    return r.stdout.strip() or None
if a[:2] == ["pr", "view"]:
    p = st["prs"][a[2]]
    if os.environ.get("FAKE_GH_ORIGIN") and not p.get("pinned_head"):
        p["headRefOid"] = origin_head(p.get("headRefName"))
    out(p)
if a[:2] == ["pr", "create"]:
    n = str(100 + len(st["prs"]))
    st["prs"][n] = {"title": opt(a, "--title"), "body": open(opt(a, "--body-file")).read(), "headRefName": opt(a, "--head"),
                    "state": "OPEN", "isDraft": False, "labels": [{"name": l} for l in opts(a, "--label")],
                    "url": f"https://github.com/example-org/example-app/pull/{n}", "headRefOid": origin_head(opt(a, "--head"))}
    save(); print(st["prs"][n]["url"]); sys.exit(0)
if a[:2] == ["pr", "edit"]:
    p = st["prs"][a[2]]
    p["labels"] += [{"name": l} for l in opts(a, "--add-label") if {"name": l} not in p["labels"]]
    p["labels"] = [l for l in p["labels"] if l["name"] not in opts(a, "--remove-label")]
    save(); sys.exit(0)
if a[:2] == ["pr", "list"]:
    want = {"open": "OPEN", "merged": "MERGED"}.get(opt(a, "--state", "open"))
    out([dict(p, number=int(k)) for k, p in st["prs"].items() if p.get("state", "OPEN") == want])
if a[:2] == ["pr", "checks"]:
    if st.get("no_checks"):
        st["no_checks"] -= 1; save()
        print("no checks reported on the 'x' branch", file=sys.stderr); sys.exit(1)
    if st.get("checks_pending"):
        st["checks_pending"] -= 1; save()
        print(json.dumps([{"name": "ci", "bucket": "pass"}, {"name": "release-gate", "bucket": "pending"}])); sys.exit(8)
    out(st["prs"][a[2]].get("checks", [{"name": "ci", "bucket": "pass"}, {"name": "release-gate", "bucket": "pass"}]))
if a[:2] == ["pr", "merge"]:
    p = st["prs"][a[2]]
    m = opt(a, "--match-head-commit")
    if m and m != p.get("headRefOid"):
        print("Head branch was modified", file=sys.stderr); sys.exit(1)
    p["state"] = "MERGED"; p["mergeCommit"] = {"oid": "abc123"}; p["mergedAt"] = "2026-01-01T00:00:00Z"
    p.setdefault("files", [{"path": "src/export.py"}])
    st.setdefault("runs", []).append({"databaseId": 7, "status": "waiting", "conclusion": "", "url": "https://run/7",
                                      "headSha": "abc123"})
    save(); sys.exit(0)
if a[:2] == ["run", "list"]:
    out([r for r in st.get("runs", []) if r["headSha"] == opt(a, "--commit")])
if a[:2] == ["variable", "list"]:
    out([{"name": k, "value": v} for k, v in st.get("variables", {}).items()])
if a[:2] == ["variable", "set"]:
    st.setdefault("variables", {})[a[2]] = opt(a, "--body"); save(); sys.exit(0)
if a[:2] == ["variable", "delete"]:
    st.setdefault("variables", {}).pop(a[2], None); save(); sys.exit(0)
if a and a[0] == "api" and len(a) > 1 and "/actions/runs?" in a[1]:
    out({"workflow_runs": st.get("runs_api", [])})
if a and a[0] == "api" and len(a) > 1 and a[1].split("?")[0].endswith("/jobs"):
    rid = a[1].split("/actions/runs/")[1].split("/")[0]
    out({"jobs": st.get("jobs_api", {}).get(rid, [])})
if a and a[0] == "api" and len(a) > 3 and "/statuses/" in a[3]:
    st.setdefault("statuses", []).append(dict(json.loads(stdin), sha=a[3].rsplit("/", 1)[-1])); save(); out({})
if a and a[0] == "api" and len(a) > 3 and a[3].endswith("/statuses"):
    sha = a[3].split("/commits/")[1].split("/")[0]
    out([x for x in st.get("statuses", []) if x.get("sha") == sha])
if a and a[0] == "api" and len(a) > 3 and a[3].endswith("/pending_deployments"):
    if a[2] == "GET":
        out([{"environment": {"id": 1, "name": "production"}}])
    for r in st.get("runs", []):
        r["status"], r["conclusion"] = "completed", "success"
    st["approved"] = json.loads(stdin) if stdin else True
    out([])
if a and a[0] == "api" and a[2:3] == ["DELETE"]:
    st.setdefault("deleted_refs", []).append(a[3]); out({})
if a[:2] == ["api", "user"]:
    print(st["me"]); sys.exit(0)
if a[:2] == ["api", "graphql"]:
    req = json.loads(stdin); q = req["query"]; v = req.get("variables") or {}
    if "createProjectV2Field" in q:
        p = next(p for p in st["projects"] if p["id"] == v["p"])
        p["fields"].append({"id": nid("F"), "name": "Priority", "options": [{"id": nid("O"), "name": o["name"]} for o in v["o"]]})
        out({"data": {"createProjectV2Field": {"projectV2Field": {"id": "x"}}}})
    if "updateProjectV2Field(" in q:
        for p in st["projects"]:
            for f in p["fields"]:
                if f["id"] == v["f"]:
                    f["options"] = [{"id": nid("O"), "name": o["name"]} for o in v["o"]]
        out({"data": {"updateProjectV2Field": {"projectV2Field": {"id": v["f"]}}}})
    if "createProjectV2(" in q:
        n = len(st["projects"]) + 1
        p = {"id": nid("PVT"), "number": n, "title": v["t"], "url": f"https://github.com/users/example-org/projects/{n}",
             "fields": [{"id": nid("F"), "name": "Status", "options": [{"id": nid("O"), "name": x} for x in ("Todo", "In Progress", "Done")]}]}
        st["projects"].append(p)
        out({"data": {"createProjectV2": {"projectV2": {"number": n, "url": p["url"]}}}})
    if "linkProjectV2ToRepository" in q or "updateProjectV2Collaborators" in q:
        out({"data": {"x": {"repository": {"id": "R1"}}}})
    if "projectsV2(first:100)" in q:
        out({"data": {"repositoryOwner": {"id": "U1", "__typename": "User", "projectsV2": {"nodes": [
            {"number": p["number"], "title": p["title"], "url": p["url"]} for p in st["projects"]]}}}})
    if "projectV2(number:" in q:
        p = next((p for p in st["projects"] if p["number"] == v["n"]), None)
        out({"data": {"repositoryOwner": {"projectV2": proj_view(p) if p else None}}})
    if "removeSubIssue" in q:
        cn = next(int(k) for k, i in st["issues"].items() if i["id"] == v["c"])
        st["issues"][str(cn)].pop("parent", None)
        out({"data": {"removeSubIssue": {"issue": {"number": 0}}}})
    if "subIssues(first:100)" in q:
        pi = st["issues"].get(str(v["n"]))
        kids = [{"number": int(k), "title": i["title"], "state": i["state"],
                 "repository": {"nameWithOwner": "example-org/example-app"}}
                for k, i in st["issues"].items() if i.get("parent") == v["n"]]
        out({"data": {"repository": {"issue": {"id": pi["id"], "subIssues": {"nodes": kids}} if pi else None}}})
    if "addSubIssue" in q:
        pn = next(int(k) for k, i in st["issues"].items() if i["id"] == v["p"])
        cn = next(int(k) for k, i in st["issues"].items() if i["id"] == v["c"])
        st["issues"][str(cn)]["parent"] = pn
        out({"data": {"addSubIssue": {"issue": {"number": pn}, "subIssue": {"number": cn}}}})
    if "issue(number:" in q:
        out({"data": {"repository": {"issue": issue_view(v["n"]) if str(v["n"]) in st["issues"] else None}}})
    if "repository(owner:$o,name:$r){ id }" in q:
        out({"data": {"repository": {"id": "R1"}}})
    if "addProjectV2ItemById" in q:
        n = next(int(k) for k, i in st["issues"].items() if i["id"] == v["c"])
        it = {"id": nid("PVTI"), "project": v["p"], "issue": n, "values": {}}
        st["items"].append(it)
        out({"data": {"addProjectV2ItemById": {"item": {"id": it["id"]}}}})
    if "updateProjectV2ItemFieldValue" in q:
        it = next(i for i in st["items"] if i["id"] == v["i"])
        it["values"][v["f"]] = v["o"]
        out({"data": {"updateProjectV2ItemFieldValue": {"projectV2Item": {"id": it["id"]}}}})
    if "items(first:100" in q:
        nodes = []
        for it in st["items"]:
            if it["project"] != v["p"]:
                continue
            iv = issue_view(it["issue"])
            nodes.append({"id": it["id"], "content": {"__typename": "Issue", "number": it["issue"], "title": iv["title"],
                          "state": iv["state"], "url": iv["url"], "createdAt": iv["createdAt"], "parent": iv["parent"],
                          "repository": {"nameWithOwner": "example-org/example-app"},
                          "assignees": iv["assignees"], "labels": iv["labels"]},
                          "fieldValues": {"nodes": values(it)}})
        out({"data": {"node": {"items": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": nodes}}}})
    out({"errors": [{"message": "fake gh: unhandled query"}]})
if a and a[0] == "api":
    out({"permissions": {"admin": True}, "private": bool(os.environ.get("FAKE_GH_PRIVATE"))})
sys.exit(0)
'''


def install_fake_gh_projects(bin_dir: Path):
    bin_dir.mkdir(parents=True, exist_ok=True)
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH_PROJECTS)
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    return gh
