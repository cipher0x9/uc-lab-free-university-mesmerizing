# CUCM Deep Dive — CallManager Architecture Master Class

**Campus:** UC AI Free University · CYPHER0X9 / cipher0x9 · MIT  
**Axiom:** THE CALL MUST ALWAYS CONNECT  
**Scope:** Cisco Unified Communications Manager (CallManager) — architecture, call flow, dial plan objects, media, mobility, DR, licensing  
**Level:** Intermediate → Advanced (lab + production design)

---

## 0. Learning outcomes

By the end of this pack you can:

1. Draw the CUCM cluster topology (Publisher, Subscribers, TFTP, CTI, Media) and explain failover paths.
2. Trace a call from off-hook → ringback → connect → disconnect with signaling and media paths.
3. Design device pools, regions, locations, partitions, and CSS that do not loop or black-hole digits.
4. Choose MGCP vs SIP trunks for gateways and explain media resource selection (MTP, XCODE, CONF, MOH).
5. Plan Extension Mobility, CM groups, and disaster recovery (backup/restore + DRS).
6. Map licensing (user-based / UCL / CUWL / Flex) to real deployment choices.

---

## 1. Cluster architecture

### 1.1 Roles

| Role | Function | Notes |
|------|----------|-------|
| **Publisher** | Master DB (Informix), writes for most config | First node; keep lightly loaded for call processing if possible |
| **Subscriber** | Call processing, CTI, registration | Scale-out; primary for phones |
| **TFTP** | Phone config/firmware/locale files | Often co-located; can be dedicated |
| **CTI Manager** | JTAPI/TAPI applications (Finesse, UCCX, recording) | Bind apps to specific CTI Manager group |
| **Media** | Software conf, MOH, annunciator, MTP (if enabled) | Prefer hardware DSP where scale matters |
| **IM&P** | Presence (separate product, often paired) | Not call control |

### 1.2 Database model

- **Publisher** owns the master configuration database.
- **Subscribers** hold read-only replicas for call processing; some tables allow local write (e.g., some user-facing state) but design as if Publisher is authoritative for config.
- Change management: bulk admin / BAT / AXL against Publisher; verify replication with RTMT / CLI `utils dbreplication runtimestate`.
- **Never** rebuild Publisher casually; document hostname, security password, cluster security mode, certificates.

### 1.3 Call processing node selection

Phones register to a **Cisco Unified CM Group** (ordered list of up to 3 CUCM nodes). Registration sequence:

1. Phone obtains TFTP (DHCP option 150 / DNS / manual).
2. Downloads `SEP<MAC>.cnf.xml` (or device profile for EM).
3. Tries CM Group members in order until SCCP/SIP register succeeds.
4. Keepalives / registration refresh maintain liveness; failover on dead primary.

**Design rule:** Put phones’ primary CM near them (same site or region); use tertiary only for DR.

### 1.4 Services checklist (lab)

```
CallManager
TFTP
Cisco CTIManager
Cisco IP Voice Media Streaming App   # MOH, conf, annunciator, software MTP
Cisco DirSync                        # if LDAP sync
Cisco AXL Web Service
Cisco Certificate Authority Proxy Function (CAPF)  # if LSC
Cisco Extension Mobility
Cisco Bulk Provisioning Service
```

CLI health:

```bash
utils service list
utils dbreplication runtimestate
show status
show network cluster
utils diagnose test
```

---

## 2. Call flow: off-hook → ringback → connect

### 2.1 SIP phone simplified (internal)

```
Alice (SEP)                    CUCM A                     Bob (SEP)
   |                             |                          |
   |---- INVITE (digits) ------->|                          |
   |<--- 100 Trying -------------|                          |
   |                             |---- INVITE ------------->|
   |                             |<--- 180 Ringing ---------|
   |<--- 180 Ringing ------------|                          |
   |                             |<--- 200 OK (SDP) --------|
   |<--- 200 OK (SDP) -----------|                          |
   |---- ACK ------------------->|---- ACK ---------------->|
   |============= RTP Alice <-> Bob (direct or via MTP) ===|
   |---- BYE ------------------->|---- BYE ---------------->|
   |<--- 200 OK -----------------|                          |
```

**Key points:**

- **Signaling** always through CUCM (or via trunk to CUBE/SBC).
- **Media** is peer-to-peer when codecs/regions allow; forced through MTP/transcoder when required.
- Early media / ringback: 180 with SDP or 183 Session Progress; local ringback if no early media.

### 2.2 SCCP phone (classic)

SCCP is station control: off-hook event → CUCM collects digits → CUCM rings destination → media setup via OpenReceiveChannel / StartMediaTransmission. Same logical states: dialing, proceeding, alerting, connected, hold, transfer.

### 2.3 Off-net via SIP trunk (CUBE)

