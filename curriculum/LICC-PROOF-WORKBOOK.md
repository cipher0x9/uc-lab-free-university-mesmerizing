# LICC Proof Workbook

**CYPHER0X9 · UC Lab Free University · curriculum pack · MIT**  
**L**eg · **I**D · **C**ounter · **C**apture

This is the habit that separates operators from button-clickers.

---

## 1) The four questions (memorize)

1. **Leg** — Which hop in the path failed?  
2. **ID** — Which correlation key joins the story?  
3. **Counter** — Which KPI or error counter moved?  
4. **Capture** — What durable artifact proves it?

If you cannot answer all four, you are still guessing.

---

## 2) Blank ticket template (copy)

```text
TITLE:
TIME WINDOW (UTC):
USER IMPACT:
LEG MAP:  A → B → C → D
FAILED LEG:
IDs: Call-ID / GUID / DN / Agent / Session
COUNTERS BEFORE/AFTER:
CAPTURES: (pcap / SDL / SBC / CCaaS / screenshot)
HYPOTHESIS:
CHANGE MADE:
RESULT:
ROLLBACK PLAN:
```

---

## 3) Worked example — one-way audio

| LICC | Entry |
|------|-------|
| Leg | Media between SBC and softphone; SIP OK |
| ID | SIP Call-ID `abc@edge` · RTP SSRC |
| Counter | SBC "no RTP" alarm · client packet loss 12% |
| Capture | 30s pcap + SBC media stats export |

Fix that changes only GUI without media proof = incomplete.

---

## 4) Worked example — UCCE queue stuck

| LICC | Entry |
|------|-------|
| Leg | ICM routing → agent PG → phone |
| ID | Router Call Key · Peripheral Call Key |
| Counter | Agents ready = 0 · Max queued |
| Capture | Script editor path + RTRA-style snapshot (lab) |

---

## 5) Worked example — E911 misroute

| LICC | Entry |
|------|-------|
| Leg | ELIN mapping → gateway → PSAP path |
| ID | ELIN · device pool · location ID |
| Counter | Test call success/fail log |
| Capture | CER/test call record (lab) · redacted |

Treat emergency as **highest severity**. Dual-person validation when possible.

---

## 6) Weekly practice

Pick one incident (real lab or public postmortem style) and fill the template. Spaced review 1h→90d.

---

## 7) Twin grammar

AI sibling uses **RTMA** (Run · Trace · Metric · Artifact). Same brain, different domain.

**Educational only · MIT**
