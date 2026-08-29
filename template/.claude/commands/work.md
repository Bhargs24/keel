---
description: Decide what to build next, verify the ground is solid, then start it
argument-hint: [optional TASK-ID or description. Leave empty to let Claude decide]
---

**$ARGUMENTS**

**If that is empty, you decide what to build next. Do not ask the developer.**
They should not have to hold the sequence in their head; that is what the build
plan, the dependency graph and this command are for.

If they did name something, still run the whole procedure below and **say plainly
if their choice is not the right next thing.** They may have a reason you do not
know, and if they repeat it, do it.

---

# Step 1 · Verify the ground before adding to it

**Never start new work on a foundation that is not solid.** In order:

**1.1 Anything already in flight?**

```
python tools/track.py status
python tools/track.py mine
```

If a task is `doing` or `blocked`, **that is the answer.** Finish it, unblock
it, or hand it over. Two half-finished things are worth less than one finished
one. Say so and stop here.

**1.2 Is what is marked done actually done?**

Audit the **most recent completions**, and **every dependency of the task you
are about to recommend**. Not all of history: the ones this decision rests on.

For each, read its `Test / DoD` in `your build plan or issue tracker` and
check it holds. If a dependency is marked done but does not meet its own
definition of done, **that is the next task**, not the one after it. Move it back:

```
python tools/track.py block <ID> --on "" "audit: <the clause that fails>"
```

**Building on a task that is done-in-name-only is the most expensive mistake
available**, because everything after it inherits the gap.

**1.3 Is anything out of order?**

```
python tools/track.py check
```

Then look for what the check cannot: a task done whose dependency is not, work
started in a later milestone while an earlier one has open items, a screen built
before the projection it reads. **Say what you find.**

---

# Step 2 · Build the candidate set

Tasks that are `todo`, owned by this person, with **every dependency genuinely
done** — verified in 1.2, not merely marked.

```
python tools/track.py next --for <name>
python tools/track.py blocked
```

If the set is empty, go to Step 5.

---

# Step 3 · Rank them, in this order

Apply these in sequence. An earlier rule beats a later one.

**1 · Earliest milestone first.** Never build M2 while M0 has open work. The
milestones are ordered for a reason and skipping ahead produces work that gets
rebuilt.

**2 · What unblocks the other person.** A task holding up the other person is
worth more than one that only unblocks you, because a blocked person produces
nothing. Weigh this heavily.

**3 · Benches before the things they gate.** No capture mode is wired before its
bench is green. A bench that gates several steps is high value even though it
ships nothing a user sees.

**4 · The critical path to this milestone's deliverable.** Read the milestone's
line in your roadmap. Which open task does that
deliverable actually require? Prefer it over adjacent work in the same milestone.

**5 · Risk first within a tier.** Between two otherwise equal tasks, prefer the
one that would **invalidate more later work if it turns out wrong.** Finding
that out early is worth more than finishing something safe.

**6 · Then, and only then, size.** Prefer the one that finishes.

---

# Step 4 · Sanity-check against the whole plan

Before recommending, check the decision against things the tracker does not know:

- **`BUILD-ROADMAP.md`** — does building this now match what the milestone is
  meant to deliver?
- **`docs/20-WORK/INTEGRATION.md` if you have one** — is this on the right side of the seam, and does it
  respect the ownership map?
- **`docs/40-HANDOFF/`** — did the last session leave a reason to do something
  else first?
- **your open-decisions list** — is there an open founder decision or an
  unprovisioned account that this work will hit halfway through?
- **The unassigned work.** `CO-001`, `CH-001`, `DS-001` and the spikes are on the
  critical path with nobody on them.

> **If the highest-value next action is not a coding task, say so.** Sometimes
> the honest answer is *"the best thing you can do today is not this branch, it
> is the content hire, or `SP-01`, which needs twenty pages of real student work
> and no code at all."* **Say it. Do not recommend a task because a task is what
> was asked for.**

---

# Step 5 · Recommend, with the reasoning visible

Give the developer, in under fifteen lines:

- **The verdict on the ground.** What is in flight, whether what is done holds,
  whether anything is out of order. **If any of this is bad, that is the whole
  answer and there is no recommendation yet.**
- **The task you chose**, and **why, against the ranking above.** Name the rule
  that decided it: *"it unblocks four of the other person's tasks"*, *"it is the only M0
  item left on the critical path"*.
- **The runner-up**, in one line, so they can overrule you with information.
- **What it will touch and what done looks like**, from the step's block.
- **Anything that will bite** — an unmade decision, a missing account, a spec
  gap you can already see.

If the candidate set was empty: say what everyone is waiting on, who could
unblock it, and **what the most useful non-code action is right now.**

**Then wait for a yes.**

---

# Step 6 · On yes, run the whole ceremony yourself

1. Claim it in `docs/10-STATUS/NOW.md`, commit. Claiming is a commit.
2. `python tools/track.py start <ID>`
3. `git switch -c <owner>/<ID>-<short-slug>` — the prefix is how CI knows whose
   files are whose, and a branch without one fails.
4. `your spec-fetch step, if you have one` if the specifications are missing.
5. Read the step's full block, then the surface or engine spec it points at.
   **Do not infer behaviour that is written down.**
6. Say in four or five lines what you are about to do, and **anything in the
   spec that looks wrong or ambiguous.**
7. **Above T0 blast radius, enter plan mode first** (your change protocol).

Then build, and `track log <ID> "..."` on every real decision, surprise or dead
end, unprompted.
