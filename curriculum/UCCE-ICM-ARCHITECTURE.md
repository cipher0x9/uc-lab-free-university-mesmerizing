# UCCE / ICM Architecture — Enterprise Contact Center Routing

**Campus:** UC AI Free University · CYPHER0X9 / cipher0x9 · MIT  
**Axiom:** THE CALL MUST ALWAYS CONNECT  
**Scope:** Cisco Unified Contact Center Enterprise / ICM — Router, Logger, PG, CVP, PQ, reporting, failover, PCCE vs UCCE  
**Level:** Advanced

---

## 0. Outcomes

1. Name every core ICM component and its failure domain.  
2. Trace a call from ingress (CUBE/CUCM/CVP) to agent desktop.  
3. Read and reason about ICM scripts and routing targets.  
4. Contrast skill groups vs precision queues.  
5. Explain CVP comprehensive vs call control models at a design level.  
6. Map reporting (HDS, CUIC) and HA pairs.  
7. Know when PCCE fits vs full UCCE.

---

## 1. Big picture

```
                    +------------------+
   PSTN/ITSP        |  CUBE / Ingress  |
       |            +--------+---------+
       |                     |
       v                     v
   +-------+   SIP    +--------------+     MRCP/HTTP    +----------+
   | CUCM  |<-------->|     CVP      |<--------------->| VXML/Media|
   +---+---+          +------+-------+                 +----------+
       |                     |
       | JTAPI/SIP           | GED-125 / VRU PIM
       v                     v
   +---+----------------------+---+
   |         ICM / CCE            |
   |  Router A/B  ·  Logger A/B   |
   |  HDS · AW · ADS              |
   +-------------+----------------+
                 |
            PG (CUCM PIM, VRU PIM, MR PIM...)
                 |
            Agent phone (CUCM) + Finesse
```

**THE CALL MUST ALWAYS CONNECT** here means: ingress survivability, Router dual-sided, CVP redundancy, agent re-queue on failure, and never black-hole the VRU leg.

---

## 2. Core ICM components

### 2.1 Router (Central Controller)

- Real-time **decision engine**.  
- Runs routing scripts; selects skill group / PQ / agent / label / VRU.  
- Deployed as **Side A / Side B** synchronized pair.  
- Private network for state sync; public/visible network for clients.

### 2.2 Logger

- Persists configuration and historical data path to DB.  
- Paired A/B with Router (often same central controller complex).  
- Source of truth for config replication to AWs.

### 2.3 Administrative Workstation (AW) / ADS

- Configuration UI (Configuration Manager, Script Editor, CCE Admin).  
- Real-time data consumers.  
- **ADS** (Administration Data Server) in modern packaging.

### 2.4 HDS — Historical Data Server

- Longer retention reporting database.  
- CUIC / custom SQL reporting source.  
- Size for CDR/TCD growth; purge policies matter.

### 2.5 Peripheral Gateway (PG)

- Bridges ICM to a **Peripheral** (CUCM, VRU/CVP, ACDs, MR).  
- Contains **PIMs** (Peripheral Interface Managers).  
- Often duplex pairs (PG A/B) for HA.

### 2.6 CTI Server / CTI OS (legacy) / Finesse

- Desktop CTI: agent state, call control, data.  
- Modern: **Finesse** (REST/XMPP) + notifications.

### 2.7 Definitions quick table

| Term | Meaning |
|------|---------|
| Peripheral | ACD/switch/CVR entity ICM controls or monitors |
| Routing client | Source of route requests (CUCM PG, VRU, etc.) |
| Label | Digits/string returned to routing client to complete call |
| Correlation ID | Ties call legs across VRU/ICM |
| Dialed Number (DN) | Ingress address matched to call type |
| Call Type | Maps DN + conditions to scheduled script |
| Skill Group | Agent pool with skill |
| Precision Queue | Attribute-based targeting |
| Agent Desk Settings | Wrap codes, auto-answer, miss policies |

---

## 3. Call flow — comprehensive CVP (typical enterprise)

1. Caller dials DID → ITSP → CUBE → **CVP** (or CUCM → CVP).  
2. CVP sends new call to ICM (VRU PG / GED-125).  
3. ICM runs script: play prompt, collect digits, DB dip, queue.  
4. Queue treatment on CVP (VXML application) under ICM microapp / comprehensive app control.  
5. Agent available → ICM requests connect → CUCM rings agent device.  
6. CVP transfers/connects caller to agent (SIP REFER or hairpin model per design).  
7. Finesse shows call variables; agent answers.  
8. RONA / disconnect / transfer / conference follow scripted rules.  
9. TCD/RCD written; HDS updated for reporting.

### 3.1 Labels and translation

ICM returns a **label** that the routing client understands:

