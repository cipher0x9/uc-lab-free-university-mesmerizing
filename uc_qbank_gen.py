#!/usr/bin/env python3
"""Generate and inject the Wave-1 UC/CC practice-bank sections.

The generator is deliberately deterministic and idempotent: it appends only
missing bank IDs, preserves the original SECTIONS bytes, and reconciles the
visible section statistic with the parsed array length.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_HTML = ROOT / "university" / "v17-UNIVERSITY.html"


@dataclass(frozen=True)
class Topic:
    section_id: str
    title: str
    focus: tuple[str, ...]


TOPICS = (
    Topic("qb-sip-deep", "SIP Deep", ("transactions", "dialogs", "Via routing", "Record-Route", "SDP offers", "response classes", "PRACK", "re-INVITE", "session timers", "forking", "TLS identity", "ladder correlation", "B2BUA boundaries", "CSeq ordering", "Contact routing", "early media", "REFER transfer", "OPTIONS health", "DNS NAPTR/SRV", "cause mapping")),
    Topic("qb-cucm-deep", "CUCM Deep", ("database replication", "regions", "locations", "device pools", "route patterns", "calling search spaces", "partitions", "media resources", "TFTP", "SDL traces", "SIP normalization", "digit analysis", "SRST", "CAC", "CTI", "Extension Mobility", "route lists", "transformation patterns", "certificates", "service activation")),
    Topic("qb-cube-deep", "CUBE Deep", ("dial peers", "voice class tenants", "SIP profiles", "translation rules", "codec classes", "DTMF relay", "early offer", "bind statements", "TLS trustpoints", "media flow-around", "transcoding", "OPTIONS keepalive", "URI matching", "cause codes", "debug ccsip", "VRF routing", "HA pairs", "fax relay", "privacy headers", "call legs")),
    Topic("qb-webex", "Webex", ("Control Hub", "calling locations", "local gateway", "Dedicated Instance", "Webex App", "identity sync", "SSO", "media quality", "hybrid services", "devices", "number management", "emergency calling", "analytics", "recording", "voicemail", "queues", "auto attendants", "API webhooks", "site survivability", "release channels")),
    Topic("qb-teams", "Microsoft Teams Phone", ("Phone System", "Direct Routing", "Operator Connect", "Calling Plans", "SBC pairing", "voice routes", "PSTN usages", "dial plans", "resource accounts", "auto attendants", "call queues", "CQD", "Call Analytics", "media bypass", "Location Information Service", "network regions", "emergency policies", "normalization rules", "certificates", "tenant policy")),
    Topic("qb-zoom", "Zoom Phone", ("sites", "BYOC", "SBC routing", "call queues", "auto receptionists", "emergency locations", "number inventory", "routing rules", "policy groups", "quality dashboards", "recording", "voicemail", "shared line groups", "devices", "provisioning", "SSO", "nomadic emergency", "analytics", "survivability", "porting")),
    Topic("qb-genesys", "Genesys Cloud CX", ("organizations", "architect flows", "queues", "skills", "divisions", "trunks", "sites", "edges", "BYOC", "WebRTC", "data actions", "wrap-up codes", "quality policies", "workforce management", "analytics", "recording", "OAuth clients", "event notifications", "routing methods", "outbound campaigns")),
    Topic("qb-nice", "NICE CXone", ("ACD skills", "Studio scripts", "points of contact", "campaigns", "agent states", "business units", "dispositions", "digital channels", "recording", "quality management", "workforce management", "interaction analytics", "SIP trunks", "IVR", "API authentication", "data retention", "screen recording", "routing", "reports", "tenant controls")),
    Topic("qb-five9", "Five9", ("domains", "campaigns", "skills", "IVR scripts", "dispositions", "agent states", "station types", "connectors", "recording", "quality management", "workforce management", "dialers", "lists", "DNC controls", "SIP connectivity", "number inventory", "reports", "web services", "tenant roles", "failover")),
    Topic("qb-twilio", "Twilio Flex", ("Studio flows", "TaskRouter", "workers", "workspaces", "task queues", "routing expressions", "Functions", "Event Streams", "Media Streams", "SIP Domains", "Elastic SIP Trunking", "Voice SDK", "webhooks", "status callbacks", "recording", "Conversations", "Verify", "API credentials", "rate limits", "observability")),
    Topic("qb-avaya", "Avaya Aura", ("Communication Manager", "Session Manager", "System Manager", "SIP entities", "entity links", "routing policies", "adaptations", "network regions", "signaling groups", "trunk groups", "ARS", "AAR", "media gateways", "DSP resources", "survivable servers", "AES", "vectoring", "VDNs", "traceSM", "SAT traces")),
    Topic("qb-mitel", "Mitel", ("call control", "SIP trunks", "dial plans", "hunt groups", "device provisioning", "embedded voicemail", "media gateways", "survivability", "licenses", "roles", "call routing", "emergency services", "recording", "contact center", "quality metrics", "certificates", "network zones", "failover", "backups", "upgrades")),
    Topic("qb-8x8", "8x8", ("sites", "users", "devices", "number inventory", "call queues", "ring groups", "auto attendants", "routing", "emergency addresses", "quality analytics", "recording", "voicemail", "contact center", "SSO", "roles", "APIs", "porting", "policies", "network readiness", "business continuity")),
    Topic("qb-ringcentral", "RingCentral", ("sites", "extensions", "devices", "phone numbers", "call queues", "IVR menus", "routing rules", "emergency response locations", "quality analytics", "recording", "voicemail", "contact center", "SSO", "roles", "APIs", "number porting", "templates", "network readiness", "survivability", "audit logs")),
    Topic("qb-asterisk", "Asterisk and FreePBX", ("PJSIP endpoints", "transports", "AORs", "auth objects", "dialplan contexts", "extensions", "trunks", "NAT settings", "RTP ranges", "codec negotiation", "DTMF modes", "queues", "ring groups", "IVR", "voicemail", "CDRs", "CEL", "AMI", "ARI", "packet capture")),
    Topic("qb-migration", "UC Migration", ("discovery", "inventory", "dependency maps", "target architecture", "number porting", "dial-plan normalization", "identity readiness", "network readiness", "pilot cohorts", "parallel run", "UAT", "cutover waves", "rollback", "hypercare", "decommission", "data retention", "recording continuity", "emergency continuity", "license mapping", "success metrics")),
    Topic("qb-cc-arch", "Contact Center Architecture", ("entry points", "IVR", "routing engine", "queues", "skills", "agent desktop", "CRM integration", "recording", "quality management", "workforce management", "analytics", "digital channels", "outbound", "fraud controls", "PCI boundaries", "identity", "data actions", "event streams", "resilience", "capacity")),
    Topic("qb-cloud", "Cloud UC and CC", ("shared responsibility", "regions", "availability zones", "tenancy", "identity federation", "private connectivity", "internet egress", "SBC edges", "media locality", "autoscaling", "observability", "API quotas", "data residency", "encryption", "key management", "backup", "disaster recovery", "status pages", "synthetic probes", "cost allocation")),
    Topic("qb-security", "UC Security", ("TLS", "SRTP", "certificate chains", "mutual authentication", "SBC policy", "toll fraud", "credential stuffing", "least privilege", "MFA", "SSO", "RBAC", "audit logs", "recording access", "PII", "PCI scope", "patching", "segmentation", "rate limiting", "threat detection", "incident response")),
    Topic("qb-e911-deep", "Emergency Calling Deep", ("dispatchable location", "emergency response locations", "location discovery", "nomadic users", "dynamic location", "ELIN", "ERL", "PSAP routing", "callback numbers", "on-site notification", "test procedures", "carrier validation", "floor and room data", "network identifiers", "fallback routing", "remote users", "change control", "audit evidence", "outage continuity", "legal review")),
    Topic("qb-recording", "Call Recording", ("recording policies", "consent", "media forking", "SIPREC", "stereo channels", "pause and resume", "PCI controls", "encryption", "retention", "legal hold", "search", "playback authorization", "screen recording", "metadata", "clock sync", "storage capacity", "failure alarms", "export controls", "audit trails", "quality sampling")),
    Topic("qb-qm-wfm", "Quality and Workforce Management", ("evaluation forms", "calibration", "sampling", "coaching", "screen capture", "speech analytics", "sentiment", "forecasting", "scheduling", "adherence", "shrinkage", "occupancy", "service level", "abandonment", "intraday management", "skills", "work rules", "time zones", "exceptions", "governance")),
    Topic("qb-api", "UC and CC APIs", ("REST resources", "OAuth", "scopes", "webhooks", "event ordering", "idempotency", "pagination", "rate limits", "retry backoff", "correlation IDs", "schema versioning", "secrets", "signature validation", "timeouts", "circuit breakers", "dead-letter queues", "observability", "sandbox testing", "data minimization", "rollback")),
    Topic("qb-ai-cc", "AI in Contact Center", ("transcription", "summarization", "agent assist", "intent classification", "knowledge retrieval", "grounding", "hallucination", "evaluation sets", "latency budgets", "human escalation", "PII redaction", "prompt injection", "model drift", "bias testing", "confidence thresholds", "auditability", "feedback loops", "cost controls", "availability fallback", "change governance")),
    Topic("qb-interview", "UC and CC Interviews", ("requirements framing", "architecture tradeoffs", "call-flow narration", "failure domains", "LICC proof", "capacity math", "security posture", "migration sequencing", "rollback design", "stakeholder communication", "incident command", "vendor neutrality", "cost modeling", "SLA design", "observability", "automation", "postmortems", "mentoring", "executive summaries", "teach-back")),
    Topic("qb-network", "UC Network", ("latency", "jitter", "loss", "QoS trust boundaries", "DSCP", "queues", "policing", "shaping", "VLANs", "DHCP options", "DNS", "NTP", "MTU", "fragmentation", "NAT", "firewalls", "path MTU", "Wi-Fi roaming", "capacity", "packet capture")),
    Topic("qb-sbc", "Session Border Controllers", ("B2BUA behavior", "topology hiding", "admission control", "header normalization", "media anchoring", "NAT traversal", "TLS termination", "SRTP interworking", "codec policy", "DTMF interworking", "transcoding", "routing tables", "health probes", "rate limits", "DoS protection", "HA state", "certificate rotation", "cause mapping", "packet capture", "call-leg correlation")),
    Topic("qb-voice-quality", "Voice Quality", ("MOS", "latency", "jitter", "packet loss", "concealment", "codec choice", "sample rate", "packetization", "jitter buffers", "echo", "gain", "clipping", "DTMF", "QoS", "Wi-Fi", "transcoding", "RTP sequence", "RTCP reports", "one-way audio", "synthetic calls")),
)


# Sixty vendor-neutral facts form the common technical spine in every bank.
# Twenty topic anchors are added per bank, producing 80 facts x 5 variants.
COMMON_FACTS = (
    ("SIP transaction", "A request and its final response form the core transaction exchange", "It is the RTP stream", "It is a DNS zone", "It is a codec", "Correlate method, branch, CSeq, and responses before diagnosing media."),
    ("SIP dialog", "Call-ID plus local and remote tags identify a dialog", "Only an IP address identifies it", "Only CSeq identifies it", "Only the From URI identifies it", "Dialog identifiers survive route hops better than display names."),
    ("SIP provisional response", "A 1xx response reports call progress before a final response", "It always ends the dialog", "It carries RTP statistics", "It changes DNS", "Distinguish signaling progress from confirmed media."),
    ("SIP success response", "A 2xx response indicates successful handling of a request", "It proves two-way audio", "It proves QoS", "It is always retransmitted forever", "Signaling success alone does not prove a healthy media plane."),
    ("SIP client error", "A 4xx response generally describes a request or client-side condition", "It is always a server crash", "It is an RTP packet", "It guarantees retry success", "Read the exact code and Reason header in context."),
    ("SIP server error", "A 5xx response generally reports server-side failure to fulfill the request", "It proves caller fraud", "It is a codec payload", "It means DNS succeeded end to end", "Use Retry-After when present and protect upstreams from retry storms."),
    ("SDP offer and answer", "Endpoints negotiate media addresses, ports, codecs, and attributes", "It configures user licensing", "It replaces SIP routing", "It is a voicemail database", "Compare both SDP bodies, not just the SIP status line."),
    ("RTP", "RTP transports time-sensitive media and carries sequence and timestamp fields", "RTP resolves DNS", "RTP provisions phones", "RTP is a certificate format", "Sequence gaps and timestamp behavior are primary media evidence."),
    ("RTCP", "RTCP reports reception quality and participant statistics for RTP sessions", "RTCP replaces call signaling", "RTCP is always TCP", "RTCP assigns phone numbers", "Use RTCP loss and jitter reports beside packet captures."),
    ("one-way audio", "A bidirectional signaling success can coexist with a broken media path in one direction", "It is always a handset speaker fault", "It proves the call never connected", "It is fixed by changing caller ID", "Trace each RTP leg independently through NAT, firewall, and SBC boundaries."),
    ("NAT", "Address translation can invalidate embedded media addresses unless traversal or anchoring corrects them", "NAT encrypts RTP", "NAT assigns codecs", "NAT eliminates firewalls", "Compare advertised SDP addresses with observed packet sources and destinations."),
    ("B2BUA", "A back-to-back user agent terminates one signaling leg and originates another", "It only forwards Ethernet frames", "It is a DNS resolver", "It cannot alter SDP", "Correlate both legs because identifiers and headers can change at the boundary."),
    ("TLS", "TLS protects signaling in transit and authenticates peers according to certificate policy", "TLS guarantees voice quality", "TLS compresses audio", "TLS removes certificate expiry", "Validate chain, name, time, purpose, and trust on both peers."),
    ("SRTP", "SRTP adds confidentiality, message authentication, and replay protection to RTP", "SRTP encrypts SIP routing", "SRTP provisions devices", "SRTP replaces identity", "Confirm key negotiation and packet counters on every media leg."),
    ("certificate expiry", "An expired certificate can break otherwise healthy signaling or API trust", "It only changes audio volume", "It improves encryption", "It is ignored by all clients", "Monitor expiration ahead of maintenance windows and rehearse rotation."),
    ("DNS SRV", "SRV records express service targets, ports, priority, and weight", "SRV stores RTP", "SRV assigns DSCP", "SRV encrypts passwords", "Test every target and failure path, not only the first answer."),
    ("NTP", "Accurate shared time is essential for certificates, logs, tokens, and cross-system correlation", "NTP selects codecs", "NTP routes calls", "NTP replaces packet capture", "Clock skew can turn one incident into several misleading timelines."),
    ("DSCP", "DSCP marks packets for differentiated treatment but does not itself create bandwidth", "DSCP guarantees zero loss", "DSCP encrypts media", "DSCP is a SIP response", "Verify marking and queue behavior at every trust boundary."),
    ("jitter", "Jitter is variation in packet arrival timing", "Jitter is constant propagation delay", "Jitter is a dial-plan loop", "Jitter is certificate drift", "Measure distributions and buffer behavior rather than relying on a single average."),
    ("packet loss", "Lost media packets may cause gaps, concealment, and lower conversational quality", "Loss always improves MOS", "Loss only affects signaling", "Loss is repaired by DNS", "Direction, burst pattern, codec, and concealment determine user impact."),
    ("latency", "Excess end-to-end delay impairs conversational interactivity even when audio is clear", "Latency is only volume", "Latency cannot vary by path", "Latency is fixed by caller ID", "Measure one-way delay when possible and separate network from processing delay."),
    ("MOS", "MOS is a quality estimate or rating, not a root-cause measurement", "MOS identifies the failed router", "MOS proves compliance", "MOS is a SIP method", "Use MOS to detect impact, then inspect loss, jitter, delay, codec, and device evidence."),
    ("codec negotiation", "Both endpoints need a mutually acceptable codec on each media leg", "The longest codec name always wins", "DNS selects the codec", "All codecs are lossless", "Inspect payload types and any transcoder allocation."),
    ("transcoding", "Transcoding consumes processing resources and can add delay or quality loss", "Transcoding removes all jitter", "Transcoding is free of capacity limits", "Transcoding changes DNS", "Track resource allocation and avoid unnecessary codec boundaries."),
    ("DTMF", "DTMF transport method must interoperate across every call leg", "DTMF is always in-band", "DTMF is a routing protocol", "DTMF cannot cross an SBC", "Compare negotiated methods and events end to end."),
    ("fax over IP", "Fax reliability depends on negotiated transport, timing, loss, and gateway behavior", "Fax always uses the voice codec unchanged", "Fax is immune to jitter", "Fax does not traverse SIP", "Capture the re-INVITE and confirm T.38 or controlled audio passthrough behavior."),
    ("dial plan", "A dial plan transforms user intent into a routable destination under policy", "A dial plan is only a contact list", "It carries RTP", "It replaces emergency policy", "Normalize early, route deterministically, and log the matched rule."),
    ("route loop", "A route loop repeatedly sends a call through the same logical path until a limit stops it", "It improves redundancy", "It is a codec mismatch", "It is expected on every transfer", "Trace hop history and matched rules; do not merely raise hop limits."),
    ("least-cost routing", "Cost selection must remain subordinate to availability, quality, policy, and emergency requirements", "Cheapest is always correct", "It removes carrier testing", "It replaces redundancy", "Model failure and quality before optimizing price."),
    ("emergency calling", "Emergency design must preserve accurate routing and dispatchable location under normal and failure conditions", "Caller ID alone is always sufficient", "Remote users need no location process", "Emergency paths need no testing", "Treat location, callback, notification, carrier validation, and fallback as one system."),
    ("call recording", "Recording success requires media, policy, metadata, storage, and access controls to agree", "A SIP 200 proves the recording exists", "Recording has no legal scope", "Storage cannot fill", "Test retrieval and playback with correct metadata, not only session initiation."),
    ("data retention", "Retention policy must align business, legal, privacy, and deletion requirements", "Keep everything forever by default", "Retention only concerns backups", "Users may bypass holds", "Prove both preservation and defensible deletion."),
    ("OAuth scope", "An access token should carry only the scopes needed by the integration", "Every token should be administrator", "Scopes replace TLS", "Scopes never expire", "Least privilege reduces blast radius when credentials are exposed."),
    ("webhook validation", "Receivers should authenticate or validate webhook origin and handle replay safely", "All inbound JSON is trusted", "Webhooks need no retries", "Webhooks are ordered forever", "Validate signatures where supported and make handlers idempotent."),
    ("API rate limit", "Clients should honor limits and retry transient failures with bounded backoff and jitter", "Retry instantly without limit", "Rate limits prove an outage", "Create new credentials per request", "Bounded retries prevent a local fault from amplifying a provider incident."),
    ("idempotency", "An idempotent operation can be retried without duplicating the intended effect", "It guarantees zero latency", "It removes authentication", "It means requests never fail", "Use stable operation keys and record outcomes across retry boundaries."),
    ("correlation ID", "A correlation ID joins events across signaling, media, APIs, and services", "It replaces timestamps", "It is always a phone number", "It should change on every log line", "Preserve and map identifiers at every boundary."),
    ("observability", "Metrics, logs, traces, synthetic probes, and user evidence answer different questions", "One dashboard proves everything", "Logs replace packet captures", "Synthetic tests prove all users are healthy", "Triangulate independent evidence before declaring recovery."),
    ("baseline", "A known-good baseline makes change impact and anomaly detection measurable", "A baseline is a vendor default", "Baselines eliminate incidents", "Only failed calls belong in a baseline", "Capture normal signaling, media, counters, latency, and capacity before migration."),
    ("change canary", "A canary limits blast radius while testing the real production path", "A canary replaces rollback", "A canary is a load test only", "Canaries should include every user", "Define success, abort thresholds, owner, and observation window in advance."),
    ("rollback", "A rollback is executable only when triggers, authority, data effects, and validation are explicit", "Rollback means restart", "Rollback can be designed after failure", "Rollback never affects data", "Time-box the decision and rehearse the reverse path."),
    ("high availability", "Redundant components help only when failure detection, state, routing, and capacity are validated", "Two nodes guarantee service", "HA removes maintenance", "HA needs no testing", "Fail one dependency at a time and prove user-path continuity."),
    ("disaster recovery", "DR addresses site or regional loss with recovery objectives, dependencies, and exercised procedures", "DR is the same as a server restart", "Backups alone prove DR", "DR has no identity dependency", "Test restore, routing, identity, carrier, data, and operational authority."),
    ("capacity", "Capacity planning combines arrival demand, concurrency, service time, media, licenses, and headroom", "Peak average is always enough", "Licenses equal bandwidth", "Capacity never changes during incidents", "Model peak and failure-mode capacity, then validate with telemetry."),
    ("contact-center service level", "Service level measures the share of eligible interactions answered within a target interval", "It is identical to occupancy", "It measures audio MOS", "It ignores queue policy", "Document interval, eligibility, abandonment treatment, and time window."),
    ("occupancy", "Occupancy compares handling workload with staffed available time and becomes risky when sustained too high", "Occupancy is network utilization", "Higher is always healthier", "Occupancy equals service level", "Read occupancy with shrinkage, adherence, backlog, and employee impact."),
    ("abandonment", "Abandonment reflects contacts that leave before answer under a defined measurement policy", "Every short abandon is an agent failure", "Abandonment measures jitter", "It has no interval", "Separate caller tolerance, wait messaging, routing, and short-abandon rules."),
    ("skills-based routing", "Skills-based routing matches interaction requirements to eligible agent capabilities and policy", "It always selects the longest-idle agent", "It eliminates queues", "It ignores proficiency", "Test scarcity, overflow, priority, proficiency, and fallback behavior."),
    ("IVR", "An IVR collects intent or data and routes under defined error, timeout, and escape behavior", "An IVR is only a greeting", "It replaces authentication policy", "It needs no telemetry", "Measure containment, errors, latency, transfers, and caller escape."),
    ("agent state", "Accurate agent state is required for routing, adherence, reporting, and capacity interpretation", "Agent state only changes screen color", "It has no timestamp", "It is unrelated to queues", "Correlate desktop events, routing events, telephony state, and reason codes."),
    ("recording consent", "Consent requirements depend on jurisdiction, purpose, channel, and organizational policy", "One global rule always applies", "Consent is only a storage issue", "Consent never changes", "Use legal review and make announcements and controls testable."),
    ("PCI boundary", "Reducing sensitive payment data exposure reduces compliance scope and breach impact", "Record all card data for proof", "PCI only applies to networks", "Pause controls need no audit", "Tokenize or isolate payment capture and verify recording suppression."),
    ("identity federation", "Federation links enterprise identity to service access but still needs lifecycle and authorization controls", "SSO eliminates offboarding", "Federation replaces RBAC", "Identity cannot fail regionally", "Test joiner, mover, leaver, break-glass, and certificate rotation paths."),
    ("RBAC", "Role-based access should grant the minimum capabilities needed for a job function", "Every operator needs global admin", "RBAC encrypts RTP", "RBAC replaces audit logs", "Separate build, approve, operate, investigate, and export privileges."),
    ("backup", "A backup is useful only when integrity, retention, access, and restore have been tested", "Backup success proves restore success", "Backups need no encryption", "Snapshots replace runbooks", "Run representative restores and record recovery time and data loss."),
    ("postmortem", "A useful postmortem explains system conditions, evidence, decisions, and prevention without blame", "It names one person as root cause", "It omits timelines", "It closes before actions have owners", "Track corrective actions to verified completion."),
    ("LICC proof", "A complete troubleshooting claim names the Leg, correlation ID, Counter, and Capture", "A screenshot alone is enough", "Restarting proves root cause", "User reports replace telemetry", "Evidence should include expected observation and a falsifier."),
    ("failure domain", "A failure domain is the smallest boundary whose loss explains the affected scope", "It is always one server", "It equals vendor name", "It cannot cross dependencies", "Map tenant, site, region, carrier, identity, edge, and endpoint blast radius."),
    ("synthetic call", "A synthetic call tests a defined path repeatedly and can detect failure before broad user reports", "It proves every feature", "It needs no cleanup", "It replaces human validation", "Tag probes, exclude them from business KPIs, and alert on path-specific failures."),
    ("teach-back", "Explaining a design with path, failure, evidence, and rollback exposes shallow understanding", "Memorizing menu names is equivalent", "Teach-back needs no diagram", "Only trainers use it", "A concise defense should survive why, how, fail, prove, and reverse questions."),
)


def rotated_options(correct: str, wrong: tuple[str, str, str], seed: int) -> tuple[list[str], str]:
    options = [correct, *wrong]
    shift = seed % 4
    options = options[shift:] + options[:shift]
    return options, "ABCD"[options.index(correct)]


def question_html(number: int, prompt: str, correct: str, wrong: tuple[str, str, str], explanation: str) -> str:
    options, letter = rotated_options(correct, wrong, number)
    choices = " ".join(f"{'ABCD'[i]}) {html.escape(value)}" for i, value in enumerate(options))
    return (
        f"<details><summary>Q{number}. {html.escape(prompt)}</summary>"
        f"<p>{choices}</p><p class=\"ans\">✅ Answer: {letter} — {html.escape(explanation)}</p></details>"
    )


def fact_variants(topic: Topic, fact_number: int, fact: tuple[str, str, str, str, str, str]) -> list[str]:
    concept, correct, w1, w2, w3, why = fact
    context = topic.title
    wrong = (w1, w2, w3)
    base = (fact_number - 1) * 5
    return [
        question_html(base + 1, f"In {context}, what best describes {concept}?", correct, wrong, why),
        question_html(base + 2, f"Which statement is the strongest match for {concept}?", correct, (w2, w3, w1), why),
        question_html(base + 3, f"A review finds uncertainty around {concept}. What should the engineer assert first?", correct, (w3, w1, w2), why),
        question_html(base + 4, f"Which {concept} claim survives an evidence review?", correct, wrong, why),
        question_html(base + 5, f"Choose the accurate true-or-false evaluation for {concept}.", f"True — {correct}", (f"False — {correct}", f"True — {w1}", f"True — {w2}"), why),
    ]


def anchor_fact(topic: Topic, focus: str, index: int) -> tuple[str, str, str, str, str, str]:
    rules = (
        ("path placement", f"Place {focus} on the signaling, media, identity, policy, or evidence path before changing it", f"Treat {focus} as an isolated menu label", f"Assume {focus} affects every call leg equally", f"Restart all nodes before locating {focus}", "Path placement narrows the failure domain and prevents symptom-driven changes."),
        ("configuration control", f"Baseline and peer-review the {focus} configuration, then change one bounded variable", f"Change {focus} on every site at once", f"Skip rollback because {focus} is familiar", f"Use screenshots as the only source of truth", "A versioned baseline, canary, and rollback make configuration change observable."),
        ("failure evidence", f"Prove {focus} with a named leg, correlation ID, moving counter, and capture or platform artifact", f"Declare {focus} healthy from a green icon", f"Restart until the symptom disappears", f"Use an unrelated historical alarm", "LICC evidence connects symptom, path, measurement, and falsifier."),
        ("capacity", f"Validate {focus} at normal peak and during the intended failure mode with explicit headroom", f"Size {focus} from daily average only", f"Assume licenses prove media capacity", f"Ignore retry amplification around {focus}", "Failure-mode demand and retries often expose limits hidden by averages."),
        ("security", f"Apply least privilege, authenticated control, auditability, and bounded exposure to {focus}", f"Expose {focus} broadly for convenience", f"Share permanent administrator credentials", f"Disable logs to reduce storage", "Security controls must reduce blast radius without hiding operational evidence."),
        ("migration", f"Map dependencies for {focus}, pilot it, define abort thresholds, and rehearse rollback", f"Migrate {focus} in an unmeasured big bang", f"Decommission the source before validation", f"Let success criteria emerge after cutover", "Dependency mapping and reversible waves turn migration risk into measured decisions."),
        ("operations", f"Own {focus} with an SLO, alert, runbook, escalation path, and post-change validation", f"Wait for users to report every {focus} failure", f"Alert on every event without thresholds", f"Close incidents when the dashboard turns green", "Operations require user-path validation and explicit ownership, not dashboard color alone."),
    )
    dimension, correct, w1, w2, w3, why = rules[index % len(rules)]
    return (f"{focus} — {dimension}", correct, w1, w2, w3, why)


def diagram(topic: Topic) -> str:
    labels = [html.escape(x) for x in topic.focus[:5]]
    colors = ("#38bdf8", "#22c55e", "#f59e0b", "#a78bfa", "#fb7185")
    boxes = []
    for i, (label, color) in enumerate(zip(labels, colors)):
        x = 18 + i * 166
        boxes.append(f'<rect x="{x}" y="48" width="142" height="54" rx="12" fill="{color}" opacity=".16" stroke="{color}"/><text x="{x + 71}" y="80" text-anchor="middle" fill="currentColor" font-size="11">{label}</text>')
        if i < 4:
            boxes.append(f'<path d="M{x + 142} 75h24" stroke="{color}" stroke-width="3"/><path d="m{x + 161} 70 7 5-7 5" fill="none" stroke="{color}" stroke-width="3"/>')
    return '<svg viewBox="0 0 850 125" role="img" aria-label="Study path"><rect width="850" height="125" rx="16" fill="currentColor" opacity=".035"/>' + "".join(boxes) + "</svg>"


def build_section(topic: Topic, ordinal: int) -> dict[str, str]:
    facts = list(COMMON_FACTS)
    facts.extend(anchor_fact(topic, focus, i) for i, focus in enumerate(topic.focus))
    assert len(facts) == 80, f"{topic.section_id}: expected 80 facts, got {len(facts)}"
    questions = "".join(fragment for i, fact in enumerate(facts, 1) for fragment in fact_variants(topic, i, fact))
    focus_chips = "".join(f"<span class=\"tag\">{html.escape(x)}</span>" for x in topic.focus)
    body = f"""
