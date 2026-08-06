# CUBE Dial-Peer Lab (Educational)

**CYPHER0X9 · UC Lab Free University · curriculum pack · MIT**  
**Note:** Examples are **synthetic lab patterns**, not production configs.

---

## 1) CUBE role

CUBE is the **policy + interop + security edge** for many Cisco voice designs:

- SIP trunk to ITSP  
- Interop with CUCM  
- Header manipulation  
- CAC / security  
- Media flow control  

---

## 2) Dial-peer mental model

| Concept | Meaning |
|---------|---------|
| Incoming dial-peer | How call is classified arriving |
| Outgoing dial-peer | Where call is sent |
| Preference / priority | Selection order |
| Destination-pattern | Match logic |
| Session target | Next hop |
| Voice class URI / codecs / tenants | Policy packs |

---

## 3) Lab story (fictional numbers)

```text
ITSP  ↔  CUBE  ↔  CUCM
+1555000XXXX     extensions 1XXX
```

Goals:

1. Inbound DID → CUCM  
2. Outbound +E.164 → ITSP  
3. Emergency special route  
4. Reject toll-fraud patterns  

---

## 4) Debug order

1. `show dial-peer voice summary` (concept)  
2. Debug/ccapi / sip messages in lab only  
3. Confirm matched peer  
4. Confirm SIP response  
5. Confirm media  

LICC every time.

---

## 5) Safety

- No real carrier credentials in notes  
- No public paste of production running-config  
- Lab VRF / lab interface only  

**Educational only · MIT · pin Cisco CUBE configuration guides for real builds**
