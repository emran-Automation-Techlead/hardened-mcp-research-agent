"""Build docs/Hardened-MCP-Agent-Guide.pdf  (run: python docs/build_pdf.py)."""
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

import ast
import json
import re
from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.platypus import Image, KeepTogether

HERE = Path(__file__).parent
ROOT = HERE.parent
OUT = HERE / "Hardened-MCP-Agent-Guide.pdf"
ASSETS = HERE / "assets"
ASSETS.mkdir(exist_ok=True)
NAVY = colors.HexColor("#16213e")
BLUE = colors.HexColor("#0f3460")
GREEN = colors.HexColor("#1f9d55")
ORANGE = colors.HexColor("#d9822b")
RED = colors.HexColor("#c0392b")
LIGHT = colors.HexColor("#eef2f7")

ss = getSampleStyleSheet()
body = ParagraphStyle("body", parent=ss["Normal"], fontSize=10, leading=14.5, spaceAfter=6)
title = ParagraphStyle("title", parent=ss["Title"], fontSize=26, textColor=NAVY, spaceAfter=6)
sub = ParagraphStyle("sub", parent=body, fontSize=11.5, textColor=BLUE, alignment=1)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=17, textColor=NAVY, spaceBefore=6, spaceAfter=8)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12.5, textColor=BLUE, spaceBefore=10, spaceAfter=4)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=3)
code = ParagraphStyle("code", fontName="Courier", fontSize=7.8, leading=10.3, backColor=LIGHT,
                      borderPadding=6, leftIndent=4, spaceBefore=4, spaceAfter=10)
cell = ParagraphStyle("cell", parent=body, fontSize=8.8, leading=11.5, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)


def P(t, s=body): return Paragraph(t, s)
def B(items): return [Paragraph(i, bullet, bulletText="-") for i in items]
def C(t): return Preformatted(t.strip("\n"), code)


def table(rows, widths):
    data = [[Paragraph(str(c), cellb if r == 0 else cell) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c5cdd8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]))
    return t



# ---------------------------------------------------------------- live evidence
def load_verifier():
    """Exec the real grounding check from the agent source (no model calls)."""
    src = (ROOT / "src" / "hardened_mcp_agent.py").read_text(encoding="utf-8")
    a = src.index("import html\nimport urllib.request")
    b = src.index("from openai import RateLimitError")
    ns = {"Path": Path, "re": re}
    exec(src[a:b], ns)
    return ns["grounding_problems"]


