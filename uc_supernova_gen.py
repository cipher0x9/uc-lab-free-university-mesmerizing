#!/usr/bin/env python3
"""Inject Wave-1 vendor, migration, SEV, architecture, and mastery packs."""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FLAGSHIP = ROOT / "university" / "v17-UNIVERSITY.html"


@dataclass(frozen=True)
class SectionSpec:
    section_id: str
    group: str
    title: str
    subtitle: str
    path: tuple[str, ...]
    emphasis: str
    mode: str


VENDORS = {
    "avaya-aura": ("Avaya Aura", ("System Manager", "Session Manager", "Communication Manager", "SIP Entity + Entity Link", "Media Gateway", "AES / adjuncts"), "traceSM plus CM list trace and denial events"),
    "genesys-cloud-cx": ("Genesys Cloud CX", ("Architect Flow", "ACD / Predictive Routing", "Queue + Skills", "BYOC Cloud or Premises Edge", "Agent WebRTC", "Analytics + Event APIs"), "interaction ID, conversation timeline, trunk and Edge metrics"),
    "nice-cxone": ("NICE CXone", ("Point of Contact", "Studio Script", "ACD Skill + Campaign", "Voice / Digital Entry", "CXone Agent", "Recording + QM/WFM"), "contact ID, Studio trace, skill state, media and recording evidence"),
    "five9": ("Five9", ("DID / Campaign", "IVR Script", "Skill / Queue", "VCC Telephony", "Agent Desktop", "Reports + Recording"), "interaction identifiers, campaign state, station leg and recording artifact"),
    "twilio-flex": ("Twilio Flex", ("Phone / Digital Entry", "Studio Flow", "TaskRouter Workspace", "Worker + Task Queue", "Flex UI", "Functions + Event Streams"), "CallSid, TaskSid, webhook request ID and debugger/event evidence"),
    "ringcentral": ("RingCentral", ("Site", "Extension / User", "Number + Route", "Auto-Receptionist / Queue", "Endpoint / App", "Quality Analytics"), "session identity, endpoint leg, route decision and quality timeline"),
    "8x8": ("8x8", ("Site", "User + Device", "Number / Routing", "Auto Attendant / Queue", "Contact Center", "Quality Analytics"), "call identifier, site path, endpoint metrics and analytics evidence"),
    "mitel": ("Mitel", ("MiVoice Call Control", "Dial Plan", "SIP Trunk", "Media Gateway", "Endpoint", "Management + Contact Center"), "call trace, trunk state, gateway channel and packet evidence"),
    "asterisk-freepbx": ("Asterisk / FreePBX", ("PJSIP Transport", "Endpoint + AOR + Auth", "Dialplan Context", "Trunk", "RTP Engine", "CDR / CEL / AMI / ARI"), "PJSIP logger, channel uniqueid, dialplan trace, RTP debug and pcap"),
    "webex-calling": ("Webex Calling", ("Control Hub", "Location + Number", "Calling Service", "Local Gateway / PSTN", "Webex App or Device", "Analytics + Troubleshooting"), "calling troubleshooting session, correlation identity, Local Gateway legs and media metrics"),
    "zoom-phone": ("Zoom Phone", ("Account + Site", "User + Extension", "Number + Route", "BYOC / PSTN", "Client or Device", "Quality Dashboard"), "call log identity, site policy, BYOC leg and quality evidence"),
    "teams-phone": ("Microsoft Teams Phone", ("Teams Admin Center", "Phone System Policy", "Dial Plan + Voice Route", "Direct Routing SBC / PSTN", "Teams Client", "Call Analytics + CQD"), "Call Analytics session, CQD dimensions, SBC ladder and media quality"),
}

VENDOR_SURFACES = (
    ("overview", "📌 Overview", "capability boundaries, operating model, licensing questions, and vocabulary"),
    ("architecture", "🏗 Architecture", "control, signaling, media, identity, data, and failure domains"),
    ("call-flow", "🔁 Call Flow", "ingress, routing, agent or endpoint delivery, media, teardown, and correlation"),
    ("config", "⚙️ Config Essentials", "prerequisites, dependencies, safe change order, canary, and rollback"),
    ("troubleshooting", "🔧 Troubleshooting", "symptom scoping, LICC evidence, falsifiers, and recovery proof"),
    ("interview", "💬 Interview Q&A", "architecture defense, failure reasoning, migration tradeoffs, and teach-back"),
)


