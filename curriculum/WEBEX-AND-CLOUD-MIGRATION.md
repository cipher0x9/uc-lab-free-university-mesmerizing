# Webex and Cloud Migration — Hybrid UC Paths

**Campus:** UC AI Free University · CYPHER0X9 / cipher0x9 · MIT  
**Axiom:** THE CALL MUST ALWAYS CONNECT  
**Scope:** Webex suite, hybrid calling, PSTN, CUCM→Webex Calling migration, Control Hub, APIs  
**Level:** Architecture + program

---

## 0. Outcomes

1. Describe Webex Calling, Messaging, Meetings, Contact Center roles.  
2. Design hybrid architectures with Local Gateway / premises PSTN.  
3. Choose migration patterns (phased, pilot, dual-running).  
4. Operate Control Hub as the cloud control plane.  
5. Automate with APIs responsibly.  
6. Keep emergency calling correct through every phase.

---

## 1. Webex suite overview

| Service | Function | Replaces / coexists with |
|---------|----------|---------------------------|
| **Webex Messaging** | Team chat, spaces | Jabber IM, other chat |
| **Webex Meetings** | Conferences | CMS / other meeting stacks |
| **Webex Calling** | Cloud PBX | CUCM (partial/full) |
| **Webex Webinars / Events** | Large broadcast | Separate meeting SKUs |
| **Webex Contact Center** | CCaaS | UCCX/UCCE |
| **Control Hub** | Admin plane | Multiple element managers |
| **Devices** | MPP, RoomOS | On-prem phone management |

**Brand note:** Campus materials use CYPHER0X9 education framing; always validate live vendor SKUs before purchase.

---

## 2. Architecture patterns

### 2.1 Cloud-first Webex Calling

```
Endpoints (MPP / Webex App / Room)
        |
   Webex Calling cloud
        |
   PSTN: CCP / cloud connected PSTN / premises LGW
```

### 2.2 Hybrid: CUCM + Webex App (UCM Calling)

```
Webex App → CUCM (call control remains on-prem)
Messaging/Meetings → cloud
```

Good interim: modern client, stable dial plan.

### 2.3 Hybrid: Webex Calling + Local Gateway (CUBE)

```
Webex Calling ↔ Local Gateway (CUBE) ↔ ITSP / PRI / regional PSTN
                 optional ↔ CUCM (dial plan interconnect)
```

### 2.4 Dual call control coexistence

```
Site A: still CUCM
Site B: Webex Calling
Inter-org dialing via trunk / dial plan rules / translation
```

**Risk:** feature asymmetry, 911 splits, transfer across islands.

---

## 3. PSTN attachment models

| Model | Description | Pros | Cons |
|-------|-------------|------|------|
| Cloud Connected PSTN (CCP) | Provider integrated to Webex | Speed | Geo coverage |
| Cisco Calling Plans | Cisco-sourced numbers | Simplicity | Availability |
| Premises PSTN via LGW | CUBE to ITSP | Keep contracts, sovereignty | Ops burden |
| Mixed | Per location | Flexibility | Complexity |

### 3.1 Local Gateway essentials

- CUBE IOS/IOS-XE validated version  
- Secure SIP trunk to Webex edge (TLS)  
- Dial peers both directions  
- Numbering E.164  
- Capacity and HA dual CUBE  
- Monitoring OPTIONS + call quality  

---

## 4. Migration paths from CUCM

### 4.1 Strategy options

1. **Pilot group** — IT first, then friendly business unit.  
2. **Site-by-site** — align with WAN/LAN refresh.  
3. **Persona-based** — knowledge workers first; contact center last.  
4. **Big bang** — rare; only small orgs with perfect prep.  

### 4.2 Workstream map

| Workstream | Artifacts |
|------------|-----------|
| Numbers | Inventory DID, port plan, LOA |
| Dial plan | Extension continuity, short dial |
| Endpoints | MPP vs existing 88xx onboarding path |
| Users | Identity, licenses, SSO |
| Features | Hunt, pickup, shared lines, PAG |
| Applications | Attendant console, recording, fax |
| Contact center | Separate program |
| Emergency | RedSky/Wx emergency config |
| Training | End user + helpdesk |
| Decommission | CUCM node retire criteria |

### 4.3 Feature parity matrix (build this)

| Feature | CUCM today | Webex Calling | Gap action |
|---------|------------|---------------|------------|
| Shared line | Yes | Check limits | Redesign |
| EM | Yes | Hot desking analogs | Process |
| SNR / Mobile connect | Yes | Single number reach | Configure |
| Hunt | Yes | Cloud hunt | Remap |
| Call park | Yes | Yes/limits | Train |
| CTI heavy app | Yes | API different | Rebuild |
| Analog gateways | Yes | ATA / LGW | Design |

### 4.4 Number porting

- Freeze window  
- Test DIDs first  
- Call-in and call-out validation matrix  
- SMS/fax dependencies  
- Caller ID name (CNAM) separate  

---

## 5. Coexistence patterns

### 5.1 Dial plan interconnect

- Route inter-system calls via SIP trunks (CUCM ↔ LGW ↔ Webex).  
- Normalize +E.164.  
- Prevent tromboning (call leaves and re-enters unnecessarily).  

### 5.2 Directory

- Unified directory via Entra ID / LDAP to both.  
- Avoid duplicate contacts with wrong dial strings.

### 5.3 Meetings + calling

Users may join meetings from Webex while calling still on CUCM — train which app does what during transition.

---

## 6. Device management

### 6.1 MPP phones

