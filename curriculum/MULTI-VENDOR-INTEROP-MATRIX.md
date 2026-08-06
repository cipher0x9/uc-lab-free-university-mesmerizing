# Multi-Vendor Interop Matrix

**CYPHER0X9 · UC Lab Free University · curriculum pack · MIT**  
Jobs hire **braids**, not single logos.

---

## 1) Why interop is the job

Enterprises combine:

- Cisco CUCM / Webex  
- Microsoft Teams Phone  
- Zoom Phone / others  
- CCaaS (Genesys, Connect, Five9, NICE, WxCC)  
- Carrier SIP  
- Recording / WFO  
- Identity (Entra / Okta / AD)  

Your value: **follow the call across brands**.

---

## 2) Interop seams (where tickets live)

| Seam | Typical pain |
|------|----------------|
| SBC ↔ PBX | Numbering, early media |
| PBX ↔ CCaaS | Transfer, REFER, headers |
| Teams ↔ CUCM | Dual-run dial plan |
| WebRTC ↔ SIP | ICE, codec, DTLS-SRTP |
| Recorder ↔ media | Fork, SIPREC |
| IdP ↔ clients | SSO loops |

---

## 3) Design rules that survive vendors

1. E.164 at boundaries  
2. Document who normalizes numbers  
3. One diagram for signaling, one for media  
4. Fail-soft routes  
5. LICC on every severity-1  
6. Dual-run metrics before cutover  

---

## 4) Interview gold

"Tell me about a multi-vendor outage you fixed" — answer with LICC, not brand loyalty.

---

## 5) Study path

1. SIP/SBC pack  
2. CUCM pack  
3. Teams Direct Routing pack  
4. CCaaS pack  
5. Recording pack  
6. Run a dual-run paper exercise  

**Educational only · MIT**
