# CCX Contact Center Express — UCCX Mid-Market Mastery

**Campus:** UC AI Free University · CYPHER0X9 / cipher0x9 · MIT  
**Axiom:** THE CALL MUST ALWAYS CONNECT  
**Scope:** Cisco Unified Contact Center Express — scripting, Finesse, CTI, channels, reporting, DR, licensing  
**Level:** Intermediate → Advanced

---

## 0. Outcomes

1. Place UCCX correctly vs UCCE/PCCE/CCaaS.  
2. Build resilient scripts (contact flow) with queues and prioritization.  
3. Integrate tightly with CUCM (CTI ports, route points, application user).  
4. Operate Finesse agent/supervisor desktops.  
5. Plan HA, backup, and license compliance.  
6. Troubleshoot RONA, ghost calls, and stuck CTI ports.

---

## 1. Where UCCX fits

| Platform | Scale / complexity | Notes |
|----------|-------------------|-------|
| UCCX | Up to mid-market (hundreds of agents class) | Single box/cluster simplicity |
| PCCE | Packaged enterprise | Validated design |
| UCCE | Large / complex | Deep ICM |
| CCaaS | Cloud elastic | WxCC, Connect, etc. |

UCCX strengths: speed to value, tight CUCM, CCX Editor scripts, lower ops overhead.  
Limits: multi-site complex routing, massive scale, deep multi-peripheral.

---

## 2. Architecture

```
PSTN → CUBE → CUCM → CTI Route Point (trigger)
                         |
                      UCCX Engine
                       /    \
               CTI Ports    Script / Queue
                    |
              Agent Phone (CUCM) + Finesse
```

### 2.1 Key components

| Component | Role |
|-----------|------|
| UCCX Engine | Executes scripts, queues, selects agents |
| Database | Config + historical (Informix classic) |
| Cisco Finesse | Agent desktop |
| CUIC / Live Data | Reporting (version-dependent packaging) |
| SocialMiner / Chat (legacy paths) | Digital (era-dependent) |
| Media | Prompts on repository |

### 2.2 Cluster

- HA pair: primary/secondary.  
- Failover behavior for engine and DB — **test it**.  
- Publishers of truth for config; know which node is master for services.

---

## 3. CUCM integration objects

### 3.1 Must-have CUCM config

1. **Application user** (e.g., `uccxuser`) with Standard CTI roles.  
2. Associate **CTI route points** (triggers) and **CTI ports** (sessions).  
3. CSS/partitions so RP reachable from gateway CSS.  
4. Agent phones associated for monitoring/control.  
5. RmCm provider configuration on UCCX pointing to CUCM.

### 3.2 CTI ports sizing

- Ports ≈ concurrent IVR sessions + queue treatment sessions (design formula per Cisco SRND for your version).  
- Undersize → calls rejected under load.  
- Over-associate devices → JTAPI login slow.

### 3.3 Triggers

- Directory numbers that start applications.  
- Map one trigger → one application (script).  
- Holiday vs main: separate triggers or script calendar logic.

---

## 4. Scripting (CCX Editor)

### 4.1 Building blocks

| Step | Use |
|------|-----|
| Accept | Answer call |
| Play Prompt | Audio |
| Get Digit String | Input |
| Menu | Branch |
| Select Resource | Queue to CSQ |
| Connect | To agent |
| Call Redirect | Transfer out |
| Set Enterprise Call Info | Data to desktop |
| DB Read / Write | Backend |
| HTTP steps | REST integrations |
| Exception handling | Graceful fail |

### 4.2 CSQ — Contact Service Queue

- Skills-based or resource group based.  
- Agents with skill competence levels.  
- Selection criteria: longest available, most skilled, etc.  
- Dequeue on timeout → overflow script path.

### 4.3 Prompt discipline

- Format and sample rate consistent.  
- Naming convention `AA_Main_EN_v3.wav`.  
- Repository upload + script version lock.  
- Accessibility: speech rate, language.

### 4.4 Anti-patterns

1. No timeout on Get Digit → stuck call.  
2. Infinite queue without escape.  
3. Hardcoded holidays.  
4. DB step without error path.  
5. Debug prompts left in production.

### 4.5 Sample high-level script

```
Accept
Play Welcome
Menu
  1 → Sales CSQ
  2 → Support CSQ
  0 → Operator redirect
  Default → re-prompt ×3 → disconnect polite
Select Resource (CSQ) with queue music + position announce
  On connect → Set call vars → Connect
  On timeout → Play apologize → Redirect to VM / overflow CSQ
```

---

## 5. Agent and supervisor

### 5.1 Agent states

Logout → Login → Not Ready → Ready → Reserved → Talking → Work / Wrap-up  

Reason codes for Not Ready (meeting, break, training) — standardize for WFM.

### 5.2 Finesse

- Team-based layout  
- Gadgets: call control, history, CRM, workflow  
- Desktop workflow automatic screen pop on call variable  
- Supervisor: monitor, barge (if licensed/configured), team state  

### 5.3 IPPA / legacy CAD

Brownfield may still mention CAD/CSD — modernize to Finesse.

---

## 6. CTI and call variables

- Enterprise data fields passed to Finesse.  
- ECC-like usage within UCCX variable model.  
- Screen pop URL encoding — sanitize inputs.  
- Call attached data on transfer between agents.

---

## 7. Email, chat, social

