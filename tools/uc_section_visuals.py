#!/usr/bin/env python3
"""Classify every campus section into honest visual chrome.

A reader opening any section should see a 3-hop flow plus protocol/port
chips when the section text already implies them. No invented ports.
No new curriculum — stamps are derived from id / title / sub / group.
"""

from __future__ import annotations

import json
import re
from typing import Any

# Honest, well-known UC/CC marks only. If a topic has no stable port,
# emit protocol or structural chips — never a guessed number.
RULES: list[dict[str, Any]] = [
    {"k": ["5061", "sips", "sip tls"], "ports": ["5061/tcp SIP-TLS"], "protos": ["SIP", "TLS"], "flow": ["UA", "TLS edge", "Peer UA"], "icon": "lock"},
    {"k": ["sip", "invite", "dialog", "cseq", "via ", "record-route", "options "], "ports": ["5060/udp-tcp SIP"], "protos": ["SIP"], "flow": ["UAC", "Proxy / B2BUA", "UAS"], "icon": "sip"},
    {"k": ["srtp", "srtp"], "ports": [], "protos": ["SRTP"], "flow": ["Offer SRTP", "Key / suite", "Two-way media"], "icon": "lock"},
    {"k": ["rtp", "rtcp", "jitter", "mos", "one-way", "one way", "ssrc"], "ports": ["16384–32767/udp RTP"], "protos": ["RTP", "RTCP"], "flow": ["Endpoint A", "Media path", "Endpoint B"], "icon": "wave"},
    {"k": ["webrtc", "ice", "stun", "turn", "dtls"], "ports": ["3478/udp STUN", "5349/tcp TURN-TLS"], "protos": ["WebRTC", "ICE", "DTLS-SRTP"], "flow": ["Browser", "STUN/TURN", "Media peer"], "icon": "ice"},
    {"k": ["sccp", "skinny"], "ports": ["2000/tcp SCCP"], "protos": ["SCCP"], "flow": ["Phone", "CUCM", "Media resource"], "icon": "phone"},
    {"k": ["mgcp"], "ports": ["2427/udp MGCP", "2727/udp CA"], "protos": ["MGCP"], "flow": ["Call agent", "Gateway", "FXS / analog"], "icon": "legacy"},
    {"k": ["h.323", "h323", "q.931"], "ports": ["1720/tcp H.323"], "protos": ["H.323"], "flow": ["Terminal", "Gatekeeper", "Gateway"], "icon": "legacy"},
    {"k": ["t.38", "t38", "fax"], "ports": ["5060/udp SIP"], "protos": ["T.38", "SIP"], "flow": ["Fax endpoint", "Gateway", "T.38 peer"], "icon": "fax"},
    {"k": ["https", "oauth", "webhook", "rest", "api", "graphql"], "ports": ["443/tcp HTTPS"], "protos": ["HTTPS", "TLS"], "flow": ["Client", "API / IdP", "Resource"], "icon": "cloud"},
    {"k": ["tftp"], "ports": ["69/udp TFTP"], "protos": ["TFTP"], "flow": ["Phone", "TFTP", "Config / firmware"], "icon": "box"},
    {"k": ["dns", "srv", "naptr", "nxdomain"], "ports": ["53/udp-tcp DNS"], "protos": ["DNS", "SRV"], "flow": ["Client", "DNS SRV", "Target host"], "icon": "net"},
    {"k": ["ntp", "time sync", "clock skew", "clock drift"], "ports": ["123/udp NTP"], "protos": ["NTP"], "flow": ["Node", "NTP source", "Log / cert time"], "icon": "clock"},
    {"k": ["ldap", "ldaps", "active directory", "dirsync"], "ports": ["389/tcp LDAP", "636/tcp LDAPS"], "protos": ["LDAP"], "flow": ["UC node", "Directory", "Identity"], "icon": "id"},
    {"k": ["dhcp", "option 150", "option 66"], "ports": ["67/68/udp DHCP"], "protos": ["DHCP"], "flow": ["Phone", "DHCP", "TFTP / CUCM"], "icon": "net"},
    {"k": ["ssh", "cli "], "ports": ["22/tcp SSH"], "protos": ["SSH"], "flow": ["Operator", "Edge CLI", "Change proof"], "icon": "lock"},
    {"k": ["snmp"], "ports": ["161/udp SNMP"], "protos": ["SNMP"], "flow": ["NMS", "Agent", "Trap / poll"], "icon": "chart"},
    {"k": ["syslog"], "ports": ["514/udp syslog"], "protos": ["syslog"], "flow": ["Device", "Syslog", "SIEM"], "icon": "chart"},
    {"k": ["cti", "jtapi", "tsp"], "ports": ["2748/tcp CTI"], "protos": ["CTI"], "flow": ["Desktop", "CTI manager", "Call control"], "icon": "agent"},
    {"k": ["expressway", "mra", "collab-edge", "traversal"], "ports": ["8443/tcp MRA", "5061/tcp SIP-TLS"], "protos": ["MRA", "TLS"], "flow": ["Client", "Exp-E → Exp-C", "CUCM"], "icon": "edge"},
    {"k": ["cube", "sbc", "b2bua", "session border"], "ports": ["5060/5061 SIP", "16384–32767/udp RTP"], "protos": ["SIP", "RTP"], "flow": ["ITSP", "CUBE / SBC", "Call control"], "icon": "shield"},
    {"k": ["cucm", "callmanager", "unified communications manager"], "ports": ["5060/5061 SIP", "2000/tcp SCCP", "69/udp TFTP"], "protos": ["SIP", "SCCP"], "flow": ["Phone", "CUCM", "Trunk / MR"], "icon": "phone"},
    {"k": ["teams", "direct routing", "cqd"], "ports": ["443/tcp Teams", "3478–3481/udp STUN", "50000–50059/udp media"], "protos": ["HTTPS", "STUN", "SRTP"], "flow": ["Teams client", "Phone System", "SBC / PSTN"], "icon": "cloud"},
    {"k": ["webex calling", "webex app", "control hub", "wxcc", "webex cc", "webex contact"], "ports": ["443/tcp Webex"], "protos": ["HTTPS", "SIP", "SRTP"], "flow": ["App / LGW", "Webex cloud", "PSTN / agent"], "icon": "cloud"},
    {"k": ["amazon connect", "connect ", "contact flow", "ctr"], "ports": ["443/tcp HTTPS"], "protos": ["HTTPS", "WebRTC"], "flow": ["Contact", "Flow / queue", "Agent"], "icon": "agent"},
    {"k": ["genesys", "architect flow", "purecloud"], "ports": ["443/tcp HTTPS"], "protos": ["HTTPS"], "flow": ["Entry", "Architect", "Queue / agent"], "icon": "agent"},
    {"k": ["nice", "cxone", "five9"], "ports": ["443/tcp HTTPS", "5060/5061 SIP"], "protos": ["HTTPS", "SIP"], "flow": ["Entry", "ACD / script", "Agent"], "icon": "agent"},
    {"k": ["twilio", "taskrouter", "flex"], "ports": ["443/tcp HTTPS", "5060/5061 SIP"], "protos": ["HTTPS", "SIP"], "flow": ["Webhook", "TaskRouter", "Flex agent"], "icon": "cloud"},
    {"k": ["zoom"], "ports": ["443/tcp Zoom", "8801–8810/udp media"], "protos": ["HTTPS", "SRTP"], "flow": ["Client", "Zoom Phone", "BYOC / PSTN"], "icon": "cloud"},
    {"k": ["avaya", "session manager", "communication manager"], "ports": ["5060/5061 SIP"], "protos": ["SIP"], "flow": ["Endpoint", "SM / CM", "Trunk"], "icon": "phone"},
    {"k": ["asterisk", "freepbx", "pjsip"], "ports": ["5060/5061 SIP", "10000–20000/udp RTP"], "protos": ["PJSIP", "RTP"], "flow": ["Endpoint", "Asterisk", "Trunk"], "icon": "phone"},
    {"k": ["ringcentral", "8x8", "mitel"], "ports": ["443/tcp HTTPS", "5060/5061 SIP"], "protos": ["HTTPS", "SIP"], "flow": ["User", "Cloud UC", "PSTN"], "icon": "cloud"},
    {"k": ["ucce", "icm", "pcce", "cvp", "finesse"], "ports": ["443/tcp Finesse", "5060 SIP"], "protos": ["SIP", "HTTPS"], "flow": ["Ingress / CVP", "ICM script", "Agent"], "icon": "agent"},
    {"k": ["e911", "redsky", "psap", "elin", "erl", "lis", "nomadic", "emergency"], "ports": ["5060/5061 SIP"], "protos": ["SIP", "LIS"], "flow": ["User / LIS", "ELIN route", "PSAP"], "icon": "alert"},
    {"k": ["qos", "dscp", "ef ", "af41", "jitter", "dscp"], "ports": [], "protos": ["DSCP EF 46", "AF41", "CS3"], "flow": ["Mark", "Trust boundary", "Queue / prove"], "icon": "chart"},
    {"k": ["wifi", "wmm", "roam", "ssid"], "ports": [], "protos": ["WMM", "DSCP"], "flow": ["Handset", "AP / WLC", "Wired UC"], "icon": "net"},
    {"k": ["sd-wan", "sdwan", "sase"], "ports": [], "protos": ["DSCP", "IPsec"], "flow": ["Site", "SD-WAN edge", "Cloud / DC"], "icon": "net"},
    {"k": ["pri", "isdn", "fxs", "fxo", "analog", "pimg"], "ports": [], "protos": ["PRI / Q.931", "FXS/FXO"], "flow": ["Analog / PRI", "Gateway", "SIP UC"], "icon": "legacy"},
    {"k": ["recording", "siprec", "wfo", "qm", "compliance"], "ports": ["5060 SIP", "443/tcp API"], "protos": ["SIPREC", "SRTP"], "flow": ["Media fork", "Recorder", "Retrieve"], "icon": "rec"},
    {"k": ["sso", "saml", "oauth", "idp", "mfa"], "ports": ["443/tcp HTTPS"], "protos": ["SAML / OIDC"], "flow": ["User", "IdP", "UC app"], "icon": "id"},
    {"k": ["cert", "pkix", "tls", "mtls"], "ports": ["443/tcp", "5061/tcp"], "protos": ["TLS"], "flow": ["Trust store", "Handshake", "Secure hop"], "icon": "lock"},
    {"k": ["dial plan", "css", "partition", "route pattern", "translation"], "ports": ["5060 SIP"], "protos": ["SIP"], "flow": ["Digits in", "CSS / RP", "Egress"], "icon": "route"},
    {"k": ["queue", "agent", "ivr", "skill", "acd", "contact center", "ccaas"], "ports": ["443/tcp"], "protos": ["SIP", "HTTPS"], "flow": ["Ingress", "IVR / queue", "Agent"], "icon": "agent"},
    {"k": ["migration", "cutover", "hypercare", "porting", "dual-run"], "ports": [], "protos": ["SIP", "LICC"], "flow": ["Discover", "Pilot", "Cutover"], "icon": "truck"},
    {"k": ["licc", "falsifier", "capture", "counter"], "ports": [], "protos": ["LICC"], "flow": ["Leg", "ID + Counter", "Capture"], "icon": "proof"},
    {"k": ["interview", "teach-back", "whiteboard"], "ports": [], "protos": ["LICC"], "flow": ["Path", "Failure", "Proof"], "icon": "talk"},
    {"k": ["ai ", "llm", "dialogflow", "agent assist", "ml "], "ports": ["443/tcp HTTPS"], "protos": ["HTTPS"], "flow": ["Audio / text", "Model", "Agent / bot"], "icon": "ai"},
]