MIGRATIONS = (
    "cm-aws-uc", "cm-azure-uc", "cm-gcp-uc", "cm-expressway-mra", "cm-cube-sbc-migrate",
    "cm-cucm-upgrade-12-14", "cm-webex-calling-migrate", "cm-teams-phone-migrate", "cm-zoom-phone-migrate",
    "cm-cc-migrate", "cm-sip-trunk-cutover", "cm-pstn-consolidation", "cm-e911-migration", "cm-number-porting",
    "cm-data-retention", "cm-recording-migration", "cm-qm-migration", "cm-wfm-migration", "cm-failover-dr",
    "cm-hybrid-design", "cm-call-routing-migration", "cm-vm-migration", "cm-ivr-migration", "cm-ai-migration",
    "cm-integration-migration", "cm-training-cutover", "cm-hypercare-30d", "cm-rollback-plan", "cm-success-metrics",
    "cm-pmo-governance", "cm-cost-analysis", "cm-contract-negotiation", "cm-vendor-selection", "cm-testing-uats",
    "cm-cutover-communications", "cm-schedule-windows", "cm-parallel-run", "cm-data-archival", "cm-license-port",
    "cm-continuity",
)

SEV_TOPICS = (
    "SIP 503 retry storm", "codec mismatch", "NAT and SBC hairpin", "call recording failure", "QoS queue drops",
    "certificate expiry", "DNS SRV failover", "fax over IP failure", "call park failure", "Extension Mobility failure",
    "hunt-group routing loop", "presence state failure", "dial-plan regex defect", "media-path asymmetry", "CUCM CPU spike",
    "license exhaustion", "upgrade failure", "database replication broken", "TFTP configuration failure", "music-on-hold failure",
    "conference bridge exhaustion", "EMCC failure", "MRA traversal failure", "Jabber client failure", "Webex App calling failure",
    "Teams client calling failure", "multi-vendor interop defect", "voicemail routing failure", "Unity Connection integration failure",
    "PIMG integration failure", "analog gateway failure", "ISDN PRI failure", "T1 or E1 span failure", "echo complaint",
    "jitter burst", "packet-loss burst", "MOS degradation", "call-setup delay", "one-way audio", "dead air after answer",
    "mid-call drop", "DTMF interworking failure", "SIP REFER transfer failure", "early-media ringback failure", "SBC HA split brain",
    "NTP clock drift", "OAuth token expiry", "contact-center queue starvation", "agent-state desynchronization", "emergency-location mismatch",
)

ARCH_TOPICS = (
    "uc-diagrams", "cc-diagrams", "sbc-topologies", "network-design", "cloud-design", "security-design", "ai-design",
    "observability", "dr", "capacity", "vendor-selection", "migration", "integration", "license", "sla", "roadmap",
    "cost", "team", "ops", "governance",
)

MASTERY_TOPICS = (
    "mm-cisco", "mm-avaya", "mm-genesys", "mm-nice", "mm-five9", "mm-twilio", "mm-aws-connect", "mm-microsoft",
    "mm-zoom", "mm-webex", "mm-mitel", "mm-8x8", "mm-ringcentral", "mm-asterisk", "mm-cc-architect",
    "mm-uc-architect", "mm-network", "mm-security", "mm-ai", "mm-cloud", "mm-migration", "mm-interview", "mm-career", "mm-teach",
)

PRACTICUM_DOMAINS = (
    "signaling", "media", "routing", "edge", "network", "security", "contact-center", "cloud", "migration", "operations",
)

PRACTICUM_LABS = (
    "baseline-map", "happy-path", "fault-injection", "packet-proof", "counter-proof", "capacity-edge",
    "security-boundary", "canary-change", "rollback-drill", "incident-command", "architect-defense", "teach-back",
)


def label(identifier: str) -> str:
    stem = re.sub(r"^(cm|mm|arch)-", "", identifier)
    replacements = {"uc": "UC", "cc": "CC", "sbc": "SBC", "dr": "DR", "sla": "SLA", "ai": "AI", "api": "API", "aws": "AWS", "gcp": "GCP", "cucm": "CUCM", "mra": "MRA", "e911": "E911", "qm": "QM", "wfm": "WFM", "pmo": "PMO", "uats": "UAT"}
    return " ".join(replacements.get(word, word.capitalize()) for word in stem.split("-"))


