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
        if path.endswith("/rulesets") and method == "GET": out([])
        if path.endswith("environments/production") and method == "GET": sys.exit(1)
        if "collaborators" in path and method == "GET": sys.exit(1)
        if path.count("/") == 2 and method == "GET":
            out({"permissions": {"admin": True}, "private": False, "security_and_analysis": {}})
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
