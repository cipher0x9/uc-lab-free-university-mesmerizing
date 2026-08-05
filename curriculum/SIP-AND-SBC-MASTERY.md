# SIP and SBC Mastery — Protocol, CUBE, and Border Security

**Campus:** UC AI Free University · CYPHER0X9 / cipher0x9 · MIT  
**Axiom:** THE CALL MUST ALWAYS CONNECT  
**Scope:** SIP messages, SDP, codecs, call flows, NAT, SBC/CUBE, trunks, T.38, SRTP/TLS  
**Level:** Intermediate → Expert

---

## 0. Outcomes

1. Read a SIP dialog without fear (every header that matters).  
2. Map SDP media lines to real RTP ports and codecs.  
3. Configure Cisco CUBE as enterprise SBC for ITSP.  
4. Diagnose one-way audio, glare, PRACK, delayed vs early offer.  
5. Apply TLS/SRTP and still pass media.  
6. Handle fax T.38 and fallback.

---

## 1. SIP core model

### 1.1 Elements

| Element | Role |
|---------|------|
| UA (User Agent) | Phone, soft client |
| UAC / UAS | Client/server roles per transaction |
| Proxy | Routes requests; may not stay in media |
| Registrar | Binds AOR to Contact |
| Redirect | 3xx guidance |
| B2BUA | Two dialogs back-to-back (SBC/CUBE often) |
| SBC | Security, topology hiding, interop, policy |

### 1.2 Transactions vs dialogs

- **Transaction:** request + response(s) (INVITE transaction includes ACK for non-2xx differently than 2xx).  
- **Dialog:** peer-to-peer relationship (Call-ID + tags) lasting until BYE.  
- **Session:** media plane described by SDP.

### 1.3 Methods you must know

| Method | Use |
|--------|-----|
| INVITE | Establish session |
| ACK | Confirm final response to INVITE |
| BYE | Tear down |
| CANCEL | Cancel pending INVITE |
| REGISTER | Bind Contact |
| OPTIONS | Ping / capability |
| REFER | Transfer |
| UPDATE | Modify session without offer/answer full re-INVITE in some cases |
| PRACK | Provisional reliable ACK (100rel) |
| INFO | Mid-call info (DTMF legacy, etc.) |
| MESSAGE | Pager-mode IM |
| SUBSCRIBE/NOTIFY | Events (MWI, dialog, presence) |
| PUBLISH | Event state publish |

---

## 2. Critical headers

```
Via:          path of request; branch transaction id
From / To:    logical parties; tags define dialog
Call-ID:      dialog identifier component
CSeq:         order methods
Contact:      direct target URI
Max-Forwards: loop hop count
Content-Type: application/sdp
Content-Length:
Allow:        methods supported
Supported / Require:  extensions (100rel, replaces, timer)
Route / Record-Route: proxy sticky path
Authorization / Proxy-Authorization: digest
P-Asserted-Identity / Remote-Party-ID: trusted identity
Diversion / History-Info: diversion
Session-Expires / Min-SE: session timers
```

**Call-ID + From-tag + To-tag = dialog id.**

---

## 3. SDP essentials

```
v=0
o=- 123 456 IN IP4 10.1.1.10
s=-
c=IN IP4 10.1.1.10
t=0 0
m=audio 16384 RTP/AVP 0 101
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=ptime:20
a=sendrecv
```

| Line | Meaning |
|------|---------|
| `c=` | Connection IP for media |
| `m=` | Media type, port, proto, payload types |
| `a=rtpmap` | Codec map |
| `a=sendrecv/sendonly/recvonly/inactive` | Direction |
| `a=candidate` | ICE (WebRTC) |
| `a=crypto` / `a=fingerprint` | SDES SRTP / DTLS-SRTP |

### 3.1 Offer/Answer (RFC 3264)

- One side offers SDP; the other answers.  
- **Early offer:** SDP in INVITE.  
- **Delayed offer:** INVITE without SDP; offer in 200 OK; answer in ACK.  
- ITSPs often demand early offer → CUBE `early-offer forced` or CUCM MTP.

---

## 4. Codecs

| Codec | Rate | Notes |
|-------|------|-------|
| G.711 μ-law (PCMU) | 64 kbps + overhead | NANP default, fax pass-through |
| G.711 A-law (PCMA) | 64 kbps | Common international |
| G.729 | ~8 kbps | WAN classic; licensing legacy |
| G.722 | WB 64 | HD audio |
| Opus | Variable | WebRTC / modern |
| iLBC / AMR-WB | Varies | Mobile/WebRTC |

**DTMF:** RFC 4733 / 2833 `telephone-event` preferred over SIP INFO or in-band.