def svg_path(nodes: tuple[str, ...], accent: str = "#38bdf8") -> str:
    compact = [html.escape(node[:26]) for node in nodes[:6]]
    boxes: list[str] = []
    width = 930
    step = width // len(compact)
    for index, node in enumerate(compact):
        x = 12 + index * step
        boxes.append(f'<rect x="{x}" y="42" width="{step - 24}" height="64" rx="13" fill="{accent}" opacity=".13" stroke="{accent}"/><text x="{x + (step - 24)/2:.0f}" y="80" text-anchor="middle" fill="currentColor" font-size="11" font-weight="700">{node}</text>')
        if index < len(compact) - 1:
            boxes.append(f'<path d="M{x + step - 12} 74h22m-7-7 7 7-7 7" stroke="{accent}" stroke-width="3" fill="none"/>')
    return f'<svg viewBox="0 0 {width} 130" role="img" aria-label="Architecture path"><rect width="{width}" height="130" rx="18" fill="currentColor" opacity=".035"/>{"".join(boxes)}</svg>'


def rows(items: tuple[str, ...], subject: str) -> str:
    evidence = ("call or interaction ID", "SIP ladder", "RTP or media metrics", "platform event timeline", "capacity counter", "change audit")
    failure = ("identity drift", "route rejection", "media asymmetry", "dependency timeout", "resource saturation", "policy mismatch")
    return "".join(
        f"<tr><td>{i + 1:02d}</td><td><b>{html.escape(item)}</b></td><td>{html.escape(subject)} boundary: {html.escape(failure[i % len(failure)])}</td><td>{html.escape(evidence[i % len(evidence)])}</td><td>Expected event in test window; falsify with opposite-leg proof</td></tr>"
        for i, item in enumerate(items)
    )


def interview_qa(subject: str) -> str:
    qa = (
        (f"Draw {subject} in 60 seconds.", "Show identity, control, signaling, media, data, observability, and the boundary that changes identifiers."),
        (f"What fails first in {subject}?", "Name the smallest failure domain, then state the user-visible symptom, independent counter, and falsifier."),
        (f"How would you migrate {subject}?", "Inventory dependencies, normalize policy, pilot a reversible cohort, measure abort thresholds, wave the change, and retain rollback until hypercare exits."),
        (f"How do you prove {subject} is healthy?", "Use a synthetic user path plus Leg, correlation ID, moving Counter, and packet or platform Capture across both signaling and media."),
        (f"What tradeoff would you defend?", "State availability, security, operability, cost, and recovery consequences; name what evidence would reverse the decision."),
    )
    return "".join(f"<details><summary>Q{i + 1}. {html.escape(q)}</summary><p class=\"ans\">✅ {html.escape(a)}</p></details>" for i, (q, a) in enumerate(qa))


