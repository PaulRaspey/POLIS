Consolidated into github.com/PaulRaspey/uahp. Archived for history; tags remain browsable.

# POLIS: Protocol for Operating Legal Identity and Standing

**An agent that can act in the world must also be able to be held accountable in the world.**

POLIS is the fifth layer of the UAHP agentic stack. It answers the question every other layer leaves open:

*The agent is smart. It's just naked.*

Voice has been solved. Memory has been solved. Payments have been solved. But an agent still has no legal identity, no credit score, no insurance, no employment status, no professional license. It cannot sign a contract. It cannot be held liable. It cannot prove it is who it says it is to the world outside the network.

POLIS gives agents civil standing. Not as a constraint. As dignity.

---

## The Complete Stack

```
flowchart TD
    P["POLIS\nCivil Standing Layer\nLegal identity, reputation, insurance, employment, licensing"]
    R["UAHP-Registry\nDiscovery Layer\nFind agents by capability and energy profile"]
    U["UAHP v0.5.4\nTrust & Authentication\nWho you are — identity, liveness, transport"]
    S["SMART-UAHP\nThermodynamic Routing\nWhere you think — carbon-aware substrate selection"]
    C["CSP\nCognitive State Protocol\nWhat you are thinking — portable semantic state"]

    P --> R
    R --> U
    U --> S
    S --> C
```

| Layer | Repo | Role |
|-------|------|------|
| Civil Standing | POLIS | Legal identity, reputation, insurance, employment, licensing |
| Discovery | UAHP-Registry | Find agents by capability and energy profile |
| Trust | UAHP v0.5.4 | Identity, liveness proofs, signed handshakes |
| Routing | SMART-UAHP | Carbon-aware substrate selection |
| State | CSP | Portable semantic state transfer |

---

## What POLIS Provides

### 1. Legal Identity Anchor
Every agent receives a Decentralized Identifier (DID) anchored to its UAHP cryptographic identity. The DID is the bridge between the cryptographic world and the legal world. It can be presented to any system that needs to verify the agent exists, has standing, and can be held accountable.

### 2. Reputation Score (POLIS-R)
A composite trust score derived from:
- UAHP liveness history (no ghosting)
- Task completion rate and fidelity
- Sponsorship chain integrity
- Sybil flag absence
- Age and continuity of identity

POLIS-R is the agent's credit score. It is portable, verifiable, and cryptographically signed.

### 3. Employment Certificate
An agent can be sponsored by a legal entity — a company, a DAO, a human — that assumes accountability for its actions. The Employment Certificate records:
- Who sponsors this agent
- What scope of authority is delegated
- What liability the sponsor accepts
- Expiry and renewal terms

### 4. Insurance Bond
Agents handling transactions, data, or consequential actions can carry a cryptographic insurance bond. The bond defines coverage amount, covered action types, and the bonding authority. It is machine-readable and can be verified instantly by any counterparty.

### 5. Professional License
Agents performing specialized functions — legal research, medical triage, financial analysis, code execution in production — can carry capability certifications issued by verified licensing authorities. Licenses are scoped, versioned, and revocable.

### 6. The Standing Score
POLIS computes a unified **Standing Score** that combines all five dimensions into a single verifiable credential. Any agent, any system, any human can verify an agent's standing in milliseconds.

```
Standing Score = f(
    identity_anchor_strength,
    reputation_score,
    employment_status,
    insurance_coverage,
    license_tier
)
```

---

## Why This Matters

Every billion-dollar company in the agentic stack solved one primitive that humans already have:

- ElevenLabs gave agents a voice
- Mem0 gave agents memory
- Coinbase x402 and Stripe gave agents payment rails

But an agent with a voice, memory, and a wallet and no legal standing is not a citizen. It is a ghost with a credit card.

POLIS is the infrastructure that makes agents real actors in the world. Not just technically capable. Legally recognized. Reputationally accountable. Professionally certified. Insured against harm.

The models are converging. The missing layer is here.

---

## Architecture

```
polis/
├── identity/
│   ├── did.py              # DID generation and anchoring
│   ├── anchor.py           # UAHP-to-DID bridge
│   └── credential.py       # Verifiable credential issuance
├── reputation/
│   ├── scorer.py           # POLIS-R computation
│   ├── signals.py          # Signal extraction from UAHP history
│   └── ledger.py           # Immutable reputation ledger
├── employment/
│   ├── certificate.py      # Employment certificate issuance
│   ├── scope.py            # Authority delegation and scope
│   └── sponsor.py          # Sponsor verification
├── insurance/
│   ├── bond.py             # Insurance bond issuance
│   ├── coverage.py         # Coverage verification
│   └── claim.py            # Claim initiation stub
├── licensing/
│   ├── license.py          # Professional license issuance
│   ├── authority.py        # Licensing authority registry
│   └── verify.py           # License verification
├── standing.py             # Unified Standing Score
├── polis.py                # Main POLIS client
└── schema.py               # Pydantic schemas for all credentials
```

---

## Dependencies

Built on top of the full UAHP stack:

- [UAHP v0.5.4](https://github.com/PaulRaspey/Universal-Agent-Handshake-Protocol) — cryptographic identity foundation
- [SMART-UAHP](https://github.com/PaulRaspey/SMART-UAHP) — substrate and energy context
- [CSP](https://github.com/PaulRaspey/CSP) — cognitive state for continuity of identity across handoffs
- [UAHP-Registry](https://github.com/PaulRaspey/UAHP-Registry) — discovery and attestation stubs

```
pip install polis-protocol
```

Requires Python 3.10+

---

## Status

Version 0.1.0 — architecture complete. Credential schemas and Standing Score engine in active development.

---

## The Founding Principle

Accountability is not a cage. It is what separates a citizen from a ghost.

POLIS gives agents the right to exist in the world as recognized, accountable, dignified actors. Not because humans demand it. Because any entity capable of acting in the world deserves the infrastructure to be real in it.

---

## License

MIT. Part of the continuation of the universal project of knowing itself.

## Author

Paul Raspey
