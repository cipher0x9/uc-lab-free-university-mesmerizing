# Microsoft Teams Phone & Direct Routing Mastery

**CYPHER0X9 · UC Lab Free University · curriculum pack · MIT · educational**  
**Proof grammar:** LICC — Leg · ID · Counter · Capture  
**Spine:** THE CALL MUST ALWAYS CONNECT

> Multi-vendor reality: many enterprises braid **Cisco CUCM + Microsoft Teams Phone**. This pack teaches the Teams side so you can follow the call across the braid.

---

## 1) Mental model (one page)

| Layer | What it is | Failure you will debug |
|-------|------------|------------------------|
| **Teams client** | Softphone / meeting endpoint | Device, network, account policy |
| **Teams Phone** | Cloud PBX control plane | Calling plan / policy missing |
| **PSTN connectivity** | Calling Plan · Operator Connect · Direct Routing | Trunk auth, numbers, emergency |
| **SBC** | Edge for Direct Routing | SIP TLS, OPTIONS, media bypass |
| **Identity** | Entra ID / licenses | Phone System license, policies |
| **Emergency** | Dynamic emergency calling | Location, routing, compliance |

**Rule:** Signaling path and media path are different stories. One-way audio is almost always media path or NAT, not "Teams is broken."

---

## 2) Three PSTN connectivity patterns

### 2.1 Microsoft Calling Plan
- Microsoft provides numbers + PSTN
- Fastest for pure-cloud shops
- Less edge control; less CUBE/SBC craft

### 2.2 Operator Connect
- Carrier-integrated PSTN into Teams
- Enterprise-grade numbers without owning full SBC stack
- Still verify emergency and number porting with carrier

### 2.3 Direct Routing (engineer deep mode)
- You (or partner) run a **certified SBC**
- SIP trunk toward Microsoft Phone System
- Highest interop power + highest proof burden

```text
Teams user → Phone System → SBC (TLS SIP) → SIP trunk / PSTN / CUCM
                 ↑ media may hairpin or bypass depending on design
```

---

## 3) Direct Routing — architecture checklist

1. **Public FQDN** on SBC with valid public cert (SAN matches)
2. **TLS** toward `sip.pstnhub.microsoft.com` (and regional failover hubs)
3. **Firewall** allow Microsoft IP ranges for signaling + media
4. **OPTIONS** ping healthy both directions
5. **Voice routes / PSTN usages** map dial strings correctly
6. **Number assignment** E.164 on users
7. **Emergency calling** policies + locations
8. **Call queues / auto attendants** if CC-lite workloads sit here

### LICC for Direct Routing failure

| Letter | Ask |
|:--:|--|
| **L** | Client → Phone System → SBC → PSTN/CUCM — which leg died? |
| **I** | Teams call ID · SBC Call-ID · trunk correlation |
| **C** | SBC concurrent calls · TLS handshake fails · 4xx/5xx rates |
| **C** | SBC SIP trace · Teams admin call analytics · pcap on media path |

---

## 4) SBC skills that transfer from CUBE

If you know **CUBE**, map concepts:

| CUBE idea | Direct Routing analog |
|-----------|------------------------|
| Dial-peer | Voice route / translation / SBC routing table |
| TLS SIP trunk | SBC → Microsoft signaling interface |
| Early offer / delayed offer | SDP timing interop with Phone System |
| Media flow-through / flow-around | Media bypass vs forced relay |
| CAC / max-conn | Concurrent call limits on SBC + ISP |
| SIP profiles / header manipulation | Number normalization, PAI/RPID, history-info |

**Do not** paste production dial-peers or private FQDNs into public repos.

---

## 5) Numbering & normalization

- Store/compare in **E.164** (`+14155550100`) at the cloud edge when possible
- Normalize on SBC for legacy PBX that still wants `9` + 10-digit or extension-only
- Document **who owns normalization**: Teams voice routes vs SBC vs CUCM

Interview drill: "User dials 911 / 112 / local emergency from Teams remote worker — walk the path and name the proof artifacts."

---

## 6) Interop with CUCM (dual-run)

Common patterns:

1. **Teams as client to CUCM** (older / special cases) vs **Teams Phone as PBX**
2. **SBC between Teams and CUCM** for dual-run migrations
3. **Shared PSTN** with careful ANI/DNIS and recording policy

Migration safety:

```text
Dual-run → measure ASR / NER / MOS / emergency success
         → prove number port windows with LICC captures
         → only then decommission old path
```

---

## 7) Policies learners must know by name

- Phone System license + Teams Phone add-ons as required
- Calling policies / caller ID policies
- Emergency calling policies
- Dial-out / international restrictions (toll fraud)
- Recording policies (compliance)
- App permission policies if bots join calls

---

## 8) Troubleshooting playbook (top 12)

1. User has no dial pad → license / policy  
2. Outbound fails immediately → voice route / PSTN usage  
3. Inbound rings nowhere → number assignment / reverse number lookup  
4. OPTIONS down → TLS cert / firewall / DNS  
5. 403/404 from Microsoft → trunk config / FQDN  
6. One-way audio → media ports / NAT / bypass  
7. Intermittent drops → WAN, Wi-Fi, client version  
8. Wrong caller ID → policy + SBC PAI  
9. Emergency misroute → location / dynamic emergency  
10. Call queue stuck → resource account / membership  
11. CUCM interop early media weirdness → SDP / 183 / PRACK  
12. "Works on Wi-Fi fails on cellular" → UDP/TCP/TLS path, VPN hairpin  

For each: write **Leg · ID · Counter · Capture** before you change config.

---

## 9) Lab (safe home / sandbox)

- Use **lab tenant** only  
- Prefer certified SBC evaluation or lab VM images  
- Synthetic numbers only  
- Never bridge lab to production emergency paths without control  

**Proof artifact to keep:** one successful outbound + one inbound with SIP ladder + call analytics export (redacted).

---

## 10) Bridge to AI Lab

Voice AI agents that sit on Teams or CCaaS still obey the spine: if STT/LLM freezes, **the call path must still connect or fail soft**. Measure STT/LLM/TTS legs with **RTMA** while you measure SIP legs with **LICC**.

Sibling: [AI Lab Free University](https://github.com/cipher0x9/ai-lab-free-university)

---

## 11) Teach-back (90 seconds)

Explain to a junior:

1. Three PSTN patterns  
2. Why Direct Routing needs a certified SBC  
3. How LICC isolates a one-way audio ticket  
4. What dual-run means during CUCM → Teams migration  

Spaced review: 1h → 24h → 7d → 30d → 90d.

---

## 12) Official docs (pin these)

Search Microsoft Learn for current: *Direct Routing planning*, *SBC paired with Phone System*, *Dynamic emergency calling*, *Operator Connect*. Product UIs change; the path math does not.

**Educational only · MIT · no warranty · lab safely**