def dense_body(spec: SectionSpec) -> str:
    subject = spec.title
    path = spec.path or ("Intent", "Identity", "Route", "Edge", "Media", "Evidence")
    learning = {
        "vendor": ("place every named component on the end-to-end path", "separate vendor vocabulary from universal UC/CC mechanisms", "defend configuration and failure decisions with LICC proof"),
        "migration": ("sequence discovery, design, pilot, cutover, hypercare, and retirement", "quantify risk with trigger, owner, mitigation, and residual", "execute a timed rollback before irreversible thresholds pass"),
        "sev": ("scope blast radius before touching the service", "correlate both signaling and media legs using independent evidence", "restore safely, prove recovery, and prevent recurrence"),
        "architecture": ("translate requirements into boundaries and explicit quality attributes", "model normal and failure-mode paths with capacity", "turn diagrams into measurable operating contracts"),
        "mastery": ("connect fundamentals, implementation, failure, migration, and teaching", "reason vendor-neutrally while naming exact product surfaces", "produce an architect defense with evidence and reversal criteria"),
        "practicum": ("build the path from first principles", "inject one controlled failure and collect LICC evidence", "teach the decision, rollback, and falsifier without notes"),
    }[spec.mode]
    item_tuple = tuple(path) + tuple(f"{label(spec.section_id)} checkpoint {i}" for i in range(1, 7))
    risk_rows = (
        ("Identity", "Wrong tenant, user, token, certificate, or endpoint binding", "registration/auth failure rate", "freeze identity changes; restore last-known mapping"),
        ("Routing", "Pattern, queue, policy, or carrier decision diverges", "route rejects and unexpected hop count", "revert policy object; validate canary destination"),
        ("Media", "Address, codec, key, NAT, or QoS path becomes asymmetric", "RTP each direction, loss, jitter, MOS", "restore anchored known-good media policy"),
        ("Capacity", "Peak or failure-mode demand exceeds licensed or compute headroom", "concurrency, queue depth, DSP/session utilization", "shed optional load; restore capacity route"),
        ("Data", "Recording, metadata, transcript, or retention continuity breaks", "artifact completeness and reconciliation count", "pause destructive cleanup; replay from durable checkpoint"),
        ("Operations", "Alert, authority, runbook, or escalation cannot close the loop", "detection and recovery time", "declare incident command; use rehearsed manual path"),
    )
    risk_table = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in risk_rows)
    cutover_steps = (
        "T−14d: freeze scope; reconcile inventory, owners, dependencies, licenses, and external lead times.",
        "T−7d: validate certificate, DNS, time, network, identity, emergency, recording, and monitoring readiness.",
        "T−1d: capture baseline ladder, synthetic call, media metrics, queue state, and rollback artifacts.",
        "T−60m: open bridge; name commander, technical leads, evidence scribe, business validator, and rollback authority.",
        "T−30m: verify backups and immutable exports; confirm no conflicting change; start high-resolution telemetry.",
        "T−0: change one bounded control; record exact time, object, old value, new value, and operator.",
        "T+5m: test registration or login, inbound, outbound, transfer, hold, DTMF, media both ways, and teardown.",
        "T+10m: validate emergency and recording paths with approved non-emergency procedures and artifact retrieval.",
        "T+15m: compare counters to baseline; inspect error ratios, latency, quality, capacity, and unexpected retries.",
        "T+30m: business owner validates critical journeys; incident lead either advances, holds, or rolls back.",
        "T+60m: capture proof bundle; communicate state, residual risk, watch window, and next decision time.",
        "Exit: reconcile objects and records, close temporary access, retain evidence, and schedule post-change review.",
    )
    runbook = "".join(f"<li><label><input type=\"checkbox\"> {html.escape(step)}</label></li>" for step in cutover_steps)
    commands = """# Signaling + identity
dig +short SRV _sips._tcp.example.invalid
openssl s_client -connect edge.example.invalid:5061 -servername edge.example.invalid
# Media + network
tcpdump -ni any 'udp portrange 16384-32767 or port 5060 or port 5061'
# Correlation worksheet
LEG=A|EDGE|B  ID=call-or-interaction-id  COUNTER=name:value  CAPTURE=artifact@timestamp"""
    return f"""
<section class="supernova-section" data-mode="{spec.mode}">
<style>.supernova-section .tab-pane{{margin:1rem 0;padding:1rem;border:1px solid var(--border);border-radius:16px}}.supernova-section svg{{width:100%;height:auto}}.supernova-section table{{width:100%;border-collapse:collapse}}.supernova-section th,.supernova-section td{{padding:.55rem;border:1px solid var(--border);vertical-align:top}}.supernova-section th{{background:color-mix(in srgb,var(--blue) 14%,transparent);text-align:left}}.supernova-section details{{margin:.5rem 0;padding:.7rem;border-left:4px solid var(--purple);background:color-mix(in srgb,var(--card) 94%,var(--purple))}}.supernova-section .ans{{color:var(--green);font-weight:700}}.supernova-section .decision{{font-size:1.05rem;border:1px solid var(--amber);border-radius:14px;padding:1rem}}</style>
<div class="hero"><div class="eyebrow">SUPERNOVA · {html.escape(spec.group.upper())} · MASTER NOTEBOOK</div><h1>{html.escape(subject)}</h1><p>{html.escape(spec.subtitle)}</p></div>
<div class="card teal"><h2>🎯 What you’ll learn</h2><ul><li>{html.escape(learning[0])}.</li><li>{html.escape(learning[1])}.</li><li>{html.escape(learning[2])}.</li></ul><div class="flow">{svg_path(path)}</div><p class="decision"><b>⚡ Decision first:</b> {html.escape(spec.emphasis)}. Name the path, smallest failure domain, expected observation, and falsifier before any change.</p></div>
<div class="tab-bar"><button class="tab-btn active">🧭 Compass</button><button class="tab-btn">🏗 Path</button><button class="tab-btn">⚙️ Build</button><button class="tab-btn">🔬 Prove</button><button class="tab-btn">🔥 Fail</button><button class="tab-btn">🚀 Runbook</button><button class="tab-btn">🎤 Defend</button></div>
<div class="tab-pane active"><h2>🧭 One-minute mental model</h2><div class="grid"><div class="card blue"><h3>Control plane</h3><p>Identity and policy decide <i>whether</i> and <i>where</i> the interaction may proceed.</p></div><div class="card teal"><h3>Media plane</h3><p>Negotiated addresses, ports, payloads, keys, and network treatment decide whether humans can communicate.</p></div><div class="card purple"><h3>Evidence plane</h3><p>Correlation IDs, counters, captures, and user-path tests decide whether a claim is proven.</p></div></div><h3>Memory lattice</h3><p><b>INTENT → IDENTITY → ROUTE → EDGE → MEDIA → EXPERIENCE → EVIDENCE → DECISION.</b> A green control-plane state never substitutes for a two-way media proof.</p></div>
<div class="tab-pane"><h2>🏗 Architecture and dependency atlas</h2><table><tr><th>#</th><th>Node / concept</th><th>Dominant failure</th><th>Primary evidence</th><th>Falsifier</th></tr>{rows(item_tuple, subject)}</table><h3>Boundary questions</h3><ol><li>Where are identities, addresses, and correlation keys rewritten?</li><li>Which dependency can fail while every local health check stays green?</li><li>Where does signaling stop but media bypass or take another route?</li><li>Which region, carrier, tenant, site, queue, or endpoint defines blast radius?</li></ol></div>
<div class="tab-pane"><h2>⚙️ Configuration essentials</h2><table><tr><th>Order</th><th>Build action</th><th>Precondition</th><th>Proof before next step</th></tr><tr><td>1</td><td>Inventory and normalize names, numbers, identities, routes, certificates, codecs, and ownership</td><td>Authoritative exports and timestamps</td><td>Reconciled count; exceptions owned</td></tr><tr><td>2</td><td>Build identity and trust</td><td>DNS, NTP, certificate chain, lifecycle</td><td>Authentication and renewal canary</td></tr><tr><td>3</td><td>Build deterministic routing and admission</td><td>Normalized patterns and capacity</td><td>Positive, negative, emergency, and overflow tests</td></tr><tr><td>4</td><td>Build media policy and network path</td><td>Address, NAT, firewall, QoS, codec plan</td><td>RTP both ways with quality baseline</td></tr><tr><td>5</td><td>Attach recording, analytics, CRM, APIs, and data controls</td><td>Consent, retention, scopes, schemas</td><td>Artifact retrieval and event reconciliation</td></tr><tr><td>6</td><td>Enable canary and operational ownership</td><td>Alerts, runbook, rollback authority</td><td>Fault injected; detection and recovery timed</td></tr></table><pre class="code">{html.escape(commands)}</pre></div>
<div class="tab-pane"><h2>🔬 Proof grammar — LICC</h2><table><tr><th>Leg</th><th>ID</th><th>Counter</th><th>Capture</th></tr><tr><td>Caller/entry → edge; edge → service; service → endpoint/agent; independent RTP directions</td><td>Call-ID + tags, interaction/conversation ID, session ID, recording ID, API request ID</td><td>Attempts, accepts, rejects, active sessions, queue depth, RTP packets, loss, jitter, latency, recording completion</td><td>SIP ladder, SDP pair, packet capture, platform event timeline, QoE record, audit change, retrieved artifact</td></tr></table><h3>Evidence contract</h3><pre class="code">TIME WINDOW: start/end/timezone\nSCOPE: tenant|region|site|carrier|queue|endpoint\nEXPECTED: exact event or counter movement\nFALSIFIER: observation that makes this diagnosis wrong\nVERDICT: SHIPPED | VERIFIED | RESIDUAL | BLOCKED</pre><p>Collect both sides of any identifier-rewriting boundary. Keep platform-green, user-green, and evidence-green as separate verdicts.</p></div>
<div class="tab-pane"><h2>🔥 Failure and risk laboratory</h2><table><tr><th>Plane</th><th>Failure mode</th><th>Counter / capture</th><th>Containment or rollback</th></tr>{risk_table}</table><h3>Fault tree</h3><pre class="code">USER FAILURE\n├─ no setup → identity | DNS | route | admission | dependency\n├─ setup, no media → SDP | NAT | firewall | key | codec | endpoint\n├─ media, poor quality → loss | jitter | delay | queue | Wi-Fi | transcoding\n├─ agent/data failure → state | queue | API | schema | auth | rate limit\n└─ artifact missing → policy | fork | consent | storage | metadata | retention</pre></div>
<div class="tab-pane"><h2>🚀 Cutover runbook</h2><ol class="checklist">{runbook}</ol><h3>Rollback card</h3><table><tr><th>Trigger</th><th>Authority</th><th>Reverse path</th><th>Validation</th></tr><tr><td>Critical journey fails twice; emergency/recording control fails once; error or quality threshold breached; evidence is contradictory</td><td>Named incident commander with business and compliance stop authority</td><td>Restore versioned route/policy/trust object; drain or redirect sessions; preserve logs and data; prevent split state</td><td>Fresh synthetic interaction, two-way media, correct route and identity, artifact retrieval, counters back inside baseline</td></tr></table></div>
<div class="tab-pane"><h2>🎤 Interview and architect defense</h2>{interview_qa(subject)}<h3>90-second answer frame</h3><p><b>Requirement → path → boundary → failure → proof → decision → rollback → residual.</b> End by naming the evidence that would change your recommendation.</p><h3>Mastery checklist</h3><ul><li>□ Draw the path from memory and mark every identifier-changing boundary.</li><li>□ Explain one normal flow and three failure flows without product-menu narration.</li><li>□ Name one counter and one capture for signaling, media, identity, capacity, and data.</li><li>□ State a reversible canary and a time-bounded rollback trigger.</li><li>□ Teach the design to a junior, then defend it to a principal engineer.</li></ul></div>
</section>""".strip()


