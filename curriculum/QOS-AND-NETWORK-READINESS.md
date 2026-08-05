# QoS and Network Readiness — Voice-Grade Fabric

**Campus:** UC AI Free University · CYPHER0X9 / cipher0x9 · MIT  
**Axiom:** THE CALL MUST ALWAYS CONNECT  
**Scope:** QoS models, DSCP/CoS, trust, LLQ, police/shape, budgets, PoE, wireless voice, SD-WAN  
**Level:** Network + UC joint design

---

## 0. Outcomes

1. State latency/jitter/loss budgets and defend them.  
2. Design trust boundaries and DSCP end-to-end.  
3. Configure LLQ + optional scavenger for UC.  
4. Run a network readiness assessment before phone rollout.  
5. Specify PoE and switch features for endpoints.  
6. Qualify Wi-Fi 6/7 for voice and SD-WAN for multi-site.

---

## 1. Why voice dies on “perfectly fine” data networks

Voice is **real-time, inelastic, low-rate, bi-directional**. A network that passes Speedtest can still:

- Bufferbloat → jitter → robotic audio  
- Bursty loss → dropouts  
- Asymmetric routing → one-way audio  
- Priority inversion → MOH freeze under backup storms  
- CAPWAP overload → wireless RONA  

**UC quality is a path property, not a server property.**

---

## 2. Impairment budgets (design targets)

| Metric | Target (G.711 enterprise) | Stretch / notes |
|--------|---------------------------|-----------------|
| Mouth-to-ear latency | ≤ 150 ms one-way preferred | Up to ~200 ms still usable; >300 ms poor |
| Jitter | ≤ 20–30 ms | Jitter buffers hide some |
| Packet loss | ≤ 0.5–1% | G.729 more fragile than G.711 |
| Consecutive loss | Avoid bursts | PLC helps limited gaps |
| MOS (est.) | ≥ 4.0 | Context-dependent |

Video and content share different classes; do not put 4K share in EF.

### 2.1 Latency budget breakdown (example 150 ms)

| Segment | Budget |
|---------|--------|
| Encoding + packetization | 20–40 ms |
| Endpoint jitter buffer | 20–60 ms |
| LAN access | 1–5 ms |
| WAN | variable — design constraint |
| Decoding | 10–20 ms |
| Serialization (slow links) | care on low-bps |

---

## 3. QoS models

### 3.1 Best Effort

No differentiation — unacceptable for multi-service campus WAN.

### 3.2 IntServ (RSVP)

Per-flow reservation — rare as campus default; sometimes WAN overlays.

### 3.3 DiffServ (dominant)

Classify → mark → queue → drop schedule at each hop. **Per-hop behavior (PHB)** consistency is the game.

### 3.4 Cisco QoS strategy (practical 4/5-class)

| Class | DSCP | Use |
|-------|------|-----|
| Voice bearer | EF (46) | RTP audio |
| Video interactive | AF41 / CS4 | Realtime video |
| Call signaling | CS3 (24) | SIP/SCCP (note historical CS3 vs AF31 debates — **standardize and document**) |
| Critical data | AF21/AF22 | Business apps |
| Best effort | DF (0) | Default |
| Scavenger | CS1 | Bulk backup |

**Mark media EF; mark signaling CS3 (or your standard); never trust endpoint blindly at WAN edge without policy.**

---

## 4. CoS / DSCP mapping

### 4.1 L2 CoS (802.1p) on trunks

| CoS | Typical map |
|-----|-------------|
| 5 | Voice (EF) |
| 4 | Video |
| 3 | Signaling |
| 0 | BE |

### 4.2 Switch trust

```ios
! Access edge example (conceptual)
interface GigabitEthernet1/0/10
 description IP-Phone
 switchport mode access
 switchport voice vlan 20
 auto qos voip cisco-phone
 spanning-tree portfast
 power inline auto
```

Trust **phone** (CDP/LLDP detected) not free PC port.

### 4.3 Mapping tables

Ensure:

- Access switch sets DSCP  
- Distribution preserves  
- WAN router does not recolor EF → BE  
- Wireless controller marks CAPWAP outer carefully; inner DSCP copy policies matter  

---

## 5. Trust boundaries

```
[Softphone on BYOD] --untrusted--> [Access policy]
[Hard phone] --conditional trust--> [Access]
[CUCM server farm] --trusted DC--> 
[CUBE facing ITSP] --re-mark per contract-->
```

