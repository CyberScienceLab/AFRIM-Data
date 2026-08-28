## What does this change?

<!-- One or two sentences. Which record(s) does this touch? -->

## Checklist

- [ ] `pytest` passes locally (CI will also run this, but check first)
- [ ] Every reference has a `status`: `active` if you've verified it exists and matches your citation, `verify` if not
- [ ] If this is a flagship-level page, `claim_profile` has both `does_establish` and `does_not_establish` filled in
- [ ] `maturity.base` follows the safer-grade rule — the lower grade when ambiguous
- [ ] No `[ACTION`, `[verify]` (as a literal marker), personal names, or other internal/editorial language — see the CI guard in `tests/test_validate.py`
- [ ] If you're asserting something doesn't exist yet ("no method for X"), that claim is scoped/dated, not an unqualified absolute

## Anything the reviewer should know?

<!-- Open questions, things you're unsure about, alternatives you considered. -->
