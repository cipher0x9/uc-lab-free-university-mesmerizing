# Unified Messaging and Collaboration — Voicemail, Clients, Presence

**Campus:** UC AI Free University · CYPHER0X9 / cipher0x9 · MIT  
**Axiom:** THE CALL MUST ALWAYS CONNECT  
**Scope:** Unity Connection, Jabber, Webex App, hybrid calendar, presence, integration, on-prem→cloud  
**Level:** Intermediate

---

## 0. Outcomes

1. Architect Unity Connection for multi-site CUCM.  
2. Trace MWI, message waiting, and secure messaging paths.  
3. Deploy soft clients (Jabber/Webex) with reliable SSO and media.  
4. Design presence and hybrid calendar without loops.  
5. Plan migration from on-prem UC to hybrid/cloud collaboration.

---

## 1. Product map (mental model)

| Capability | On-prem classic | Cloud / hybrid |
|------------|-----------------|----------------|
| Call control | CUCM | Webex Calling / UCM Cloud |
| Voicemail | Unity Connection | Webex Voicemail / VxVM / cloud VM |
| IM/Presence | IM&P | Webex Messaging |
| Meetings | Meeting Server / Webex | Webex Meetings |
| Soft client | Jabber | Webex App |
| Calendar | Exchange / Google hybrid | Hybrid Calendar Service |

**Reality 2026:** Many estates are **hybrid** — CUCM + Webex App + Unity or cloud VM.

---

## 2. Cisco Unity Connection (CUC) architecture

### 2.1 Core roles

- **Publisher / Subscriber** CUC cluster  
- Message store (mailboxes)  
- SCCP or SIP integration to CUCM (SIP preferred modern)  
- IMAP / single inbox to Exchange/Microsoft 365  
- VUI / TUI telephone user interface  
- HTTPS VM for visual voicemail  

### 2.2 Ports and call handlers

| Object | Purpose |
|--------|---------|
| Call handler | AA menus, greetings |
| Directory handler | Dial by name |
| Interview handler | Form questions |
| User mailbox | Subscriber |
| Routing rules | Direct vs forwarded call logic |
| Restriction tables | Outdial fraud control |
| Classes of service | Feature authorization |
| Schedules | Open/closed greetings |

### 2.3 Integration with CUCM

**SIP trunk** (recommended pattern):

```
CUCM SIP Trunk → CUC
Route pattern voicemail pilot → trunk
Voicemail profile on DNs → pilot
MWI numbers configured (or SIP unsolicited MWI / SIP NOTIFY patterns per design)
```

**SCCP integration** (legacy ports): still seen; know for brownfield.

### 2.4 Call flow — forwarded to VM

```
Caller → DN busy/CFNA → CF target pilot → CUC routing rule (Forwarded)
  → User greeting → record → MWI ON → phone lamp / soft client badge
```

Direct dial to pilot → opening greeting / auto-attendant.

### 2.5 Single Inbox

- Sync messages with Exchange/M365.  
- Quotas and retention dual systems — define authority.  
- OAuth vs basic auth evolution — follow current Microsoft requirements.  
- Visual voicemail clients depend on secure IMAP/HTTPS APIs.

### 2.6 Networking and HA

- CUC cluster failover behavior for ports.  
- Place media near users if centralized WAN weak (or accept centralization).  
- Backup: COBRAS / DRS-style practices per version docs; test restore of mailboxes.

### 2.7 Fraud and security

- Restrict TRAP outdial and transfers.  
- Secure delete / encryption at rest options.  
- Admin account RBAC.  
- TLS SIP to CUCM where possible.  
- Lock restriction tables — classic toll fraud vector via VM.

---

## 3. MWI mechanics

| Method | Notes |
|--------|-------|
| SCCP MWI | Legacy lamp control |
| SIP unsolicited notify | Common |
| SIP subscribe/notify | Dialog events |
| Soft client push | Jabber/Webex cloud path |

**Troubleshooting MWI:**

1. Message actually left?  
2. Correct mailbox ↔ DN association?  
3. MWI numbers / notification config?  
4. Partition/CSS for MWI on/off numbers?  
5. Phone supports lamp vs only softkey?

---

## 4. Cisco Jabber (classic soft client)

### 4.1 Modes

- **Full UC** — IM&P + CUCM phone services  
- **Phone only mode**  
- **IM only**  

### 4.2 Services discovery

- DNS SRV: `_cisco-uds`, `_cuplogin`, collab-edge  
- `jabber-config.xml` TFTP/HTTP  
- MRA (Mobile Remote Access) via Expressway-C/E for external  

### 4.3 Common breakages

| Symptom | Cause |
|---------|-------|
| No phone services | UDS / CUCM CCMCIP / CTI failures |
| Deskphone control fails | CTI user device association |
| MRA register fail | Expressway traversal, certs, SRV |
| Media one-way external | Firewall / TURN lacking |
| SSO loop | IdP metadata clock skew |

### 4.4 Jabber → Webex App trajectory

Many orgs migrate users to **Webex App** calling (UCM calling or WxCalling). Plan feature parity: hunt groups, EM, recording, contact center step-aside.

---

## 5. Webex App (collaboration client)

### 5.1 Pillars

- Messaging spaces  
- Meetings  
- Calling (Webex Calling **or** Calling in Webex App UCM)  
- Presence / status  
- Whiteboard / file share  

### 5.2 Control Hub

- User lifecycle (directory connector / SCIM / manual)  
- Service assignment licenses  
- Device management  
- Security: SSO, MFA, token policies  
- Analytics  

### 5.3 Calling in Webex with UCM

- Webex App registers to CUCM (softphone mode) or controls desk phone.  
- Hybrid requirements: Webex discovery, certificates, possibly MRA.  
- Maintain dial plan consistency with hard phones.