```
Phone --SIP--> CUCM --SIP--> CUBE --SIP--> ITSP
                |              |
                |  dial-peer   |
                |  match URI   |
                +-- media may hairpin or flow-through
```

Digit analysis on CUCM: **Route Pattern** → **Route List** → **Route Group** → **SIP Trunk** → CUBE dial-peers → PSTN.

### 2.4 States every engineer must name

| State | Meaning | Common failure |
|-------|---------|----------------|
| Off-hook / Dial tone | Line seized | No dial tone = registration/CSS/service |
| Digit collection | DA running | Wrong CSS / partition |
| Proceeding | Route found | 404 / unallocated |
| Alerting / Ringback | Far end ringing | One-way early media |
| Connected | RTP up | One-way / no-way audio |
| Hold / Transfer / Conference | Feature media | MOH/MTP shortage |
| Released | BYE/Cancel | Dropped call mid-dialog |

---

## 3. Device pools and regional media

### 3.1 Device pool components

A **Device Pool** bundles:

- Cisco Unified CM Group
- Date/Time Group
- Region (codec preference between regions)
- Location (CAC bandwidth)
- SRST Reference (optional)
- Media Resource Group List (MRGL)
- Local Route Group settings (if used)
- Calling Search Space for auto-registration (optional)
- Device Mobility related groups

**Phone = Device Pool + Device CSS + Line CSS + Partition on DN.**

### 3.2 Regions and codec

- Region A ↔ Region B: max audio/video bit rate and preference list.
- Intra-region often G.711; inter-region G.729/Opus if WAN constrained.
- Mismatch without transcoder → call fails or forces MTP/XCODE.

### 3.3 Locations (CAC)

- Each location has audio/video bandwidth pools.
- When call would exceed remaining BW, CUCM rejects or uses AAR (Automated Alternate Routing) if configured.
- Locations ≠ physical sites necessarily, but map 1:1 for clarity.

**Lab exercise:** Set location BW to 24 kbps; place two G.711 calls; observe second fail or AAR.

---

## 4. Partitions and Calling Search Spaces

### 4.1 Mental model

- **Partition** = container for dialable patterns (DNs, route patterns, translation patterns, hunt pilots).
- **CSS** = ordered list of partitions a device/line is allowed to search.

Digit analysis walks CSS partitions **in order**; first match wins.

### 4.2 Classic design

```
Partitions:  PT-Internal, PT-Local, PT-LD, PT-Intl, PT-911, PT-Block
CSS-Internal: PT-Internal, PT-911
CSS-Local:    PT-Internal, PT-Local, PT-911
CSS-National: PT-Internal, PT-Local, PT-LD, PT-911
CSS-Intl:     ... + PT-Intl
CSS-Blocked:  PT-Block (catch-all block patterns)
```

**Line CSS vs Device CSS:** Effective CSS = Device CSS partitions + Line CSS partitions (order: device then line, or per version/docs — treat as union with line often more privileged in many designs). Document your standard.

### 4.3 Common anti-patterns

1. One giant CSS with everything → toll fraud risk.
2. Overlapping patterns without careful order → wrong trunk.
3. Translation patterns in partitions reachable by unintended CSS → loops.
4. 911 only on line CSS forgotten on soft clients → compliance failure.

---

## 5. Route patterns, lists, groups, trunks

### 5.1 Objects chain

```
Route Pattern  →  Route List  →  Route Group(s)  →  Gateway / Trunk
     |                 |               |
  discard/predot    priority      members + distribution
  CSS of RP         failover      circular / top-down
```

### 5.2 Digit manipulation (summary)

| Tool | When |
|------|------|
| Route pattern discard/predot | Strip access code |
| Called Party Transform | Outbound to trunk |
| Calling Party Transform | CLID presentation |
| Translation Pattern | Normalize before DA continues |
| SIP Normalization / Lua on CUBE | Vendor interop |

### 5.3 MGCP vs SIP trunks

| Aspect | MGCP gateway | SIP trunk |
|--------|--------------|-----------|
| Control | CUCM is call agent; gateway is dumb | Peer signaling; smarter edge |
| Features | Tight CUCM integration, PRI classic | Flexible, CUBE, ITSP, multi-vendor |
| Survivability | SRST common | SRST/CUBE local dial-peers |
| Debug | `debug mgcp packet` | `debug ccsip messages` |
| Modern bias | Legacy PRI sites | **Default for new design** |

**SIP trunk checklist:** SIP profile, SIP security profile (non-secure / TLS), MTP required?, Early offer vs delayed offer, OPTIONS ping, Rerouting CSS, AAR, normalization script.

---

## 6. Media resources

### 6.1 Types

