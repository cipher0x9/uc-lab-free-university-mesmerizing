# UC Troubleshooting Playbook (UC-TROUBLESHOOTING-PLAYBOOK.md)
**Publisher/Brand:** CYPHER0X9 / UC Free University Campus  
**License:** MIT License  
**Deployment Model:** Offline-First Diagnostic Reference & Operational Playbook  
**Scope:** Unified Communications Troubleshooting, LICC Methodology, Packet Capture Analysis, CUBE Debugging, Root Cause Postmortems  

---

## Executive Diagnostic Framework: The LICC Methodology

Systematic troubleshooting of real-time voice and video networks requires a rigid diagnostic methodology to isolate failures across complex multi-tier topologies. The **LICC Methodology** provides a structured 4-stage operational protocol:

```
  +--------------------+     +--------------------+     +--------------------+     +--------------------+
  |  1. LOG ACQUISITION| --> |  2. ISOLATION      | --> |  3. CORRELATION    | --> |  4. CONFIRMATION   |
  |  (RTMT/PCAP/CUBE)  |     |  (Layer 1-7 Bounds)|     |  (Time/Call-ID/SDP)|     |  (LICC Proof Block)|
  +--------------------+     +--------------------+     +--------------------+     +--------------------+
```

1. **Log Acquisition:** Gather un-truncated, precise timestamped logs (Wireshark PCAPs, CUCM SDL traces, CUBE debugs, RTMT alerts) covering the exact failure window.
2. **Isolation:** Determine the operational layer (Physical, Network, Transport, SIP Signaling, SDP Negotiation, RTP Media Plane) and boundary (Client-to-CUCM, CUCM-to-CUBE, CUBE-to-ITSP).
3. **Correlation:** Match SIP Call-IDs across proxies, trace SDP IP/port declarations against firewall/RTP logs, and align timestamped events across multi-vendor nodes.
4. **Confirmation:** Execute targeted remediations and construct a verifiable **LICC Proof Block** empirical evidence log confirming resolution.

---

## 1. Common UC Failure Scenarios & Standard Protocols

### 1.1 One-Way or No-Way Audio
One-way or complete audio silence is almost exclusively a media plane (RTP/RTCP) or NAT/firewall traversal failure, rarely a SIP signaling issue.

```
Endpoint A (10.1.10.50) ---- SIP OK ---- CUBE (192.168.1.1) ---- SIP OK ---- ITSP Proxy
 Endpoint A  <======= Audio Stream Sent ======> CUBE
 Endpoint A  <------- NO AUDIO RETURN (Blocked by FW/NAT) ------ CUBE (192.168.1.1)
```

#### Diagnostic Decision Tree:
```
                                 [One-Way / No-Way Audio]
                                            |
                                            v
                             Does SIP 200 OK contain valid SDP?
                                      /           \
                                    No             Yes
                                   /                 \
                Inspect SIP Proxy/Transcoder      Inspect SDP Connection Address (c=)
                Check Codec Mismatch              and Media Port (m=)
                                                        |
                                                        v
                                       Is 'c=' IP reachable from endpoint?
                                                 /             \
                                               No               Yes
                                              /                   \
                               Fix Routing/NAT Traversal    Check Firewalls/ACLs blocking
                               Enable HNT / STUN / ICE       UDP ports 16384-32767
```

#### Root Causes & Actionable Commands:
* **Asymmetric Routing / Firewall Drop:** UDP ports 16384–32767 blocked between media endpoints.
* **NAT IP Leak in SDP:** SDP payload reports an internal RFC 1918 IP address (`c=IN IP4 10.1.10.50`) to an external ITSP.
* **MTP/Transcoder Failure:** No hardware/software Media Termination Point available for codec conversion (e.g., G.711 to G.729).

---

### 1.2 No Dial Tone / Immediate Busy Signal (Fast Busy)
Fast busy (reorder tone) indicates a call routing or signaling failure before media setup completes.

#### Common SIP Response Codes Mapped:
* **SIP 404 Not Found:** Unassigned extension or invalid dial pattern matching in CUCM/CUBE route pattern.
* **SIP 403 Forbidden:** Calling Search Space (CSS) lacks access to the partition containing the target pattern, or SIP trunk digest authentication failed.
* **SIP 503 Service Unavailable:** No active gateways/Trunks available in the Route List, or CUBE `max-calls` limit reached.
* **SIP 488 Not Acceptable Here:** Codec selection mismatch during SDP offer/answer exchange without transcoder resources.

