"""Build docs/Hardened-MCP-Agent-Guide.pdf  (run: python docs/build_pdf.py)."""
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

OUT = Path(__file__).with_name("Hardened-MCP-Agent-Guide.pdf")
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
    box(d, 270, 5, 210, 32, "AWS + Azure blog feeds only", GREEN, 7.5)
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
    FE --> H[aws.amazon.com + azure.microsoft.com feeds only]
    A --> R[cloud-landscape-report.md]
    R --> V[Report validator<br/>ranks 1-20 + category counts]
    A -.spans.-> T[(Trace: OpenAI Traces)]
    L -.same trace_id.- T
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
s += [Spacer(1, 40 * mm), P("Hardened MCP Research Agent", title),
      P("AWS vs Azure Radar - how it works, how to use it, and how to verify it", sub),
      Spacer(1, 8 * mm),
      P("A Python agent built on the OpenAI Agents SDK that reads private project notes through a "
        "Filesystem MCP server and the public AWS and Azure blog feeds through a Fetch MCP server, "
        "with every tool call allow-listed, audited and traceable.", sub),
      Spacer(1, 10 * mm),
      table([["Item", "Value"],
             ["Repository", "github.com/emran-Automation-Techlead/hardened-mcp-research-agent"],
             ["Main file", "src/hardened_mcp_agent.py (notebook-style, top-level await)"],
             ["Agents / MCP servers", "1 working agent (+1 optional helper) / 2 MCP servers"],
             ["Model", "gpt-4.1"],
             ["Credential handling", "OPENAI_API_KEY is read from your own environment or .env; it is never "
                                     "printed, logged or passed to MCP processes"]],
            [45 * mm, 125 * mm]),
      PageBreak()]

s += [P("1. What the project does", h1),
      P("The agent plays a research analyst for a fictional team, <b>Project Nimbus</b>, deciding whether to "
        "standardise on AWS or Azure. It reads the team's local notes and TODO list, pulls the latest 10 posts "
        "from the AWS News Blog feed and the Azure Blog feed, groups all 20 posts by service category "
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
                                "two exact feed URLs and bounds max_length, start_index, raw.",
              "OWASP MCP06. Blocks data exfiltration through URLs."],
             ["6a-6c Tests", "Offline checks: dummy secrets excluded from env; audit log has only approved "
                             "fields; bad URLs are blocked with no network calls.",
              "Security controls are tested, not assumed."],
             ["7 Agent run", "Starts both servers, runs the agent inside trace(), retries once if the report "
                             "was not saved, then displays the saved file.",
              "Success is verified from disk, not from the model's claim."],
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
    "tool spans: list_allowed_directories, list_directory, read_text_file x2, fetch x2 (AWS, Azure), write_file, "
    "and a read_text_file to read the report back.",
    "<b>Match counts.</b> The number of tool spans that executed should equal the audit-log events with status "
    "permitted for that trace_id. A blocked call typically shows an error in the trace but has no succeeded record.",
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

s += [P("6. How and where to use it", h1),
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

s += [P("7. Limitations", h1)]
s += B([
    "Pinning and hash checks reduce supply-chain risk but say nothing about vulnerabilities inside a package.",
    "A feed snapshot shows what was published recently; it does not measure investment, pricing or quality.",
    "Category assignment is made by the model, so the validator checks arithmetic consistency, not whether "
    "each category is the best choice.",
    "The audit log is a local file; for production use, ship it to append-only storage.",
    "Only the code-level policy is a hard boundary. Prompt rules are guidance.",
])
s += [P("8. Conclusion", h1),
      P("The project shows that giving an agent real tools does not require giving it real trust. Two MCP servers "
        "are wrapped by a thin policy layer that enforces exactly which tools, paths and URLs are permitted; "
        "packages are pinned and hash-checked; child processes receive a minimal environment; and every call "
        "leaves a content-free audit record tied to a trace_id."),
      P("Because the same trace_id appears in the Agents SDK trace and in the local audit log, a run can be "
        "reviewed from both sides: what the model decided (the trace) and what the system allowed (the audit log). "
        "That combination, plus a deterministic report validator, makes the agent's behaviour inspectable "
        "rather than assumed - the pattern worth reusing for any agent that touches files or the network."),
      P("Next steps: package the script as a CLI, add CI to run the offline policy tests, and add a script that "
        "refreshes recorded hashes during intentional upgrades.")]


def footer(c, d):
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
