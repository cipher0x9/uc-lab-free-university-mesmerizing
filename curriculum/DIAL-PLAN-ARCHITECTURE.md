# Dial Plan Architecture — Numbering, Routing, and Digit Policy

**Campus:** UC AI Free University · CYPHER0X9 / cipher0x9 · MIT  
**Axiom:** THE CALL MUST ALWAYS CONNECT  
**Scope:** Enterprise dial plan design for CUCM/hybrid — numbering, filters, translations, TOD, hunt, LRG, TEHO, 911  
**Level:** Design + implementation

---

## 0. Outcomes

1. Design a multi-site numbering plan without overlap collisions.
2. Implement partitions/CSS + route patterns that enforce least privilege.
3. Use translation patterns and transforms without creating loops.
4. Build time-of-day, hunt, route group, and local route group patterns.
5. Engineer TEHO (tail-end hop off) safely with CAC and legal constraints.
6. Embed emergency routing as a first-class design object, not an afterthought.

---

## 1. Numbering plan design

### 1.1 Design inputs

| Input | Why |
|-------|-----|
| Sites / countries | Country codes, emergency numbers, regulator |
| User count + growth | Digit length, spare ranges |
| DID inventory | Mapping PSTN ↔ internal |
| Contact center | Pilot DNs, VDNs, free phone numbers |
| Analog / fax / elevators | Special CSS and 911 |
| Cloud coexistence | Webex Calling location numbers, dual stack |

### 1.2 Internal schemes

| Scheme | Example | Pros | Cons |
|--------|---------|------|------|
| 4-digit flat | 1000–8999 | Simple | Small orgs only |
| 5–6 digit flat | 5XXXX | Simple DA | Limited multi-site |
| Site code + ext | 2 + 4 digits → 21XXX | Clear site | Longer dialing |
| +E.164 globalized | +15551234567 | Interop king | UX + training |
| Mixed | Internal short + globalized core | Pragmatic | Complexity |

**Modern recommendation:** Internal short dial for UX + **globalized** core (+E.164) on trunks and directories. Normalize early with translation patterns.

### 1.3 Access codes

- `9` PSTN (NANP tradition) — still common, colliding with extensions starting with 9.
- `0` attendant — train vs emergency `0` in some countries.
- `8` TEHO or secondary trunk — document ruthlessly.
- Prefer **explicit** patterns over `@` wildcards when fraud control matters.

### 1.4 DID mapping strategies

1. **Direct map:** last 4 of DID = extension.  
2. **Translation on inbound trunk CSS:** 10-digit → 5-digit.  
3. **Directory Number external phone number mask** for outbound CLID.  
4. **SID/SIP identity** headers for STIR/SHAKEN-aware providers.

---

## 2. Digit analysis engine (CUCM)

### 2.1 Order of operations (conceptual)

1. User dials digits (en bloc or overlap).
2. CUCM applies **CSS** (device + line).
3. Search partitions for: Translation Pattern → DN / Route Pattern / Hunt Pilot / Call Park etc.
4. First best match (most specific / first in CSS order depending on pattern logic).
5. Apply discard / prefix / transform masks.
6. Select Route List → Route Group → device.
7. Apply outbound calling/called party transforms on trunk/device.

### 2.2 Pattern syntax essentials