- Onboard via Control Hub activation codes / MAC  
- Firmware cloud-managed  
- Local network: DHCP, NTP, VLAN still required  
- QoS still required — cloud does not magically mark EF  

### 6.2 RoomOS devices

- Control Hub workspace  
- Calendar hybrid  
- Webex meetings optimized  

### 6.3 Soft clients

- Webex App calling enablement  
- Headsets certified  
- OS permissions (mic)  

---

## 7. Webex Control Hub operations

### 7.1 Daily ops

- User add/remove / license templates  
- Device status  
- Calling quality dashboards  
- Security alerts  

### 7.2 Org settings that matter

- SSO / MFA  
- File sharing controls  
- External communication policies  
- Retention  
- Role-based admins (least privilege)  

### 7.3 Locations

Calling locations map to emergency enablement, PSTN, and dialing behavior — design before bulk user load.

---

## 8. API-driven automation

### 8.1 Use cases

- User onboarding  
- Number assignment  
- Device inventory export  
- Compliance archival triggers  
- Workspace creation  

### 8.2 Practices

- Service accounts / integration bots with scoped tokens  
- Idempotent scripts  
- Audit log every mutation  
- Rate limit handling  
- Never store refresh tokens in git  

### 8.3 Example automation flow (conceptual)

```
HRIS new hire → identity group
  → Control Hub license template
  → assign number from pool API
  → send onboarding space message
  → ITSM close ticket
```

---

## 9. Security and compliance in cloud UC

- SSO + MFA  
- End-to-end encryption options where applicable (meetings)  
- Data residency selections  
- eDiscovery / Legal hold for messaging  
- Bring-your-own-key discussions for regulated industries  
- Admin audit logs exported to SIEM  

---

## 10. Emergency calling in migration

**Non-negotiable checklist:**

- [ ] Kari’s Law direct 911  
- [ ] Dispatchable location (RAY BAUM’S)  
- [ ] User nomadic softphone workflow  
- [ ] Test call per location after cutover  
- [ ] No period where site lacks configured emergency  
- [ ] PSAP callback numbers validated  

Cloud and on-prem emergency stacks can differ — **never dual-disable during move**.

---

## 11. Network readiness for cloud UC

- Internet edge capacity + breakout  
- Split tunnel VPN for Webex media (recommended patterns)  
- DNS, NTP, proxy exceptions  
- QoS on WAN for RTP to cloud (DSCP trust to edge)  
- Certificate trust on clients  

See `QOS-AND-NETWORK-READINESS.md`.

---

## 12. Contact center cloud (pointer)

Webex Contact Center migration is its own program: IVR rewrite, agent desktop, WFM, recording, CRM. See `CCaaS-2026-DEEP.md`. Do not bury CC inside a PBX move casually.

---

## 13. Program governance

### 13.1 RACI sketch

| Decision | A | R | C | I |
|----------|---|---|---|---|
| Dial plan standard | Arch | Voice eng | CC, Security | Helpdesk |
| Cutover date | Business | PMO | Voice | All |
| PSTN contract | Procurement | Voice | Legal | Finance |
| Emergency accept | Compliance | Voice | Facilities | Exec |

### 13.2 Exit criteria from coexistence

- <X% calls still on CUCM  
- No critical app dependency  
- 30 days stable quality metrics  
- Backup/restore cloud admin procedures drilled  
- CUCM reduced to decommission candidate  

---

## 14. Rollback plans

Every cutover wave:

1. Keep CUCM config frozen but online until hypercare ends.  
2. Number routing can revert at carrier / LGW.  
3. Devices re-point plan documented.  
4. Comms templates ready.  

Rollback is a **routing** problem first, ego problem second.

---

## 15. Lab / sandbox exercises

1. Control Hub trial: user, MPP sim, call between clients.  
2. LGW lab trunk to Webex sandbox (if available).  
3. Build parity matrix for a fictional 3-site CUCM.  
4. Porting tabletop exercise.  
5. API list users and export numbers (read-only).  
6. Emergency location config dry-run.

---

## 16. Troubleshooting cloud calling

| Issue | Checks |
|-------|--------|
| No dial tone soft client | License, location, network, SSO |
| Cannot reach on-prem ext | Interconnect dial plan, LGW |
| One-way audio WFH | VPN split tunnel, local firewall |
| Device offline | MAC, activation, DHCP, firewall 443 |
| Poor MOS | ISP, Wi-Fi, QoS, split tunnel |
| Wrong caller ID | Number assignment, CLID policy |

LICC still applies: Leg (client→cloud→LGW→ITSP), ID (SIP Call-ID / correlation), Counter, Capture (client media stats + CUBE PCAP).

---

## 17. Cost and license awareness

- User vs workspace vs device licenses  
- Meetings features attach differently  
- PSTN usage vs commitment  
- Parallel run costs (double) during migration — budget hypercare  

---

## 18. Self-check

1. UCM Calling in Webex App vs Webex Calling?  
2. When is LGW mandatory?  
3. Why site-by-site often beats big bang?  
4. What never pauses during migration (emergency)?  
5. Name three Control Hub security settings.  

---

## 19. Wave plan template

```
Wave 0: IdP, Control Hub, network exceptions
Wave 1: IT pilot 25 users
Wave 2: Site remote-branch (small)
Wave 3: HQ floor knowledge workers
Wave 4: Analog/fax/specialty
Wave 5: Contact center (separate gate)
Wave 6: Decommission CUCM services
```

---

**Brand:** CYPHER0X9 · cipher0x9 · MIT · THE CALL MUST ALWAYS CONNECT  
**End of WEBEX-AND-CLOUD-MIGRATION.md**