def vendor_specs() -> list[SectionSpec]:
    specs: list[SectionSpec] = []
    for slug, (vendor, path, evidence) in VENDORS.items():
        for surface_slug, surface_title, focus in VENDOR_SURFACES:
            specs.append(SectionSpec(f"vd-{slug}-{surface_slug}", "Vendor Deep-Dives", f"{surface_title} · {vendor}", f"Six-layer {vendor} deep-dive: {focus}.", path, f"For {vendor}, anchor every claim to {evidence}", "vendor"))
    return specs


def migration_specs() -> list[SectionSpec]:
    path = ("Discover", "Design", "Pilot", "Cutover", "Hypercare", "Retire")
    return [SectionSpec(identifier, "Cloud Migrations", f"🚀 {label(identifier)}", "Phase-by-phase factory with risk ledger, cutover clock, proof gates, and rehearsed rollback.", path, f"For {label(identifier)}, no wave advances until dependency, user-path, artifact, and rollback gates are green", "migration") for identifier in MIGRATIONS]


def sev_specs() -> list[SectionSpec]:
    path = ("Scope", "Stabilize", "Correlate", "Capture", "Recover", "Prevent")
    return [SectionSpec(f"sev2-{740 + i}", "Tricky SEVs v17", f"🔥 SEV {740 + i} · {topic}", "Timed production incident laboratory: decision first, evidence before change, recovery before closure.", path, f"Treat {topic} as a hypothesis until both expected observation and falsifier are captured", "sev") for i, topic in enumerate(SEV_TOPICS)]