---

## 6. Webex Calling (cloud PSTN / cloud PBX sketch)

See also `WEBEX-AND-CLOUD-MIGRATION.md`. Here: messaging adjacency.

- Numbers in cloud locations  
- Local gateway (CUBE) for PSTN premises breakout  
- Features: hunt, call queue, auto attendant (cloud)  
- Voicemail in cloud; integrate email notification  

---

## 7. Hybrid calendar

### 7.1 Purpose

Webex/@meet scheduling from Outlook/Google; one-button join; presence in meetings.

### 7.2 Components (conceptual)

- Hybrid Calendar Service (Expressway or cloud-connected calendar)  
- Exchange impersonation / Graph app permissions  
- Domain verification in Control Hub  

### 7.3 Failure modes

- Wrong OAuth scopes  
- Room mailbox not enabled  
- Multiple @meet expanders  
- Time zone skew  

---

## 8. Unified presence design

### 8.1 Sources of truth

| State | Source |
|-------|--------|
| On a call | CUCM / cloud calling |
| In meeting | Meetings platform |
| IM available | Messaging |
| Calendar busy | Calendar service |
| Custom DND | Client |

### 8.2 Privacy

- Directory photo policies  
- Presence federation (XMPP legacy / business messaging)  
- Contact list vs org-wide search  

### 8.3 Contact center agents

Agent “Not Ready” ≠ Webex DND. Train dual presence models; consider presence integration carefully so ACD state remains authoritative for routing.

---

## 9. Integration patterns

### 9.1 Directory

- LDAP sync CUCM end users  
- Azure AD / Entra ID for Webex  
- Single identity story reduces ticket load  

### 9.2 SSO

- SAML / OIDC  
- Clock sync critical  
- Emergency break-glass local admin accounts  

### 9.3 Voicemail notification

- SMTP from CUC  
- Webex email notify  
- SMS gateways (compliance)  

### 9.4 Recording and compliance

- On-prem recorders on SIP/JTAPI  
- Cloud compliance archiver for messaging  
- Legal hold differs by plane (voice vs message)

---

## 10. Migration patterns (messaging + clients)

### 10.1 Phased

1. Deploy Webex Messaging alongside Jabber IM (dual client period short).  
2. Move meetings fully to Webex.  
3. Softphone to Webex App (UCM calling).  
4. Evaluate Unity → cloud voicemail.  
5. Evaluate CUCM → Webex Calling last (most sensitive).  

### 10.2 Cutover risks

- Lost VM messages if not exported  
- Contact lists  
- Deskphone control habits  
- MRA vs cloud edge mental model  
- 911 for softphone nomadic users  

### 10.3 Coexistence rules

- One primary soft client per persona where possible.  
- Shared DN dual-reg caution.  
- Clear dialing domains.

---

## 11. Auto-attendant design (Unity)

Best practices:

- Shallow menus (chunk ±7).  
- Always 0 human escape (business hours).  
- Language selection first if multi-lingual.  
- Holiday schedules tested yearly.  
- Name dial backup.  
- Log and review failed transfers monthly.

Sample tree:

```
Opening
 1 Sales → hunt / CC pilot
 2 Support → CC
 3 Directory
 0 Operator
 * Retry
```

---

## 12. Visual voicemail and UX

- Pin lock  
- Envelope information  
- Secure messaging (cannot forward) for clinical/finance  
- Quota warnings before full  

---

## 13. Lab exercises

1. SIP integrate CUC; leave message; MWI on/off.  
2. Build AA with schedule open/closed.  
3. Restriction table block international outdial from VM.  
4. Jabber or Webex App softphone call + escalate to meeting.  
5. Hybrid calendar @webex join button.  
6. Fail CUC publisher; test subscriber call answer.

---

## 14. Troubleshooting matrix

| Issue | Checks |
|-------|--------|
| No VM answer | Pilot RP, trunk, CUC ports, routing rules |
| MWI stuck | Notification table, phone reset, CUC MWI resync |
| AA transfer fail | CSS on CUC ports / SIP trunk CSS, restriction |
| Single inbox delay | Auth, throttling, item sync logs |
| Soft client no reg | Discovery SRV, certs, license, MRA |
| Presence wrong | Calendar connector, DND, multiple devices |

Use **LICC**: Leg (caller→CUCM→CUC), ID (SIP Call-ID), Counter, Capture (CUC traces + CUCM SDI).

---

## 15. Capacity planning notes

- Concurrent ports (sessions) on CUC sized for peak + AA.  
- Storage for message retention policy.  
- G.711 vs G.729 prompt sets.  
- Transcoding if codec mismatch to CUC.

---

## 16. Compliance checklist

- [ ] Message retention policy written  
- [ ] Encryption in transit for SIP/IMAP/HTTPS  
- [ ] Toll fraud lock on VM outdial  
- [ ] eDiscovery owner named (cloud messaging)  
- [ ] Break-glass admin  
- [ ] BAA/HIPAA if healthcare (process + tech)  

---

## 17. Self-check

1. Direct vs forwarded routing rules — difference?  
2. Why restriction tables matter for fraud?  
3. Jabber MRA vs Webex cloud edge?  
4. Why agent ACD state overrides IM DND?  
5. What breaks MWI without breaking deposit?  

---

## 18. Glossary

CUC, MWI, TUI, VUI, CoS (Unity), Single Inbox, MRA, Expressway, Control Hub, UDS, CTI, Hybrid Calendar, Visual Voicemail.

---

**Brand:** CYPHER0X9 · cipher0x9 · MIT · THE CALL MUST ALWAYS CONNECT  
**End of UNIFIED-MESSAGING-AND-COLLABORATION.md**
