# Enterprise E911 & NG911 Architecture Specification
**Document ID:** CYPHER0X9-E911-NG911-SPEC  
**Author:** CYPHER0X9 Security & Network Engineering  
**License:** MIT License  

---

## 1. Executive Summary & Regulatory Framework

Enterprise emergency calling compliance requires strict adherence to U.S. federal mandates (Kari's Law and RAY BAUM's Act) alongside Next Generation 911 (NG911) standards defined by NENA (National Emergency Number Association).

### 1.1 Regulatory Compliance Matrix

| Regulation | Scope / Requirement | Technical Mandate | Enforcement Date |
| :--- | :--- | :--- | :--- |
| **Kari's Law** | Direct 911 Dialing | Elimination of prefix digits (e.g., `9911` $\rightarrow$ `911`). | Feb 16, 2020 |
| **Kari's Law** | On-Site Notification | Real-time alert to security desk via Email, SMS, or Webhook. | Feb 16, 2020 |
| **RAY BAUM's Act Sec. 506** | Dispatchable Location (Fixed) | Building name, floor, room number, or suite identifier. | Jan 6, 2021 |
| **RAY BAUM's Act Sec. 506** | Dispatchable Location (Non-Fixed) | Dynamic location tracking for softphones, Wi-Fi, and VPN. | Jan 6, 2022 |

---

## 2. Legacy E911 vs. Next Generation 911 (NG911)

### 2.1 Architecture Comparison

| Feature / Component | Legacy E911 Architecture | NG911 (NENA i3 Standard) |
| :--- | :--- | :--- |
| **Trunking Protocol** | T1/E1 CAMA (Central Office Trunk) | SIP / IMS IPv6 Core |
| **Caller Identity** | ANI (Automatic Number Identification) | SIP `P-Asserted-Identity`, `From` Header |
| **Location Data** | ALI (Automatic Location Identification) DB | PIDF-LO (Presence Information Data Format Location Object) |
| **Routing Mechanism** | Selective Router (SR) via Shell Records | ECRF (Emergency Call Routing Function) via GIS |
| **Data Format** | Fixed 512-byte ERL ASCII / MSAG | XML-encoded GML (Geography Markup Language) |
| **Media Types** | Voice (In-band TTY/TDD) | Voice, Video, Text (RTT), Telemetry Data |

---

## 3. Location Infrastructure & Tracking Methods

### 3.1 Location Identification Protocols

```
┌─────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│  IP Phone / PC  │───────>│ Cisco Expressway │───────>│ CUCM / Cisco Emergency │
│  (LLDP-MED/HELD)│        │   or SBC / VPN   │        │     Responder    │
└─────────────────┘        └──────────────────┘        └──────────────────┘
         │                                                       │
         ▼                                                       ▼
┌─────────────────┐                                    ┌──────────────────┐
│ Network Switch  │                                    │ E911 Service Provider │
│ (Port/Subnet/AP)│                                    │ (RedSky / Intrado) │
└─────────────────┘                                    └──────────────────┘
```

#### Location Discovery Protocols
1. **LLDP-MED (ANSI/TIA-1057):** Switches broadcast `Location Identification TLV` (ELIN or Civic Address) directly to IP endpoints during DHCP handshake.
2. **HELD (HTTP Enabled Location Delivery - RFC 5985):** Softphones query LIS (Location Information Server) over HTTPS to retrieve current URI/PIDF-LO.
3. **Cisco Discovery Protocol (CDP):** CUCM/CER queries switch stacks via SNMP to bind IP/MAC addresses to switch ports and Emergency Response Locations (ERLs).

### 3.2 Dispatchable Location Data Schema (PIDF-LO XML Example)

```xml
<presence xmlns="urn:ietf:params:xml:ns:pidf"
          entity="pres:911-endpoint@corp.internal">
  <tuple id="loc-data">
    <status>
      <geopriv xmlns="urn:ietf:params:xml:ns:pidf:geopriv10">
        <location-info>
          <civicAddress xmlns="urn:ietf:params:xml:ns:pidf:geopriv10:civicAddr">
            <country>US</country>
            <A1>NY</A1>
            <A3>New York</A3>
            <RD>5th Ave</RD>
            <HNO>350</HNO>
            <FL>42</FL>
            <LOC>Suite 4201 / Desk 42-B</LOC>
            <PC>10118</PC>
          </civicAddress>
        </location-info>
        <usage-rules>
          <retransmission-allowed>false</retransmission-allowed>
        </usage-rules>
      </geopriv>
    </status>
  </tuple>
</presence>
```

---

## 4. RedSky (Everbridge) & E911 Provider Integration

### 4.1 SIP Trunking Integration Architecture

RedSky E911 Cloud Services (E911 Anywhere / Horizon) interface with Enterprise SBCs via SIP RFC 3261 & RFC 6442.

#### RedSky Call Flow Sequence
1. Endpoint dials `911`.
2. CUCM routes call to local SBC or Cisco Emergency Responder (CER).
3. CER updates SIP invite with `PIDF-LO` XML body or injects ELIN in `From:` / `Remote-Party-ID:`.
4. SBC forwards call via TLS/SRTP to RedSky Emergency Routing Service (ERS).
5. RedSky ECRF resolves location $\rightarrow$ routes call to correct PSAP over ESInet.

```
Endpoint (911) ──> CUCM/CER ──> Enterprise SBC ──(SIP+PIDF-LO/TLS)──> RedSky ERS ──> ESInet ──> PSAP
```

### 4.2 RedSky ERL & ELIN Configuration Table

