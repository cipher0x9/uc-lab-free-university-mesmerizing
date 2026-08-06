# Call Recording, WFO & Compliance

**CYPHER0X9 · UC Lab Free University · curriculum pack · MIT**  
**Proof:** LICC · Legal/compliance awareness required

Recording is not "just another feature." It is a **trust, legal, and media-path** problem.

---

## 1) Why recordings break (and get people fired)

| Failure | Impact |
|---------|--------|
| Silent no-record | Compliance violation, lost dispute evidence |
| Partial record | Dispute unusable |
| Wrong party notification | Legal risk |
| PII in wrong store | Privacy incident |
| Clock skew | Evidence challenged |
| Dual-stream missing | Agent-only or customer-only audio |

---

## 2) Recording architectures (patterns)

1. **Media forking / SPAN / network tap** — passive  
2. **SIPREC** — standardized session recording  
3. **Built-in platform recording** (CUCM, CCaaS, Teams, Webex)  
4. **Client-side / softphone** — weak for enterprise compliance  
5. **Cloud CCaaS native** + WFO suite (NICE, Verint, Calabrio-class)

Map **where media is seen** before you trust a vendor checkbox.

---

## 3) Contact center realities

- **Screen + voice** recording for QA  
- **Pause/resume** for PCI (payment card)  
- **Retention** policies by region  
- **Consent** announcements / two-party consent jurisdictions  
- **Evaluation forms** and calibration sessions  

### LICC for "recording missing"

| Letter | Ask |
|:--:|--|
| **L** | Ingress media → recorder → storage → WFO UI |
| **I** | Call GUID · recording ID · agent ID · contact ID |
| **C** | Fork success rate · storage errors · license exhaustion |
| **C** | SIPREC metadata · recorder logs · redacted audio sample in lab |

---

## 4) Compliance themes (not legal advice)

Educational awareness only — consult counsel for production:

- Consent laws vary by country/state  
- Financial / healthcare retention rules  
- Cross-border storage  
- Right to access / delete requests  
- AI transcription / coaching may create **new** data stores  

---

## 5) AI on recordings (2026)

| Use | Proof need |
|-----|------------|
| Transcription | Accuracy + language pack |
| Summarization | Hallucination risk |
| Auto-QA scoring | Bias + human review |
| Agent assist training | PII scrubbing |

Bridge: AI Lab **RTMA** for model quality; UC **LICC** for media path.

---

## 6) Design checklist

- [ ] Media path documented  
- [ ] Failure alarms (not silent)  
- [ ] Clock sync (NTP)  
- [ ] Encryption at rest + in transit  
- [ ] Access control + audit log  
- [ ] Retention + legal hold  
- [ ] PCI pause tested  
- [ ] Dual-run migration proof before cutover  

---

## 7) Teach-back

Explain SIPREC vs passive tap, and why "checkbox enabled" is not evidence of compliance.

**Educational only · not legal advice · MIT**
