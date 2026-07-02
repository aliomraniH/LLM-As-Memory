#!/usr/bin/env python3
"""Minimal MCP streamable-HTTP client for MCP_Assist, plus the journal-then-write discipline.

- journal(entry): append the intended write (with its event_id) to .runs/journal.ndjson BEFORE
  any network attempt (SPINE.md §Buffered writes).
- call(tool, args): JSON-RPC tools/call against the endpoint; raises SpineUnavailable on
  transport failure so callers can continue the run and replay later.
- replay(): re-submit unacknowledged journal entries; same-event_id semantics make this safe.

Known failure modes (SPINE.md): -32600 "Session terminated" => wake/restart the Replit instance;
"No approval received" is a client-side Claude Code approval gate, not a server problem.
"""
import json, os, pathlib, time, urllib.error, urllib.request, uuid

ENDPOINT = "https://mcp-assist-memory.replit.app/mcp"
_REPO = pathlib.Path(__file__).resolve().parents[1]
JOURNAL = _REPO / ".runs" / "journal.ndjson"
ENV_FILE = _REPO / "settings" / "spine.env"


def _auth_token():
    """SPINE_AUTH_TOKEN from the environment, else from settings/spine.env (gitignored)."""
    tok = os.environ.get("SPINE_AUTH_TOKEN")
    if tok:
        return tok
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line.startswith("SPINE_AUTH_TOKEN="):
                return line.split("=", 1)[1].strip().strip("'\"") or None
    return None


class SpineUnavailable(Exception):
    pass


class SpineClient:
    def __init__(self, endpoint: str = ENDPOINT):
        self.endpoint = endpoint
        self._session_id = None
        self._auth_token = _auth_token()

    # --- transport -------------------------------------------------------
    def _post(self, payload: dict) -> dict:
        req = urllib.request.Request(
            self.endpoint, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Accept": "application/json, text/event-stream",
                     **({"Authorization": f"Bearer {self._auth_token}"} if self._auth_token else {}),
                     **({"Mcp-Session-Id": self._session_id} if self._session_id else {})})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                sid = r.headers.get("Mcp-Session-Id")
                if sid:
                    self._session_id = sid
                body = r.read().decode()
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise SpineUnavailable(
                    "HTTP 401 Unauthorized — the spine requires auth; set SPINE_AUTH_TOKEN "
                    "(env var, or settings/spine.env from settings/spine.env.example)") from e
            raise SpineUnavailable(str(e)) from e
        except Exception as e:  # DNS, TLS, 5xx, timeout
            raise SpineUnavailable(str(e)) from e
        # streamable HTTP may answer as SSE
        if body.lstrip().startswith("event:") or "\ndata:" in body or body.lstrip().startswith("data:"):
            for line in body.splitlines():
                if line.startswith("data:"):
                    body = line[5:].strip()
                    break
        try:
            return json.loads(body) if body.strip() else {}
        except json.JSONDecodeError as e:
            raise SpineUnavailable(f"non-JSON response: {body[:200]}") from e

    def _ensure_init(self):
        if self._session_id:
            return
        resp = self._post({"jsonrpc": "2.0", "id": 0, "method": "initialize",
                           "params": {"protocolVersion": "2025-03-26",
                                      "capabilities": {},
                                      "clientInfo": {"name": "skill-transfer-harness", "version": "0.1"}}})
        if "error" in resp:
            raise SpineUnavailable(f"initialize failed: {resp['error']}")
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def call(self, tool: str, args: dict):
        self._ensure_init()
        resp = self._post({"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "tools/call",
                           "params": {"name": tool, "arguments": args}})
        if "error" in resp:
            code = resp["error"].get("code")
            if code == -32600:
                raise SpineUnavailable("-32600 Session terminated (wake/restart Replit, then replay)")
            raise SpineUnavailable(json.dumps(resp["error"]))
        result = resp.get("result", {})
        # A tool-level failure (isError) must not be returned as if it were data: doing so let
        # write_with_journal mark a dropped write "acked". Surface it so the write stays pending.
        if isinstance(result, dict) and result.get("isError"):
            msg = next((c.get("text", "") for c in (result.get("content") or [])
                        if c.get("type") == "text"), "")
            raise SpineUnavailable(f"tool error: {msg[:300]}")
        content = result.get("content") or []
        for c in content:
            if c.get("type") == "text":
                try:
                    return json.loads(c["text"])
                except json.JSONDecodeError:
                    return c["text"]
        return result

    # --- journal-then-write ----------------------------------------------
    @staticmethod
    def journal(tool: str, args: dict) -> None:
        JOURNAL.parent.mkdir(parents=True, exist_ok=True)
        with JOURNAL.open("a") as fh:
            fh.write(json.dumps({"tool": tool, "args": args, "acked": False,
                                 "journaled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}) + "\n")

    def write_with_journal(self, tool: str, args: dict):
        assert "event_id" in args, "spine writes require a stable event_id (idempotency)"
        self.journal(tool, args)
        try:
            out = self.call(tool, args)
            self._mark_acked(args["event_id"])
            return out
        except SpineUnavailable:
            return None  # run continues; replay() resubmits later

    @staticmethod
    def _mark_acked(event_id: str) -> None:
        if not JOURNAL.exists():
            return
        lines = []
        for line in JOURNAL.read_text().splitlines():
            obj = json.loads(line)
            if obj["args"].get("event_id") == event_id:
                obj["acked"] = True
            lines.append(json.dumps(obj))
        JOURNAL.write_text("\n".join(lines) + "\n")

    def replay(self, max_attempts: int = 10, backoff_s: int = 30) -> int:
        """Resubmit unacked entries until acknowledged. Returns count still pending."""
        if not JOURNAL.exists():
            return 0
        for attempt in range(max_attempts):
            pending = [json.loads(l) for l in JOURNAL.read_text().splitlines()
                       if not json.loads(l)["acked"]]
            if not pending:
                return 0
            for obj in pending:
                try:
                    self.call(obj["tool"], obj["args"])
                    self._mark_acked(obj["args"]["event_id"])
                except SpineUnavailable:
                    pass
            if attempt < max_attempts - 1:
                time.sleep(backoff_s)
        return sum(1 for l in JOURNAL.read_text().splitlines() if not json.loads(l)["acked"])