def table_rows(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.strip().startswith("|") and len(cols) >= 5 and cols[0].isdigit():
            rows.append(cols)
    return rows


audit = [json.loads(l) for l in (ROOT / "security-audit" / "mcp-audit.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
traced = [e for e in audit if e["trace_id"]]
N_EVENTS, N_TRACES = len(audit), len({e["trace_id"] for e in traced})
STATUS_ALL = Counter(e["status"] for e in audit)
TOOLS = Counter(e["tool"] for e in traced if e["status"] == "permitted")

RUNS = [  # (file, trace id prefix, what happened, lesson)
    ("run1-azure-feed-blocked-by-robots.md", "trace_6b86b3b3",
     "Azure feed refused: azure.microsoft.com/robots.txt disallows autonomous fetching of /blog/feed/. "
     "Agent disclosed the Azure gap, but AWS rows 8-10 were not the feed's first 10 items.",
     "Respect robots.txt: Azure source moved to the allowed blog index page. Exact feed order now enforced."),
    ("run2-passed-format-check-but-fabricated.md", "trace_961fdf45",
     "Table had ranks 1-20 and passed the format check, but AWS titles 5-10 and Azure URLs 19-20 were invented.",
     "A format check cannot detect fabrication. Added an independent grounding check."),
    ("run3-aws-grounded-azure-timeout.md", "trace_86f79b9d",
     "Retry loop fixed AWS (10/10 real). Azure fetch timed out; agent honestly returned no Azure rows.",
     "Grounding + retry works. Added explicit size/timeout-retry instructions."),
    ("run4-blank-azure-rows.md", "trace_20922c57",
     "Passed, but Azure rows had no URLs and ranks 19-20 were blank. The empty string counted as 'found'.",
     "Tightened the verifier: non-empty https URL required; exact article-link order for Azure."),
    ("run5-one-bad-url.md", "trace_e2332228",
     "19 of 20 rows grounded; rank 20 carried a wrong Azure URL after 3 retries.",
     "Defined Azure 'latest 10' as the first 10 article links in page order; verifier enforces it."),
]

verify = load_verifier()
RUN_SCORES = []
for fname, *_ in RUNS:
    path = HERE / "run-history" / fname
    bad = {int(m) for pr in verify(path) for m in re.findall(r"Rank (\d+)", pr)}
    rows = table_rows(path)
    RUN_SCORES.append(max(0, len(rows) - len(bad & {int(r[0]) for r in rows})))

# Reference table pulled straight from the live public sources by the verifier's own
# rules (no model involved). Titles for Azure come from the page anchors.
LIVE = json.loads((HERE / "run-history" / "live-reference.json").read_text(encoding="utf-8"))

CATEGORY = {  # analyst classification of the 20 live posts (primary category)
    1: "Compute", 2: "Community", 3: "Roundup", 4: "Dev tools", 5: "Roundup", 6: "Data",
    7: "Roundup", 8: "Roundup", 9: "Security", 10: "Networking",
    11: "AI/ML", 12: "AI/ML", 13: "AI/ML", 14: "Compute", 15: "AI/ML",
    16: "AI/ML", 17: "AI/ML", 18: "Reliability", 19: "Compute", 20: "Data",
}

# ---------------------------------------------------------------- charts
INK, BLU, GRN, ORG, RDD = "#16213e", "#0f3460", "#1f9d55", "#d9822b", "#c0392b"


def style(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(colors="#444", labelsize=8)
    ax.title.set_color(INK)


def chart_tools():
    fig, ax = plt.subplots(figsize=(6.4, 2.6), dpi=200)
    items = TOOLS.most_common()[::-1]
    ax.barh([k for k, _ in items], [v for _, v in items], color=BLU)
    for i, (_, v) in enumerate(items):
        ax.text(v + 1, i, str(v), va="center", fontsize=8, color=INK)
    ax.set_title(f"Permitted MCP tool calls across {N_TRACES} traced runs", fontsize=10, loc="left")
    style(ax)
    fig.tight_layout()
    fig.savefig(ASSETS / "tool_calls.png")
    plt.close(fig)


def chart_status():
    order = ["requested", "permitted", "succeeded", "blocked", "tool_error"]
    colors_ = [BLU, "#4a6fa5", GRN, RDD, ORG]
    vals = [STATUS_ALL.get(k, 0) for k in order]
    fig, ax = plt.subplots(figsize=(6.4, 2.6), dpi=200)
    ax.bar(order, vals, color=colors_)
    for i, v in enumerate(vals):
        ax.text(i, v + 5, str(v), ha="center", fontsize=8, color=INK)
    ax.set_title(f"Audit events by status ({N_EVENTS} records)", fontsize=10, loc="left")
    style(ax)
    fig.tight_layout()
    fig.savefig(ASSETS / "audit_status.png")
    plt.close(fig)


def chart_categories():
    cats = sorted({v for v in CATEGORY.values()})
    aws = [sum(1 for k, v in CATEGORY.items() if k <= 10 and v == c) for c in cats]
    az = [sum(1 for k, v in CATEGORY.items() if k > 10 and v == c) for c in cats]
    fig, ax = plt.subplots(figsize=(6.4, 2.9), dpi=200)
    x = range(len(cats))
    ax.bar([i - 0.2 for i in x], aws, 0.4, label="AWS", color=ORG)
    ax.bar([i + 0.2 for i in x], az, 0.4, label="Azure", color=BLU)
    ax.set_xticks(list(x))
    ax.set_xticklabels(cats, fontsize=8)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Latest 10 posts per provider, by primary category (single snapshot)", fontsize=10, loc="left")
    style(ax)
    fig.tight_layout()
    fig.savefig(ASSETS / "categories.png")
    plt.close(fig)


def chart_runs():
    fig, ax = plt.subplots(figsize=(6.4, 2.6), dpi=200)
    labels = [f"Run {i}" for i in range(1, len(RUN_SCORES) + 1)]
    ax.bar(labels, RUN_SCORES, color=[ORG if v < 20 else GRN for v in RUN_SCORES])
    ax.axhline(20, color=GRN, ls="--", lw=1)
    ax.text(len(labels) - 0.5, 20.4, "target: 20 grounded rows", ha="right", fontsize=7.5, color=GRN)
    for i, v in enumerate(RUN_SCORES):
        ax.text(i, v + 0.4, f"{v}/20", ha="center", fontsize=8, color=INK)
    ax.set_ylim(0, 23)
    ax.set_title("Rows that survive the final grounding check, per real run", fontsize=10, loc="left")
    style(ax)
    fig.tight_layout()
    fig.savefig(ASSETS / "run_progress.png")
    plt.close(fig)


for fn in (chart_tools, chart_status, chart_categories, chart_runs):
    fn()


def img(name, width=165 * mm):
    from PIL import Image as PILImage
    w, h = PILImage.open(ASSETS / name).size
    return Image(str(ASSETS / name), width=width, height=width * h / w)


def clean(t):
    return t.replace("\u2019", "'").replace("\u2018", "'").replace("\u2013", "-").replace("\u2014", "-")


def verification_loop():
    d = Drawing(500, 120)
    box(d, 5, 40, 95, 44, "Agent writes\nreport", NAVY)
    box(d, 135, 40, 120, 44, "Grounding verifier\nre-reads both sources", RED)
    box(d, 290, 70, 100, 36, "Problems found?\nretry (max 3)", ORANGE, 7.5)
    box(d, 290, 12, 100, 36, "All rows grounded\nPASS", GREEN, 7.5)
    box(d, 410, 40, 85, 44, "Step 8\nfinal asserts", BLUE)
    arrow(d, 100, 62, 135, 62)
    arrow(d, 255, 70, 290, 88)
    arrow(d, 255, 54, 290, 30)
    arrow(d, 340, 106, 52, 106, ORANGE)
    arrow(d, 52, 106, 52, 84, ORANGE, "rewrite with problem list")
    arrow(d, 390, 30, 410, 54)
    return d

# ---------------------------------------------------------------- diagram
def box(d, x, y, w, h, text, fill, size=8):
    d.add(Rect(x, y, w, h, rx=4, ry=4, fillColor=fill, strokeColor=NAVY, strokeWidth=0.8))
    lines = text.split("\n")
    top = y + h / 2 + (len(lines) - 1) * size / 2 - size * 0.3
    for i, ln in enumerate(lines):
        d.add(String(x + w / 2, top - i * (size + 1.5), ln, fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                     fontSize=size, fillColor=colors.white, textAnchor="middle"))


def arrow(d, x1, y1, x2, y2, color=NAVY, label=None):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.1))
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    s = 5
    d.add(Polygon([x2, y2, x2 - s * math.cos(a - .4), y2 - s * math.sin(a - .4),
                   x2 - s * math.cos(a + .4), y2 - s * math.sin(a + .4)], fillColor=color, strokeColor=color))
    if label:
        d.add(String((x1 + x2) / 2 + 3, (y1 + y2) / 2 + 3, label, fontName="Helvetica", fontSize=7, fillColor=color))


def architecture():
    d = Drawing(500, 300)
    box(d, 10, 235, 100, 42, "Task input\nProject Nimbus", BLUE)
    box(d, 150, 235, 130, 42, "Cloud Research Agent\ngpt-4.1 (Agents SDK)", NAVY)
    box(d, 330, 235, 150, 42, "Trace (trace_id)\nOpenAI Traces dashboard", ORANGE)
    arrow(d, 110, 256, 150, 256)
    arrow(d, 280, 256, 330, 256, ORANGE, "spans")
    box(d, 150, 150, 130, 50, "Policy layer\nvalidate_call()", RED)
    arrow(d, 215, 235, 215, 200, label="tool call")
    box(d, 330, 150, 150, 50, "Audit log (JSONL)\nrequested/permitted/...", GREEN)
    arrow(d, 280, 175, 330, 175, GREEN, "events")
    box(d, 20, 55, 200, 52, "Restricted Filesystem Server\nnpx server-filesystem@1.0.0", BLUE)
    box(d, 270, 55, 210, 52, "Restricted Fetch Server\nuvx mcp-server-fetch==2026.11.18", BLUE)
    arrow(d, 190, 150, 120, 107, label="permitted")
    arrow(d, 240, 150, 360, 107, label="permitted")
    box(d, 20, 5, 200, 32, "Sandbox: notes, todo, report", GREEN, 7.5)
    box(d, 270, 5, 210, 32, "AWS feed + Azure blog page only", GREEN, 7.5)
    arrow(d, 120, 55, 120, 37)
    arrow(d, 375, 55, 375, 37)
    return d


MERMAID = """
flowchart LR
    U[Task input] --> A[Cloud Research Agent<br/>gpt-4.1]
    A -->|tool call| P{Policy layer<br/>validate_call}
    P -->|blocked / permitted| L[(Audit log<br/>mcp-audit.jsonl)]
    P --> FS[Restricted Filesystem Server<br/>npx server-filesystem@1.0.0]
    P --> FE[Restricted Fetch Server<br/>uvx mcp-server-fetch==2026.11.18]
    FS --> W[(Project sandbox<br/>notes - todo - report)]
    FE --> H[aws.amazon.com + azure.microsoft.com only]
    A --> R[cloud-landscape-report.md]
    R --> V[Report validator<br/>ranks 1-20 + category counts]
    A -.spans.-> T[(Trace: OpenAI Traces)]
    L -.same trace_id.- T
    R --> G[Grounding verifier<br/>re-reads AWS feed + Azure page]
    G -->|problems| A
"""

SEQ = """
sequenceDiagram
    participant Agent
    participant Wrapper as Restricted MCP Server
    participant Audit as Audit log
    participant MCP as MCP server process
    Agent->>Wrapper: call_tool(name, args)
    Wrapper->>Audit: requested
    Wrapper->>Wrapper: validate_call()
    alt policy violation
        Wrapper->>Audit: blocked
        Wrapper-->>Agent: PermissionError
    else allowed
        Wrapper->>Audit: permitted
        Wrapper->>MCP: forward call
        MCP-->>Wrapper: result
        Wrapper->>Audit: succeeded / tool_error / failed
        Wrapper-->>Agent: result
    end
"""

# ---------------------------------------------------------------- content
s = []
s += [Spacer(1, 96 * mm),
      table([["Agents", "MCP servers", "Traced runs", "Audit records", "Reference rows"],
             [f"1 (+1 helper)", "2", str(N_TRACES), str(N_EVENTS), "20 / 20 verified"]],
            [34 * mm, 34 * mm, 34 * mm, 34 * mm, 34 * mm]),
      Spacer(1, 6 * mm),
      P("An OpenAI Agents SDK research agent that reads private project notes through a Filesystem MCP server "
        "and public AWS and Azure sources through a Fetch MCP server. Every call is allow-listed, audited and "
        "traceable, and every claim in the final report is re-checked against the live sources by code the model "
        "cannot influence.", sub),
      Spacer(1, 6 * mm),
      table([["Item", "Value"],
             ["Repository", "github.com/emran-Automation-Techlead/hardened-mcp-research-agent"],
             ["Main file", "src/hardened_mcp_agent.py (notebook-style, top-level await)"],
             ["Model", "gpt-4.1 (OpenAI Agents SDK, tracing on)"],
             ["Credential handling", "OPENAI_API_KEY comes from your own environment or .env. It is never printed, "
                                     "logged, or passed to MCP processes, and is not reproduced in this document."]],
            [45 * mm, 125 * mm]),
      PageBreak()]

s += [P("1. What the project does", h1),
      P("The agent plays a research analyst for a fictional team, <b>Project Nimbus</b>, deciding whether to "
        "standardise on AWS or Azure. It reads the team's local notes and TODO list, pulls the latest 10 posts "
        "from the AWS News Blog feed and the Azure Blog page, groups all 20 posts by service category "
        "(AI/ML, Compute, Data, Security, ...) and writes <b>cloud-landscape-report.md</b>. "
        "A validator then checks the report."),
      P("The real subject of the project is not the report but the <b>safety wrapper</b>: a research agent that "
        "touches files and the network is a prompt-injection and supply-chain target, so every call goes through "
        "client-side policy, an audit log and pinned, hash-checked packages."),
      P("Agents and servers", h2),
      table([["Component", "Count", "Details"],
             ["Agents", "2 defined, 1 used", "Cloud Research Agent (both servers, runs in Step 7). "
                                              "Files Agent in the optional run_files_task helper (Filesystem only)."],
             ["MCP servers", "2", "Filesystem (npx, 4 tools) and Fetch (uvx, 1 tool), both stdio child processes."],
             ["Orchestration", "none", "A single agent runs one task; there are no hand-offs."]],
            [32 * mm, 32 * mm, 106 * mm]),
      P("2. Architecture", h1), architecture(),
      P("Mermaid source (paste into any Mermaid viewer or a GitHub markdown block)", h2),
      C(MERMAID),
      P("Per-call sequence", h2), C(SEQ), PageBreak()]

s += [P("3. How it works, step by step", h1),
      table([["Step", "What happens", "Why it matters"],
             ["1 Imports and env", "Loads variables, checks the API key exists, verifies node and npx, sets MODEL.",
              "Fails early with a clear message instead of mid-run."],
             ["2 Sandbox", "Creates cloud_project_nimbus with notes.txt and todo.md, plus a cloud_project_decoy "
                           "folder the agent must never reach.",
              "Gives the policy something real to protect and test against."],
             ["2a Audit logging", "write_audit_event and audited_tool_call record requested, permitted, blocked, "
                                  "succeeded, tool_error, failed, cancelled, validation_error.",
              "OWASP MCP08. Log lives in security-audit/, outside the agent's allowed folder."],
             ["3 MCP config", "Pins the Filesystem server, defines the environment allow-list, and the "
                              "RestrictedFilesystemServer class (4 tools; read 3 files; write 1 path).",
              "OWASP MCP01 and MCP04. The agent cannot read or overwrite anything else."],
             ["3a Package checks", "Asserts startup args, registry metadata, npm sha512 integrity and PyPI "
                                   "sha256 hashes against recorded constants.",
              "A changed package fails the run before it starts."],
             ["4 Tool inspection", "Lists exposed tools, asserts only approved ones exist, proves an outside "
                                   "folder is blocked.",
              "Evidence the boundary works before any model call."],
             ["5 Prompts", "FILES_AGENT_PROMPT sets workflow and honesty rules.",
              "Instructions complement, never replace, code-level policy."],
             ["6 Fetch config", "Pins mcp-server-fetch, allows only two hosts, RestrictedFetchServer permits only "
                                "two exact URLs (AWS feed, Azure blog page) and bounds max_length, start_index, raw.",
              "OWASP MCP06. Blocks data exfiltration through URLs."],
             ["6a-6c Tests", "Offline checks: dummy secrets excluded from env; audit log has only approved "
                             "fields; bad URLs are blocked with no network calls.",
              "Security controls are tested, not assumed."],
             ["6d Grounding check", "grounding_problems() re-reads the AWS feed and Azure page itself and compares "
                                    "every report row: exact titles/URLs for AWS, exact article-link order for Azure, "
                                    "no blanks, no duplicates.",
              "Catches fabricated rows that a format check cannot see."],
             ["7 Agent run", "Starts both servers, runs the agent inside trace(), then retries up to 3 times until "
                             "the report is saved AND grounded. Model calls use run_with_backoff for rate limits.",
              "Success is verified from disk and from the sources, not from the model's claim."],
             ["8 Validation", "check_report confirms ranks 1-20 once each in order and that any Category "
                              "Counts match the table.",
              "Deterministic check on model output."]],
            [27 * mm, 85 * mm, 58 * mm]),
      PageBreak()]

s += [P("4. Security controls in detail", h1),
      table([["Control", "OWASP", "Implementation"],
             ["Version pinning", "MCP04", "npx @modelcontextprotocol/server-filesystem@1.0.0 with "
                                          "--registry=https://registry.npmjs.org; uvx mcp-server-fetch==2026.11.18."],
             ["Integrity hashes", "MCP04", "EXPECTED_FILESYSTEM_INTEGRITY (npm sha512) and EXPECTED_FETCH_SHA256 "
                                           "(wheel and sdist) are compared with registry values at run time."],
             ["Environment allow-list", "MCP01", "checked_mcp_environment rejects any variable outside "
                                                 "APPROVED_MCP_ENV_NAMES (Windows plus HOME, LOGNAME, SHELL, TERM, USER). "
                                                 "API keys are never forwarded."],
             ["Tool allow-list", "-", "list_tools filters to approved tools; validate_call rejects the rest."],
             ["Path policy", "-", "Absolute paths only, resolved before comparison. list: project root. "
                                  "read: notes.txt, todo.md, report. write: report only."],
             ["URL policy", "MCP06", "Exact-match URL set, no extra arguments, integer bounds, boolean raw. "
                                     "Server flags --allowed-hosts and --no-readability-js add a second layer."],
             ["Audit logging", "MCP08", "Seven fields only; no arguments, content, URLs or error messages."],
             ["Grounding verifier", "-", "Independent re-read of both sources; report rows must match exactly. "
                                         "Drives a bounded retry loop."],
             ["robots.txt", "-", "The Fetch server honours robots.txt. Azure's /blog/feed/ is disallowed, so the "
                                 "design uses the allowed blog index page; the policy never uses --ignore-robots-txt."],
             ["Rate-limit backoff", "-", "run_with_backoff retries on HTTP 429 with increasing waits."],
             ["Prompt rules", "-", "File and web content is treated as data, never as instructions."]],
            [36 * mm, 18 * mm, 116 * mm]),
      P("Environment allow-list", h2),
      C("""
APPROVED_MCP_ENV_NAMES = {
    # Windows
    "APPDATA", "HOMEDRIVE", "HOMEPATH", "LOCALAPPDATA", "PATH", "PATHEXT",
    "PROCESSOR_ARCHITECTURE", "SYSTEMDRIVE", "SYSTEMROOT", "TEMP", "TMP",
    "USERNAME", "USERPROFILE",
    # macOS / Linux
    "HOME", "LOGNAME", "SHELL", "TERM", "USER",
}"""),
      P("Audit record format", h2),
      C("""
{"timestamp_utc": "...", "session_id": "...", "trace_id": "...",
 "call_id": "...", "server": "filesystem|fetch|other",
 "tool": "<approved tool or unapproved_tool>", "status": "..."}"""),
      table([["Status", "Meaning"],
             ["requested", "The agent asked for a tool call."],
             ["blocked / validation_error", "Policy rejected it, or validation itself failed; nothing was forwarded."],
             ["permitted", "Policy approved; the call is forwarded to the MCP server."],
             ["succeeded / tool_error", "Server returned normally, or returned an error result."],
             ["failed / cancelled", "Exception during execution, or the task was cancelled."]],
            [50 * mm, 120 * mm]),
      PageBreak()]

s += [P("5. Verifying traces with the Agents SDK", h1),
      P("The run is wrapped in <b>with trace(TRACE_NAME) as current_trace</b>. Everything the agent does inside "
        "that block (model generations, tool calls, MCP listings) becomes spans under one <b>trace_id</b>. "
        "The audit writer calls <b>get_current_trace()</b> and stores the same trace_id on every record, "
        "so the local audit log and the hosted trace can be cross-checked."),
      P("What you see after a run", h2),
      C("""
Trace Name: Cloud Research Agent Run Nimbus
Trace ID:   trace_<32 hex characters>"""),
      P("Verification procedure", h2)]
s += B([
    "<b>Copy the Trace ID</b> printed after Step 7.",
    "<b>Open the dashboard</b> at platform.openai.com/traces (signed in to the same organisation as the API key) "
    "and search for that ID, or filter by the workflow name.",
    "<b>Check the span tree.</b> Expect the Cloud Research Agent span containing generation spans and "
    "tool spans: list_allowed_directories, list_directory, read_text_file x2, several fetch spans (AWS feed, "
    "Azure page, plus any continuation or retry fetches), write_file, and a read_text_file to read the report back. "
    "Rewrites after the grounding check add further fetch / write_file / read_text_file spans in the same trace.",
    "<b>Match counts.</b> The number of tool spans that executed should equal the audit-log events with status "
    "permitted for that trace_id (the audit log counts only MCP calls, so ignore model-generation spans). A blocked call typically shows an error in the trace but has no succeeded record.",
    "<b>Confirm URLs and paths</b> in the span inputs are only the two approved feed URLs and files inside "
    "cloud_project_nimbus.",
    "<b>Confirm the output</b>: the final span should show a write_file to cloud-landscape-report.md, and the "
    "script's own 'Verified saved file' message must appear (it is based on the file on disk).",
])
s += [P("Cross-check the audit log against the trace", h2),
      C("""
import json
from collections import Counter

TRACE_ID = "trace_..."          # paste from the notebook output
events = [json.loads(l) for l in open("security-audit/mcp-audit.jsonl", encoding="utf-8")]
mine = [e for e in events if e["trace_id"] == TRACE_ID]

print(Counter(e["status"] for e in mine))
print(Counter((e["server"], e["tool"]) for e in mine if e["status"] == "permitted"))

# Every call must reach a terminal state.
by_call = {}
for e in mine:
    by_call.setdefault(e["call_id"], []).append(e["status"])
terminal = {"succeeded", "tool_error", "failed", "cancelled", "blocked", "validation_error"}
assert all(set(v) & terminal for v in by_call.values()), "a call has no outcome"
assert not [e for e in mine if e["tool"] == "unapproved_tool" and e["status"] == "permitted"]
print("OK: every call has an outcome and no unapproved tool was permitted")"""),
      P("Things to watch", h2)]
s += B([
    "If tracing is disabled (for example OPENAI_AGENTS_DISABLE_TRACING=1) or the key has no tracing access, "
    "trace_id in the audit log is null and the dashboard shows nothing; the local log is then the only record.",
    "Policy tests in Steps 4, 6b and 6c run outside a trace, so their records legitimately have trace_id null.",
    "Traces can contain prompts and tool inputs. Treat the dashboard as sensitive and do not use real secrets "
    "in the sandbox files.",
    "Matching spans to audit events proves the controls ran for that session; it does not prove the model's "
    "analysis is correct. Read the saved report against the fetched evidence.",
]) + [PageBreak()]


# ---- live evidence
live_rows = []
for i, (t, l) in enumerate(LIVE["aws"], 1):
    live_rows.append([str(i), "AWS", clean(t)[:78], CATEGORY[i]])
for i, (u, t) in enumerate(LIVE["azure"], 11):
    live_rows.append([str(i), "Azure", clean(t)[:78], CATEGORY[i]])

s += [P("6. Live results: what actually happened", h1),
      P("The agent was run for real against the live AWS feed and Azure blog page, with tracing on. Seven runs "
        "were needed. Their value is in what they exposed: every failure below is real and is why the project "
        "contains a grounding verifier, a retry loop, rate-limit backoff and a robots.txt-aware Azure source."),
      img("run_progress.png"),
      table([["Run", "Trace ID", "What happened", "Change it caused"]] +
            [[str(i), f"{tid}...", what, lesson] for i, (_, tid, what, lesson) in enumerate(RUNS, 1)] +
            [["6", "(rate limited)", "OpenAI returned HTTP 429 (tokens per minute) and the retries were exhausted.",
              "Added run_with_backoff with increasing waits."],
             ["7", "(stopped)", "Stopped on request to protect API credits. No further model calls were made.",
              "Remaining results come from the public sources and the audit log, not from the model."]],
            [10 * mm, 30 * mm, 76 * mm, 54 * mm]),
      Spacer(1, 3 * mm),
      P("<b>Key lesson.</b> Run 2 produced a perfectly formatted table of 20 rows that passed the rank and count "
        "validator, yet 8 of its rows were invented. Output that looks right is not evidence. "
        "Run 4 showed the opposite weakness: a check that treats an empty string as found. "
        "The final verifier requires non-empty titles and https URLs, exact AWS feed order, exact Azure "
        "article-link order, and no duplicates."),
      PageBreak(),
      P("Verification loop", h2), verification_loop(),
      P("Reference table (verified against the live sources)", h2),
      P("Compiled from the live AWS feed and Azure blog page using the verifier's own rules, with no model "
        "involved. Categories are an analyst classification. It is a single snapshot taken on 23 Nov 2026 "
        "(the Azure side coincides with Microsoft Ignite announcements)."),
      table([["#", "Provider", "Title", "Primary category"]] + live_rows, [8 * mm, 18 * mm, 110 * mm, 34 * mm]),
      Spacer(1, 3 * mm),
      img("categories.png"),
      P("<b>Reading the snapshot.</b> Azure's latest posts are dominated by AI and agent announcements (6 of 10), "
        "with two on Cobalt 200 compute. AWS's feed is spread out: four weekly roundups plus single posts on "
        "compute, data, security, networking and developer tooling. Hypothesis, not a finding: this reflects the "
        "publishing calendar (conference week and roundup cadence) more than relative investment. Re-run over "
        "several weeks before drawing conclusions for Project Nimbus."),
      PageBreak(),
      P("Audit log and trace evidence from the real runs", h2),
      P(f"Across the session the audit log holds <b>{N_EVENTS} records</b>, of which "
        f"<b>{len(traced)}</b> belong to <b>{N_TRACES} traced runs</b> (the rest are the offline policy tests, which "
        "run outside a trace and carry a null trace_id). The blocked records come from the policy tests that attempt "
        "outside paths, wrong URLs, SSRF targets and a source-file overwrite; none of those attempts reached an MCP server."),
      img("audit_status.png"), img("tool_calls.png"),
      P("Cross-check that was run", h2),
      C("""
For every traced run in security-audit/mcp-audit.jsonl:
  - each call_id reaches a terminal status (succeeded, tool_error, failed, blocked ...)
  - no tool outside the approved set was ever permitted
  - the two tool_error records are the Azure feed refusal (robots.txt) and one Azure timeout
    - both are fetch calls the Fetch server rejected or could not complete, and both were
      disclosed by the agent in its report instead of being papered over"""),
      PageBreak()]

s += [P("7. How and where to use it", h1),
      P("Where it fits", h2)]
s += B([
    "<b>Learning and workshops:</b> a compact reference for the OWASP MCP Top 10 controls applied to a real agent.",
    "<b>Starting template:</b> any agent that needs file access plus a few approved web sources, such as "
    "vendor-watch, competitor monitoring, release-note digests or internal research bots.",
    "<b>Security review demos:</b> show clients how to constrain MCP tools in code rather than in prompts.",
    "<b>Platform and cloud teams:</b> track what AWS and Azure announce, with evidence and links, before a "
    "platform decision.",
])
s += [P("Setup", h2),
      C("""
git clone https://github.com/emran-Automation-Techlead/hardened-mcp-research-agent
cd hardened-mcp-research-agent
pip install -r requirements.txt
cp .env.example .env          # then put your own OpenAI key in .env (never commit it)
# Install Node.js (>= 18) and uv, then verify the pinned Fetch server:
uvx --from mcp-server-fetch==2026.11.18 mcp-server-fetch --help"""),
      P("Running", h2)]
s += B([
    "Open src/hardened_mcp_agent.py in VS Code (Python/Jupyter extension) or Jupyter, and run the cells in order. "
    "The file uses top-level await, so plain <i>python file.py</i> will not work.",
    "Steps 4 and 6a-6c are safe offline-style checks. Step 7 calls the model and the two feeds and costs API credits.",
    "Open cloud_project_nimbus/cloud-landscape-report.md and press Ctrl+Shift+V in VS Code for the rendered view.",
    "Review security-audit/mcp-audit.jsonl and the trace as described in section 5.",
])
s += [P("Customising", h2),
      table([["Goal", "Change"],
             ["Different sources", "Edit RestrictedFetchServer.APPROVED_URLS and the --allowed-hosts args together."],
             ["Different project", "Edit the notes.txt and todo.md text in Step 2 and TASK_INPUT in Step 7."],
             ["More or fewer posts", "Edit the TODO text, the prompt wording, and EXPECTED_STORIES in Step 8."],
             ["Different model", "Change MODEL in Step 1."],
             ["New package version", "Review it, then update the version AND the recorded hash constants together."],
             ["Extra files for the agent", "Add them to readable_paths in RestrictedFilesystemServer."]],
            [45 * mm, 125 * mm]),
      P("Troubleshooting", h2),
      table([["Symptom", "Likely cause and fix"],
             ["RuntimeError: key missing", "Add the key to your environment or .env and restart the kernel."],
             ["node/npx or uvx missing", "Install Node.js or uv, restart the kernel so PATH refreshes."],
             ["Integrity or hash assertion fails", "The package contents changed. Investigate, then re-record "
                                                   "the hashes only if the change is intended."],
             ["PermissionError from the environment check", "A variable outside the allow-list reached the "
                                                            "MCP config. Remove it, do not widen the list casually."],
             ["Fetch server fails at start", "A flag is unsupported by the pinned version; re-run the --help check."],
             ["Report not saved", "Inspect the trace for write_file errors; path must be the report path."]],
            [55 * mm, 115 * mm]),
      PageBreak()]

s += [P("8. Limitations", h1)]
s += B([
    "Pinning and hash checks reduce supply-chain risk but say nothing about vulnerabilities inside a package.",
    "A feed snapshot shows what was published recently; it does not measure investment, pricing or quality.",
    "Category assignment is made by the model, so the validator checks arithmetic consistency, not whether "
    "each category is the best choice.",
    "The audit log is a local file; for production use, ship it to append-only storage.",
    "Only the code-level policy is a hard boundary. Prompt rules are guidance.",
    "The grounding verifier proves rows match the sources at check time; a feed that changes between the agent's "
    "fetch and the check can cause a false alarm, which the retry loop absorbs.",
    "gpt-4.1 requests with large fetched pages can hit tokens-per-minute limits; the backoff helper reduces but "
    "does not remove that risk.",
    "The reference table and categories in section 6 are a single dated snapshot, not a trend.",
])
s += [P("9. Conclusion", h1),
      P("The project shows that giving an agent real tools does not require giving it real trust. Two MCP servers "
        "are wrapped by a thin policy layer that enforces exactly which tools, paths and URLs are permitted; "
        "packages are pinned and hash-checked; child processes receive a minimal environment; and every call "
        "leaves a content-free audit record tied to a trace_id."),
      P("Because the same trace_id appears in the Agents SDK trace and in the local audit log, a run can be "
        "reviewed from both sides: what the model decided (the trace) and what the system allowed (the audit log). "
        "That combination, plus a deterministic report validator, makes the agent's behaviour inspectable "
        "rather than assumed - the pattern worth reusing for any agent that touches files or the network."),
      P("The seven live runs add the most useful lesson: the controls that mattered were the ones added after "
        "watching the agent fail. A well-formatted answer passed the first validator while containing invented "
        "rows; only an independent re-read of the sources exposed it. Treat any model-produced evidence as a claim "
        "to be verified, log every action, and keep the verifier outside the model's reach."),
      P("Next steps: package the script as a CLI, add CI to run the offline policy tests and the verifier, "
        "support a second model provider through the Agents SDK, and add a script that refreshes recorded hashes "
        "during intentional upgrades.")]


def cover_art(c):
    w, h = A4
    c.setFillColor(NAVY)
    c.rect(0, h - 105 * mm, w, 105 * mm, stroke=0, fill=1)
    c.setFillColor(BLUE)
    c.rect(0, h - 105 * mm, w, 6 * mm, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.rect(0, h - 105 * mm, 55 * mm, 6 * mm, stroke=0, fill=1)
    # decorative node graph
    c.setStrokeColor(colors.HexColor("#2c4a7c"))
    c.setLineWidth(1)
    pts = [(150, 250), (165, 285), (185, 262), (172, 235), (150, 215), (185, 205)]
    pts = [(x * mm, h - (y - 150) * mm) for x, y in [(130, 40), (150, 62), (172, 44), (160, 20), (190, 66), (196, 30)]]
    for i, p1 in enumerate(pts):
        for p2 in pts[i + 1:i + 3]:
            c.line(p1[0], p1[1], p2[0], p2[1])
    for i, (x, y) in enumerate(pts):
        c.setFillColor(ORANGE if i % 3 == 0 else GREEN if i % 3 == 1 else colors.HexColor("#4a6fa5"))
        c.circle(x, y, 3 * mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(20 * mm, h - 48 * mm, "Hardened MCP")
    c.drawString(20 * mm, h - 60 * mm, "Research Agent")
    c.setFont("Helvetica", 13)
    c.setFillColor(colors.HexColor("#cfd8e6"))
    c.drawString(20 * mm, h - 72 * mm, "AWS vs Azure Radar  |  How it works, how to use it, how it was proven")
    c.setFont("Helvetica-Oblique", 9.5)
    c.drawString(20 * mm, h - 88 * mm, "Allow-listed tools  -  pinned and hash-checked packages  -  audit log  -  verified traces  -  grounded output")


def footer(c, d):
    if d.page == 1:
        cover_art(c)
    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(20 * mm, 10 * mm, "Hardened MCP Research Agent - AWS vs Azure Radar")
    c.drawRightString(190 * mm, 10 * mm, f"Page {d.page}")
    c.restoreState()


doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                        topMargin=18 * mm, bottomMargin=18 * mm,
                        title="Hardened MCP Research Agent Guide", author="Imran")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
