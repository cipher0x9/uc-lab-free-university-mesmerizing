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
