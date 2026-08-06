# Expressway, MRA & Collaboration Edge

**CYPHER0X9 · UC Lab Free University · curriculum pack · MIT**  
**Proof:** LICC · **Spine:** THE CALL MUST ALWAYS CONNECT

Remote and mobile workers changed the edge. This pack covers **Collaboration Edge / MRA (Mobile and Remote Access)** mental models so you can debug "works on-prem, fails from home" without superstition.

---

## 1) Why the edge exists

| Goal | Edge pattern |
|------|----------------|
| Register soft clients from internet | MRA via Expressway-C/E (or successor cloud edge patterns) |
| B2B / federation | Traversal, DNS SRV, cert trust |
| Secure media | TURN/ICE, firewall traversal |
| Keep core private | DMZ proxy, no naked CUCM on internet |

**Never** put CUCM admin or unrestricted SIP on the open internet "because it was easy."

---

## 2) Expressway-C / Expressway-E split (classic)

```text
Internet → Expressway-E (DMZ) ⇄ traversal zone ⇄ Expressway-C (inside) → CUCM / IMP / etc.
```

| Node | Trust zone | Typical jobs |
|------|------------|--------------|
| **E** | DMZ | External interfaces, certificates, TURN |
| **C** | Internal | Talk to CUCM, IMP, directories |

Learners: draw this on paper before touching certs.

---

## 3) MRA registration path (simplified)

1. Client discovers edge via DNS (`_collab-edge._tls` SRV patterns — verify current docs)  
2. TLS to Expressway-E  
3. Auth / UDS / service discovery through C  
4. Device registers toward CUCM through the edge path  
5. Media negotiated with ICE/TURN as required  

### LICC for "Jabber/Webex app won't register from home"

| Letter | Example |
|:--:|--|
| **L** | DNS → E → C → CUCM |
| **I** | Client device name · Expressway session · CUCM registration attempt |
| **C** | Failed reg count · TLS errors · auth fail rate |
| **C** | Expressway diagnostic log · client problem report · CUCM SDL (lab only) |

---

## 4) Certificates (the real boss fight)

- Public cert on **E** with correct SANs  
- Internal trust between C and E  
- CUCM / tomcat / CallManager certs trusted by C where required  
- Expiry calendar — weekend outages love expired edge certs  

Drill: "Call works, directory lookup fails" often = **service discovery / cert / SSO**, not dial plan.

---

## 5) DNS is half of UC

Inventory every SRV/A record the client needs. Lab exercise:

1. List records  
2. Query from **internal** DNS and **public** DNS  
3. Capture mismatch as the ticket root cause  

---

## 6) Firewall ports (concept, not a paste dump)

Learn categories, not only numbers:

- Client → E signaling TLS  
- Media RTP/TURN ranges  
- Traversal between E and C  
- Admin interfaces restricted  

Always re-check **current** Cisco collaboration port reference for your version. Wrong port sheet version = silent fails.

---

## 7) Common failure patterns

1. Split-brain DNS  
2. Missing SAN on edge cert  
3. Expired cert  
4. SSO broken only externally  
5. CUCM CSS/partition OK on-prem, edge user different device pool  
6. Media one-way only on MRA (TURN missing)  
7. Cluster overload / too many registrations through undersized edge  
8. Geo DNS steering to wrong edge  

---

## 8) Cloud-edge evolution note (2026)

Many orgs move soft clients toward **cloud registration / Webex app** while keeping hybrid calling. The skill that survives:

> Follow identity → signaling → media → proof.

Whether the edge logo is Expressway or a cloud edge service, LICC still applies.

---

## 9) Lab safety

- Dedicated lab domain and certs  
- Never open production CUCM admin to 0.0.0.0/0  
- Redact FQDNs in shared notes  

**Artifact:** registration success screenshot + redacted Expressway status + DNS query output.

---

## 10) Teach-back

Draw C/E, name three cert trust relationships, and walk a failed remote registration with LICC in under two minutes.

**Educational only · MIT · pin official Cisco collab edge docs for production**