| Token | Meaning |
|-------|---------|
| `X` | 0–9 |
| `!` | One or more digits |
| `@` | NANP macro (use carefully) |
| `[2-9]` | Range |
| `\`+ | Literal + |
| `.` | Discard delimiter (PreDot) |

Examples:

```
9.[2-9]XXXXXX          # local 7-digit after 9
9.[2-9]XX[2-9]XXXXXX   # 10-digit NANP
9011.!                 # international
911 / 9911 / 9.911     # emergency variants
\+1XXXXXXXXXX          # globalized
```

---

## 3. Route filters

Route filters refine `@` patterns and large number plans:

- Filter tags: AREA-CODE, LOCAL-AREA-CODE, OFFICE-CODE, etc.
- Attach filter to route pattern using `@`.
- Use to allow/block specific NPAs without thousands of patterns.

**When to avoid `@`:** multi-country clusters, complex TEHO, fraud-sensitive trunks — prefer explicit patterns + CSS.

---

## 4. Translation patterns

### 4.1 Jobs of a translation pattern

- Normalize dialed string (add site code, strip +).
- Block patterns (`\+1900!` → block).
- Provide abbreviated dial (x100 → full DN).
- Reroute service codes.

### 4.2 Loop prevention

Translation patterns can re-enter digit analysis:

1. Put TP in partition only certain CSS can hit.
2. After translation, **CSS of the translation pattern** controls next search — set intentionally.
3. Avoid TP A → TP B → TP A cycles.
4. Prefer single normalize step at edge (phone CSS or trunk inbound CSS).

### 4.3 Example — inbound DID normalize

```
Translation Pattern: 212555XXXX
Partition: PT-Inbound-Norm
CSS (on TP): CSS-Internal-Only
Called Party Transform Mask: 5XXXX
```

---

## 5. Digit manipulation toolbox

| Mechanism | Scope | Typical use |
|-----------|-------|-------------|
| Discard Digits (PreDot) | Route pattern | Strip 9 |
| Called Party Transform Mask | Pattern / RL / device | Prefix, strip | 
| Calling Party Transform | Pattern / device | CLID |
| External Phone Number Mask | DN / device | Outbound presentation |
| Transformation Patterns (CUCM) | Globalized dial plan | Inbound/outbound separate |
| CUBE translation-profile / sip-profiles | Edge | ITSP quirks |
| Lua normalization | SIP trunk | Header surgery |

**Golden rule:** Manipulate **once** at the correct layer. Double strip = wrong number; double prefix = unroutable.

### 5.1 Worked example — outbound LD

User dials: `912125550100`  
Route pattern: `9.@` discard PreDot → `12125550100`  
Called transform on trunk: prefix `+` → `+12125550100`  
ITSP expects E.164 with `+`.

### 5.2 Worked example — extension to DID CLID

DN 5100, external mask `212555XXXX` → CLID `2125555100` (or +1…).

---

## 6. Time-of-Day (TOD) routing

### 6.1 Building blocks

- **Time Period** — hours/days  
- **Time Schedule** — collection of periods  
- **Partition** controlled by time schedule  
- Or **TOD** on hunt / translation depending on design

### 6.2 Classic after-hours pattern

```
Business partition PT-Main-Open   (schedule Mon–Fri 08:00–18:00)
After-hours        PT-Main-Closed (inverse / always)

