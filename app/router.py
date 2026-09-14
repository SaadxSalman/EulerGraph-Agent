from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDecision:
    intent: str
    needs_retrieval: bool
    needs_symbolic_check: bool
    needs_formal_proof: bool
    rationale: str


class QueryRouter:
    """Deterministic routing policy used before an optional LLM router."""

    _proof_terms = ("prove", "proof", "show that", "derive", "demonstrate")
    _compute_terms = ("calculate", "compute", "solve", "evaluate", "simplify")
    _calculus_terms = ("derivative", "differentiate", "integral", "integrate", "limit")
    _algebra_terms = ("matrix", "eigen", "group", "ring", "vector", "polynomial")

    def decide(self, query: str, requested_mode: str) -> RouteDecision:
        normalized = query.lower()
        proof = requested_mode == "proof" or any(term in normalized for term in self._proof_terms)
        calculus = any(term in normalized for term in self._calculus_terms)
        algebra = any(term in normalized for term in self._algebra_terms)
        compute = requested_mode == "compute" or any(term in normalized for term in self._compute_terms)
        if proof:
            intent = "proof"
        elif calculus:
            intent = "calculus"
        elif algebra:
            intent = "algebra"
        elif compute:
            intent = "computation"
        else:
            intent = "explanation"
        return RouteDecision(
            intent=intent,
            needs_retrieval=True,
            needs_symbolic_check=compute or calculus or proof,
            needs_formal_proof=proof,
            rationale=f"Classified as {intent}; retrieval grounds terminology and the verifier handles the highest-risk claims.",
        )
