# Security

## Reporting

If you find a security issue in this learning pack, open a private security advisory on GitHub or contact the maintainer via the GitHub profile:

**[@cipher0x9](https://github.com/cipher0x9)** · display name **CYPHER0X9**

## Safe use of this repo

- This is an **educational** UC / Contact Center curriculum and prompt library.
- Do **not** paste production credentials, customer data, dial plans, or private captures into issues or forks.
- Lab safely. Pin official vendor documentation before production changes.
- Treat any generated automation prompts as **read-only by default**.

## Account hygiene (for contributors)

- Enable 2FA on GitHub
- Prefer SSH keys or fine-scoped PATs over passwords
- Never commit `.env`, tokens, or private keys

## Links (canonical)

| | |
|--|--|
| Profile | https://github.com/cipher0x9 |
| This repo | https://github.com/cipher0x9/uc-lab-free-university |
| Sibling AI | https://github.com/cipher0x9/ai-lab-free-university |
| Hub | https://linktr.ee/cyphermonkey |

---

## Next Level security notes (additive · 2026-08-05)

### Educational pack hygiene
- Do not commit `.env`, tokens, private keys, customer pcap with audio, or private dial plans.
- Redact ANI/DNIS in public forks and issues.
- Treat captures as sensitive even in labs if real numbers appear.

### Real-time security topics taught in campus (study only)
- TLS for signaling · SRTP for media · 802.1X for device access  
- Toll-fraud class patterns · certificate expiry storms · optional SRTP silent downgrade  
- Zero-trust ideas for trunks and admin planes  

### Incident reporting for this repo
Prefer GitHub private security advisory when possible.  
Profile: [@cipher0x9](https://github.com/cipher0x9) · brand **CYPHER0X9**

### Operator checklist when using prompts/agents
1. Read-only by default  
2. Human PROCEED before outbound messages  
3. No production credentials in prompt text  
4. Pin vendor documentation versions for production change windows  