**Rules:**

1. Define where marks become trusted.  
2. Police excess EF to prevent voice queue DoS.  
3. Softphones: use 802.1X + dynamic VLAN + optional AVC, or accept best-effort with SD-WAN SLA policies.

---

## 6. Queuing: LLQ and friends

### 6.1 LLQ (Low Latency Queuing)

Priority queue for EF with **conditional priority** + bandwidth remaining for other classes.

```ios
class-map match-any VOICE
 match dscp ef
class-map match-any SIGNAL
 match dscp cs3
class-map match-any VIDEO
 match dscp af41
!
policy-map WAN-EDGE
 class VOICE
  priority percent 15
 class VIDEO
  bandwidth percent 20
 class SIGNAL
  bandwidth percent 5
 class class-default
  fair-queue
  random-detect
!
interface Tunnel100
 service-policy output WAN-EDGE
```

### 6.2 Policing vs shaping

| Tool | Behavior | Use |
|------|----------|-----|
| Police | Drop/remark excess | Ingress security, EF cap |
| Shape | Buffer and smooth | Parent shaper to subrate WAN |

**VoIP tip:** Shape parent to CIR; LLQ child inside. Avoid deep buffers before priority class.

### 6.3 WRED

Use on data classes, not on EF priority queue.

---

## 7. Admission control linkage

QoS ≠ infinite priority. Couple with:

- **CUCM Locations CAC**  
- **RSVP-enabled locations** (if used)  
- **Wireless CAC / SIP CAC**  
- **SD-WAN app-aware SLA** (brownout detect)

Otherwise EF overload collapses the priority class.

---

## 8. Network readiness assessment (NRA)

### 8.1 Phases

1. **Discovery** — topology, WAN bandwidth, oversubscription, wireless, PoE inventory.  
2. **Baseline** — latency/jitter/loss via IP SLA / TWAMP / ThousandEyes-class tools / iPerf controlled.  
3. **QoS gap** — marks present? trusted? LLQ configured?  
4. **Pilot** — one floor, MOS samples, call stats.  
5. **Remediate** — buffers, circuits, QoS, DHCP, DNS, NTP.  
6. **Sign-off** — written readiness with residual risks.

### 8.2 Checklist (minimum)

- [ ] Separate voice VLAN; DHCP option 150/66 correct  
- [ ] NTP consistent across phones/CUCM/CUBE  
- [ ] DNS for SRV if used  
- [ ] CDP/LLDP-MED voice VLAN assignment  
- [ ] PoE budget N+1 for peak phone boot  
- [ ] WAN LLQ + shaper  
- [ ] Firewall allows SIP/RTP ports intentionally (preferably via SBC only)  
- [ ] SPAN/ERSPAN available for troubleshooting  
- [ ] MTU / TCP MSS path for TLS SIP  
- [ ] Asymmetric routes documented  

### 8.3 IP SLA sample (IOS conceptual)

```ios
ip sla 10
 udp-jitter 10.10.20.1 16384 codec g711ulaw
ip sla schedule 10 life forever start-time now
```

---

## 9. Switching features for UC

| Feature | Why |
|---------|-----|
| Voice VLAN | Separate broadcast/QoS |
| Portfast / edge | Fast phone boot |
| BPDU Guard | Stop loops from desk |
| Storm control | Protect |
| IPv4 DHCP snooping / DAI | Security |
| Port security | Optional sticky |
| EEE care | Some endpoints dislike aggressive EEE |
| Multicast for MOH | Sparse-mode design if multicast MOH |

---

## 10. PoE engineering

### 10.1 Classes

| Standard | Power | Devices |
|----------|-------|---------|
| 802.3af | ~15 W | Basic phones |
| 802.3at | ~30 W | Advanced phones, some APs |
| 802.3bt | 60–90 W | Wi-Fi 6/7 APs, video |

### 10.2 Practices

- Budget **boot surge** not just steady state.  
- Watch stack power / PSU redundancy.  
- LLDP power negotiation vs CDP.  
- Soft fail: phone resets under brownout → mass re-registration events.

---

## 11. Wireless voice (Wi-Fi 6 / 7)

### 11.1 RF prerequisites

- -67 dBm or better coverage for voice in all work areas  
- SNR ≥ 25 dB preferred  
- Channel plan 5/6 GHz preference; avoid 2.4 for primary voice  
- Roaming: 802.11k/v/r carefully validated with vendor phones  
- Voice QoS: WMM UP marking; Platinum/Platinum-like WLAN profiles  