CSS includes both; open hours DN/pilot live in Open;
Closed hours CTI RP / Unity / WxCC night service in Closed.
```

### 6.3 Use cases

- Night service auto-attendant  
- Least-cost routing windows  
- Block international after hours for most CSS  
- Contact center schedule alignment (also scripted in ICM/UCCX)

**Pitfall:** Cluster nodes in different time zones — set Date/Time Groups correctly per device pool.

---

## 7. Hunt groups and call coverage

### 7.1 Objects

```
Line Group → Hunt List → Hunt Pilot
```

- **Line Group:** members (DNs), distribution (top-down, circular, longest idle, broadcast), ring/no-answer timers.
- **Hunt List:** ordered line groups.
- **Hunt Pilot:** dialable number in a partition; CSS for forwards.

### 7.2 Coverage design

| Model | Behavior | When |
|-------|----------|------|
| Broadcast | All ring | Small teams |
| Circular | Round-robin | Fairness |
| Longest idle | Idle preference | Sales floor |
| Top-down | Priority skilled | Tier-1 first |

Final forwarding: CFNA/CFB on pilot → AA / queue / Voicemail.

### 7.3 Hunt vs contact center

Hunt is **not** a contact center: no skills-based routing depth, limited reporting, no advanced queue treatment. Use UCCX/UCCE/WxCC when SLA, skills, and omnichannel matter.

---

## 8. Route groups and route lists

### 8.1 Distribution

- **Top-down:** primary trunk first  
- **Circular:** load share  
- Members: SIP trunks, MGCP gateways, H.323 (legacy)

### 8.2 Failover logic

Route List tries RG members until setup succeeds or list exhausted → user reorder tone / announcement.

**Test:** Shut primary CUBE; confirm secondary takes calls; confirm recovery.

### 8.3 Call classification

OnNet vs OffNet affects:

- Call forward restrictions  
- Outside dial tone  
- Drop conference on drop of external  
- Toll fraud policies  

---

## 9. Local Route Groups (LRG)

### 9.1 Problem

Centralized route patterns for `9.@` but each site must egress its **local** gateway.

### 9.2 Solution

- Route pattern points to Route List that uses **Standard Local Route Group**.
- Device Pool defines which Route Group is “local” for that site.

```
RP 9.@ → RL-PSTN-LRG → (Standard Local Route Group)
Device Pool NYC → Local RG = RG-NYC-CUBE
Device Pool LON → Local RG = RG-LON-CUBE
```

### 9.3 Benefits

- One pattern set globally  
- Site-specific egress  
- Cleaner multi-site operations  

### 9.4 Pitfalls

- Forgot to set LRG on device pool → call fail  
- Softphone VPN user in wrong DP → wrong egress / wrong 911  

---

## 10. Tail-End Hop Off (TEHO)

### 10.1 Concept

Route long-distance/international calls across the enterprise IP WAN and egress PSTN near the destination site to save toll charges.

```
User in NYC dials Paris number
  → CUCM matches TEHO RP for FR
  → Trunk/RL toward Paris CUBE
  → Local FR PSTN hop-off
```

### 10.2 Design controls

1. **Legal/regulatory** — some countries restrict TEHO.  
2. **CAC** — do not saturate WAN.  
3. **Codec** — G.729/Opus + transcoding plan.  
4. **CLID** — presentation and emergency semantics.  
5. **Failover** — if remote site down, fall back to local ITSP (costlier).  
6. **Fraud** — TEHO patterns are attractive abuse targets; tight CSS.

### 10.3 Pattern sketch

```
Partition PT-TEHO-EU
Patterns for country codes toward EU site RLs
CSS-TEHO-Enabled on finance/exec only (example)
Fallback RP in PT-PSTN-Local for same numbers via local ITSP lower priority? 
  → Prefer explicit primary/secondary RL members instead of ambiguous overlaps