- CUCM: route to agent device target / translation pattern.  
- CVP: transfer label to agent / queue.

Misaligned labels = ring wrong DN, fail connect, or loop.

---

## 4. ICM scripting essentials

### 4.1 Objects in a script

- **Start** → **Set Variable** → **Run External Script** (VRU)  
- **Queue to Skill Group / PQ**  
- **Select** LAA / longest available  
- **If** / **Switch** on call variables, time, ECC  
- **DB Lookup** / **Application Gateway**  
- **Label** / **Dynamic Label**  
- **Termination** nodes (release, busy)

### 4.2 Call variables and ECC

- Call.CallerEnteredDigits, Call.CallingLineID, Call.DialedNumberString  
- Peripheral variables 1–10  
- **ECC** (Expanded Call Context) for richer data to Finesse/CRM  

### 4.3 Scheduling

Call Type schedules map time-of-day to scripts (open, holiday, emergency closed).

### 4.4 Script hygiene

1. One business function per script version; use sub-scripts / formulas carefully.  
2. Default paths for every If.  
3. Queue overflow and max wait exits.  
4. Avoid tight loops without Wait.  
5. Version control exports; change control with business sign-off.

---

## 5. Skill groups vs precision queues

### 5.1 Skill groups

- Agents belong to skill groups (priority per membership).  
- Script: Queue to skill group with priority.  
- Mature, widely understood, good for stable orgs.

### 5.2 Precision queues (PQ)

- Agents have **attributes** (language=es, product=gold, licensed=true).  
- PQ steps: expression + consider-if + wait timers + next step relax.  
- Better for multi-dimensional routing without skill group explosion.

### 5.3 Comparison

| Dimension | Skill Group | Precision Queue |
|-----------|-------------|-----------------|
| Model | Membership | Attributes + steps |
| Explosion risk | High (combo skills) | Lower if attributes designed well |
| Reporting | Classic | PQ reports / CUIC |
| Ops change | Add skills | Change attributes / steps |
| Best for | Stable queues | Complex omnichannel attributes |

---

## 6. CVP architecture

### 6.1 Components

| Component | Role |
|-----------|------|
| CVP Call/VXML Server | Call control + VXML execution |
| Call Server | SIP / ICM interface |
| VXML Server | Complex self-service apps |
| Media Server | WAV prompts (HTTP) |
| OAMP | Operations console |
| Reporting Server | CVP-specific reporting (optional designs) |
| Gateways | VXML gateways / cubeless designs vary |

### 6.2 Deployment models (conceptual)

- **Comprehensive:** ICM controls queue treatment via CVP; primary enterprise model.  
- **Call Director:** ICM labels only; limited treatment.  
- **VRU-only:** Self-service emphasis.

### 6.3 Survivability

- Multiple CVP call servers behind VIP / DNS.  
- CUBE dial-peer preference.  
- Local survivability bootstrap (SRST) does **not** replace ICM — define degraded mode (local hunt).

---

## 7. ICM ↔ CUCM integration

### 7.1 JTAPI / TAPI and PG

- CUCM PG monitors agent lines / CTI route points / CTI ports (model-dependent).  
- Application user with controlled device association.  
- Partition/CSS so CTI RPs are reachable from CVP/CUBE ingress path.

### 7.2 Agent device design

- One agent, controlled device(s); extension mobility caveats.  
- Device targets in ICM match CUCM DNs.  
- Monitor mode / recording media forking separate design (MediaSense legacy, Webex, CUBE Media Proxy, etc.).

### 7.3 Common failures

| Symptom | Check |
|---------|-------|
| Agent not reservable | PG status, device association, desk settings |
| RONA storms | Ring timer, phone shared lines, network |
| No call variables on desk | ECC payload, Finesse gadget, CTI Server |
| Blind transfer drops | CSS, MTP, ICM post-route |

---

## 8. Reporting

### 8.1 Path

```
Router real-time → AW real-time feeds
Logger / HDS → historical
CUIC → stock + custom reports
```

### 8.2 Key metrics

- ASA, AHT, SLA %, abandon, RONA, utilize, occupancy  
- Queue wait, max queued, handle time components  
- Transfer out, consult, conference  

### 8.3 Discipline

- Agree definitions with business (SLA clock start?).  
- Interval vs daily reconciliation.  
- Half-hour intervals classic; don’t change casually.  
- Retain raw data per compliance.

---

## 9. Failover and HA

### 9.1 Dual-sided central controller

- Side A preferred; Side B takes over on private/public network failure modes.  
- **Private network** isolation is a classic split-brain risk — design redundant private links.  
- Visible network for PGs and clients.

### 9.2 PG duplex

- Active/Hot-standby PIM pairs.  
- Test failover during maintenance windows.

