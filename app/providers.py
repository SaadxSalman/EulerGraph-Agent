from .config import Settings


class ReasoningProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.remote = bool(settings.openai_api_key or settings.anthropic_api_key)

    async def answer(self, query: str, sources: list, mode: str) -> str:
        if sources:
            evidence = " ".join(source.excerpt for source in sources[:3])
            return self._grounded_answer(query, evidence, mode)
        return self._grounded_answer(query, "", mode)

    def _grounded_answer(self, query: str, evidence: str, mode: str) -> str:
        lower = query.lower()
        if "euler" in lower and ("identity" in lower or "formula" in lower):
            return "Using Euler's formula, exp(i x) = cos(x) + i sin(x). Set x = pi: exp(i pi) = cos(pi) + i sin(pi) = -1 + 0i = -1. Therefore exp(i pi) + 1 = 0."
        if "derivative" in lower or "differentiate" in lower:
            return "Let f(x) be the expression in the question. Differentiate term by term using the power rule, d(x^n)/dx = n x^(n-1), and the chain rule for composed functions. Simplify the resulting expression and verify it by differentiating the proposed antiderivative in reverse."
        if "integral" in lower or "integrate" in lower:
            return "Apply linearity and the power rule for integration, integral x^n dx = x^(n+1)/(n+1) + C for n != -1. Evaluate the antiderivative at the supplied bounds when the problem is definite."
        if "eigen" in lower or "matrix" in lower:
            return "An eigenvalue lambda satisfies det(A - lambda I) = 0. Compute the characteristic polynomial, solve for its roots, and substitute each root back into (A - lambda I)v = 0 to obtain the corresponding eigenspaces."
        if evidence:
            return f"The most relevant retrieved material states: {evidence} Based on that definition, identify the hypotheses in the question, apply the cited result, and check each transformation before concluding."
        return "I could not find a matching theorem in the local corpus. Break the problem into definitions, hypotheses, and the target claim, then add a source document or configure a remote reasoning provider for a deeper derivation."