---

### 1.3 Dead Air / Call Setup Freeze
Call stays in an `INVITE` state for 30–60 seconds before dropping without ringback audio.

* **Primary Cause:** SIP `180 Ringing` or `183 Session Progress` messages fail to traverse upstream due to missing `PRACK` (Provisional Response Acknowledgement - RFC 3262) support or blocked UDP 5060/5061 signaling packets.
* **Fix:** Enforce `rel100 require` or `rel100 supported` consistently on CUBE dial-peers.

---

### 1.4 Echo, Delay, & Jitter Issues
Voice quality degradation impacts user experience due to network transport flaws or inadequate acoustic processing.

| Quality Metric | Severity Threshold | Root Cause | Remediation Protocol |
| :--- | :--- | :--- | :--- |
| **One-Way Delay** | > 150 ms (ITU-T G.114) | Sub-optimal WAN routing, satellite links | Implement MPLS/SD-WAN prioritized queues |
| **Jitter** | > 30 ms | Unregulated bursty data traffic | Enforce Strict Priority (LLQ) queuing for Voice |
| **Packet Loss** | > 1.0% | Buffer bloat, interface drops, duplex mismatch | Clear interface errors, re-architect queue depth |
| **Hybrid/Acoustic Echo**| Tail length > 32 ms | Impedance mismatch on FXO/PSTN trunks or cheap speakerphones | Enable Hardware Echo Canceler (ECAN) on DSPs (`echo-cancel enable`) |

---

### 1.5 Dropped Calls at Exactly 15 or 30 Minutes
Calls reliably disconnect at exact, predictable duration intervals (e.g., 15 minutes, 30 minutes, 60 minutes).

#### Root Cause Analysis:
SIP Session Timers (RFC 4028) refresh the call state via periodic `re-INVITE` or `UPDATE` messages. If mid-call signaling fails due to stateful firewall UDP session timeouts (which default to 30 or 60 seconds), the refresh message is dropped. The endpoint that initiated the session timer waits for an ACK/200 OK; when unacknowledged, it terminates the session with a `BYE`.

```text
Endpoint A                               CUBE / SIP Proxy
    |                                           |
    |==== Active Call (Media Streaming RTP) ====|  (Elapsed: 15 Mins)
    |                                           |
    |--- SIP UPDATE / re-INVITE (Session Keepalive) --> [Firewall Drops Packet]
    |--- SIP UPDATE (Retry 1) ------------------------> [Firewall Drops Packet]
    |--- SIP UPDATE (Retry 2) ------------------------> [Firewall Drops Packet]
    |                                           |
    |*** Timer Expire (No 200 OK Received) *****|
    |--- SIP BYE (Call Terminated) ------------->|
```

* **Remediation:** Increase firewall UDP SIP session timeout to 86400 seconds or align SIP Session Refresh Interval (`min-se`) across CUBE and ITSP.

---

## 2. Advanced Packet Capture & Wireshark Diagnostics

### 2.1 Wireshark Display Filters for UC Diagnostics
Mastering Wireshark display filters is required for rapid root-cause isolation.

```wireshark
! Filter by SIP Call-ID (Traces a single end-to-end call across proxies)
sip.Call-ID == "84920184-38291-a-b-c@10.1.10.50"

! Filter SIP Error Responses (4xx, 5xx, 6xx)
sip.Status-Code >= 400

! Filter Specific RTP Stream by SSRC or Payload Type (G.711u = 0, G.729 = 18)
rtp.p_type == 0 || rtp.p_type == 18

! Identify Packet Drops & Out-of-Order Delivery in RTP Stream
rtp.sequence.nr && rtp.jitter > 30

! Filter ICMP Unreachable (Port Unreachable causing call drop/one-way audio)
icmp.type == 3 && icmp.code == 3
```

