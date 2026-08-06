# UC Home Lab & Packet Proof

**CYPHER0X9 · UC Lab Free University · curriculum pack · MIT**  
**Goal:** build proof habits without a $2M data center.

---

## 1) Lab philosophy

| Principle | Practice |
|-----------|----------|
| Synthetic only | Fake numbers, fake customers |
| Isolated | Lab VLAN / cloud lab account |
| Reproducible | Notes + captures |
| Safe | No production trunks without change control |

---

## 2) Minimum viable UC lab options

1. **Packet-only lab** — Wireshark + sample PCAPs + SIP ladder drawing  
2. **Soft SBC / opensource SIP** (lab) + softphones  
3. **Vendor trial / dCloud-class environments** when available  
4. **CUCM lab** (hardware or nested virtualization where licensed/legal)  
5. **CCaaS free tiers** for flow design practice  

You can learn 70% of troubleshooting from **SIP ladders + LICC** before you own a cluster.

---

## 3) Essential tools

- Wireshark (SIP, RTP analysis)  
- `sngrep` (if Linux lab)  
- Softphones (X-Lite-class / Zoiper-class / vendor clients)  
- Certificate lab (mkcert / internal CA)  
- Git for lab notes (no secrets)  

---

## 4) Capture hygiene

1. Filter early (host/IP)  
2. Note Call-ID before you filter it away  
3. Redact before sharing  
4. Store with ticket ID + timestamp  

---

## 5) First 10 lab missions

1. Register two softphones  
2. Call A→B, capture SIP INVITE…BYE  
3. Force 404 and explain  
4. Force auth fail and explain  
5. One-way audio simulation (block RTP)  
6. Codec mismatch simulation  
7. TLS SIP vs UDP SIP compare  
8. Draw LICC for each  
9. Write a 5-line postmortem  
10. Teach a friend without showing passwords  

---

## 6) Bridge to career

Hiring managers light up when you say:

> "Here is a redacted SIP ladder and the counter that moved."

Not:

> "I watched a YouTube video about CUCM."

**Educational only · MIT · never expose production**
