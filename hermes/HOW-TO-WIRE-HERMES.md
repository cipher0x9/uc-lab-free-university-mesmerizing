# How to wire Hermes later

## Goal
This pack = **source of truth**. Hermes = **scheduler + coach + enricher**.

## Patterns
1. **Morning coach (15 min):** 1 UC section + 1 language drill + 1 AI micro-task  
2. **University enrich:** generate interview Qs / lab / SEV seed → human PROCEED before merge  
3. **RAG brain:** index `prompts/**/*.md` + section exports; require file-path citations  
4. **Nature mode:** voice-first walking quizzes  
5. **Agency mode:** draft client education from UC sections; approve before send  

## Implementation sketch
1. Hermes workspace root → `UC-LAB-FREE-SHARE/`  
2. Tools: read files, append `artifacts/YYYY-MM-DD.md`  
3. Schedule daily + weekly review  
4. Safety: no outbound messages without approval  
5. Track studied section IDs  

## Seed instruction for Hermes
> You are my Free University enrichment agent. Root: UC-LAB-FREE-SHARE.  
> Daily: pick next study items from university + prompts/01 + prompts/02,  
> write GREEN checklist to artifacts/today.md,  
> propose ≤3 curriculum bullets — do not rewrite HTML unless I say PROCEED.

## Quality rule
Fewer mesmerizing pages beat multi-hundred-MB dumps. Always additive. Human gate for publish.

---

## NEXT LEVEL ADDITIVE LAYER · 2026-08-05

## Next Level Hermes schedule (copy/adapt)

### Daily (15–25 min)
```
1. Speak spine: THE CALL MUST ALWAYS CONNECT
2. Open university section from "Next Level" groups (rotate)
3. Active recall: blank page Feynman (chunk±7)
4. LICC 4 lines on a fictional or redacted SEV
5. Mnemonic drill (Mon SIP Rockstar / Wed ICM Brain / Fri CUBE Bouncer)
6. Write GREEN checklist → artifacts/YYYY-MM-DD.md
```

### Weekly
- Migration dual-run tabletop (even if not migrating)
- One SIP ladder annotation
- One QoS or codec math sheet
- Peer teach-back 90 seconds

### Monthly
- Principal interview story using LICC
- Emergency path freshness audit (lab policy)
- Review wrong-reason hunting cards

### Hermes tool permissions (recommended)
| Tool | Default |
|------|---------|
| Read curriculum / prompts | Allow |
| Append artifacts/ | Allow |
| Edit university HTML | Deny until PROCEED |
| Send email/chat/social | Deny until PROCEED |
| Run shell against prod | Never |

### Sample daily artifact schema
```markdown
# UC Lab · YYYY-MM-DD
Spine: THE CALL MUST ALWAYS CONNECT
Section IDs studied:
Feynman summary (5 lines):
LICC:
- L:
- I:
- C:
- C:
Mnemonic score (0-12 SIP / 0-8 ICM / 0-10 CUBE):
Gaps for +24h review:
GREEN: yes/no
```

### RAG notes
Index:
- `university/v17-UNIVERSITY.html` section titles (export if needed)
- `prompts/**/*.md`
- `START-HERE.md`, `README.md`

Require path citations. Prefer shorter truthful answers over hallucinated vendor clicks.

---

## PASS 2 · latest-practice wiring (additive · 2026-08-05)

### AI-assisted UC ops loop
1. Ingest symptom text (no ANI/customer PII).  
2. Emit path hypothesis ≤5 + LICC skeleton.  
3. Pull matching campus section titles (RAG) with path citations.  
4. Propose captures list — human runs captures.  
5. Write GREEN checklist to `artifacts/today.md` only.

### Observability wiring
| Signal class | Example sources (lab) | Hermes output |
|--------------|----------------------|---------------|
| Voice trunk | ASR / NER study tables | “Counter to watch” card |
| Contact center | SL / abandon study tables | Queue-path questions |
| Media | jitter / loss / MOS concepts | One-way audio drill |
| AI channel | containment / assist latency (conceptual) | Link FUTURE-OF-UC §2 |

### Security hardening jobs (scheduled weekly)
- Quiz: least-privilege admin roles  
- Quiz: recording consent & retention concepts  
- Red-team: “would this runbook leak secrets if pasted into a public issue?”

### API automation jobs
- Nightly: validate local markdown links (including `FUTURE-OF-UC.md`)  
- On demand: draft idempotent provision pseudo-code **without credentials**  
- Block: any tool that could mutate live CUCM/CCaaS without PROCEED flag