| Resource | Purpose |
|----------|---------|
| **MTP** | DTMF relay mismatch (RFC2833 vs OOB), early offer, protocol conversion, hold |
| **Transcoder (XCODE)** | Codec conversion G.711 ↔ G.729 etc. |
| **Conference bridge** | Ad-hoc / meet-me |
| **MOH** | Music on hold (unicast/multicast) |
| **Annunciator** | Tones, MLPP, some prompts |
| **IPVMS** | Software media on CUCM node |
| **PVDM / DSP farm** | Hardware on ISR/ASR; SCCP or SIP-based |

### 6.2 MRG / MRGL

- **Media Resource Group** = list of resources.
- **Media Resource Group List** = ordered list of MRGs (device pool or device).
- Selection walks MRGL; local resources first, then remote.

**Design:** Site MRG (local DSP) → Regional → Central software. Avoid hairpinning all media to HQ.

### 6.3 When MTP is forced

- DTMF capability mismatch
- SIP early offer required by ITSP but phone delayed offer
- Certain transfer/hold scenarios
- Protocol conversion (H.323–SIP legacy)

Shortage symptoms: features fail, transfers die, DTMF ignored, call setup 503.

---

## 7. Extension Mobility (EM)

### 7.1 Model

- **Device Profile** holds user DN, CSS, softkey template, services.
- User logs in on a phone → phone adopts profile (logout restores default).
- EM service URL on phones; Cisco Extension Mobility service activated.

### 7.2 Design notes

- Max concurrent logins, auto-logout timers.
- EMCC (cross-cluster) for multi-cluster roaming — heavier design.
- Do not put site-specific CSS only on device if users roam with line-level national rights.
- Audit: who is logged where (compliance / 911 location implications).

### 7.3 Failure modes

| Symptom | Check |
|---------|-------|
| Login fails | Service activated? User associated? Phone EM enabled? |
| Wrong DN after login | Wrong device profile / dual lines |
| 911 wrong location | ERL/RedSky user vs device location — test EM desks |

---

## 8. Disaster recovery

### 8.1 Call processing HA

1. **CM Group:** 3 servers ordered; phones fail over.
2. **Device Pool** per site with correct CM Group.
3. **SIP trunk** dual destinations / DNS SRV / multiple trunks in RG.
4. **CUBE** dual routers, dial-peer preference, binding.
5. **SRST / E-SRST** for WAN loss to HQ CUCM.

### 8.2 DRS (Disaster Recovery System)

- Schedule regular backups (config + optionally TFTP files).
- Store off-box SFTP.
- Document restore order: Publisher first, then subscribers.
- Cluster security password must match for restore scenarios.
- Practice restore in lab annually.

### 8.3 DR runbook skeleton

```
1. Declare severity (node / site / cluster / DC)
2. Confirm monitoring (RTMT, syslog, SNMP, CUIC if CCE)
3. Isolate: network vs app vs cert vs license
4. Fail traffic: CM group / RG / DNS / load balancer
5. Communicate: NOC + contact center ops
6. Repair: service restart → node rebuild → restore
7. Validate: registration count, test call matrix, 911 test
8. Postmortem: LICC evidence + action items
```

---

## 9. Licensing (practical map)

| Model | Idea | Notes |
|-------|------|-------|
| **UCL** | Per device/user tier (Essential/Basic/Enhanced/Enhanced Plus) | Older on-prem framing |
| **CUWL** | Professional / Standard workspace | Bundles soft clients etc. |
| **Flex / subscription** | Cloud-oriented / hybrid | Webex Calling / mixed |
| **PLM / CSSM** | License manager | Smart Licensing era |

**Ops rules:**

- Count phones, soft clients, telepresence, room devices separately.
- Over-subscription kills registration after grace — monitor license alerts.
- Contact center agents often need separate UCCX/UCCE/WxCC licenses.

---

## 10. Security surfaces (CUCM-centric)

- Admin UI: HTTPS, strong accounts, SSO where possible, limit EMCC/AXL exposure.
- Phone: signed firmware, optional LSC (MIC/LSC), encrypted config.
- Signaling: TLS SIP, SRTP media (mixed mode / secure mode complexity).
- SIP trunks: digest or TLS mutual auth; never open UDP/5060 to internet without SBC.
- Toll fraud: CSS discipline, after-hours blocking, CUBE fraud controls.

---

## 11. Lab build order (recommended)

1. Single-node CUCM lab → SIP phone register → internal call.
2. Add second node → CM group failover test.
3. Partitions/CSS → restricted vs open CSS test calls.
4. SIP trunk to CUBE → PSTN simulator / ITSP sandbox.
5. Regions/locations CAC stress test.
6. DSP farm transcoder + MTP exhaustion test.
7. Extension Mobility login/logout + 911 location check.
8. DRS backup; optional restore to snapshot lab.

---

## 12. Verification matrix

