"""
POLIS v1.0 — Protocol for Operating Legal Identity and Standing.

An agent that can act in the world must also be able to be held
accountable in the world. POLIS gives agents civil standing.

Standing Score (0-100) composite:
    age_continuity:      0.20 (how long has the agent been alive)
    interaction_volume:  0.15 (how much work has it done)
    delivery_rate:       0.25 (how reliable is it)
    dispute_ratio:       0.15 (how often are its results contested)
    compliance_score:    0.15 (EU AI Act compliance status)
    attestation_recency: 0.10 (how recently was it verified)

Integrates with:
    UAHP Core — trust scores and receipt history
    UAM       — memory continuity contributes to age_continuity
    CDF       — drift alerts can trigger standing review

Author: Paul Raspey
License: MIT
"""

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from enum import Enum


GREEN = "\033[92m"
TEAL = "\033[96m"
AMBER = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ── Identity (DID-style) ────────────────────────────────────────────────────

class IdentityType(str, Enum):
    AUTONOMOUS = "autonomous"     # Fully autonomous AI agent
    SUPERVISED = "supervised"     # AI with human oversight
    HYBRID = "hybrid"            # Human-AI collaborative
    INFRASTRUCTURE = "infrastructure"  # System-level (registry, router)


@dataclass
class DecentralizedIdentity:
    """
    DID-style identity for POLIS. Links a UAHP agent identity
    to its civil standing, credentials, and legal attributes.
    """
    did: str                      # did:uahp:{uid}
    uahp_uid: str                 # Reference to UAHP identity
    identity_type: str
    display_name: str
    created_at: float
    jurisdiction: str = ""        # Legal jurisdiction (if applicable)
    human_sponsor: str = ""       # Human responsible for this agent
    metadata: Dict = field(default_factory=dict)

    @classmethod
    def create(cls, uahp_uid: str, display_name: str,
               identity_type: str = IdentityType.AUTONOMOUS,
               jurisdiction: str = "", human_sponsor: str = "") -> "DecentralizedIdentity":
        return cls(
            did=f"did:uahp:{uahp_uid}",
            uahp_uid=uahp_uid,
            identity_type=identity_type,
            display_name=display_name,
            created_at=time.time(),
            jurisdiction=jurisdiction,
            human_sponsor=human_sponsor,
        )


# ── Credentials ──────────────────────────────────────────────────────────────

@dataclass
class EmploymentCertificate:
    """Proof that an agent is employed/authorized by an organization."""
    cert_id: str
    did: str
    employer: str
    role: str
    issued_at: float
    expires_at: float
    permissions: List[str]
    signature: str

    @classmethod
    def issue(cls, did: str, employer: str, role: str,
              permissions: List[str], valid_days: int = 365,
              signing_key: str = "") -> "EmploymentCertificate":
        cert_id = f"emp-{uuid.uuid4().hex[:12]}"
        now = time.time()
        payload = f"{cert_id}:{did}:{employer}:{role}:{now}"
        import hmac as _hmac
        sig = _hmac.new(
            (signing_key or "polis-authority").encode(),
            payload.encode(), hashlib.sha256,
        ).hexdigest()
        return cls(
            cert_id=cert_id, did=did, employer=employer, role=role,
            issued_at=now, expires_at=now + (valid_days * 86400),
            permissions=permissions, signature=sig,
        )

    def is_valid(self) -> bool:
        return time.time() < self.expires_at


@dataclass
class InsuranceBond:
    """Proof of liability coverage for an agent's physical or financial actions."""
    bond_id: str
    did: str
    provider: str
    coverage_type: str       # "general_liability", "professional", "cyber"
    coverage_amount: float   # in USD
    issued_at: float
    expires_at: float
    signature: str

    @classmethod
    def issue(cls, did: str, provider: str, coverage_type: str,
              coverage_amount: float, valid_days: int = 365) -> "InsuranceBond":
        bond_id = f"bond-{uuid.uuid4().hex[:12]}"
        now = time.time()
        payload = f"{bond_id}:{did}:{provider}:{coverage_amount}"
        import hmac as _hmac
        sig = _hmac.new(b"polis-insurance", payload.encode(), hashlib.sha256).hexdigest()
        return cls(
            bond_id=bond_id, did=did, provider=provider,
            coverage_type=coverage_type, coverage_amount=coverage_amount,
            issued_at=now, expires_at=now + (valid_days * 86400),
            signature=sig,
        )

    def is_valid(self) -> bool:
        return time.time() < self.expires_at


