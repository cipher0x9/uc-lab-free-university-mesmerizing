# Presence, IM & Collaboration Clients

**CYPHER0X9 · UC Lab Free University · curriculum pack · MIT**

Voice is only one plane. Users live in **presence + messaging + meetings + calling**.

---

## 1) Stack map

| Capability | On-prem classic | Cloud modern |
|------------|-----------------|--------------|
| Presence / IM | Cisco IM&P + Jabber | Teams / Webex app |
| Softphone | Jabber / IP Communicator | Teams / Webex Calling app |
| Meetings | CMS / Webex | Teams / Webex Meetings |
| Voicemail MWI | CUC | Cloud VM visual |

---

## 2) Presence truth table

Presence is a distributed system:

- Client publish  
- Server aggregation  
- Calendar / DND / call state injection  
- Federation delays  

Ticket: "shows available but on a call" → which publisher lost the race?

---

## 3) Soft client failure classes

1. Auth / SSO  
2. Service discovery  
3. Config / device CSF  
4. Media devices (mic/speaker permissions)  
5. Network (proxy, VPN, captive portal)  
6. Version skew  

---

## 4) LICC for "can't chat / can't call from soft client"

Separate **IM leg** from **call leg**. Different servers, different logs, same angry user.

---

## 5) Migration note

Moving Jabber → Webex app or Teams is an **identity + habit + dial plan** migration, not only an MSI push.

**Educational only · MIT**