### 2.2 Wireshark Voice Call Flow & RTP Analysis Steps
1. Navigate to **Telephony -> VoIP Calls**.
2. Select target call session based on `From`, `To`, and `Start Time`.
3. Click **Flow Sequence** to visualize full SIP handshake (`INVITE`, `100 Trying`, `180 Ringing`, `200 OK`, `ACK`, `BYE`).
4. Select stream and click **Player / Stream Analysis** to calculate Jitter, Delta, Packet Loss percentage, and listen to decoded audio payload.

---

## 3. Real-Time Diagnostics: CUBE CLI & Cisco RTMT

### 3.1 Essential Cisco CUBE Debug Commands
> **WARNING:** Running un-filtered `debug voip ccapi inout` on high-volume production CUBE gateways will cause CPU saturation. Always apply targeted conditions!

```cisco
! Step 1: Apply Strict Debug Condition by Calling or Called Number
debug voip condition calling number 4401
debug voip condition called number 918005550199

! Step 2: Enable Targeted Signaling & Call Control Debugs
debug voip ccapi inout         ! Traces Call Control API (dial-peer matching & bridge legs)
debug ccsip messages           ! Captures full inbound/outbound SIP header text
debug ccsip states             ! Traces SIP state machine state transitions

! Step 3: View Real-Time Output safely
terminal monitor

! Step 4: CRITICAL - Disable Debugs immediately after test
undebug all
! OR
no debug voip condition 1
```

### 3.2 Cisco Real-Time Monitoring Tool (RTMT) Workflow
1. Launch RTMT and authenticate to CUCM Publisher.
2. Navigate to **Trace & Log Central -> Collect Traces**.
3. Select **Cisco CallManager** service logs across all cluster nodes.
4. Set relative timeframe (e.g., "Range: Last 30 minutes").
5. Process raw `.txt`/`.sdl` files through **Cisco CodeYellow / TranslatorX** to analyze call control signal flows.

---

## 4. Operational Incident Postmortem Templates & LICC Proof Blocks

Every resolved tier-3 UC incident MUST culminate in an empirical Postmortem Document featuring an immutable **LICC Proof Block**.

```markdown
# INCIDENT POSTMORTEM REPORT
**Incident Reference:** INC-2026-88392  
**Date/Time of Outage:** 2026-08-04 14:15:00 UTC  
**Impact:** 450 Contact Center Agents experienced one-way audio on inbound PSTN calls.  
**Root Cause:** Security team applied an unannounced ASA firewall rule dropping inbound UDP media ports 16384-32767 between DMZ CUBE and internal Media Resources.

---

### LICC PROOF BLOCK (Empirical Verification)

```text
==================================== LICC PROOF BLOCK ====================================
1. LOG ACQUISITION:
   - Wireshark Trace File: CUBE_WAN_Capture_20260804_1420.pcap
   - CUBE CLI Debug Output: ccsip_debug_20260804.txt

2. ISOLATION:
   - SIP Signaling: SUCCESS (INVITE/200 OK/ACK exchange completed cleanly)
   - Media Flow Analysis: 
     Endpoint A (CUBE 192.168.1.1:17002) --> Audio Sent to Agent (10.2.10.45:24000) [PASSED]
     Agent (10.2.10.45:24000) --> Audio Sent to CUBE [BLOCKED BY ASA FW RULE 104]

3. CORRELATION:
   - Wireshark RTP Analysis: SSRC 0x4A2B81FF shows 0 packets received at CUBE WAN side.
   - ASA Syslog Event: %ASA-4-106023: Deny udp src Inside:10.2.10.45/24000 dst Outside:192.168.1.1/17002 by access-group "DMZ-IN"

4. CONFIRMATION & REMEDIATION VERIFICATION:
   - Executed ASA Access-List Adjustment:
     'access-list DMZ-IN extended permit udp 10.2.0.0 0.0.255.255 192.168.1.0 0.0.0.255 range 16384 32767'
   - Post-Fix Wireshark Capture Test (Call-ID: 9940182-call-proof@cucm.corp):
     Total Packets Sent: 2450 | Lost Packets: 0 (0.0%) | Average Jitter: 2.1 ms
   - Audio Quality Verification: Bi-directional G.711u stream verified clean.
==========================================================================================
```
---

---
**License Notice:** Released under the MIT License. Copyright (c) CYPHER0X9 / UC Free University Campus. Free for commercial and academic reuse with attribution.