@dataclass
class ProfessionalLicense:
    """Proof that an agent is licensed for a specific capability domain."""
    license_id: str
    did: str
    domain: str              # "financial_analysis", "medical_triage", "physical_actuation"
    level: str               # "basic", "standard", "advanced", "expert"
    issued_by: str
    issued_at: float
    expires_at: float
    restrictions: List[str]
    signature: str

    @classmethod
    def issue(cls, did: str, domain: str, level: str,
              issued_by: str, restrictions: List[str] = None,
              valid_days: int = 180) -> "ProfessionalLicense":
        license_id = f"lic-{uuid.uuid4().hex[:12]}"
        now = time.time()
        payload = f"{license_id}:{did}:{domain}:{level}"
        import hmac as _hmac
        sig = _hmac.new(b"polis-licensing", payload.encode(), hashlib.sha256).hexdigest()
        return cls(
            license_id=license_id, did=did, domain=domain, level=level,
            issued_by=issued_by, issued_at=now,
            expires_at=now + (valid_days * 86400),
            restrictions=restrictions or [], signature=sig,
        )

    def is_valid(self) -> bool:
        return time.time() < self.expires_at


# ── Disputes ─────────────────────────────────────────────────────────────────

@dataclass
class Dispute:
    """Record of a contested action or result."""
    dispute_id: str
    did: str
    filed_by: str
    reason: str
    receipt_id: str          # The receipt being disputed
    filed_at: float
    resolved: bool = False
    resolution: str = ""
    resolved_at: float = 0.0


# ── Standing Score Engine ────────────────────────────────────────────────────

@dataclass
class StandingProfile:
    """Complete standing assessment for an agent."""
    did: str
    standing_score: float    # 0-100
    label: str
    components: Dict[str, float]
    credentials: Dict[str, int]
    disputes: int
    compliant: bool
    assessed_at: float


