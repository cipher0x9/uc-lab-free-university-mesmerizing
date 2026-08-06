# Media, Codecs & Transcoding

**CYPHER0X9 · UC Lab Free University · curriculum pack · MIT**  
**Spine:** signaling can succeed while media is garbage — prove both.

---

## 1) Signaling ≠ media

| Plane | Carries | Typical debug |
|-------|---------|---------------|
| Signaling | SIP / SCCP / HTTPS control | 4xx, auth, dial plan |
| Media | RTP / SRTP | one-way, choppy, no audio |

If 200 OK exists but no audio: **you are not done.**

---

## 2) Codec negotiation (SDP)

Learn to read SDP offers:

- `m=audio` lines  
- payload types  
- `a=rtpmap`  
- ptime  
- crypto lines for SRTP  

Common codecs (names to know): **G.711 μ/A**, **G.729**, **Opus**, **G.722**, video H.264/H.265 variants depending on stack.

---

## 3) Transcoding when and why

| Need | Cost |
|------|------|
| Interop between islands | DSP / cloud media resources |
| Bandwidth save | Complexity + delay |
| Recording systems demanding G.711 | Forced transcode |

Transcode adds **latency and failure modes**. Prefer end-to-end common codec when possible.

---

## 4) One-way audio map

1. NAT / private IP in SDP  
2. Firewall missing RTP range  
3. Asymmetric routing  
4. SRTP mismatch  
5. Mid-call re-INVITE breaks path  
6. Hairpin through dead media resource  

LICC the media leg separately from SIP leg.

---

## 5) QoS touchpoints

- Mark EF/AF appropriately at edge  
- Trust boundaries on WAN  
- Wi-Fi WMM  
- VPN double-encrypt tax  

See also: `QOS-AND-NETWORK-READINESS.md`

---

## 6) Metrics that matter

| Metric | Why |
|--------|-----|
| MOS / POLQA estimates | User pain |
| Packet loss / jitter / RTT | Root path |
| Concealment time | Codec stress |
| Transcoder utilization | Capacity |

---

## 7) Lab drill

Capture one G.711 call and one Opus/WebRTC-style call. Compare SDP and listen. Keep redacted pcap as Capture.

**Educational only · MIT**
