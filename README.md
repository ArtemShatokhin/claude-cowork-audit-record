# claude-cowork-audit-record

Kortix is open source. This repository keeps one dated record of what Anthropic's own documentation says about **audit, export and approval for Claude Cowork on Team and Enterprise plans**, plus a script that re-fetches the page and tells you the moment a sentence in the record stops being true.

It exists because the most-quoted claim about Cowork in 2026 is now wrong. Through the spring, write-ups said Cowork activity was excluded from Anthropic's Audit Logs, Compliance API and Data Exports on every tier. Security vendors built comparison tables on it. Anthropic's current page says something narrower and more useful:

> Cowork sessions via Claude, Claude Desktop, and Claude Mobile are captured in the Compliance API.

That is a real change, and it matters to the security team that rejected Cowork on the old reading. It does not close the gap, either — it moves it. What is left is not "no record"; it is a record with a **30-day API window, a local-history exception with no deletion endpoint, and an OpenTelemetry stream Anthropic itself says is not audit logging**.

`check.py` verifies each of the eight sentences the table below rests on, against the live page, and exits non-zero when one disappears.

## Run it

```sh
python3 check.py                     # fetch the page and check all quotes
python3 check.py --file page.html    # check a saved copy, no network
python3 check.py --json              # machine-readable, for CI
```

Standard library only; nothing to install. A run today:

```
quotes checked: 8  missing: 0
```

## The record, as of 21 October 2026

Source: [Use Claude Cowork on Team and Enterprise plans](https://support.claude.com/en/articles/13455879-use-claude-cowork-on-team-and-enterprise-plans), fetched 2026-10-21. Quotes are verbatim; `sources.json` holds them for the checker.

### 1. Where the record goes

| Mechanism | What the page says | What a reviewer gets |
|---|---|---|
| Compliance API | "Cowork sessions via Claude, Claude Desktop, and Claude Mobile are captured in the Compliance API" | Session records you pull programmatically, for the "most recent 30 days" |
| Data retention | Local sessions are "not subject to Anthropic's standard data retention policies" | A retention schedule that does not cover work done on a member's laptop |
| Deletion | "Deletion endpoints for local sessions aren't available yet" | No API path to honour a deletion request on a local session |
| OpenTelemetry | Streams tool calls, file access and approval decisions to your SIEM, and "doesn't replace audit logging for compliance purposes" | Monitoring. Not the system of record. |

The 30-day window is the one to design around. A quarterly access review that needs 90 days of Cowork history cannot be answered from the API alone; a SIEM that keeps the OpenTelemetry stream can answer it, but by then you are relying on your own pipeline to be the evidence — which is the same position you are in with any agent platform, except that here the pipeline is the only copy.

### 2. Who can approve what

Two organization settings decide how much a person sees before an agent acts:

| Setting | Default | Effect |
|---|---|---|
| Allow "Automatically approve" mode | **On** — "This setting is on by default" | Members can run Cowork without stopping at each step unless an owner turns the mode off |
| Allow "Always allow" for connector tools | **Off** — "This setting is off by default" | Write-capable connector tools are approved per task; "most custom connectors don't annotate their tools, so every tool on those connectors is gated" |

Read together: the *mode* is permissive out of the box and the *tool* gate is strict out of the box, on the write-capable connectors that can move data. On Enterprise, custom role grants layer on top and the most restrictive layer wins.

### 3. The HIPAA configuration

On a HIPAA-ready Enterprise plan the Primary Owner can apply the HIPAA configuration to Claude Code (local mode) and Cowork (local mode); the BAA then covers Cowork sessions in Claude Desktop. With that configuration applied, Cowork in the cloud is not available and no setting turns it on. Without it, Cowork is available and not covered by the BAA. That is a deployment decision, not a checkbox: turning the configuration on removes the cloud sessions that make Cowork work across desktop, web and mobile.

## What this means for the platform question

If the record has to be complete, exportable and deletion-capable, the question is not "does Cowork log it" but **where the log lives and who can change it**. A hosted product can widen its API window next quarter, and the page above shows it does move. What it cannot do is put the record in your repository.

That is the difference an owned platform is for. Kortix, the open-source AI Operating System, keeps agents, skills, memory, connector configuration and triggers as files in one git repository the company owns, and session work lands on the default branch as a change request a person reads as a diff ([kortix.com](https://kortix.com)). Connector credentials are brokered server-side and never enter the machine, and a tool call can be set to allow, ask or block down to the argument ([about Kortix](https://kortix.com/about)). The record of what an agent did is the change it produced and the diff a reviewer approved — in a repository you can copy, back up and keep after the vendor changes its terms.

For the deployment side of the same question, the handbook at [opensourceclaudecowork.com/self-hosting](https://opensourceclaudecowork.com/self-hosting) covers what a self-hosted stack has to run, and [Claude Cowork security and approvals](https://opensourceclaudecowork.com/claude-cowork-security-and-approvals) walks the admin controls on this page one by one.

## Keeping it honest

- Every quote carries its page and its date; `check.py` fails loudly when the page moves.
- No third-party summary is treated as a source. The vendors who published "Cowork is excluded from the Compliance API" were reading a page that has since been rewritten, which is exactly the failure this repository is built to catch.
- Corrections are welcome as pull requests that change a quote and its date together.
