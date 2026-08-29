# Ownership protocol: whose work is whose

*Class: **LIVING** · Last-updated: 2026-08-29 · Review-by: 2026-09-29 · Owner: founder. Who may change what, and the three ways work legitimately crosses the line. Enforced by `tools/ownership_check.py` in CI. The allocation itself is `docs/20-WORK/WORK-SPLIT.md`; the map is `docs/20-WORK/OWNERSHIP.map`.*

> ## The rule
>
> **You change your own area. You do not change anyone else's.**
>
> Not to fix an obvious bug. Not because it is a one-line change. Not because you are already in the file.
>
> **Three exceptions exist, all of them written down, all of them in Part 2.**

---

## Part 1 · Why this is a rule and not a courtesy

People work this repository through long-running AI sessions. A session has no sense of whose work it is standing in. Asked to fix the console it will happily reach into the API and change a handler, because from inside the session that is the shortest path.

**Three things break when it does.**

**The other person's branch conflicts**, usually while they are mid-way through something stateful, and the merge costs more than the fix saved.

**Ownership stops meaning anything.** If both people edit everything, nobody can answer *"is this mine, and is it finished?"*, and the claim in `NOW.md` becomes decoration.

**Review collapses.** `CODEOWNERS` routes review by path. Work that lands outside its owner's area either bypasses the person who understands it, or blocks on a review they were never expecting.

**A rule in a document does not survive this.** A session reads the rule, then reasons its way past it. **So the boundary is a CI check**, and the check is the actual rule: `tools/ownership_check.py`.

---

## Part 2 · The three ways work legitimately crosses

### 2.1 · Crossing - you need a change in their area to unblock yours

**Preferred: do not do it.** Say what you need, the owner makes the change in their own branch. This is almost always faster than the merge you would otherwise cause, and it keeps the person who understands the code in the loop.

**When it genuinely has to happen in your branch** - a rename that spans both sides, a contract change that is meaningless split in two - then:

1. Write a **crossing note** at `docs/20-WORK/crossings/YYYY-MM-DD-<slug>.md`, in the same change.
2. Name **every path** you touched outside your area. The check reads this file and matches paths literally.
3. The owner reviews and approves. `CODEOWNERS` already requires it; the note is why they can approve quickly.

**A crossing note is a small, real document, not a checkbox.** Template in Part 4.

### 2.2 · Handoff - a step changes owner permanently

Work moves. A step turns out to belong on the other side, or one person is blocked and the other picks it up.

1. Update the plan in `docs/20-WORK/`.
2. Update the claim in `docs/10-STATUS/NOW.md`.
3. Write the handoff into `docs/40-HANDOFF/`: **what is done, what is half-done, what the next action is, and what you know that is not written anywhere.** That last one is the whole value.
4. If the *path* ownership changes and not just the step, update `docs/20-WORK/OWNERSHIP.map` - **and that edit needs both of them to approve**, because it changes the rule itself.

**A handoff with no handoff note is not a handoff, it is an abandonment.**

### 2.3 · Joint work - you genuinely have to build it together

Rare, and specific. The obvious case is **the shared contract everyone depends on**, because everyone depends on it forever and a misunderstanding is expensive in every direction.

1. Claim it in `NOW.md` with **both names and the word `JOINT`**.
2. **Agree the file boundary inside the shared step before starting**, and write it in the claim. "Joint" does not mean both editing the same file; it means one step, two clearly separated parts.
3. Work on one branch, both push to it. **Nobody reviews their own half.**
4. When it lands, record **one** owner in `NOW.md`. Joint ownership is for the duration of the work, never a steady state.

---

## Part 2.4 · What actually needs a second pair of eyes

With a small team, requiring review on every pull request means **every change waits on someone mid-way through their own deep work.** In practice you either sit blocked or start rubber-stamping, and rubber-stamping is worse than no review because it looks like review.

**Review is required on four things and nothing else:**

1. **The shared contract.** Append-only, no undo.
2. **Anything under a crossing note.** The owner must approve their own area.
3. **The permission and auth paths.** A quiet mistake here is a trust failure.
4. **Anything you have marked protected**, and any change to a quality bar.

**Everything else self-merges on a green fast gate.** The ownership check already prevents the failure that reviews were mostly guarding against, and the benches catch what a skim-read never would.

---

## Part 3 · Two things that are never allowed

**`packages/shared` is never hand-edited, by anyone, in either half.** It is generated by `make gen` from the event schemas. If it is wrong, the schema is wrong. Change the schema, regenerate, commit the result. CI fails on a hand edit and separately fails if the generated output has drifted from its source.

**Fixing something in the other area silently.** If you find a real bug outside your area, **report it, do not repair it**. Add a line to `NOW.md` under the owner's claim, or open an issue. You do not know what they are mid-way through, and a helpful fix landing under someone else's feet is the most annoying way to be right.

---

## Part 4 · The crossing note

`docs/20-WORK/crossings/2026-09-04-projection-read-shape.md`

```markdown
# Crossing · <one line: what and why>

*Date: YYYY-MM-DD · From: <person> · Into: <person> · Task: <TASK-ID>*

## Paths touched
- services/api/internal/handlers/orders.go

## Why this could not be done by the owner
<The honest reason. "It was quicker" is not one. A rename that spans
both sides, or a contract change that is meaningless split in two, is.>

## What changed, in one paragraph
<So the owner can review without reading the diff cold.>

## What the owner should check
<The thing you are least sure about. Be specific.>

## Agreed with
<name>, <when and where>
```

**Path lines must match what CI sees**, so paste them from `git diff --name-only`.

---

## Part 5 · How the check works

**Your role comes from the branch name.** Self-declaring, no GitHub API, works locally:

```
alex/T-001-api-skeleton
sam/T-002-web-shell
```

A branch that declares no role fails the check. **That is deliberate**: the branch name is how the boundary is known.

**Run it before you push:**

```bash
python tools/ownership_check.py
```

| Outcome | Meaning |
|---|---|
| pass | every file is yours, shared, or covered by a crossing note in this change |
| fail, trespass | named files belong to the other person. Ask them, or write the note |
| fail, generated | `packages/shared` was hand-edited. Fix the schema instead |
| fail, no role | branch does not start a key from `tracker/people.toml` |

**Longest matching prefix wins**, so `services/api/handlers` (one owner) beats `services/api` (another). This is the mechanism: **an ownership split has to be visible in the directory tree, or it cannot be checked.**

An unmapped new path defaults to `SHARED`, so the check never blocks genuinely new work. **Map it as soon as it has an owner.**

## Changelog

| Date | Change | Why | By |
|---|---|---|---|
| 2026-08-29 | created | Two people through long-running AI sessions on one monorepo. A session has no sense of whose work it is standing in, and a rule in prose does not survive that, so the boundary is a CI check | <person> |
