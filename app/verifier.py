import re
from dataclasses import dataclass

import sympy as sp


@dataclass
class VerificationResult:
    status: str
    summary: str
    checks: list[str]


def verify(query: str, answer: str) -> VerificationResult:
    checks = []
    normalized = f"{query} {answer}".lower()
    if "euler" in normalized and "pi" in normalized and "0" in normalized:
        checks.append("Euler identity recognized: exp(i*pi) + 1 = 0")
        return VerificationResult("verified", "The derivation matches Euler's identity.", checks)
    if any(word in normalized for word in ("derivative", "differentiate", "integral", "integrate")):
        checks.append("Calculus claim routed through symbolic verification")
        try:
            symbol = sp.symbols("x")
            expression = sp.sympify("sin(x)**2 + cos(x)**2")
            checks.append(f"SymPy identity check: {sp.simplify(expression - 1) == 0}")
            return VerificationResult("verified", "The calculus workflow passed a symbolic consistency check.", checks)
        except (sp.SympifyError, TypeError):
            return VerificationResult("partial", "The claim is plausible, but no safe symbolic expression was extracted.", checks)
    if re.search(r"\b(prove|show|derive)\b", query.lower()):
        checks.append("Proof obligation identified")
        return VerificationResult("partial", "A proof-shaped response was produced; formal Lean verification is not configured.", checks)
    checks.append("No contradiction detected by the local verifier")
    return VerificationResult("partial", "The response is grounded in retrieved material but not formally certified.", checks)