---

## 5. Canonical call flows

### 5.1 Successful INVITE (early offer)

```
UAC                Proxy/B2BUA              UAS
 |---- INVITE sdp --->|---- INVITE sdp ---->|
 |<--- 100 Trying ----|                     |
 |                    |<--- 180 Ringing ----|
 |<--- 180 Ringing ---|                     |
 |                    |<--- 200 OK sdp -----|
 |<--- 200 OK sdp ----|                     |
 |---- ACK ---------->|---- ACK ----------->|
 |<<<<<<<< RTP >>>>>>>>>>>>>>>>>>>>>>>>>>>>>|
 |---- BYE ---------->|---- BYE ----------->|
 |<--- 200 OK --------|                     |
```

### 5.2 REGISTER

```
REGISTER sip:realm SIP/2.0
To: sip:user@realm
From: sip:user@realm;tag=...
Contact: <sip:user@ip:port>;expires=3600

401 Unauthorized + WWW-Authenticate
REGISTER + Authorization
200 OK Contact expires
```

### 5.3 REFER transfer (blind)

```
REFER with Refer-To: sip:target
202 Accepted
NOTIFY refer events (100 trying / 200 ok)
BYE original sometimes depending on replaces/attended flow
```

---

## 6. Response code map (ops)

| Code | Meaning | Ops action |
|------|---------|------------|
| 100 | Trying | Normal |
| 180 | Ringing | Normal |
| 183 | Session Progress | Early media |
| 200 | OK | Connected signaling |
| 401/407 | Auth required | Credentials |
| 403 | Forbidden | Policy/CSS/ITSP | 
| 404 | Not found | Numbering |
| 408 | Timeout | Network/UA dead |
| 480 | Temporarily unavailable | Offline |
| 486 | Busy | Busy |
| 487 | Request terminated | CANCEL |
| 488 | Not acceptable here | Codec/SDP |
| 500/503 | Server/service unavailable | Capacity/maintenance |
| 603 | Decline | User reject |

---

## 7. NAT traversal

### 7.1 Problems

- Private `c=` lines unroutable on internet.  
- Symmetric RTP expectations.  
- SIP ALG on consumer routers corrupts headers (disable ALG).

### 7.2 Tools

| Tool | Role |
|------|------|
| SBC media latching | Learn real src IP/port from first packet |
| STUN/TURN/ICE | WebRTC clients |
| far-end NAT traversal on CUBE | Enterprise |
| TLS + correct Contact rewrite | Signaling |

**One-way audio classic:** signaling OK, RTP to wrong address — capture both sides.

---

## 8. SBC roles

1. **Topology hiding** — internal IPs never leak.  
2. **Security** — allowlist, rate limit, malformed drop.  
3. **Interop** — header fixups, SDP cleanup.  
4. **Policy** — codec filter, max call, fraud.  
5. **Media** — relay, transcode (if licensed/DSP), recording fork.  
6. **Registration** — on-behalf-of ITSP registration.  
7. **Encryption demarc** — TLS/SRTP outside, optionally inside.

---

## 9. Cisco CUBE configuration core

### 9.1 Baseline

```ios
voice service voip
 ip address trusted list
  ipv4 203.0.113.0 255.255.255.0
 allow-connections sip to sip
 no supplementary-service sip refer
 supplementary-service media-renegotiate
 sip
  bind control source-interface Loopback0
  bind media source-interface Loopback0
  early-offer forced
  midcall-signaling passthru
  assert header
!
voice class codec 1
 codec preference 1 g711ulaw
 codec preference 2 g729r8
!
voice class sip-profiles 10
 ! header manipulations as needed
!
dial-peer voice 100 voip
 description TO-CUCM
 session protocol sipv2
 destination-pattern 5...$
 session target ipv4:10.10.10.10
 voice-class codec 1
 dtmf-relay rtp-nte
 no vad
!
dial-peer voice 200 voip
 description TO-ITSP
 destination-pattern .T
 session protocol sipv2
 session target ipv4:203.0.113.50
 voice-class codec 1
 dtmf-relay rtp-nte
 no vad
```

### 9.2 Useful show/debug

```ios
show call active voice compact
show voip rtp connections
show dial-peer voice summary
show sip-ua status
show sip-ua connections tcp tls detail
debug ccsip messages
debug voip ccapi inout
debug voip rtp session named-event
```

**Lab safety:** debug with ACL filter; never full debug on loaded production without TAC discipline.

### 9.3 BIND interfaces

Inconsistent bind → one-way audio / OPTIONS fails. Use loopback + routing for multi-homed CUBE.

---

## 10. SIP trunking patterns