| Test | Pass criteria |
|------|----------------|
| Internal call | Bidirectional audio, correct CLID |
| Outbound local/LD | Correct RP, strip, CLI |
| Inbound DID | Correct DN, CSS for transfer |
| Hold/resume | MOH or silence per policy; audio returns |
| Transfer (blind/consult) | Correct final parties |
| Conference | 3-way audio |
| Codec inter-region | XCODE engages or G.729 end-to-end |
| Node kill | Phones re-register ≤ acceptable SLA |
| EM | Profile DN active; logout restores |
| 911 | Correct PSAP/ERL (lab simulation) |

---

## 13. Config snippets (reference patterns)

### 13.1 SIP trunk essentials (conceptual)

```
Device > Trunk > SIP Trunk
  Destination Address: 10.10.20.1
  SIP Trunk Security Profile: Non Secure SIP Trunk Profile
  SIP Profile: Standard SIP Profile (Early Offer if required)
  Media Termination Point Required: [as needed]
  Rerouting Calling Search Space: CSS-Trunk-Inbound
  Out-of-Dialog Refer CSS: ...
  Calling/Connected Party Selection: Originator
```

### 13.2 Route pattern example

```
Pattern: 9.@          # or 9.[2-9]XXXXXX for NANP local
Partition: PT-Local
Gateway/Route List: RL-PSTN
Call Classification: OffNet
Discard Digits: PreDot
```

### 13.3 CUBE dial-peer pair (edge)

```ios
voice service voip
 sip
  bind control source-interface Loopback0
  bind media source-interface Loopback0
  early-offer forced
!
dial-peer voice 100 voip
 description TO-CUCM
 destination-pattern 5...$
 session protocol sipv2
 session target ipv4:10.10.10.10
 voice-class codec 1
 dtmf-relay rtp-nte
!
dial-peer voice 200 voip
 description TO-ITSP
 destination-pattern 9T
 session protocol sipv2
 session target dns:sip.provider.example
 voice-class codec 1
 dtmf-relay rtp-nte
```

---

## 14. Failure mode encyclopedia (CUCM)

| Symptom | Likely causes | First probes |
|---------|---------------|--------------|
| Phone unregistered | VLAN/DHCP/TFTP/CM dead/cert | `show status`, switch port, TFTP reachability |
| No dial tone | Not registered, CSS empty, softkey | Registration state, DN |
| Fast busy on dial | No RP match, CSS, CAC, trunk down | Digit analysis, route list |
| Ring no answer wrong | CFNA, hunt, wrong DN | Line settings |
| One-way audio | NAT, missing MTP, ACL, asymmetric route | Capture RTP both sides |
| Transfer fail | MTP, CSS after transfer, CTI | MRGL, traces |
| MOH silence | MRG, multicast blocked, codec | MOH source assignment |
| Intermittent drop | WAN, keepalive, SIP timer, POE | SPAN + CUBE debug |

---

## 15. Proof block template (use in labs)

```
LICC — Leg · ID · Counter · Capture
Leg:     Alice → CUCM → CUBE → ITSP
ID:      CallManager Trace timestamp / SIP Call-ID / GCID
Counter: Attempt #, node, RP matched, trunk chosen
Capture: Packet capture at phone VLAN + CUBE outside + RTMT SDI
Result:  PASS/FAIL + audio path diagram
```

---

## 16. Glossary (fast)

- **DN** — Directory Number  
- **CSS** — Calling Search Space  
- **RP** — Route Pattern  
- **RL/RG** — Route List / Route Group  
- **MRGL** — Media Resource Group List  
- **EM** — Extension Mobility  
- **DRS** — Disaster Recovery System  
- **CAC** — Call Admission Control  
- **MTP** — Media Termination Point  
- **AAR** — Automated Alternate Routing  

---

## 17. Self-check questions

1. Why might media go through MTP even for two G.711 phones?
2. What is the difference between Region and Location?
3. How does partition order inside a CSS affect digit analysis?
4. When do you prefer SIP trunk over MGCP gateway?
5. What is the restore order after total cluster loss?
6. How does EM interact with emergency location?
7. What breaks first when DSPs are exhausted?
8. How do CM Groups relate to Device Pools?

---

## 18. Next packs

- `DIAL-PLAN-ARCHITECTURE.md` — numbering, TOD, LRG, TEHO, 911  
- `SIP-AND-SBC-MASTERY.md` — SIP/CUBE deep  
- `UC-TROUBLESHOOTING-PLAYBOOK.md` — LICC methodology  
- `E911-AND-EMERGENCY-SERVICES.md` — compliance routing  

---

**Brand:** CYPHER0X9 · cipher0x9 · MIT · THE CALL MUST ALWAYS CONNECT  
**Campus:** UC AI Free University — offline curriculum pack  
**End of CUCM-DEEP-DIVE.md**