Depending on version and product packaging:

- Email queues with agent reply  
- Web chat  
- Social routing via earlier SocialMiner-type components or newer Webex/digital paths  

**Design note:** Digital async changes SLA math — don’t reuse voice-only staffing blindly.

---

## 8. Reporting

### 8.1 Real-time

- Live Data / Finesse supervisor  
- CSQ waiting, agents logged in, oldest contact  

### 8.2 Historical

- CUIC stock reports: CSQ activity, agent detail, abandoned  
- Traffic analysis for port sizing  
- Abandon on queue vs IVR abandon split  

### 8.3 Definitions workshop

Agree with business:

- When SLA clock starts  
- Short call threshold  
- RONA counted how  
- Transfer counted as handle?

---

## 9. Disaster recovery

### 9.1 HA pair

- Heartbeat / failover of engine  
- Agents re-login behavior  
- CTI reconnection  

### 9.2 Backup

- Scheduled UCCX backup to remote SFTP  
- Document restore order with CUCM dependency  
- Export scripts separately for git-like versioning (script export)

### 9.3 CUCM dependency

If CUCM dies, UCCX cannot control devices — **THE CALL MUST ALWAYS CONNECT** degraded plan:

- CUBE local SRST hunt to phones  
- Night mode cell overflow  
- Status page for agents  

### 9.4 DR drill checklist

- [ ] Fail primary UCCX  
- [ ] Place test call through trigger  
- [ ] Agent RONA and requeue  
- [ ] Historical report gap acceptable?  
- [ ] Restore backup to lab quarterly  

---

## 10. Licensing

| License type | Concept |
|--------------|---------|
| Concurrent agent | Seats logged in |
| Enhanced / Premium | Feature tiers (historical naming) |
| Server / HA | Platform |
| Outbound / IVR ports | Session capacity |
| Recording / QM | Adjacent products |

**Ops:** Monitor license usage peaks; month-end campaigns surprise concurrent spikes.

---

## 11. Outbound (preview)

- Campaigns, progressive/preview dialing features depend on license.  
- Compliance: TCPA-like rules, consent, time-of-day local.  
- CPA (call progress analysis) for answering machines.

---

## 12. Security

- Finesse HTTPS  
- Application user least privilege  
- Script injection via HTTP steps — validate  
- Recording announcement laws  
- Restrict redirect to international patterns  

---

## 13. Troubleshooting playbook

| Symptom | Likely | Probe |
|---------|--------|-------|
| Trigger unregistered | App user, CTI RP, RmCm | CUCM device reg, UCCX Cisco Unified CM Telephony |
| Dead air after accept | Prompt missing, codec, media | Script step, CAP |
| Never queues | Select Resource misconfig | CSQ resources |
| Agents ready but no offer | Skills, CSQ mapping, team | Resource list |
| RONA high | Ring time, device, network | Phone shared line? |
| Stuck CTI port | Call not cleared | Port state, engine restart last resort |
| Finesse blank | SSO, Tomcat, network | Client logs |
| Failover pain | HA config, DNS | Node services |

### LICC for UCCX

```
Leg:     ITSP → CUBE → CUCM RP → UCCX → CTI Port → Agent DN
ID:      UCCX contact ID / CUCM GCID / SIP Call-ID
Counter: queue attempt, RONA #2
Capture: UCCX logs + CUCM SDI + Finesse client + PCAP
```

---

## 14. Lab curriculum

1. Install integration: RP + 4 CTI ports + 2 agents.  
2. Simple menu script to two CSQs.  
3. Priority boost for gold CLID prefix.  
4. Overflow to voicemail after 120 s.  
5. Finesse screen pop with ANI.  
6. HA failover drill.  
7. CUIC abandoned calls report validate against manual count.

---

## 15. Upgrade and change management

- Align UCCX version with CUCM compatibility matrix.  
- JTAPI client versions.  
- Script export before upgrade.  
- Finesse custom gadgets retest.  
- After upgrade: trigger registration, test call matrix, license rehost awareness.

---

## 16. When to leave UCCX

Move up/out when:

- Agent count / multi-channel complexity exceeds comfort  
- Multi-cluster CUCM global routing needed  
- Advanced PQ attribute models / enterprise WFM  
- Cloud elasticity / AI bot fabric primary  

Migrate paths: UCCX → PCCE/UCCE or → WxCC / other CCaaS (see `CCaaS-2026-DEEP.md`).

---

## 17. Interview quick hits

1. CTI route point vs CTI port?  
2. What is CSQ selection criteria?  
3. How does RONA work?  
4. UCCX HA vs UCCE dual side?  
5. Why associate phones to app user?  
6. How to version prompts?  

---

## 18. Ops runbook snippet

```
Daily: check engine service, trigger reg, license peak, backup job
Weekly: abandon % review, RONA top agents, stuck port scan
Monthly: prompt audit, holiday schedule, DR tabletop
Quarterly: restore test, failover test, security patch window
```

---

## 19. Self-check

1. Size CTI ports for 50 agents, 30% queue, 20 IVR sessions — reason.  
2. Map CSS from gateway to RP.  
3. Design overflow for priority customers.  
4. List three fraud controls.  

---

**Brand:** CYPHER0X9 · cipher0x9 · MIT · THE CALL MUST ALWAYS CONNECT  
**End of CCX-CONTACT-CENTER-EXPRESS.md**