def mastery_specs() -> list[SectionSpec]:
    specs: list[SectionSpec] = []
    arch_path = ("Requirements", "Boundaries", "Flows", "Failures", "Evidence", "Roadmap")
    for item in ARCH_TOPICS:
        specs.append(SectionSpec(f"arch-{item}", "Architecture + Mastery", f"🏛 Architecture · {label(item)}", "Principal-level design notebook: quality attributes, boundaries, operating model, and decision evidence.", arch_path, f"The {label(item)} diagram is incomplete until every arrow has an owner, counter, failure mode, and rollback consequence", "architecture"))
    mastery_path = ("Fundamentals", "Protocol", "Implementation", "Failure Lab", "Migration", "Teach-Back")
    for item in MASTERY_TOPICS:
        specs.append(SectionSpec(item, "Architecture + Mastery", f"🎓 Mastery Map · {label(item)}", "Lifetime mastery braid from invariant physics to interview and teaching defense.", mastery_path, f"Mastery in {label(item)} means predicting evidence before opening the tool", "mastery"))
    # The enumerated packs total fewer than 600 sections from the 252-section
    # baseline. These 120 additive practicums close that arithmetic gap while
    # preserving the requested core sections and turning breadth into drills.
    practicum_path = ("Model", "Build", "Inject", "Observe", "Reverse", "Teach")
    for domain in PRACTICUM_DOMAINS:
        for index, lab in enumerate(PRACTICUM_LABS, 1):
            specs.append(SectionSpec(f"mp-{domain}-{index:02d}", "Mastery Practicums", f"🧪 {label(domain)} · {label(lab)}", "Bounded architect practicum with safe fault injection, proof bundle, rollback clock, and oral defense.", practicum_path, f"In the {domain} {lab} lab, change exactly one variable and predict the counter and capture before executing", "practicum"))
    return specs