<section class="qbank-supernova">
<style>.qbank-supernova .tab-pane{{margin:1rem 0;padding:1rem;border:1px solid var(--border);border-radius:14px}}.qbank-supernova details{{margin:.45rem 0;padding:.65rem .8rem;border-left:4px solid var(--amber);background:color-mix(in srgb,var(--card) 92%,var(--amber))}}.qbank-supernova summary{{font-weight:800;cursor:pointer}}.qbank-supernova .ans{{color:var(--green);font-weight:700}}.qbank-supernova svg{{max-width:100%;height:auto}}.qbank-supernova .flow{{overflow:auto}}.qbank-supernova .tag{{display:inline-block;margin:.2rem;padding:.28rem .55rem;border:1px solid var(--border);border-radius:999px}}</style>
<div class="hero"><div class="eyebrow">WAVE 1 · PRACTICE BANK · 400 QUESTIONS</div><h1>🧠 {html.escape(topic.title)} Practice Bank</h1><p>Master the path, challenge assumptions, and defend every answer with packet, counter, or platform evidence.</p></div>
<div class="card teal"><h2>🎯 What you’ll learn</h2><ul><li>Recognize 80 operational facts across signaling, media, policy, security, migration, and proof.</li><li>Reason through direct, reversed, scenario, best-match, and true/false variants.</li><li>Answer with <b>Leg · ID · Counter · Capture</b>, plus the observation that would falsify your diagnosis.</li></ul><div class="flow">{diagram(topic)}</div></div>
<div class="tab-bar"><button class="tab-btn active">🗺 Map</button><button class="tab-btn">🧪 Questions</button><button class="tab-btn">✅ Proof</button></div>
<div class="tab-pane active"><h2>🗺 Topic constellation</h2><p>{focus_chips}</p><div class="grid"><div class="card blue"><h3>Signal</h3><p>Who asked what, through which boundary, with which dialog identity?</p></div><div class="card teal"><h3>Media</h3><p>Which addresses, ports, payloads, packets, and quality counters moved?</p></div><div class="card purple"><h3>Control</h3><p>Which policy, identity, capacity, or dependency made the decision?</p></div></div></div>
<div class="tab-pane"><h2>🧪 400-question forge</h2><p class="muted">80 facts × five reasoning forms. Open one answer only after stating your decision and proof target aloud.</p>{questions}</div>
<div class="tab-pane"><h2>✅ Mastery gate</h2><table><tr><th>Gate</th><th>Pass signal</th><th>Falsifier</th></tr><tr><td>Path</td><td>Every hop and B2BUA leg named</td><td>An unexplained boundary remains</td></tr><tr><td>Identity</td><td>Dialog or platform correlation IDs join events</td><td>Evidence belongs to another session</td></tr><tr><td>Counter</td><td>A relevant metric moves with the test</td><td>Metric is historical or outside the window</td></tr><tr><td>Capture</td><td>Artifact proves expected signal and media behavior</td><td>Only a UI status is available</td></tr><tr><td>Rollback</td><td>Trigger, owner, reverse steps, and validation are timed</td><td>Recovery depends on improvisation</td></tr></table><pre class="code">DECISION → LEG → ID → COUNTER → CAPTURE → FALSIFIER → SAFE CHANGE → VERIFY → ROLLBACK</pre></div>
</section>""".strip()
    return {"id": topic.section_id, "num": f"QB{ordinal:02d}", "group": "Practice Banks", "title": f"🧠 {topic.title} — 400Q", "sub": "80 facts · 5 reasoning variants · proof-first", "body": body}


def locate_array(text: str) -> tuple[int, int, list[dict[str, object]]]:
    match = re.search(r"window\.SECTIONS\s*=\s*", text)
    if not match:
        raise RuntimeError("window.SECTIONS assignment not found")
    start = text.find("[", match.end())
    end = text.find("\n];", start)
    if start < 0 or end < 0:
        raise RuntimeError("SECTIONS array boundary not found")
    # ``end`` points at the newline in ``\n];``; include the following ``]``.
    sections = json.loads(text[start : end + 2])
    if not isinstance(sections, list) or any(not isinstance(x, dict) for x in sections):
        raise RuntimeError("SECTIONS is not a dense object array")
    return start, end, sections


def section_spans(text: str, start: int, end: int) -> list[tuple[int, int, dict[str, object]]]:
    """Return exact raw object spans without reserializing the full array."""
    decoder = json.JSONDecoder()
    spans: list[tuple[int, int, dict[str, object]]] = []
    cursor = start + 1
    while cursor < end:
        while cursor < end and text[cursor] in " \t\r\n,":
            cursor += 1
        if cursor >= end:
            break
        value, finish = decoder.raw_decode(text, cursor)
        if not isinstance(value, dict):
            raise RuntimeError("non-object found in SECTIONS")
        spans.append((cursor, finish, value))
        cursor = finish
    return spans


def update_stats(text: str, section_count: int) -> str:
    pattern = r'(window\.STATS\s*=\s*\{[^;]*?"sections"\s*:\s*)\d+'
    updated, count = re.subn(pattern, rf"\g<1>{section_count}", text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("window.STATS.sections was not updated exactly once")
    return updated


def inject(path: Path, dry_run: bool = False) -> tuple[int, int, int]:
    original = path.read_text(encoding="utf-8")
    # Early Wave-1 output accidentally forced every tab pane visible. Remove
    # only that scoped declaration so the campus' existing ``wireTabs``
    # controller can hide/show panes normally.
    working = original.replace(".qbank-supernova .tab-pane{display:block;", ".qbank-supernova .tab-pane{")
    start, end, existing = locate_array(working)
    # The legacy campus already had a 120-question ``qb-webex`` section. Keep
    # every byte of its body and append the new 400-question deep forge inside
    # that same stable ID instead of creating a duplicate navigation key.
    topic_by_id = {topic.section_id: (i, topic) for i, topic in enumerate(TOPICS, 1)}
    replacements: list[tuple[int, int, str]] = []
    for object_start, object_end, section in section_spans(working, start, end):
        section_id = str(section.get("id", ""))
        body = section.get("body")
        if section_id in topic_by_id and isinstance(body, str) and "qbank-supernova" not in body:
            ordinal, topic = topic_by_id[section_id]
            enriched = dict(section)
            enriched["body"] = body + "\n" + build_section(topic, ordinal)["body"]
            enriched["title"] = build_section(topic, ordinal)["title"]
            enriched["sub"] = "Legacy bank preserved · plus 400 proof-first questions"
            replacements.append((object_start, object_end, json.dumps(enriched, ensure_ascii=False, separators=(",", ":"))))
    for object_start, object_end, replacement in reversed(replacements):
        working = working[:object_start] + replacement + working[object_end:]

    _, end, existing = locate_array(working)
    existing_ids = {str(section.get("id", "")) for section in existing}
    additions = [build_section(topic, i) for i, topic in enumerate(TOPICS, 1) if topic.section_id not in existing_ids]
    if not additions:
        reconciled = update_stats(working, len(existing))
        if reconciled != original and not dry_run:
            path.write_text(reconciled, encoding="utf-8")
        return 0, len(reconciled.encode("utf-8")) - len(original.encode("utf-8")), len(existing)
    payload = ",\n" + ",\n".join(json.dumps(section, ensure_ascii=False, separators=(",", ":")) for section in additions)
    updated = working[:end] + payload + working[end:]
    updated = update_stats(updated, len(existing) + len(additions))
    # Parse the exact post-injection array before replacing the flagship.
    _, _, parsed = locate_array(updated)
    if len(parsed) != len(existing) + len(additions) or any(not x for x in parsed):
        raise RuntimeError("post-injection density check failed")
    if not dry_run:
        path.write_text(updated, encoding="utf-8")
    return len(additions), len(updated.encode("utf-8")) - len(original.encode("utf-8")), len(parsed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML, help="flagship HTML path")
    parser.add_argument("--dry-run", action="store_true", help="build and validate without writing")
    args = parser.parse_args()
    added, byte_delta, total = inject(args.html.resolve(), args.dry_run)
    print(json.dumps({"added_sections": added, "added_bytes": byte_delta, "total_sections": total, "dry_run": args.dry_run}))


if __name__ == "__main__":
    main()