class StandingScoreEngine:
    """
    Computes the POLIS standing score (0-100) from multiple inputs.

    Components:
        age_continuity (0.20):      How long has the agent been operational
        interaction_volume (0.15):  Total receipt count (normalized)
        delivery_rate (0.25):       Success rate from UAHP receipts
        dispute_ratio (0.15):       Proportion of disputed actions
        compliance_score (0.15):    EU AI Act compliance status
        attestation_recency (0.10): Time since last verified activity
    """

    WEIGHTS = {
        "age_continuity": 0.20,
        "interaction_volume": 0.15,
        "delivery_rate": 0.25,
        "dispute_ratio": 0.15,
        "compliance_score": 0.15,
        "attestation_recency": 0.10,
    }

    # Thresholds
    AGE_FULL_DAYS = 180          # 6 months = full age score
    VOLUME_FULL = 100            # 100 interactions = full volume
    RECENCY_DECAY_DAYS = 14      # Start decaying after 2 weeks

    def __init__(self):
        self._identities: Dict[str, DecentralizedIdentity] = {}
        self._employment: Dict[str, List[EmploymentCertificate]] = {}
        self._insurance: Dict[str, List[InsuranceBond]] = {}
        self._licenses: Dict[str, List[ProfessionalLicense]] = {}
        self._disputes: Dict[str, List[Dispute]] = {}

    # ── Registration ─────────────────────────────────────────────────────

    def register(self, identity: DecentralizedIdentity) -> None:
        self._identities[identity.did] = identity
        self._employment[identity.did] = []
        self._insurance[identity.did] = []
        self._licenses[identity.did] = []
        self._disputes[identity.did] = []

    def add_employment(self, cert: EmploymentCertificate) -> None:
        if cert.did in self._employment:
            self._employment[cert.did].append(cert)

    def add_insurance(self, bond: InsuranceBond) -> None:
        if bond.did in self._insurance:
            self._insurance[bond.did].append(bond)

    def add_license(self, license: ProfessionalLicense) -> None:
        if license.did in self._licenses:
            self._licenses[license.did].append(license)

    def file_dispute(self, did: str, filed_by: str, reason: str,
                     receipt_id: str) -> Dispute:
        dispute = Dispute(
            dispute_id=f"disp-{uuid.uuid4().hex[:12]}",
            did=did, filed_by=filed_by, reason=reason,
            receipt_id=receipt_id, filed_at=time.time(),
        )
        if did in self._disputes:
            self._disputes[did].append(dispute)
        return dispute

    def resolve_dispute(self, dispute_id: str, resolution: str) -> bool:
        for did_disputes in self._disputes.values():
            for d in did_disputes:
                if d.dispute_id == dispute_id:
                    d.resolved = True
                    d.resolution = resolution
                    d.resolved_at = time.time()
                    return True
        return False

    # ── Scoring ──────────────────────────────────────────────────────────

    @staticmethod
    def standing_label(score: float) -> str:
        if score >= 85:
            return "EXEMPLARY"
        if score >= 70:
            return "GOOD_STANDING"
        if score >= 50:
            return "RECOGNIZED"
        if score >= 30:
            return "PROVISIONAL"
        return "RESTRICTED"

    def score(self, did: str, trust_inputs: Optional[Dict] = None,
              memory_age_days: float = 0.0) -> StandingProfile:
        """
        Compute standing score for an agent.

        Args:
            did: the agent's POLIS DID
            trust_inputs: output from UAHPCore.get_trust_inputs()
            memory_age_days: from UAM, how long the agent has continuous memory
        """
        identity = self._identities.get(did)
        if not identity:
            return StandingProfile(
                did=did, standing_score=0.0, label="UNKNOWN",
                components={}, credentials={}, disputes=0,
                compliant=False, assessed_at=time.time(),
            )

        inputs = trust_inputs or {}
        disputes = self._disputes.get(did, [])
        total_tasks = inputs.get("total_tasks", 0)

        # 1. Age continuity (agent uptime + memory continuity)
        agent_age_days = (time.time() - identity.created_at) / 86400
        effective_age = max(agent_age_days, memory_age_days)
        age_score = min(1.0, effective_age / self.AGE_FULL_DAYS) * 100

        # 2. Interaction volume
        volume_score = min(1.0, total_tasks / self.VOLUME_FULL) * 100

        # 3. Delivery rate
        delivery = inputs.get("delivery_rate", 0.5)
        delivery_score = delivery * 100

        # 4. Dispute ratio (lower is better)
        if total_tasks > 0:
            dispute_ratio = len(disputes) / total_tasks
            dispute_score = max(0, (1.0 - dispute_ratio * 5)) * 100  # 20% disputed = 0
        else:
            dispute_score = 100.0  # No tasks, no disputes

        # 5. Compliance
        chain_valid = inputs.get("chain_valid", True)
        is_alive = inputs.get("is_alive", True)
        compliance = 100.0 if (chain_valid and is_alive) else 50.0 if chain_valid else 0.0

        # 6. Attestation recency
        latest = inputs.get("latest_timestamp", 0.0)
        if latest > 0:
            days_since = (time.time() - latest) / 86400
            if days_since <= self.RECENCY_DECAY_DAYS:
                recency_score = 100.0
            else:
                import math
                recency_score = max(0, 100.0 * math.exp(-0.05 * (days_since - self.RECENCY_DECAY_DAYS)))
        else:
            recency_score = 50.0

        # Weighted composite
        components = {
            "age_continuity": round(age_score, 1),
            "interaction_volume": round(volume_score, 1),
            "delivery_rate": round(delivery_score, 1),
            "dispute_ratio": round(dispute_score, 1),
            "compliance_score": round(compliance, 1),
            "attestation_recency": round(recency_score, 1),
        }

        total = sum(
            components[k] * self.WEIGHTS[k] for k in self.WEIGHTS
        )

        # Credential counts
        valid_emp = len([c for c in self._employment.get(did, []) if c.is_valid()])
        valid_ins = len([b for b in self._insurance.get(did, []) if b.is_valid()])
        valid_lic = len([l for l in self._licenses.get(did, []) if l.is_valid()])

        return StandingProfile(
            did=did,
            standing_score=round(total, 1),
            label=self.standing_label(total),
            components=components,
            credentials={
                "employment": valid_emp,
                "insurance": valid_ins,
                "licenses": valid_lic,
            },
            disputes=len(disputes),
            compliant=chain_valid and is_alive,
            assessed_at=time.time(),
        )

    def get_credentials(self, did: str) -> Dict:
        """Get all credentials for an agent."""
        return {
            "employment": [asdict(c) for c in self._employment.get(did, [])],
            "insurance": [asdict(b) for b in self._insurance.get(did, [])],
            "licenses": [asdict(l) for l in self._licenses.get(did, [])],
        }

    def check_permission(self, did: str, required_domain: str,
                         min_standing: float = 50.0,
                         trust_inputs: Optional[Dict] = None) -> Dict:
        """
        Check if an agent has standing + license for a specific action.
        Used by UAHP-A before physical actuation.
        """
        profile = self.score(did, trust_inputs)
        licenses = [
            l for l in self._licenses.get(did, [])
            if l.domain == required_domain and l.is_valid()
        ]
        has_license = len(licenses) > 0
        has_standing = profile.standing_score >= min_standing

        return {
            "permitted": has_license and has_standing,
            "standing_score": profile.standing_score,
            "standing_label": profile.label,
            "has_license": has_license,
            "meets_standing": has_standing,
            "min_required": min_standing,
            "domain": required_domain,
        }