GROUP_FLOW = {
    "Campus": ["Open hub", "Study a path", "Write LICC"],
    "Products": ["Register / login", "Route the call", "Prove media"],
    "Foundations": ["Layer below", "This layer", "Layer above"],
    "Tricky SEVs": ["Symptom", "LICC packet", "Recover"],
    "Tricky SEVs v17": ["Scope blast", "Correlate", "Contain"],
    "Bonus 50s": ["Pick a tip", "Place on path", "Prove it"],
    "Network Core": ["Address / mark", "Forward", "Measure"],
    "AI & Future": ["Signal / text", "Model", "Human escape"],
    "Library": ["Find the atom", "Drill", "Teach back"],
    "Architect Core": ["Requirement", "Boundary", "ADR"],
    "Evidence Library": ["Claim", "Source", "Falsifier"],
    "Architect Dojo": ["Draw", "Defend", "Score"],
    "Trading Systems": ["Open line", "Record", "Surveillance"],
    "Google CC & APIs": ["Session", "Fulfillment", "Handoff"],
    "Cloud Migrations": ["Discover", "Pilot", "Cutover"],
    "Mastery Methodologies": ["Model", "Rehearse", "Evidence"],
    "CCaaS APIs & Platforms": ["Auth", "Event / API", "Agent path"],
    "More Vendors": ["Identity", "Route", "Media"],
    "Protocol Expert": ["Transaction", "Dialog", "Media"],
    "Security Deep": ["Detect", "Contain", "Prove"],
    "Observability Deep": ["Probe", "SLO", "Alert"],
    "Network Deep": ["Access", "WAN / QoS", "UC edge"],
    "Practice Bank": ["Read fact", "Answer", "LICC"],
    "Practice Banks": ["Fact", "Variant", "Defend"],
    "Vendor Deep-Dives": ["Control", "Media", "Evidence"],
    "Architecture + Mastery": ["Quality attr.", "Flow", "Failure"],
    "Mastery Practicums": ["Model", "Inject", "Prove"],
}