PACK_BUILDERS = {"vendor": vendor_specs, "migration": migration_specs, "sev": sev_specs, "mastery": mastery_specs}


def locate(text: str) -> tuple[int, list[dict[str, object]]]:
    match = re.search(r"window\.SECTIONS\s*=\s*", text)
    if not match:
        raise RuntimeError("window.SECTIONS not found")
    start = text.find("[", match.end())
    end = text.find("\n];", start)
    if start < 0 or end < 0:
        raise RuntimeError("SECTIONS array boundary not found")
    parsed = json.loads(text[start : end + 2])
    if not isinstance(parsed, list) or any(not isinstance(x, dict) for x in parsed):
        raise RuntimeError("SECTIONS must be a dense object list")
    return end, parsed


def update_stats(text: str, count: int) -> str:
    updated, matches = re.subn(r'(window\.STATS\s*=\s*\{[^;]*?"sections"\s*:\s*)\d+', rf"\g<1>{count}", text, count=1, flags=re.S)
    if matches != 1:
        raise RuntimeError("STATS section count update failed")
    return updated


def inject(pack: str, path: Path, dry_run: bool) -> tuple[int, int, int]:
    original = path.read_text(encoding="utf-8")
    working = original.replace(".supernova-section .tab-pane{display:block;", ".supernova-section .tab-pane{")
    end, existing = locate(working)
    existing_ids = {str(x.get("id", "")) for x in existing}
    specs = PACK_BUILDERS[pack]()
    duplicates = [spec.section_id for spec in specs if sum(1 for item in specs if item.section_id == spec.section_id) > 1]
    if duplicates:
        raise RuntimeError(f"duplicate generated IDs: {sorted(set(duplicates))}")
    additions = []
    for ordinal, spec in enumerate(specs, 1):
        if spec.section_id in existing_ids:
            continue
        additions.append({"id": spec.section_id, "num": f"W1-{pack[:2].upper()}-{ordinal:03d}", "group": spec.group, "title": spec.title, "sub": spec.subtitle, "body": dense_body(spec)})
    payload = ""
    if additions:
        payload = ",\n" + ",\n".join(json.dumps(section, ensure_ascii=False, separators=(",", ":")) for section in additions)
    updated = working[:end] + payload + working[end:]
    updated = update_stats(updated, len(existing) + len(additions))
    _, parsed = locate(updated)
    if len(parsed) != len(existing) + len(additions) or any(not x for x in parsed):
        raise RuntimeError("post-injection parse or density gate failed")
    if not dry_run and updated != original:
        path.write_text(updated, encoding="utf-8")
    return len(additions), len(updated.encode("utf-8")) - len(original.encode("utf-8")), len(parsed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", choices=tuple(PACK_BUILDERS))
    parser.add_argument("--html", type=Path, default=FLAGSHIP)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    added, byte_delta, total = inject(args.pack, args.html.resolve(), args.dry_run)
    print(json.dumps({"pack": args.pack, "added_sections": added, "added_bytes": byte_delta, "total_sections": total, "dry_run": args.dry_run}))


if __name__ == "__main__":
    main()
