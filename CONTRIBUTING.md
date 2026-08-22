# Contributing

Thank you for helping learners.

1. Keep changes **additive** and educational.
2. No production secrets or customer data.
3. Prefer small, reviewable PRs (one topic per PR).
4. For large HTML curriculum changes, describe what was added and why.

Free for learning. Be kind.

---

## Next Level contribution rules (additive · 2026-08-05)

1. **DO NOT CUT. ONLY INCREASE.** Additive PRs preferred.  
2. English surface for public learner text.  
3. Offline-first: no CDN, no external fonts/JS.  
4. Preserve LICC and brand (CYPHER0X9 / cipher0x9).  
5. Keep THE CALL MUST ALWAYS CONNECT as the spine.  
6. Describe new sections: id, group, why.  
7. No production secrets.  
8. For large HTML changes, note before/after section counts.  

## Verify before you open a campus PR

```bash
python3 tools/verify_campus.py
# or
make verify
```

The flagship must stay a **632+** unique-section offline file (`university/v17-UNIVERSITY.html`).
Generators (`uc_qbank_gen.py`, `uc_supernova_gen.py`) are idempotent and refuse to thin the campus.
See [tools/README.md](./tools/README.md).  