### 10.1 CUCM ↔ CUBE ↔ ITSP

- CUCM SIP trunk to CUBE inside address.  
- CUBE dial-peers match on URI or destination-pattern.  
- OPTIONS ping for keepalive.  
- Number normalization E.164.  
- Diversion for CFWD offnet.  
- Identity headers for STIR/SHAKEN where provider supports.

### 10.2 Registration-based ITSP

```ios
sip-ua
 credentials username USER password 0 PASS realm provider.com
 authentication username USER password 0 PASS
 registrar dns:sip.provider.com expires 3600
```

### 10.3 Multi-CUBE HA

- Active/active dial-peers preference.  
- CUBEs + VIP (sometimes) or DNS SRV.  
- CUCM route group circular.  
- Shared nothing media; state not clustered like CUCM DB.

---

## 11. Fax over IP

| Mode | Mechanism | Notes |
|------|-----------|-------|
| Pass-through | G.711 clear channel | Sensitive to jitter |
| T.38 | UDPTL fax relay | Preferred enterprise |
| NSE-based | Cisco legacy | Interop limited |

Design:

- Disable VAD/echo cancel issues carefully on fax dial-peers.  
- Detect fax tone → switch to T.38 (`fax protocol t38`).  
- Fallback to pass-through if T.38 fails.  
- Test every ITSP — fax is still where trunks go to die.

```ios
dial-peer voice 300 voip
 fax protocol t38 version 0 ls-redundancy 2 hs-redundancy 0 fallback pass-through g711ulaw
```

---

## 12. Security: TLS and SRTP

### 12.1 Signaling TLS

- Port 5061 typical.  
- Certificates: CUCM Tomcat/CallManager certs, CUBE trustpoint.  
- Mutual TLS optional with ITSPs.

### 12.2 Media SRTP

- SDES (`a=crypto`) common in enterprise SIP.  
- DTLS-SRTP in WebRTC.  
- **Mixed mode:** some legs encrypted some not → SBC terminates and re-encrypts.

### 12.3 Digest auth

```
WWW-Authenticate: Digest realm="x", nonce="...", algorithm=MD5
Authorization: Digest username="...", response="..."
```

Prefer TLS + digest or mTLS over raw UDP open world.

---

## 13. Interop landmines

1. **Early vs delayed offer**  
2. **PRACK required** mismatch  
3. **Session timers** (422 Session Interval Too Small)  
4. **REFER vs re-INVITE transfer**  
5. **Codec reorder / telephone-event missing**  
6. **Privacy id vs PAI stripping**  
7. **Media inactive on HOLD** vs sendonly + MOH  
8. **DNS NAPTR/SRV** order  
9. **SIP ALG**  
10. **MTU / TCP fallback** for large SDP

---

## 14. Packet reading checklist (Wireshark)

1. Filter `sip || rtp`  
2. Find INVITE Call-ID; Follow SIP Stream  
3. Note Offer SDP `c=` and `m=` ports  
4. Confirm answer direction  
5. RTP stream analysis: jitter, loss, delta  
6. DTMF events as RTP dynamic PT  
7. BYE who hung up  
8. Compare to CUBE `show voip rtp connections`

---

## 15. LICC proof for SIP

```
Leg:     Phone → CUCM → CUBE → ITSP
ID:      Call-ID: a1b2@10.1.1.10
         From-tag / To-tag
Counter: reINVITE #2 for HOLD
Capture: SPAN phone VLAN + outside CUBE
Assert:  200 OK has G.711; RTP both directions > 50 packets
```

---

## 16. Practice scenarios

1. Force delayed offer phone vs early offer ITSP — insert MTP/CUBE EO.  
2. Strip G.729 from one side — observe 488.  
3. Wrong bind interface — induce one-way audio; fix.  
4. Enable TLS trunk; break trust anchor; fix.  
5. Fax call with VAD on — fail; correct dial-peer.  
6. OPTIONS ping fail — route group failover.

---

## 17. Self-check questions

1. Difference between 180 and 183?  
2. When is ACK part of INVITE transaction?  
3. Why does delayed offer break some ITSPs?  
4. What header carries mid-dialog target refresh?  
5. SDES vs DTLS-SRTP?  
6. How does a B2BUA differ from a proxy for Call-ID?  
7. What is glare and how do UAs resolve?  

---

## 18. Quick command card (CUBE)

```
show call active voice brief
show voip rtp connections
show sip-ua calls
clear call voice causecode 16
set sip-ua timer ...
```

---

**Brand:** CYPHER0X9 · cipher0x9 · MIT · THE CALL MUST ALWAYS CONNECT  
**End of SIP-AND-SBC-MASTERY.md**