GROUP_ICON = {
    "Campus": "campus", "Products": "phone", "Foundations": "layers",
    "Tricky SEVs": "alert", "Tricky SEVs v17": "alert", "Bonus 50s": "star",
    "Network Core": "net", "AI & Future": "ai", "Library": "book",
    "Architect Core": "arch", "Evidence Library": "proof", "Architect Dojo": "talk",
    "Trading Systems": "rec", "Google CC & APIs": "cloud", "Cloud Migrations": "truck",
    "Mastery Methodologies": "proof", "CCaaS APIs & Platforms": "agent",
    "More Vendors": "phone", "Protocol Expert": "sip", "Security Deep": "lock",
    "Observability Deep": "chart", "Network Deep": "net", "Practice Bank": "bank",
    "Practice Banks": "bank", "Vendor Deep-Dives": "phone",
    "Architecture + Mastery": "arch", "Mastery Practicums": "lab",
}

ID_HINTS = (
    ("hub-sip", ["sip"]), ("hub-cucm", ["cucm"]), ("hub-cube", ["cube", "sbc"]),
    ("hub-qos", ["qos"]), ("hub-e911", ["e911"]), ("hub-expressway", ["expressway", "mra"]),
    ("hub-icm", ["ucce", "icm"]), ("hub-pcce", ["pcce"]), ("hub-webex", ["webex cc"]),
    ("hub-amazon", ["amazon connect"]), ("hub-migrations", ["migration"]),
    ("hub-sev", ["licc"]), ("hub-interview", ["interview"]),
    ("prod-cucm", ["cucm"]), ("prod-cube", ["cube"]), ("prod-teams", ["teams"]),
    ("prod-webex", ["webex calling"]), ("prod-connect", ["amazon connect"]),
    ("prod-genesys", ["genesys"]), ("prod-expressway", ["expressway"]),
    ("prod-zoom", ["zoom"]), ("qb-sip", ["sip"]), ("qb-qos", ["qos"]),
    ("qb-cucm", ["cucm"]), ("qb-cube", ["cube"]), ("qb-rtp", ["rtp"]),
    ("mp-signaling", ["sip"]), ("mp-media", ["rtp"]), ("mp-edge", ["sbc"]),
    ("mp-network", ["qos"]), ("mp-security", ["tls"]), ("mp-contact", ["queue"]),
    ("mp-cloud", ["https"]), ("mp-migration", ["migration"]),
    ("mp-routing", ["dial plan"]), ("mp-operations", ["licc"]),
    ("vd-teams", ["teams"]), ("vd-webex", ["webex calling"]),
    ("vd-twilio", ["twilio"]), ("vd-genesys", ["genesys"]),
    ("vd-nice", ["nice"]), ("vd-five9", ["five9"]), ("vd-avaya", ["avaya"]),
    ("vd-zoom", ["zoom"]), ("vd-ringcentral", ["ringcentral"]),
    ("vd-8x8", ["8x8"]), ("vd-mitel", ["mitel"]), ("vd-asterisk", ["asterisk"]),
    ("proto-sip", ["sip"]), ("proto-rtp", ["rtp"]), ("proto-ice", ["ice"]),
    ("cm-webex", ["webex calling"]), ("cm-teams", ["teams"]),
    ("cm-zoom", ["zoom"]), ("cm-cube", ["cube"]), ("cm-aws", ["https"]),
    ("found-0", ["dhcp"]), ("net-osi", ["qos"]), ("method", ["licc"]),
)


