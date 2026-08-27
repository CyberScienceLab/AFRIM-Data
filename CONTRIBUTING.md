# Contributing to FIRAI

FIRAI (Forensic Investigation Reference for AI) is a knowledge base, not a
finished standard. Every record in `src/` is a claim about the state of AI
forensic practice, and claims here are held to the principles below before
they're held to anything else.

**Formal contribution mechanics — a CLA/DCO, a two-reviewer rule for maturity
changes, and IP terms — are not live yet.** Those require counsel review
before external contributions open. Until then, treat this document as the
principles that govern any change, including ones made by maintainers.

## Design principles

1. **Defensibility over completeness.** Every technique carries a validation
   profile and at least one reference, or is explicitly graded `Proposed`
   with a structured originality rationale — `Proposed` is not a bypass for
   having no citation. A sparse or missing cell should be visibly sparse
   (via a GAP record), not silently absent.

2. **Validation is separated from admissibility.** Research support,
   independent replication, forensic method validation, tool implementation
   verification, and operational adoption are recorded separately. None of
   them determine legal admissibility, which depends on the law and facts of
   a specific forum. The `maturity` field (`Established` / `Demonstrated` /
   `Proposed`) is a research-and-validation summary — never a legal
   conclusion, and never described as one.

3. **Safer-grade rule.** Where a maturity grade is ambiguous, use the lower,
   safer grade. The community disputes upward with evidence, not the reverse.

4. **Techniques belong to phases, not cells.** The matrix is a rendered view
   of the data, never the storage model. A technique renders in every
   `(evidence_class, phase)` cell it directly consumes or produces.
   Cross-cutting techniques that range over an entire phase render as a
   phase band instead of being duplicated into every cell — this keeps real
   gaps visible instead of papering over them.

5. **Access is a capability/coverage attribute, not a claim-strength scale.**
   `access_capability` (white/grey/black) describes what an examiner can
   reach — it does not by itself determine whether a claim is deterministic,
   probabilistic, or circumstantial. A verifiable black-box response can
   support a stronger proposition than an untrusted white-box artifact.
   Claim strength is expressed per finding, never derived from access tier.

6. **Use existing forensic vocabulary; invent only when nothing exists.**
   Phase names are classical. Evidence-handling language follows ISO/IEC
   27037 / NIST SP 800-86. New terms are reserved for genuinely AI-native
   concepts (e.g. silent-mutation volatility).

7. **Claim- and validation-awareness is content, not an afterthought.** Every
   technique states what it does and does not establish
   (`does_establish` / `does_not_establish`), alternative propositions,
   corroboration requirements, quality controls or stop conditions, and
   performance/error/uncertainty characterization — never a single "error
   rate" number standing in for all of that.

8. **Lawful and proportionate collection.** Techniques operate only under
   engagement authority and a legal basis, with purpose limitation, data
   minimization, and counsel review where legal conclusions or compulsory
   process are involved. Volatility never creates legal authority on its own.

9. **Hostile-evidence and side-effect safety.** AI artifacts (serialized
   objects, checkpoints, RAG content, prompts) are untrusted and may carry
   code execution or prompt-injection payloads. Techniques describe working
   on isolated copies, with recorded tool versions, no credential/egress
   exposure, and no live external calls during replay or testing.

10. **Epistemic caveats are content.** Known limits — non-determinism,
    adversarial evasion, contested reliability — belong on the card, not in
    a changelog only maintainers see.

11. **No categorical absence claim ships without a dated search behind it.**
    "No method exists for X" is itself a claim. Before it ships, the search
    that produced it — sources, terms, date, inclusion criteria — needs to
    exist somewhere checkable (see `novelty-and-gap-method.md`), not just be
    asserted from memory.

## Adding or editing a technique

See the data-workflow section in `README.md` for the mechanical steps
(`pytest`, `tools/compile.py`). This section is about content standards:

- Fill in `claim_profile` for anything beyond the thinnest stub.
- If you're asserting a technique is the first/only one to do something,
  scope the claim by date ("as of `<date>`, within the documented search —
  see `novelty-and-gap-method.md`") rather than an unqualified absolute.
- Every reference gets a `status`: `active` once someone has actually
  checked it exists and matches your citation, `verify` if it hasn't been
  independently confirmed yet. Don't mark something `active` because it
  sounds right.