### 9.3 Finesse HA

- Primary/secondary Finesse; agents re-login or auto-reconnect per version design.  
- Load balancers must be UC-aware (sticky where required).

### 9.4 Failure matrix

| Failure | Caller experience | Mitigation |
|---------|-------------------|------------|
| Router side fail | Brief routing pause | Dual side |
| CVP node fail | New calls to other CVP | VIP / dial-peer |
| CUCM sub fail | Agent phone re-reg | CM group |
| PG fail | Agents logged out / not routable | Duplex PG |
| WAN to agents | RONA / disconnect | Local agents design / split sites |

---

## 10. PCCE vs UCCE

| Topic | PCCE | UCCE |
|-------|------|------|
| Packaging | Packaged, constrained topology | Flexible enterprise |
| Scale | Up to packaged limits | Very large |
| Admin | CCE Admin UX simplified | Full toolset + complexity |
| CVP/ICM | Included patterns | Fully customizable |
| Ops skill | Lower barrier | Deep ICM skill |
| Use when | Standard enterprise CC | Complex multi-peripheral, global |

**Rule of thumb:** If you need exotic peripherals, massive scale, or nonstandard scripting/integrations, UCCE. If you want Cisco-validated design speed, PCCE.

---

## 11. Agent desktop (Finesse)

- Ready / Not Ready (codes) / Talk / Hold / Wrap  
- Workflows and gadgets (CRM iframe, WFM, recording)  
- Team performance (supervisor)  
- Nonvoice tasks via **Multichannel / MR PG** (email, chat, social) in enterprise designs  

---

## 12. Post-route and translation route

- **Post-route:** After IVR or first ACD, request new route from ICM with more data.  
- **Translation route:** Park call on temporary DN while ICM selects agent — classic pattern for integration with some ACDs/VRUs.

Understand when CVP comprehensive reduces need for older translation-route patterns.

---

## 13. Lab progression

1. Single skill group, simple queue script, two agents.  
2. Add CVP microapps: Play, Get Digits, Menu.  
3. RONA + requeue test.  
4. PQ with two attributes and step relaxation.  
5. CUIC stock queue report validation.  
6. PG failover drill.  
7. After-hours call type schedule.

---

## 14. Troubleshooting map

| Layer | Tools |
|-------|-------|
| ICM | Script Editor monitor mode, Rttest, OPCTest, dumplog |
| PG | procmon, OPC, PIM logs |
| CVP | Call server logs, VXML logs, OAMP |
| CUCM | SDI/SDL traces, RTMT, JTAPI logs |
| SIP edge | CUBE `debug ccsip messages`, PCAP |
| Desktop | Finesse client logs, CTI |

Always bind with **LICC**: Leg (ingress→CVP→ICM→agent), ID (ICM RouterCallKey / SIP Call-ID), Counter (attempt), Capture (picks).

---

## 15. Config / design checklist

- [ ] Dialed numbers and call types documented  
- [ ] Labels unique and routable in CUCM  
- [ ] Agent desk settings + reason codes agreed  
- [ ] ECC variables listed for CRM  
- [ ] PQ attributes governance (who can change)  
- [ ] CVP prompt package versioned  
- [ ] HDS purge and backup  
- [ ] Dual-side private network certified  
- [ ] Finesse SSO (if used) tested  
- [ ] Recording and compliance legal basis  

---

## 16. Security notes

- Limit Configuration Manager access; separate duties.  
- SQL on HDS not exposed broadly.  
- Finesse HTTPS; gadget CSP discipline.  
- Application user passwords rotated; least devices associated.  
- Toll fraud: scripted outdial and agent consult transfer CSS locked down.

---

## 17. Interview bullets (quick)

1. Explain Router vs Logger.  
2. What is a peripheral vs PIM?  
3. Skill group vs PQ with example.  
4. CVP comprehensive call flow.  
5. What is RONA handling?  
6. How does dual-sided private network failure present?  
7. PCCE limits vs UCCE flexibility.  
8. Where do historical reports live?

---

## 18. Glossary

ICM, CCE, PCCE, CVP, PG, PIM, AW, ADS, HDS, CUIC, PQ, LAA, RONA, ECC, GED-125, JTAPI, Finesse, Label, Call Type, MR PG.

---

## 19. Next packs

- `CCX-CONTACT-CENTER-EXPRESS.md` — mid-market scripting cousin  
- `CCaaS-2026-DEEP.md` — cloud contact center comparison  
- `UC-TROUBLESHOOTING-PLAYBOOK.md` — capture methodology  

---

**Brand:** CYPHER0X9 · cipher0x9 · MIT · THE CALL MUST ALWAYS CONNECT  
**End of UCCE-ICM-ARCHITECTURE.md**
