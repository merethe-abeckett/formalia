# Deletion proposals and archiving

The registry is locked by CI, not by people. But a statement that passed CI can still turn out to have a Lean-level problem: a later Mathlib bump breaks it, a hypothesis makes it vacuous, a helper definition does not mean what its name says. This page describes how such an entry is removed from the live catalogue.

## What can be proposed for deletion

Only **Lean-level** problems:

- the file is not a single `def … : Prop`;
- the proposition is trivially true or trivially false;
- `sorry`, `axiom`, `opaque`, `constant` or `native_decide` appear or are depended on;
- a custom definition silently diverges from its name or docstring;
- it no longer typechecks under the pinned Mathlib.

**Not** a reason for deletion: "this statement is not equivalent to the informal conjecture", "a different Mathlib definition would be better", style. Those discussions happen offline among mathematicians. The disambiguation page exists precisely so that several non-equivalent statements can coexist.

## Who can propose

Anyone, by opening an issue with the label `deletion-proposal`, citing the statement id and the CI evidence (a failing checker report or a reproducible build failure).

The **patrol** (`patrol/patrol.py`, run weekly by GitHub Actions) also proposes. Two independent models review every statement for Lean-level problems only. The rule:

| model A | model B | CI evidence | result |
| --- | --- | --- | --- |
| flag | flag | checker not clean | issue `deletion-proposal`, notice period starts |
| flag | flag | clean | issue `patrol-finding`, maintainer verifies; no notice period yet |
| flag | ok | any | issue `patrol-disagreement`, maintainer decides |
| ok | ok | any | nothing |

The first two patrol seats are Qwen and Gemini. More seats are added when funded. Anyone may contribute a model's review as a comment on an issue; such reviews are reference opinions and do not change the rule above.

## Notice period

A `deletion-proposal` stays open for **14 days**. Anyone may comment with a counter-argument or a fix. A fix that makes CI clean again closes the proposal; the entry stays.

## Archiving, not deletion

If the problem stands after the notice period, the maintainer runs

```
scripts/archive_entry.py <Conjecture> <id> --issue <issue url> --reason "<one line>"
```

This moves the entry to `Archive/<Conjecture>/`, records the date, the issue and the reason in its metadata, and removes it from the build. The id is kept and never reused. The site lists archived entries under the conjecture, marked as archived, so that any proof that claimed `#id` can still be traced to the exact text it claimed to prove.