| ERL Name | Subnet Range / BSSID | Assigned ELIN (Caller ID) | Civic Location Description |
| :--- | :--- | :--- | :--- |
| `NYC-HQ-FL01` | `10.100.1.0/24` | `+12125550101` | 350 5th Ave, Floor 1 |
| `NYC-HQ-FL02` | `10.100.2.0/24` | `+12125550102` | 350 5th Ave, Floor 2 |
| `WIFI-BLDG-A` | `BSSID 00:11:22:33:44:XX` | `+12125550199` | 350 5th Ave, Atrium Wi-Fi |
| `REMOTE-VPN` | `172.16.50.0/23` (HELD Server Prompt) | Dynamic PIDF-LO | Softphone Teleworker |

---

## 5. Cisco Unified Communications Manager (CUCM) & CER Configuration

### 5.1 CUCM Emergency Call Routing Logic

```
Dial Sequence: "911"
 ├── Pattern Pattern: 911 (Emergency Call Handler)
 ├── Route Partition: P_Emergency
 ├── Calling Search Space: CSS_Endpoints
 └── Route List: RL_Emergency
      ├── Route Group 1: RG_CER (Primary -> Cisco Emergency Responder)
      └── Route Group 2: RG_PSTN_Failover (Secondary -> Local Gateway CAMA/PRI/SIP)
```

### 5.2 CUCM Route Pattern & Digit Transformation Rules

```text
! CUCM Translation Pattern for Kari's Law Compliance (No Access Code)
translation-pattern modification:
  Pattern: 9.911 -> Pre-dot Strip -> Result: 911
  Pattern: 911   -> Direct Pass-through -> Result: 911

! CUCM Alert Routing Partition Configuration
partition: P_OnSite_Alert
  Calling Party Transformation Mask: +12125550100 (HQ Main Number)
  Alert Notification: Security Desk Hunt Group (Ext 55555), Webhook API (HTTP POST)
```

---

## 6. High Availability, Survivability & PSTN Failover

### 6.1 Call Path Redundancy Architecture

When primary WAN connections or cloud E911 services fail, enterprise gateways must reliably fall back to local PSTN infrastructure.

```
             ┌───────────────────────┐
             │ Cloud E911 (RedSky)   │
             └───────────────────────┘
                         ▲
                         │ Primary (SIP Trunk / WAN)
┌──────────┐   ┌───────────────────────┐   Fallback    ┌────────────────────────┐
│ Endpoint │──>│ CUCM / CER Cluster    │──────────────>│ Local Gateway (SRST)   │
└──────────┘   └───────────────────────┘  (PSTN/ISDN)  └────────────────────────┘
                         │                                         │
                         ▼                                         ▼
             ┌───────────────────────┐                 ┌────────────────────────┐
             │ On-Site Alert System  │                 │ Local PSAP (POTS/CAMA) │
             └───────────────────────┘                 └────────────────────────┘
```

### 6.2 Cisco IOS-XE Voice Gateway / SRST Configuration Script

```text
! Enable HELD and HTTP LIS parsing on IOS-XE Gateway
voice service voip
 sip
  rel1xx require
  header-passing
  midcall-signaling passthrough

! Configure Local Emergency Route Vector
dial-peer voice 911 voip
 destination-pattern 911
 session protocol sipv2
 session target dns:ers.redsky.com
 voice-class sip message-summary
 dtmf-relay rtp-nte
 accent-color cyan
 dial-peer priority 1

! Fallback Dial-Peer to Local POTS/FXO Gateway (PSTN Routing)
dial-peer voice 9110 pots
 destination-pattern 911
 port 0/0/0:23
 forward-digits 3
 clid network-number 2125550101
 dial-peer priority 2
```

---

## 7. Operational Checklists & Verification Protocols

### 7.1 Architecture Deployment & Readiness Checklist

- [ ] **Direct 911 Dialing:** Verified dialing `911` directly from all endpoints without `9` prefix.
- [ ] **On-Site Notification:** Verified real-time email, SMS, and console alerts to security team upon `911` trigger.
- [ ] **Dispatchable Location:** Configured granularity down to floor/suite level for fixed endpoints.
- [ ] **Dynamic Tracking:** Verified HELD / RedSky MyE911 agent updates location for off-premises softphones.
- [ ] **PSAP Validation:** Scheduled 911 test call with local PSAP via 911 center non-emergency line.
- [ ] **PSTN Failover:** Simulated WAN outage and verified 911 emergency call routing via local PRI/FXO gateway.
- [ ] **ELIN Pool Monitoring:** Verified sufficient ELIN capacity to support simultaneous emergency calls per floor.

### 7.2 Emergency Call Test Log Protocol

```text
+-----------------------------------------------------------------------------------+
| TEST LOG: E911 ARCHITECTURE VERIFICATION                                          |
+-------------------+--------------------+---------------+---------------+----------+
| Endpoint IP / Ext | Expected ERL/ELIN  | Actual PSAP   | Alert Received| Status   |
+-------------------+--------------------+---------------+---------------+----------+
| 10.100.1.45/4001  | NYC-HQ-FL01 / ...01| NY Metro PSAP | YES (SMS/Email)| PASSED   |
| 10.100.2.88/4002  | NYC-HQ-FL02 / ...02| NY Metro PSAP | YES (SMS/Email)| PASSED   |
| 172.16.50.12 (VPN)| DYNAMIC PIDF-LO    | RedSky ERS    | YES (Dashboard)| PASSED   |
+-------------------+--------------------+---------------+---------------+----------+
```

---

## 8. License & Copyright

```text
Copyright (c) 2026 CYPHER0X9 Security & Network Engineering

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