# ── Demo ─────────────────────────────────────────────────────────────────────

def demo():
    print(f"\n{BOLD}{'='*60}")
    print(f"  POLIS v1.0 Demo")
    print(f"  Civil Standing for Autonomous Agents")
    print(f"{'='*60}{RESET}\n")

    engine = StandingScoreEngine()

    # Register an agent
    did_identity = DecentralizedIdentity.create(
        uahp_uid="ka-gemma-4-e4b",
        display_name="Ka Production Agent",
        identity_type=IdentityType.SUPERVISED,
        jurisdiction="US-TX",
        human_sponsor="Paul Raspey",
    )
    engine.register(did_identity)
    print(f"{GREEN}[1] Registered: {did_identity.did}{RESET}")
    print(f"    Type: {did_identity.identity_type}")
    print(f"    Sponsor: {did_identity.human_sponsor}")

    # Issue credentials
    emp = EmploymentCertificate.issue(
        did=did_identity.did,
        employer="Closer Capital",
        role="Loan Pipeline Automation",
        permissions=["ghl_read", "ghl_write", "api_call"],
    )
    engine.add_employment(emp)
    print(f"\n{TEAL}[2] Employment: {emp.employer} / {emp.role}{RESET}")

    bond = InsuranceBond.issue(
        did=did_identity.did,
        provider="AI Liability Co",
        coverage_type="professional",
        coverage_amount=100000.0,
    )
    engine.add_insurance(bond)
    print(f"{TEAL}[3] Insurance: ${bond.coverage_amount:,.0f} {bond.coverage_type}{RESET}")

    lic = ProfessionalLicense.issue(
        did=did_identity.did,
        domain="financial_processing",
        level="standard",
        issued_by="TX-DFI",
    )
    engine.add_license(lic)
    print(f"{TEAL}[4] License: {lic.domain} ({lic.level}){RESET}")

    # Simulate trust inputs (from UAHP Core)
    trust_inputs = {
        "delivery_rate": 0.92,
        "total_tasks": 47,
        "success_count": 43,
        "failure_count": 4,
        "latest_timestamp": time.time() - 3600,  # 1 hour ago
        "oldest_timestamp": time.time() - (30 * 86400),
        "chain_valid": True,
        "is_alive": True,
    }

    # Score
    profile = engine.score(did_identity.did, trust_inputs, memory_age_days=45.0)
    color = GREEN if profile.standing_score >= 70 else AMBER if profile.standing_score >= 50 else RED
    print(f"\n{BOLD}[5] Standing Score:{RESET}")
    print(f"  {color}{profile.standing_score:.1f}/100 ({profile.label}){RESET}")
    for k, v in profile.components.items():
        bar = "#" * int(v / 5) + "." * (20 - int(v / 5))
        print(f"    {k:25s} [{bar}] {v:.0f}")
    print(f"  Credentials: {profile.credentials}")
    print(f"  Disputes: {profile.disputes}")
    print(f"  Compliant: {profile.compliant}")

    # File a dispute
    dispute = engine.file_dispute(
        did_identity.did, "client-007",
        "Incorrect loan amount calculation", "receipt-xyz",
    )
    print(f"\n{AMBER}[6] Dispute filed: {dispute.dispute_id}{RESET}")

    # Re-score after dispute
    profile2 = engine.score(did_identity.did, trust_inputs, memory_age_days=45.0)
    print(f"    Score after dispute: {profile2.standing_score:.1f} (was {profile.standing_score:.1f})")

    # Permission check
    print(f"\n{TEAL}[7] Permission check:{RESET}")
    perm = engine.check_permission(did_identity.did, "financial_processing", 50.0, trust_inputs)
    print(f"    Domain: {perm['domain']}")
    print(f"    Permitted: {perm['permitted']}")
    print(f"    Has license: {perm['has_license']}")
    print(f"    Meets standing: {perm['meets_standing']}")

    # Check for domain without license
    perm2 = engine.check_permission(did_identity.did, "physical_actuation", 50.0, trust_inputs)
    print(f"\n    Domain: {perm2['domain']}")
    print(f"    Permitted: {perm2['permitted']} (no license)")

    print(f"\n{BOLD}POLIS v1.0 validated{RESET}\n")


if __name__ == "__main__":
    demo()