### 11.2 Capacity

- Concurrent calls per AP limits (design, not marketing).  
- Multicast to unicast conversion for some MOH scenarios.  
- Sticky client problems — tune roaming aggressiveness.

### 11.3 Wi-Fi 6/7 notes

- OFDMA helps dense deployments.  
- Multi-link operation (Wi-Fi 7) future soft clients.  
- Still: **QoS + RF + roaming** dominate over generation marketing.

### 11.4 Test calls

Walk test with continuous call; log roaming events; measure RONA for wireless agents.

---

## 12. WAN and SD-WAN for voice

### 12.1 Circuit sizing (rough)

```
Per G.711 call ≈ 80–100 kbps with Ethernet overhead (design ~100 kbps)
Per G.729 call ≈ 30–40 kbps
N concurrent × codec × headroom (20–30%) + signaling + video
```

### 12.2 SD-WAN policies

- App map SIP + RTP (or DSCP-based)  
- SLA: latency/jitter/loss thresholds → path switch  
- Avoid mid-call path flap flapping — dampen  
- FEC / packet replication for premium voice paths (vendor feature)  
- Local breakout for SaaS Webex; careful with on-prem CUCM hairpin  

### 12.3 Brownout vs blackout

Blackout easy (path down). Brownout (high loss) kills MOS without down state — need SLA probing.

---

## 13. Data center and server farm

- CUCM/IM&P/Unity/Finesse in trusted QoS zone.  
- No deep packet buffer “storage” switches delaying East-West RTP for media servers.  
- vSwitch port groups: trust DSCP, disable noise features.  
- Snapshot/backup traffic classified scavenger.

---

## 14. Firewall / NAT interaction

Prefer:

```
Phones (private) → CUCM (private)
CUBE (DMZ/edge) → ITSP (public)
RTP through CUBE when crossing NAT
```

If firewall must pass RTP:

- Open UDP ranges deliberately  
- Disable SIP ALG  
- Watch pinholes for bidirectional media  

---

## 15. Measurement and assurance

| Tool | Use |
|------|-----|
| RTCP XR / phone statistics | Endpoint view |
| CUCM CDR/CMR | Cluster MOS/jitter |
| CUBE DSP/RTP stats | Edge |
| Wireshark RTP stream analysis | Ground truth |
| IP SLA / TWAMP | Path continuous |
| Wireless packet capture | Air issues |

CMR fields: jitter, latency, loss — trend them; don’t wait for tickets.

---

## 16. Failure modes ↔ QoS

| Symptom | Network cause |
|---------|----------------|
| Robotic audio | Loss / codec stress |
| Slow talk / underwater | Jitter buffer, clock |
| One-way | NAT/routing/ACL not QoS |
| Gaps under load | Missing LLQ / oversub EF |
| Wireless drop on roam | RF/roaming |
| Boot storms fail reg | PoE / DHCP / STP |

---

## 17. Lab exercises

1. Without QoS: flood WAN with iperf; measure MOS; enable LLQ; re-measure.  
2. Remark EF to BE mid-path; observe.  
3. Police EF at 5%; add calls until drops.  
4. Wireless walk test heatmap vs call quality.  
5. SD-WAN brownout simulation if lab allows.

---

## 18. Readiness report template

```
Site:
Circuit CIR / burst:
Max concurrent voice:
Codec plan:
QoS policy version:
Trust boundary diagram: attached
Baseline p95 latency/jitter/loss:
PoE headroom %:
Wireless voice SSID:
Open risks:
Sign-off:
```

---

## 19. Self-check

1. Why police EF?  
2. Difference shape vs police for subrate?  
3. Voice VLAN without QoS — enough?  
4. What is brownout?  
5. Why is signaling not EF?  
6. How does CAC interact with LLQ?  

---

## 20. Quick DSCP reference

| Name | Decimal | Binary |
|------|---------|--------|
| EF | 46 | 101110 |
| CS3 | 24 | 011000 |
| AF41 | 34 | 100010 |
| CS1 | 8 | 001000 |
| DF | 0 | 000000 |

---

**Brand:** CYPHER0X9 · cipher0x9 · MIT · THE CALL MUST ALWAYS CONNECT  
**End of QOS-AND-NETWORK-READINESS.md**