```

---

## 11. Emergency routing (dial plan view)

### 11.1 Must-handle patterns (NANP example)

| Dialed | Action |
|--------|--------|
| 911 | Emergency RP, no block |
| 9911 | Strip 9 → 911 |
| 9.911 | PreDot |
| 112 / 999 / 000 | As needed for geo |
| Test PSAP numbers | Lab only |

### 11.2 Design rules

1. **Every CSS** that can seize a line reaches emergency partitions.  
2. Do not require outside access code for 911 if policy says so (Kari’s Law: direct 911).  
3. ELIN / ERL / RedSky integration for location (see E911 pack).  
4. MLAG / callback numbers for PSAP return calls.  
5. Nomadic users: softphone location workflows.

### 11.3 Route pattern notes

- Mark emergency patterns clearly.  
- Priority and specificity over `9.!` catch-alls.  
- Never place emergency-only on a trunk that can be blocked by TOD fraud locks without exception path.

---

## 12. Globalized dial plan pattern (CUCM)

Cisco’s globalization approach:

1. **Localize** at phone (what user dials).  
2. **Globalize** ASAP to +E.164.  
3. Route on global forms.  
4. **Localize** again at egress for ITSP that wants national format.

Objects: Incoming Calling/Called Party Settings, Transformation Patterns, SIP profiles.

**Why bother:** Multi-national clusters, consistent TEHO, directory integration, reduced pattern sprawl.

---

## 13. Multi-cluster and SME considerations

- **SME (Session Management Edition)** — central routing cluster; leaf clusters for sites.  
- **GK / ILS / URI dialing** — directory URI, `user@domain`, hybrid Webex.  
- **Intercluster trunks (ICT / SIP)** — CSS on both sides; avoid open transit fraud.  
- **+E.164** as intercluster lingua franca.

---

## 14. Blocking and fraud patterns

```
# Premium rate / high risk examples (illustrative)
\+1900!
\+1976!
9011.980!
9.1900XXXXXXX
```

Controls:

- Separate partitions for intl  
- After-hours block on CSS  
- CUBE: `fraud-protection`, class of restriction, max connections  
- CDR alarms on destinations  
- Disable unused VM ports outdial  

---

## 15. Documentation artifacts (ship with every design)

1. Numbering plan spreadsheet (site, range, DID, pilot).  
2. Partition/CSS matrix (who can dial what).  
3. Route pattern catalog with discard/transform notes.  
4. Trunk matrix (codec, early offer, network).  
5. Emergency matrix (ERL, ELIN, test dates).  
6. TEHO legal sign-off.  
7. Change control for digit manipulation.

---

## 16. Lab exercises

### Lab A — Restricted CSS

Build CSS-Internal (no PSTN) and CSS-Local. Prove DN-to-DN works; PSTN fails for internal; works for local.

### Lab B — Translation normalize

Inbound 10-digit DID → 4-digit DN via TP; missed call CLID correct.

### Lab C — LRG

Two device pools, one RP `9.@`, two CUBEs; verify site egress.

### Lab D — Hunt

4 members, circular, CFNA to Unity Connection pilot.

### Lab E — TOD

AA day greeting vs night greeting via partition schedules.

### Lab F — TEHO simulation

Two “countries” in lab; force codec + CAC; fail remote and observe fallback.

---

## 17. Decision trees

### 17.1 User gets reorder tone

```
Registered? → N: fix reg
  Y → Digits match any pattern in CSS? → N: CSS/partition/pattern
    Y → Translation loop? → Y: fix TP CSS
      N → Route list members up? → N: trunk/CUBE
        Y → ITSP reject? → SIP codes 4xx/5xx
          CAC reject? → Locations
```

### 17.2 Wrong gateway used

```
Check RP → RL → RG order
LRG set on DP?
Overlapping patterns more specific elsewhere?
TEHO pattern stealing local?
```

---

## 18. Sample multi-site blueprint

| Site | Ext range | Local RG | Emergency |
|------|-----------|----------|-----------|
| HQ NYC | 5XXX | RG-NYC | RedSky + ELIN NYC |
| CHI | 6XXX | RG-CHI | RedSky + ELIN CHI |
| Remote VPN | 5XXX EM | RG-NYC default | User location portal |
| Contact Center | 8XXX pilots | RG-NYC | Same as HQ |

CSS tiers: Lobby / Knowledge / Manager / ContactCenter / International / TrunkInbound.

---

## 19. Interop with cloud (preview)

When coexisting with Webex Calling:

- Decide **who owns PSTN** (on-prem CUBE vs cloud CCP/local gateway).  
- Align extension dialing via dial plan rules / intercepts.  
- Avoid split-brain 911.  
- Document which numbers are authoritative in which system.

See `WEBEX-AND-CLOUD-MIGRATION.md`.

---

## 20. Self-check

1. Why is first-match CSS order dangerous with overlapping TPs?  
2. When is LRG better than per-site route patterns?  
3. What regulatory question must precede TEHO?  
4. How do you guarantee 911 without an access code?  
5. Hunt pilot vs UCCX trigger — when upgrade?  
6. What is globalization localize-globalize-localize?  
7. How does TOD interact with device pool time zones?  

---

## 21. Quick reference — object ownership

| Object | Owner team | Change risk |
|--------|------------|-------------|
| DN ranges | Voice architecture | High |
| CSS matrix | Voice + security | Critical |
| RP / TEHO | Architecture | High |
| Hunt | Ops / business | Medium |
| TOD schedules | Ops | Medium |
| Emergency | Compliance + voice | Critical |
| Trunk transforms | Voice + carrier | High |

---

**Brand:** CYPHER0X9 · cipher0x9 · MIT · THE CALL MUST ALWAYS CONNECT  
**End of DIAL-PLAN-ARCHITECTURE.md**