def _has_kw(hay: str, keyword: str) -> bool:
    """Phrase / dotted / numbered keys substring-match; short tokens use edges."""
    if any(ch in keyword for ch in " ./") or any(ch.isdigit() for ch in keyword):
        return keyword in hay
    return re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", hay) is not None


def _hay(section: dict[str, Any]) -> str:
    body = section.get("body") or ""
    return " ".join(
        [
            str(section.get("id") or ""),
            str(section.get("title") or ""),
            str(section.get("sub") or ""),
            str(section.get("group") or ""),
            body[:1600],
        ]
    ).lower()


def classify(section: dict[str, Any]) -> dict[str, Any]:
    hay = _hay(section)
    sid = str(section.get("id") or "")
    group = str(section.get("group") or "")
    head = " ".join(
        [sid, str(section.get("title") or ""), str(section.get("sub") or ""), group]
    ).lower()
    for prefix, extra in ID_HINTS:
        if sid.startswith(prefix) or prefix in sid:
            hay += " " + " ".join(extra)
            head += " " + " ".join(extra)

    ports: list[str] = []
    protos: list[str] = []
    icons: list[str] = []
    flow: list[str] | None = None
    head_flow: list[str] | None = None
    for rule in RULES:
        on_head = any(_has_kw(head, k) for k in rule["k"])
        on_all = on_head or any(_has_kw(hay, k) for k in rule["k"])
        if not on_all:
            continue
        for p in rule["ports"]:
            if p not in ports:
                ports.append(p)
        for p in rule["protos"]:
            if p not in protos:
                protos.append(p)
        if rule["icon"] not in icons:
            icons.append(rule["icon"])
        if on_head and head_flow is None:
            head_flow = list(rule["flow"])
    flow = head_flow

    if flow is None:
        flow = list(GROUP_FLOW.get(group) or ["Actor", "Function", "Next hop"])
    gicon = GROUP_ICON.get(group, "campus")
    if gicon not in icons:
        icons.insert(0, gicon)
    if "proof" not in icons:
        icons.append("proof")

    chips: list[str] = []
    for item in protos + ports:
        if item not in chips:
            chips.append(item)
    if not chips:
        chips = ["LICC", "path proof"]

    return {
        "id": sid,
        "icons": icons[:6],
        "flow": flow[:5],
        "chips": chips[:8],
        "has_port": any(ch[:1].isdigit() for ch in chips),
    }


def coverage(sections: list[dict[str, Any]]) -> dict[str, int]:
    specs = [classify(s) for s in sections]
    return {
        "sections": len(specs),
        "with_flow": sum(1 for s in specs if len(s["flow"]) >= 3),
        "with_icon": sum(1 for s in specs if s["icons"]),
        "with_chip": sum(1 for s in specs if s["chips"]),
        "with_port": sum(1 for s in specs if s["has_port"]),
    }


def lexicon_json() -> str:
    payload = {
        "rules": RULES,
        "groupFlow": GROUP_FLOW,
        "groupIcon": GROUP_ICON,
        "idHints": [[a, b] for a, b in ID_HINTS],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
